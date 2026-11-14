// Smart Rotation Engine - Interactive Frontend Logic
let radarChartInstance = null;
let timelineChartInstance = null;
let latestEvaluationData = null;
let currentRadarMode = "weighted"; // 'weighted' or 'absolute'
let recalculateTimeout = null;

document.addEventListener("DOMContentLoaded", () => {
  setupSliders();
  setupModeButtons();
  loadInitialData();

  document.getElementById("btn-recalculate").addEventListener("click", () => {
    recalculateEvaluation();
  });
});

function setupModeButtons() {
  const btnWeighted = document.getElementById("btn-mode-weighted");
  const btnAbsolute = document.getElementById("btn-mode-absolute");

  btnWeighted.addEventListener("click", () => {
    currentRadarMode = "weighted";
    btnWeighted.className = "px-2.5 py-1 rounded bg-blue-600 text-white font-medium transition text-[11px]";
    btnAbsolute.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white transition text-[11px]";
    if (latestEvaluationData) {
      updateRadarChart(latestEvaluationData.scenario_ranking);
    }
  });

  btnAbsolute.addEventListener("click", () => {
    currentRadarMode = "absolute";
    btnAbsolute.className = "px-2.5 py-1 rounded bg-blue-600 text-white font-medium transition text-[11px]";
    btnWeighted.className = "px-2.5 py-1 rounded text-slate-400 hover:text-white transition text-[11px]";
    if (latestEvaluationData) {
      updateRadarChart(latestEvaluationData.scenario_ranking);
    }
  });
}

function setupSliders() {
  const sliders = [
    { id: "slider-yield", label: "val-yield" },
    { id: "slider-water", label: "val-water" },
    { id: "slider-soil", label: "val-soil" },
    { id: "slider-cost", label: "val-cost" }
  ];

  sliders.forEach(s => {
    const el = document.getElementById(s.id);
    const lbl = document.getElementById(s.label);
    
    // Live update while sliding
    el.addEventListener("input", () => {
      lbl.innerText = `${el.value}%`;
      // Debounce slightly to make dragging smooth
      if (recalculateTimeout) clearTimeout(recalculateTimeout);
      recalculateTimeout = setTimeout(() => {
        recalculateEvaluation();
      }, 40);
    });
  });

  // Checkboxes also trigger live update
  ["chk-drill", "chk-cornhead", "chk-grainhead"].forEach(chkId => {
    const chk = document.getElementById(chkId);
    if (chk) {
      chk.addEventListener("change", () => recalculateEvaluation());
    }
  });
}

async function loadInitialData() {
  try {
    await loadSatelliteTimeline();
    await recalculateEvaluation();
  } catch (err) {
    console.error("Error loading initial data:", err);
  }
}

