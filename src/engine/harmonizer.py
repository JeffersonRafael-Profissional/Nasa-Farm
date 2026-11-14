"""
Data Harmonizer Module.
Harmonizes multi-source spatial and temporal datasets:
- NASA SMAP L4 (3-hour / 9km aggregated to 16-day)
- NASA GPM IMERG (daily precipitation to 16-day cumulative)
- MODIS / ECOSTRESS (8/16-day ET, PET, NDVI, EVI)
- NASA POWER API (daily agroclimatology)
- FAO EcoCrop & USDA SoilGrids
"""

import os
import json
import csv
from typing import Dict, List, Any
from .models import CropProfile, SoilProfile

class DataHarmonizer:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to repo root / Data
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "Data"))
        else:
            self.data_dir = data_dir

    def load_crop_profiles(self) -> Dict[str, CropProfile]:
        path = os.path.join(self.data_dir, "crop_ecophysiology_fao.json")
        with open(path, "r", encoding="utf-8") as f:
            raw_crops = json.load(f)
        
        crops = {}
        for c in raw_crops:
            crops[c["crop_id"]] = CropProfile(
                crop_id=c["crop_id"],
                common_name=c["common_name"],
                scientific_name=c["scientific_name"],
                crop_type=c["crop_type"],
                cycle_days=c["cycle_days"],
                planting_window_doy=c["planting_window_doy"],
                harvest_window_doy=c["harvest_window_doy"],
                t_base_c=c["thermal_requirements"]["t_base_c"],
                t_opt_min_c=c["thermal_requirements"]["t_opt_min_c"],
                t_opt_max_c=c["thermal_requirements"]["t_opt_max_c"],
                t_max_c=c["thermal_requirements"]["t_max_c"],
                gdd_required_c=c["thermal_requirements"]["gdd_required_c"],
                water_demand_mm=c["water_requirements"]["seasonal_water_demand_mm"],
                kc_mid=c["water_requirements"]["kc_mid"],
                n_requirement_kg_ha=c["soil_and_nutrient_impact"]["n_requirement_kg_ha"],
                n_fixation=c["soil_and_nutrient_impact"]["n_fixation"],
                n_credit_kg_ha=c["soil_and_nutrient_impact"]["n_credit_leftover_kg_ha"],
                c_n_residue_ratio=c["soil_and_nutrient_impact"]["c_n_residue_ratio"],
                residue_biomass_t_ha=c["soil_and_nutrient_impact"]["residue_biomass_t_ha"],
                root_depth_max_m=c["soil_and_nutrient_impact"]["root_depth_max_m"],
                erosion_protection=c["soil_and_nutrient_impact"]["erosion_protection_mature"]
            )
        return crops

    def load_soil_profile(self) -> SoilProfile:
        path = os.path.join(self.data_dir, "soil_profile_ames_iowa.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return SoilProfile(
            site_name=data["location"]["site_name"],
            soil_series=data["soil_taxonomy"]["soil_series"],
            textural_class=data["physical_properties"]["textural_class"],
            sand_fraction_pct=data["physical_properties"]["sand_fraction_pct"],
            silt_fraction_pct=data["physical_properties"]["silt_fraction_pct"],
            clay_fraction_pct=data["physical_properties"]["clay_fraction_pct"],
            bulk_density_g_cm3=data["physical_properties"]["bulk_density_g_cm3"],
            total_rootzone_awc_mm=data["physical_properties"]["total_rootzone_awc_mm"],
            saturation_pct=data["hydraulic_limits"]["saturation_theta_sat_pct"],
            field_capacity_pct=data["hydraulic_limits"]["field_capacity_theta_fc_pct"],
            pwp_pct=data["hydraulic_limits"]["permanent_wilting_point_theta_pwp_pct"],
            soil_organic_matter_pct=data["chemical_and_fertility_properties"]["soil_organic_matter_som_pct"],
            ph_water=data["chemical_and_fertility_properties"]["ph_water"],
            hydrologic_group=data["soil_taxonomy"]["hydrologic_soil_group"]
        )

    def load_harmonized_satellite_series(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "nasa_satellite_harmonized_series.csv")
        records = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "period_start": row["period_start"],
                    "period_end": row["period_end"],
                    "doy_mid": int(row["doy_mid"]),
                    "smap_sm_surface": float(row["smap_sm_surface_m3m3"]),
                    "smap_sm_rootzone": float(row["smap_sm_rootzone_m3m3"]),
                    "smap_sm_wetness": float(row["smap_sm_wetness_ratio"]),
                    "gpm_precipitation_mm": float(row["gpm_precipitation_mm"]),
                    "modis_ndvi": float(row["modis_ndvi"]),
                    "modis_evi": float(row["modis_evi"]),
                    "ecostress_et_mm": float(row["ecostress_et_mm"]),
                    "modis_pet_mm": float(row["modis_pet_mm"]),
                    "water_deficit_mm": float(row["water_deficit_mm"]),
                    "surface_temp_k": float(row["surface_temp_k"]),
                    "bare_soil_flag": row["bare_soil_flag"].lower() == "true",
                    "stress_risk_index": row["stress_risk_index"]
                })
        return records

    def load_rotation_rules(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "crop_rotation_rules.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("rules", [])

    def load_scenarios_comparison(self) -> List[Dict[str, Any]]:
        path = os.path.join(self.data_dir, "rotation_scenarios_comparison.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
