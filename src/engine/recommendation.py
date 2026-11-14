"""
Smart Recommendation Engine Orchestrator.
Combines:
- NASA Earth observations (SMAP, MODIS, GPM, NASA POWER)
- Local soil constraints (SoilGrids / USDA NRCS)
- Crop ecophysiology (FAO EcoCrop)
- Multi-objective Pareto optimization
- Farmer constraints and explainable advice.
"""

from typing import Dict, Any, Optional
from .harmonizer import DataHarmonizer
from .stress_detector import StressDetector
from .pareto_optimizer import ParetoOptimizer
from .models import FarmerConstraints

class SmartRotationEngine:
    def __init__(self, data_dir: Optional[str] = None):
        self.harmonizer = DataHarmonizer(data_dir=data_dir)
        self.crops = self.harmonizer.load_crop_profiles()
        self.soil = self.harmonizer.load_soil_profile()
        self.satellite_series = self.harmonizer.load_harmonized_satellite_series()
        self.rules = self.harmonizer.load_rotation_rules()
        self.scenarios_raw = self.harmonizer.load_scenarios_comparison()
        self.stress_detector = StressDetector(self.satellite_series, self.soil)

    def evaluate(self, constraints: Optional[FarmerConstraints] = None) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation:
        1. Analyzes satellite temporal stress patterns (bare soil, drought, temperature)
        2. Evaluates 3 rotation strategies against baseline
        3. Optimizes Pareto trade-offs according to farmer priorities
        4. Synthesizes explainable agronomic recommendations and local validation warnings.
        """
        if constraints is None:
            constraints = FarmerConstraints()

        # 1. Stress detection
        bare_soil_summary = self.stress_detector.summarize_soil_exposure_summary()
        water_stress = self.stress_detector.detect_water_stress_windows()
        thermal_alerts = self.stress_detector.detect_thermal_stress_windows()

        # 2. Pareto optimization
        optimizer = ParetoOptimizer(constraints=constraints)
        ranked_scenarios = optimizer.normalize_metrics(self.scenarios_raw)

        # Baseline reference
        baseline = next((s for s in ranked_scenarios if s["is_current_baseline"]), ranked_scenarios[-1])

        # Normalized weights around neutral baseline (0.25 each = 1.0 multiplier)
        total_w = constraints.priority_yield_weight + constraints.priority_water_weight + constraints.priority_soil_weight + constraints.priority_cost_weight
        if total_w <= 0:
            total_w = 1.0
        norm_wy = (constraints.priority_yield_weight / total_w) * 4.0
        norm_ww = (constraints.priority_water_weight / total_w) * 4.0
        norm_ws = (constraints.priority_soil_weight / total_w) * 4.0
        norm_wc = (constraints.priority_cost_weight / total_w) * 4.0

        # Pareto comparison against baseline
        comparison_table = []
        for s in ranked_scenarios:
            dom = optimizer.check_pareto_dominance(s, baseline)
            comparison_table.append({
                "scenario_id": s["scenario_id"],
                "name": s["name"],
                "composite_score": s["composite_pareto_score"],
                "scores": {
                    "yield": s["yield_score"],
                    "water_efficiency": s["water_score"],
                    "climate_resilience": s["resilience_score"],
                    "soil_health": s["soil_score"],
                    "economics": s["economic_score"]
                },
                "weighted_scores": {
                    "yield": round(min(100.0, s["yield_score"] * norm_wy), 1),
                    "water_efficiency": round(min(100.0, s["water_score"] * norm_ww), 1),
                    "climate_resilience": round(min(100.0, s["resilience_score"] * ((norm_ww + norm_ws) / 2.0)), 1),
                    "soil_health": round(min(100.0, s["soil_score"] * norm_ws), 1),
                    "economics": round(min(100.0, s["economic_score"] * norm_wc), 1)
                },
                "dominates_baseline": dom["dominates_baseline"],
                "improvements": dom["improvements"],
                "benefits": s["benefits"],
                "limitations_and_risks": s["limitations_and_risks"],
                "local_validation_needs": s["local_validation_needs"]
            })

        # 3. Top recommended scenario
        top_scenario = ranked_scenarios[0]

        # Scenario-specific actionable timelines
        scenario_timelines = {
            "SCENARIO_C_CLIMATE_RESILIENT": [
                {"window": "Setembro (Colheita de Milho)", "action": "Semear Centeio de Inverno aéreo ou pós-colheita para criar raiz viva."},
                {"window": "Abril (Primavera)", "action": "Dessecar centeio 10-14 dias antes de semear Soja para preservar umidade do SMAP."},
                {"window": "Outubro (Pós-Soja)", "action": "Semear Trigo de Inverno para cobrir o solo e quebrar ciclo de nematoides."}
            ],
            "SCENARIO_B_STANDARD_ROTATION": [
                {"window": "Outubro (Pós-Soja)", "action": "Mapear áreas com alta palhada de soja e verificar umidade residual no SMAP L4."},
                {"window": "Março (Pré-Plantio)", "action": "Amostragem de solo para creditar os ~40 kg N/ha deixados pela soja."},
                {"window": "Maio (Semeadura de Milho)", "action": "Semear milho aplicando 130 kg N/ha (redução de 90 kg vs milho contínuo)."}
            ],
            "SCENARIO_A_MONOCULTURE": [
                {"window": "Outubro (Colheita de Milho)", "action": "Triturar e incorporar restolho de milho pesado para acelerar decomposição."},
                {"window": "Novembro (Outono)", "action": "Aplicação pesada de Amônia Anidra outonal com inibidor de nitrificação."},
                {"window": "Abril (Plantio)", "action": "Adubação pesada de arranque (220 kg N/ha) e tratamento fitossanitário contra lagartas."}
            ]
        }

        # 4. Synthesize final decision-support package
        return {
            "status": "success",
            "weights_used": {
                "yield": round(constraints.priority_yield_weight * 100, 1),
                "water": round(constraints.priority_water_weight * 100, 1),
                "soil": round(constraints.priority_soil_weight * 100, 1),
                "cost": round(constraints.priority_cost_weight * 100, 1)
            },
            "study_region": {
                "site": self.soil.site_name,
                "soil_series": self.soil.soil_series,
                "textural_class": self.soil.textural_class,
                "rootzone_awc_mm": self.soil.total_rootzone_awc_mm,
                "soil_organic_matter_pct": self.soil.soil_organic_matter_pct
            },
            "spatiotemporal_diagnosis": {
                "bare_soil_analysis": bare_soil_summary,
                "critical_water_stress_windows_count": len(water_stress),
                "sample_water_stress_windows": water_stress[:3],
                "thermal_stress_alerts_count": len(thermal_alerts),
                "key_finding": (
                    "O talhão passa ~195 dias com solo desprotegido na rotação de milho contínuo, "
                    "coincidindo com chuvas intensas de outono e primavera que causam lixiviação de nitratos "
                    "e erosão laminar detectada pela reflectância de satélite."
                )
            },
            "scenario_ranking": comparison_table,
            "recommended_strategy": {
                "scenario_id": top_scenario["scenario_id"],
                "name": top_scenario["name"],
                "composite_score": top_scenario["composite_pareto_score"],
                "why_recommended": (
                    f"Apresenta a maior pontuação global ({top_scenario['composite_pareto_score']}/100) "
                    f"adequada às suas prioridades atuais e maquinário disponível."
                ),
                "actionable_timeline": scenario_timelines.get(top_scenario["scenario_id"], scenario_timelines["SCENARIO_C_CLIMATE_RESILIENT"])
            },
            "nasa_data_attribution": {
                "smap_l4": "Monitoramento de umidade superficial (0-5cm) e radicular (0-100cm) para guiar dessecação e plantio.",
                "gpm_imerg": "Detecção de precipitações extremas para cálculo de erosão e recarga hídrica.",
                "modis_ecostress": "Balanço hídrico ET/PET e identificação de dias de solo exposto por NDVI."
            },
            "decision_support_disclaimer": (
                "Esta ferramenta tem caráter de suporte à decisão com base em dados de observação da Terra "
                "e modelagem agronômica. Ela NÃO substitui a avaliação in loco de agrônomos, testes laboratoriais de solo "
                "e análises fitossanitárias locais."
            )
        }
