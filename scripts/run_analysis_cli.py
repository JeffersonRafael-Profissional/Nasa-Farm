"""
Smart Rotation Engine - CLI Analysis Tool.
NASA Space Apps Challenge 2026.
Executes spatiotemporal diagnosis, scenario evaluation, and Pareto ranking in terminal.
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine import SmartRotationEngine, FarmerConstraints

def run_cli():
    print("=" * 75)
    print("  NASA SPACE APPS CHALLENGE 2026: SMART ROTATION ENGINE")
    print("  Challenge: Field Shift - Adapting Farms with NASA Data")
    print("=" * 75)

    engine = SmartRotationEngine()
    constraints = FarmerConstraints()

    print(f"\n[+] Localizacao de Estudo: {engine.soil.site_name}")
    print(f"    Solo: {engine.soil.soil_series} ({engine.soil.textural_class})")
    print(f"    Capacidade de Agua no Perfil Radicular (AWC): {engine.soil.total_rootzone_awc_mm} mm")
    print(f"    Materia Organica (MOS): {engine.soil.soil_organic_matter_pct}%")

    print("\n[+] Executando Diagnostico Espaco-Temporal (SMAP L4, MODIS, GPM, NASA POWER)...")
    res = engine.evaluate(constraints)
    diag = res["spatiotemporal_diagnosis"]

    print(f"    - Periodos de solo exposto detectados (NDVI < 0.25): {diag['bare_soil_analysis']['total_bare_soil_periods_16d']} composicoes")
    print(f"    - Dias estimados de solo desprotegido / ano: ~{diag['bare_soil_analysis']['total_bare_soil_days_estimated']} dias")
    print(f"    - Janela recomendada para culturas de cobertura: {diag['bare_soil_analysis']['cover_crop_opportunity_window']}")
    print(f"    - Janelas criticas de estresse hidrico no solo: {diag['critical_water_stress_windows_count']}")

    print("\n" + "=" * 75)
    print("  COMPARATIVO DOS 3 CENARIOS DE ROTACAO (PARETO MULTIOBJETIVO)")
    print("=" * 75)

    print(f"{'Cenario':<38} | {'Produtividade':<13} | {'Agua':<8} | {'Solo':<8} | {'Score'}")
    print("-" * 75)
    for s in res["scenario_ranking"]:
        sc = s["scores"]
        name_trunc = s["name"][:36]
        print(f"{name_trunc:<38} | {sc['yield']:<13.1f} | {sc['water_efficiency']:<8.1f} | {sc['soil_health']:<8.1f} | {s['composite_score']:.1f}")

    rec = res["recommended_strategy"]
    print("\n" + "=" * 75)
    print(f"[*] RECOMENDACAO VENCEDORA: {rec['name']}")
    print("=" * 75)
    print(f"Score Composto: {rec['composite_score']}/100")
    print(f"Justificativa Agronomica: {rec['why_recommended']}")
    
    print("\nCronograma de Acoes Recomendadas:")
    for step in rec["actionable_timeline"]:
        print(f"  * {step['window']}: {step['action']}")

    print("\n[AVISO DE SUPORTE A DECISAO]:")
    print(res["decision_support_disclaimer"])
    print("=" * 75)

if __name__ == "__main__":
    run_cli()
