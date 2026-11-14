"""
Data models for the Smart Rotation Engine.
NASA Space Apps Challenge 2026 - Field Shift: Adapting Farms with NASA Data.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class CropProfile:
    crop_id: str
    common_name: str
    scientific_name: str
    crop_type: str
    cycle_days: int
    planting_window_doy: List[int]
    harvest_window_doy: List[int]
    t_base_c: float
    t_opt_min_c: float
    t_opt_max_c: float
    t_max_c: float
    gdd_required_c: float
    water_demand_mm: List[float]
    kc_mid: float
    n_requirement_kg_ha: float
    n_fixation: bool
    n_credit_kg_ha: float
    c_n_residue_ratio: float
    residue_biomass_t_ha: float
    root_depth_max_m: float
    erosion_protection: str

@dataclass
class SoilProfile:
    site_name: str
    soil_series: str
    textural_class: str
    sand_fraction_pct: float
    silt_fraction_pct: float
    clay_fraction_pct: float
    bulk_density_g_cm3: float
    total_rootzone_awc_mm: float
    saturation_pct: float
    field_capacity_pct: float
    pwp_pct: float
    soil_organic_matter_pct: float
    ph_water: float
    hydrologic_group: str

@dataclass
class FarmerConstraints:
    has_no_till_drill: bool = True
    has_row_crop_planter: bool = True
    has_combine_grain_head: bool = True
    has_combine_corn_head: bool = True
    budget_limit_per_ha_usd: float = 650.0
    irrigation_available: bool = False
    priority_yield_weight: float = 0.35
    priority_water_weight: float = 0.20
    priority_soil_weight: float = 0.30
    priority_cost_weight: float = 0.15

@dataclass
class RotationScenarioResult:
    scenario_id: str
    name: str
    crop_sequence: List[str]
    is_current_baseline: bool
    agronomic_rationale: str
    metrics: Dict[str, Any]
    nasa_data_evidence: Dict[str, str]
    benefits: List[str]
    limitations_and_risks: List[str]
    local_validation_needs: str
    pareto_score: float = 0.0
