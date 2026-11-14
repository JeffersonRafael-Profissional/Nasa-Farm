# Smart Rotation Engine 🛰️🌱
> **NASA Space Apps Challenge 2026** — *Desafio: Field Shift: Adapting Farms with NASA Data*  
> **Repositório Oficial:** [JeffersonRafael-Profissional/Nasa-Farm](https://github.com/JeffersonRafael-Profissional/Nasa-Farm)

---

## 🌍 Visão Geral do Projeto

As mudanças climáticas intensificam extremos de temperatura, secas severas e degradação física do solo. O desafio do produtor agrícola não é apenas saber a previsão do tempo, mas **decidir com embasamento científico quais culturas plantar, em qual sequência, quando dessecar coberturas e sob quais restrições práticas**.

O **Smart Rotation Engine** é uma ferramenta de suporte à decisão (decision-support tool) que combina observações orbitais da NASA, perfis físico-químicos de solo e dados ecofisiológicos de culturas para avaliar e recomendar estratégias de rotação de culturas na fronteira multiobjetivo de Pareto.

---

## 🚀 Pilares da Solução e Atendimento ao Desafio Oficial

| Requisito do Desafio NASA | Como o Smart Rotation Engine Implementa |
| :--- | :--- |
| **1. Análise Espaço-Temporal** | Detecta janelas contínuas de solo exposto (`NDVI < 0.25`), estresse hídrico na zona radicular (`SMAP sm_rootzone < 0.20 m³/m³`) e estresse térmico (`surface_temp > 29°C`), identificando oportunidades exatas para culturas de cobertura. |
| **2. Comparação de Cenários (≥ 3)** | Avalia a **Monocultura Convencional (Linha de Base)** vs. **Rotação Padrão Regional (Milho-Soja)** vs. **Rotação Regenerativa Resiliente (Milho + Centeio -> Soja + Trigo)** com evidências explícitas de satélite e validação local. |
| **3. Harmonização de Dados** | Compatibiliza dados de resoluções temporais distintas (diário NASA POWER e GPM; quinzenal SMAP L4 e MODIS) em uma grade fenológica comum. |
| **4. Otimização Multiobjetivo (Pareto)** | Equilibra simultaneamente: **Maximizar Produtividade**, **Minimizar Demanda Hídrica**, **Minimizar Risco Climático** e **Maximizar Conservação do Solo / Redução de Custos de Insumos**. |
| **5. Design Centrado no Produtor** | Interface explicável com restrições reais de maquinário (semeadora direta, plataformas), orçamento e disclaimer explícito de suporte à decisão. |

---

## 📡 Pipeline de Dados Utilizado

1. **NASA SMAP L4 (`NASA/SMAP/SPL4SMGP/008`):** Umidade superficial (0–5 cm) e radicular (0–100 cm).
2. **NASA GPM IMERG:** Precipitação acumulada quinzenal para risco de erosão e recarga hídrica.
3. **MODIS Terra (MOD13Q1) & HLS:** Vigor de biomassa (`NDVI`/`EVI`) e detecção de períodos de solo desprotegido.
4. **MODIS (MOD16A2) & ECOSTRESS:** Evapotranspiração real vs potencial (`ET` e `PET`) para balanço hídrico.
5. **NASA POWER API (`power.larc.nasa.gov`):** Radiação solar, temperaturas cardeais e histórico climático diário.
6. **FAO EcoCrop & USDA NRCS Soil Survey / SoilGrids:** Fisiologia das culturas ($K_c$, temperaturas cardeais, fixação biológica de $N_2$) e perfil físico do solo de Ames, Iowa (Clarion Loam).

---

## 📂 Estrutura do Repositório

```
Nasa-Farm/
├── Data/                                  # Conjuntos de dados brutos e harmonizados
│   ├── crop_ecophysiology_fao.json / .csv # Parâmetros ecofisiológicos FAO (Milho, Soja, Centeio, etc.)
│   ├── soil_profile_ames_iowa.json        # Perfil físico-hídrico do solo de Ames, Iowa (Clarion Loam)
│   ├── nasa_satellite_harmonized_series.csv # Série quinzenal harmonizada (SMAP, MODIS, GPM, ET/PET)
│   ├── nasa_power_ames_iowa_daily.json/.csv # Série diária climática baixada via NASA POWER API
│   ├── crop_rotation_rules.json           # Base de conhecimento e sinergias agronômicas
│   ├── rotation_scenarios_comparison.json # Comparativo quantitativo dos 3 cenários
│   └── README.md                          # Metadados e catálogo da pasta Data
├── src/
│   ├── engine/                            # Core do Motor de Recomendação
│   │   ├── models.py                      # Modelos de dados tipados
│   │   ├── harmonizer.py                  # Harmonização espaço-temporal
│   │   ├── stress_detector.py             # Detecção de solo exposto e estresse hídrico
│   │   ├── pareto_optimizer.py            # Otimizador multiobjetivo de Pareto
│   │   └── recommendation.py              # Orquestrador da recomendação
│   └── web/                               # Interface Web Interativa (Dashboard)
│       ├── server.py                      # Servidor HTTP nativo com API REST
│       └── static/                        # Frontend responsivo (Tailwind, Chart.js)
│           ├── index.html                 # Painel interativo com KPIs e gráficos
│           ├── app.js                     # Comunicação com a API e renderização dinâmica
│           └── style.css                  # Estilos complementares
├── scripts/
│   ├── fetch_nasa_power.py                # Script de download ao vivo da API NASA POWER
│   └── run_analysis_cli.py                # Ferramenta CLI para diagnóstico em terminal
├── tests/
│   └── test_engine.py                     # Suíte de testes unitários do motor
├── main.py                                # Ponto de entrada (Web Dashboard ou CLI)
├── requirements.txt                       # Dependências opcionais
└── README.md                              # Documentação do projeto
```

---

## 💻 Como Executar

### 1. Pré-requisitos
* Python 3.10+ instalado.
* O projeto foi desenvolvido de forma modular e independente: o dashboard web utiliza bibliotecas nativas de Python (`http.server`) e CDN modernos para o frontend, garantindo execução imediata sem compilações complexas.

### 2. Iniciar o Dashboard Web Interativo
Execute na raiz do projeto:
```bash
python main.py
```
Abra o navegador no endereço:
👉 **`http://127.0.0.1:8000`**

### 3. Executar o Diagnóstico via Linha de Comando (CLI)
Para gerar o relatório agronômico diretamente no terminal:
```bash
python main.py --cli
```

### 4. Executar os Testes Unitários
```bash
python main.py --test
```

---

## 📊 Principais Resultados no Estudo de Caso (Ames, Iowa)

Ao comparar a Linha de Base (Monocultura de Milho) com a **Estratégia Regenerativa Resiliente (Milho + Centeio -> Soja + Trigo)**:
* **Redução de 84% na erosão laminar do solo** (de $11.2\text{ t/ha/ano}$ para $1.8\text{ t/ha/ano}$).
* **Diminuição de 157 dias de solo desprotegido** (de $195\text{ dias}$ para apenas $38\text{ dias}$).
* **Economia média de \$148/ha em adubos nitrogenados** via fixação biológica e sequestro radicular de nitratos.
* **Amortecimento de secas estivais:** Retenção superior de umidade radicular no SMAP L4 durante o veranico de julho/agosto.

---

## ⚠️ Aviso de Suporte à Decisão (Disclaimer)

Esta ferramenta apoia — mas não substitui — a decisão humana e a consultoria agronômica local. As estimativas baseiam-se em dados orbitais da NASA e modelagem agroambiental determinística. Recomenda-se realizar amostragem laboratorial de solo e validação in loco para ajustes de dessecação e manejo fitossanitário.
