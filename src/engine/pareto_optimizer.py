"""
Pareto Multi-Objective Optimizer Module.
Balances 4 conflicting agricultural objectives:
1. Yield / Productivity Maximization
2. Water Demand & Drought Stress Minimization
3. Climate & Volatility Risk Minimization
4. Soil Conservation & Carbon Sequestration Maximization
"""

from typing import List, Dict, Any
from .models import FarmerConstraints

class ParetoOptimizer:
    def __init__(self, constraints: FarmerConstraints = None):
        self.constraints = constraints or FarmerConstraints()

    def normalize_metrics(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalizes metrics to 0-100 scales where higher is ALWAYS better.
        """
        results = []
        for s in scenarios:
            m = s["metrics"]
            
            # 1. Productivity score (already 0-100)
            score_yield = m.get("productivity_index", 50.0)

            # 2. Water efficiency score (higher WUE and lower water demand is better)
            wue = m.get("water_use_efficiency_kg_m3", 1.5)
            # 1.0 kg/m3 -> 40 pts, 2.5 kg/m3 -> 100 pts
            score_water = min(100.0, max(20.0, (wue / 2.3) * 100))

            # 3. Climate resilience score (inverse of climate risk score)
            risk = m.get("climate_risk_score_100", 50.0)
            score_resilience = 100.0 - risk

            # 4. Soil health & conservation score
            # Lower erosion is better (15 t/ha -> 20 pts, 1 t/ha -> 100 pts)
            erosion = m.get("soil_erosion_rate_t_ha_yr", 10.0)
            score_erosion = max(10.0, 100.0 - (erosion * 7.5))
            som_trend = m.get("soil_organic_matter_trend_pct_10yr", 0.0)
            score_soil = min(100.0, max(10.0, score_erosion + (som_trend * 3.0)))

            # 5. Economic & fertilizer saving score
            # 220 kg synthetic N -> 30 pts, 80 kg -> 95 pts
            syn_n = m.get("synthetic_n_fertilizer_kg_ha_yr", 180.0)
            score_economics = max(10.0, 110.0 - (syn_n * 0.35))

            # Weighted Pareto Composite Score based on farmer's personal priorities
            w_y = self.constraints.priority_yield_weight
            w_w = self.constraints.priority_water_weight
            w_s = self.constraints.priority_soil_weight
            w_c = self.constraints.priority_cost_weight
            
            total_weight = w_y + w_w + w_s + w_c
            composite_score = (
                (score_yield * w_y) +
                (score_water * w_w) +
                (score_soil * w_s) +
                (score_economics * w_c)
            ) / total_weight

            results.append({
                "scenario_id": s["scenario_id"],
                "name": s["name"],
                "is_current_baseline": s.get("is_current_baseline", False),
                "yield_score": round(score_yield, 1),
                "water_score": round(score_water, 1),
                "resilience_score": round(score_resilience, 1),
                "soil_score": round(score_soil, 1),
                "economic_score": round(score_economics, 1),
                "composite_pareto_score": round(composite_score, 1),
                "raw_metrics": m,
                "crop_sequence": s.get("crop_sequence", []),
                "agronomic_rationale": s.get("agronomic_rationale", ""),
                "benefits": s.get("benefits", []),
                "limitations_and_risks": s.get("limitations_and_risks", []),
                "local_validation_needs": s.get("local_validation_needs", "")
            })

        # Rank by composite score
        results.sort(key=lambda x: x["composite_pareto_score"], reverse=True)
        return results

    def check_pareto_dominance(self, candidate: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines whether candidate Pareto-dominates the baseline:
        Candidate is at least as good in all criteria and strictly better in at least one.
        """
        dims = ["yield_score", "water_score", "resilience_score", "soil_score", "economic_score"]
        better_count = sum(1 for d in dims if candidate[d] > baseline[d])
        worse_count = sum(1 for d in dims if candidate[d] < baseline[d])

        dominates = (better_count > 0 and worse_count == 0)
        trade_off = (better_count > 0 and worse_count > 0)

        return {
            "dominates_baseline": dominates,
            "has_trade_offs": trade_off,
            "improvements": [d for d in dims if candidate[d] > baseline[d]],
            "penalties": [d for d in dims if candidate[d] < baseline[d]]
        }
