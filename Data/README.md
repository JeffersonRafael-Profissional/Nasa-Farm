# Repositório de Dados: Smart Rotation Engine (NASA Space Apps 2026)

Este diretório contém os conjuntos de dados levantados e estruturados para alimentar o motor de decisão do projeto **Field Shift: Adapting Farms with NASA Data**.

Região de referência inicial do estudo: **Ames, Iowa, EUA** (`Lat: 42.0308, Lon: -93.6319`), epicentro agrícola do Corn Belt, permitindo cruzamento com estações de pesquisa e ampla disponibilidade de dados de satélite e solo.

---

## 📁 Estrutura de Arquivos em `/Data`

### 1. Dados Climáticos e Agroclimatologia (NASA POWER API)
- **`nasa_power_ames_iowa_daily.json` & `nasa_power_ames_iowa_daily.csv`**:
  - **Fonte:** NASA POWER API (`power.larc.nasa.gov`), Comunidade de Agroclimatologia (`community=AG`).
  - **Série Temporal:** 366 dias (Ano completo de 2024, resolução diária).
  - **Variáveis Chave:**
    - `T2M`: Temperatura média a 2 metros (°C)
    - `T2M_MAX` / `T2M_MIN`: Temperaturas extremas diárias (°C)
    - `PRECTOTCORR`: Precipitação corrigida diária (mm/dia)
    - `ALLSKY_SFC_SW_DWN`: Radiação solar incidente (MJ/m²/dia)
    - `RH2M`: Umidade relativa do ar a 2 metros (%)
    - `GWETROOT`: Umidade relativa na zona radicular do solo (0–1)
    - `GWETTOP`: Umidade superficial do solo (0–1)

### 2. Série Temporal Harmonizada de Satélites da NASA
- **`nasa_satellite_harmonized_series.csv`**:
  - **Fontes Integradas:** NASA SMAP L4, NASA GPM IMERG, MODIS (MOD13Q1 e MOD16A2) / ECOSTRESS.
  - **Cadência:** Composições harmonizadas de 16 dias ao longo do ano safra.
  - **Variáveis Chave:**
    - `smap_sm_surface_m3m3`: Umidade superficial 0–5 cm (m³/m³)
    - `smap_sm_rootzone_m3m3`: Umidade na zona radicular 0–100 cm (m³/m³)
    - `smap_sm_wetness_ratio`: Grau de saturação radicular (0 a 1)
    - `gpm_precipitation_mm`: Volume acumulado de chuvas (mm/16 dias)
    - `modis_ndvi` / `modis_evi`: Vigor vegetal e índice de biomassa fotossintética
    - `ecostress_et_mm` / `modis_pet_mm`: Evapotranspiração real vs potencial
    - `water_deficit_mm`: Balanço hídrico derivado (`PET - ET`)
    - `surface_temp_k`: Temperatura da superfície em Kelvin
    - `bare_soil_flag`: Indicador booleano de solo descoberto (`NDVI < 0.25` sem cobertura de neve)
    - `stress_risk_index`: Nível de risco de estresse combinado (`Low`, `Moderate`, `High`)

### 3. Ecofisiologia e Requisitos das Culturas (FAO EcoCrop & Agronomia)
- **`crop_ecophysiology_fao.json` & `crop_ecophysiology_fao.csv`**:
  - **Culturas Cadastradas:** Milho (*Zea mays*), Soja (*Glycine max*), Centeio de Inverno (*Secale cereale*), Trigo de Inverno (*Triticum aestivum*), Alfalfa (*Medicago sativa*).
  - **Parâmetros:**
    - Temperaturas cardeais: $T_{base}$, $T_{ótima\_min}$, $T_{ótima\_max}$, $T_{máxima}$
    - Demanda hídrica total no ciclo (mm) e coeficientes de cultura ($K_c$ inicial, médio e final)
    - Profundidade efetiva do sistema radicular ($m$)
    - Fixação biológica de nitrogênio ($N_2$) e crédito residual de N para a cultura seguinte
    - Relação C:N dos resíduos e biomassa gerada
    - Capacidade de supressão de plantas daninhas e quebra de patógenos (ex.: Nematoide do Cisto da Soja)

### 4. Perfil Físico-Químico e Hídrico do Solo
- **`soil_profile_ames_iowa.json`**:
  - **Fonte:** USDA NRCS Web Soil Survey & SoilGrids 250m.
  - **Solo:** Franco Clarion (*Typic Hapludolls*, Mollisols).
  - **Parâmetros:**
    - Granulometria: 38% Areia, 42% Silte, 20% Argila
    - Capacidade de Água Disponível (AWC): 0.18 cm/cm (180 mm nos 100 cm radiculares)
    - Limites hidráulicos: Saturação (46%), Capacidade de Campo (31%), Ponto de Murcha Permanente (13%)
    - Matéria Orgânica do Solo (MOS): 3.8% (SOC de 22 g/kg)
    - pH: 6.4 | Condutividade hidráulica saturada: 18.5 mm/h
    - Fatores de erodibilidade e vulnerabilidade a encrostamento superficial.

### 5. Regras Agronômicas do Motor de Decisão
- **`crop_rotation_rules.json`**:
  - Mapeamento formal de sinergias, créditos de adubação, penalidades de monocultura contínua, janelas de dessecação de coberturas e quebra biológica de patógenos.

### 6. Cenários de Comparação Multiobjetivo
- **`rotation_scenarios_comparison.json`**:
  - **Cenário 1 (Linha de Base):** Monocultura de Milho Contínuo (alto uso de insumos, solo exposto por 195 dias, alta erosão e pressão sanitária).
  - **Cenário 2 (Padrão Regional):** Rotação Milho - Soja (aproveitamento do crédito de N da soja, redução parcial de custos).
  - **Cenário 3 (Regenerativo Resiliente):** Rotação Quádrupla Milho + Centeio de Cobertura -> Soja + Trigo (solo protegido o ano todo, menor déficit hídrico, aumento de carbono e resiliência máxima na fronteira de Pareto).
  - Atende diretamente à exigência da NASA de comparar $\ge 3$ estratégias com evidências em dados e explicabilidade.