async function loadSatelliteTimeline() {
  const res = await fetch("/api/satellite-series");
  const data = await res.json();
  const series = data.series || [];

  const labels = series.map(d => d.period_start.slice(5)); // MM-DD
  const smapMoisture = series.map(d => d.smap_sm_rootzone);
  const modisNdvi = series.map(d => d.modis_ndvi);
  const gpmRain = series.map(d => d.gpm_precipitation_mm);

  const ctx = document.getElementById("timelineChart").getContext("2d");
  timelineChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "SMAP Umidade Raiz (m³/m³)",
          data: smapMoisture,
          borderColor: "#22d3ee",
          backgroundColor: "rgba(34, 211, 238, 0.1)",
          yAxisID: "y-moisture",
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2
        },
        {
          label: "MODIS NDVI (Vigor Vegetal)",
          data: modisNdvi,
          borderColor: "#34d399",
          backgroundColor: "rgba(52, 211, 153, 0.15)",
          fill: true,
          yAxisID: "y-ndvi",
          tension: 0.3,
          borderWidth: 2,
          pointRadius: 2
        },
        {
          label: "GPM Precipitação (mm/16d)",
          data: gpmRain,
          type: "bar",
          backgroundColor: "rgba(59, 130, 246, 0.5)",
          yAxisID: "y-rain",
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        },
        "y-moisture": {
          type: "linear",
          position: "left",
          min: 0.10,
          max: 0.45,
          title: { display: true, text: "SMAP (m³/m³)", color: "#22d3ee", font: { size: 10 } },
          ticks: { color: "#94a3b8" },
          grid: { color: "rgba(255, 255, 255, 0.05)" }
        },
        "y-ndvi": {
          type: "linear",
          position: "right",
          min: 0,
          max: 1.0,
          title: { display: true, text: "NDVI", color: "#34d399", font: { size: 10 } },
          ticks: { color: "#94a3b8" },
          grid: { drawOnChartArea: false }
        },
        "y-rain": {
          type: "linear",
          position: "right",
          min: 0,
          max: 100,
          display: false,
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

async function recalculateEvaluation() {
  const yieldWeight = parseFloat(document.getElementById("slider-yield").value) / 100;
  const waterWeight = parseFloat(document.getElementById("slider-water").value) / 100;
  const soilWeight = parseFloat(document.getElementById("slider-soil").value) / 100;
  const costWeight = parseFloat(document.getElementById("slider-cost").value) / 100;

  const payload = {
    has_no_till_drill: document.getElementById("chk-drill").checked,
    has_row_crop_planter: true,
    has_combine_corn_head: document.getElementById("chk-cornhead").checked,
    has_combine_grain_head: document.getElementById("chk-grainhead").checked,
    priority_yield_weight: yieldWeight,
    priority_water_weight: waterWeight,
    priority_soil_weight: soilWeight,
    priority_cost_weight: costWeight
  };

  const res = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  latestEvaluationData = data;
  renderResults(data);
}

function renderResults(data) {
  // Update Radar Chart
  updateRadarChart(data.scenario_ranking);

  // Update Pareto Ranking Bars
  updateParetoRankingBars(data.scenario_ranking);

  // Update KPI Cards
  const top = data.recommended_strategy;
  document.getElementById("kpi-resilience").innerHTML = `${top.composite_score}<span class="text-sm font-normal text-slate-500">/100</span>`;

  // Render Scenario Cards
  const container = document.getElementById("scenarios-container");
  container.innerHTML = "";

  data.scenario_ranking.forEach((s, idx) => {
    const isTop = idx === 0;
    const card = document.createElement("div");
    card.className = `rounded-xl p-5 border flex flex-col justify-between transition ${
      isTop 
        ? "bg-slate-900/90 border-emerald-500/50 shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/30" 
        : "bg-slate-950/60 border-slate-800"
    }`;

    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs px-2.5 py-1 rounded-full font-medium ${
            isTop 
              ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
              : "bg-slate-800 text-slate-400"
          }">
            ${isTop ? "★ ÓTIMO DE PARETO" : (s.scenario_id.includes("A") ? "LINHA DE BASE" : "PADRÃO")}
          </span>
          <div class="text-right">
            <span class="text-xs text-slate-400 block text-[10px]">SCORE GLOBAL</span>
            <span class="font-extrabold text-lg ${isTop ? "text-emerald-400" : "text-slate-200"}">${s.composite_score}/100</span>
          </div>
        </div>

        <h3 class="font-bold text-sm text-white mb-2">${s.name}</h3>

        <div class="space-y-1.5 mb-4 text-xs">
          <div class="flex justify-between text-slate-300">
            <span class="text-slate-400">Produtividade:</span>
            <span class="font-medium">${s.scores.yield} pts</span>
          </div>
          <div class="flex justify-between text-slate-300">
            <span class="text-slate-400">Eficiência Hídrica:</span>
            <span class="font-medium">${s.scores.water_efficiency} pts</span>
          </div>
          <div class="flex justify-between text-slate-300">
            <span class="text-slate-400">Saúde do Solo:</span>
            <span class="font-medium">${s.scores.soil_health} pts</span>
          </div>
          <div class="flex justify-between text-slate-300">
            <span class="text-slate-400">Economia Insumos:</span>
            <span class="font-medium">${s.scores.economics} pts</span>
          </div>
        </div>

        <div class="border-t border-slate-800/80 pt-3 space-y-2 text-xs">
          <div>
            <span class="text-emerald-400 font-medium block mb-1"><i class="fa-solid fa-check"></i> Benefícios Principais:</span>
            <ul class="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
              ${s.benefits.slice(0, 2).map(b => `<li>${b}</li>`).join("")}
            </ul>
          </div>

          <div>
            <span class="text-amber-400 font-medium block mb-1"><i class="fa-solid fa-triangle-exclamation"></i> Limitações e Riscos:</span>
            <ul class="list-disc list-inside text-slate-300 space-y-0.5 text-[11px]">
              ${s.limitations_and_risks.slice(0, 2).map(r => `<li>${r}</li>`).join("")}
            </ul>
          </div>
        </div>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 italic">
        <strong>Validação Local:</strong> ${s.local_validation_needs}
      </div>
    `;

    container.appendChild(card);
  });

  // Render Timeline Actions
  const timelineContainer = document.getElementById("timeline-actions");
  timelineContainer.innerHTML = "";
  data.recommended_strategy.actionable_timeline.forEach((item, i) => {
    const el = document.createElement("div");
    el.className = "bg-slate-900 border border-slate-800 rounded-lg p-4 relative";
    el.innerHTML = `
      <div class="text-xs font-bold text-indigo-400 mb-1 flex items-center gap-2">
        <span class="w-5 h-5 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-[10px] text-indigo-300">${i+1}</span>
        ${item.window}
      </div>
      <p class="text-xs text-slate-200">${item.action}</p>
    `;
    timelineContainer.appendChild(el);
  });
}

function updateParetoRankingBars(scenarios) {
  const container = document.getElementById("pareto-ranking-bars");
  if (!container) return;
  container.innerHTML = "";

  const barColors = [
    { bg: "bg-emerald-500", text: "text-emerald-400" },
    { bg: "bg-blue-500", text: "text-blue-400" },
    { bg: "bg-rose-500", text: "text-rose-400" }
  ];

  scenarios.forEach((s, idx) => {
    const color = barColors[idx % 3];
    const shortName = s.name.split(":")[0];
    const score = s.composite_score;

    const row = document.createElement("div");
    row.className = "space-y-1";
    row.innerHTML = `
      <div class="flex justify-between text-[11px]">
        <span class="text-slate-300 font-medium truncate max-w-[140px]">${shortName}</span>
        <span class="font-bold ${color.text}">${score} pts</span>
      </div>
      <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
        <div class="${color.bg} h-2 rounded-full transition-all duration-300 ease-out" style="width: ${score}%"></div>
      </div>
    `;
    container.appendChild(row);
  });
}

function updateRadarChart(scenarios) {
  const ctx = document.getElementById("radarChart").getContext("2d");

  const colors = [
    { border: "#34d399", bg: "rgba(52, 211, 153, 0.25)" }, // Green
    { border: "#60a5fa", bg: "rgba(96, 165, 250, 0.15)" }, // Blue
    { border: "#f87171", bg: "rgba(248, 113, 113, 0.15)" }  // Red
  ];

  // Depending on selected mode (weighted vs absolute)
  const isWeighted = currentRadarMode === "weighted";

  const datasets = scenarios.map((s, idx) => {
    const scores = isWeighted && s.weighted_scores ? s.weighted_scores : s.scores;
    return {
      label: s.name.split(":")[0],
      data: [
        scores.yield,
        scores.water_efficiency,
        scores.climate_resilience,
        scores.soil_health,
        scores.economics
      ],
      borderColor: colors[idx % 3].border,
      backgroundColor: colors[idx % 3].bg,
      borderWidth: idx === 0 ? 3 : 1.5,
      pointRadius: idx === 0 ? 3 : 2
    };
  });

  // Add the farmer's priority polygon layer
  const yieldWeight = parseFloat(document.getElementById("slider-yield").value);
  const waterWeight = parseFloat(document.getElementById("slider-water").value);
  const soilWeight = parseFloat(document.getElementById("slider-soil").value);
  const costWeight = parseFloat(document.getElementById("slider-cost").value);
  const climateWeight = (waterWeight + soilWeight) / 2;

  // Scale weights to 0-100 radar domain
  datasets.push({
    label: "🎯 Perfil de Prioridades",
    data: [
      yieldWeight * 1.5,
      waterWeight * 1.5,
      climateWeight * 1.5,
      soilWeight * 1.5,
      costWeight * 1.5
    ],
    borderColor: "#fbbf24",
    backgroundColor: "rgba(251, 191, 36, 0.08)",
    borderWidth: 2,
    borderDash: [4, 4],
    pointRadius: 3,
    pointBackgroundColor: "#fbbf24"
  });

  if (radarChartInstance) {
    radarChartInstance.data.datasets = datasets;
    radarChartInstance.update();
  } else {
    radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: ["Produtividade", "Eficiência Hídrica", "Resiliência Climática", "Saúde do Solo", "Economia Insumos"],
        datasets: datasets
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 250 },
        scales: {
          r: {
            min: 0,
            max: 100,
            angleLines: { color: "rgba(255, 255, 255, 0.1)" },
            grid: { color: "rgba(255, 255, 255, 0.08)" },
            pointLabels: {
              color: "#cbd5e1",
              font: { size: 10, weight: "bold" }
            },
            ticks: {
              color: "#64748b",
              backdropColor: "transparent",
              stepSize: 20
            }
          }
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#e2e8f0", font: { size: 10 }, boxWidth: 10 }
          }
        }
      }
    });
  }
}
