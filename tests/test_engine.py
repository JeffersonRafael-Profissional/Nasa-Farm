"""
Unit and Integration Tests for Smart Rotation Engine.
"""

import unittest
import os
from src.engine import (
    DataHarmonizer,
    StressDetector,
    ParetoOptimizer,
    SmartRotationEngine,
    FarmerConstraints
)

class TestSmartRotationEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SmartRotationEngine()

    def test_harmonizer_loads_crops(self):
        crops = self.engine.crops
        self.assertIn("corn_grain", crops)
        self.assertIn("soybean", crops)
        self.assertIn("cereal_rye_cover", crops)
        self.assertGreater(crops["corn_grain"].water_demand_mm[0], 400)

    def test_harmonizer_loads_soil(self):
        soil = self.engine.soil
        self.assertEqual(soil.soil_series, "Clarion loam (Typic Hapludolls)")
        self.assertGreater(soil.total_rootzone_awc_mm, 150)

    def test_stress_detector(self):
        bare_summary = self.engine.stress_detector.summarize_soil_exposure_summary()
        self.assertGreater(bare_summary["total_bare_soil_periods_16d"], 0)
        self.assertIn("Late September", bare_summary["cover_crop_opportunity_window"])

    def test_pareto_optimizer(self):
        optimizer = ParetoOptimizer()
        ranked = optimizer.normalize_metrics(self.engine.scenarios_raw)
        self.assertEqual(len(ranked), 3)
        # Top ranked should have highest composite score
        self.assertGreaterEqual(ranked[0]["composite_pareto_score"], ranked[1]["composite_pareto_score"])

    def test_full_evaluation(self):
        res = self.engine.evaluate()
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["scenario_ranking"]), 3)
        self.assertIn("recommended_strategy", res)
        self.assertIn("decision_support_disclaimer", res)

if __name__ == "__main__":
    unittest.main()
