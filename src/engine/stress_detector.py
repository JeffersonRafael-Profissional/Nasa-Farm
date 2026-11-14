"""
Stress Detector Module.
Answers Challenge Requirement 1:
- Detect bare field windows (low NDVI, high erosion vulnerability)
- Detect rootzone moisture stress windows (NASA SMAP sm_rootzone percentiles / deficits)
- Detect thermal stress windows (MODIS/SMAP surface_temp anomalies)
- Identify windows for cover crops and pest break interventions.
"""

from typing import List, Dict, Any

class StressDetector:
    def __init__(self, satellite_series: List[Dict[str, Any]], soil_profile):
        self.series = satellite_series
        self.soil = soil_profile

    def detect_bare_field_windows(self) -> List[Dict[str, Any]]:
        """
        Identifies continuous windows where NDVI < 0.25 and soil is exposed to erosion.
        """
        bare_windows = []
        current_window = None

        for rec in self.series:
            is_bare = rec["bare_soil_flag"]
            if is_bare:
                if current_window is None:
                    current_window = {
                        "start_date": rec["period_start"],
                        "end_date": rec["period_end"],
                        "periods_count": 1,
                        "mean_ndvi": rec["modis_ndvi"],
                        "total_rain_mm": rec["gpm_precipitation_mm"],
                        "erosion_risk": "High"
                    }
                else:
                    current_window["end_date"] = rec["period_end"]
                    current_window["periods_count"] += 1
                    current_window["mean_ndvi"] = (current_window["mean_ndvi"] + rec["modis_ndvi"]) / 2
                    current_window["total_rain_mm"] += rec["gpm_precipitation_mm"]
            else:
                if current_window is not None:
                    bare_windows.append(current_window)
                    current_window = None

        if current_window is not None:
            bare_windows.append(current_window)

        return bare_windows

    def detect_water_stress_windows(self) -> List[Dict[str, Any]]:
        """
        Identifies periods of rootzone water stress (SMAP sm_rootzone < 0.20 or water deficit > 12 mm/16d).
        """
        stress_windows = []
        for rec in self.series:
            # Critical wilting threshold roughly 0.13 m3/m3, stress starts around 0.20 m3/m3 in loam
            if rec["smap_sm_rootzone"] < 0.21 or rec["water_deficit_mm"] >= 12.0:
                stress_windows.append({
                    "period": f"{rec['period_start']} to {rec['period_end']}",
                    "doy_mid": rec["doy_mid"],
                    "smap_rootzone_m3m3": rec["smap_sm_rootzone"],
                    "water_deficit_mm": rec["water_deficit_mm"],
                    "stress_level": "Severe" if rec["smap_sm_rootzone"] < 0.18 else "Moderate",
                    "agronomic_hazard": "Critical for flowering/grain filling stages"
                })
        return stress_windows

    def detect_thermal_stress_windows(self) -> List[Dict[str, Any]]:
        """
        Identifies heat stress (surface temp > 302 K / 29°C) and frost risk (< 273.15 K).
        """
        thermal_alerts = []
        for rec in self.series:
            temp_c = rec["surface_temp_k"] - 273.15
            if temp_c > 29.0:
                thermal_alerts.append({
                    "period": f"{rec['period_start']} to {rec['period_end']}",
                    "temp_c": round(temp_c, 1),
                    "type": "Heat Stress / High Vapor Deficit",
                    "impact": "Reduces pollination efficiency and increases canopy ET"
                })
            elif temp_c < 0.0:
                thermal_alerts.append({
                    "period": f"{rec['period_start']} to {rec['period_end']}",
                    "temp_c": round(temp_c, 1),
                    "type": "Freezing / Dormancy Window",
                    "impact": "Ideal for cold-hardy cover crops (e.g. Cereal Rye)"
                })
        return thermal_alerts

    def summarize_soil_exposure_summary(self) -> Dict[str, Any]:
        bare_count = sum(1 for r in self.series if r["bare_soil_flag"])
        total_count = len(self.series)
        bare_pct = (bare_count / total_count) * 100 if total_count > 0 else 0
        total_days_exposed = round(bare_count * 16)
        
        return {
            "total_bare_soil_periods_16d": bare_count,
            "total_bare_soil_days_estimated": total_days_exposed,
            "annual_exposure_percentage": round(bare_pct, 1),
            "cover_crop_opportunity_window": "Late September through late April (DOY 260 to 120)"
        }
