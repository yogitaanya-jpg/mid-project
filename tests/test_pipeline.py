"""
test_pipeline.py
Unit tests for data integrity, statistical boundaries, and ML model outputs.
"""

import os
import unittest
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


class TestTaiwanLiteracyPipeline(unittest.TestCase):

    def test_national_data_integrity(self):
        fpath = os.path.join(PROCESSED_DIR, "taiwan_literacy_national_2019_2026.csv")
        self.assertTrue(os.path.exists(fpath), "National dataset file missing.")
        df = pd.read_csv(fpath)
        
        # Check years
        expected_years = list(range(2019, 2027))
        self.assertEqual(list(df["year"]), expected_years)
        
        # Literacy rates bounded between 90 and 100%
        self.assertTrue((df["overall_literacy_rate"] >= 90.0).all())
        self.assertTrue((df["overall_literacy_rate"] <= 100.0).all())
        self.assertTrue((df["male_literacy_rate"] <= 100.0).all())
        self.assertTrue((df["female_literacy_rate"] <= 100.0).all())
        
        # Population counts positive
        self.assertTrue((df["pop_15_plus"] > 20000000).all())
        self.assertTrue((df["literate_pop"] > 20000000).all())

    def test_county_data_integrity(self):
        fpath = os.path.join(PROCESSED_DIR, "taiwan_literacy_counties_2019_2026.csv")
        self.assertTrue(os.path.exists(fpath))
        df = pd.read_csv(fpath)
        
        # 22 administrative divisions
        unique_counties = df["county_code"].unique()
        self.assertEqual(len(unique_counties), 22)
        
        # Rates strictly bounded
        self.assertTrue((df["literacy_rate"] >= 95.0).all())
        self.assertTrue((df["literacy_rate"] <= 100.0).all())

    def test_student_habits_schema(self):
        fpath = os.path.join(PROCESSED_DIR, "student_study_habits_processed.csv")
        self.assertTrue(os.path.exists(fpath))
        df = pd.read_csv(fpath)
        
        self.assertEqual(len(df), 500)
        required_cols = [
            "student_id", "study_hours_per_week", "sleep_hours_per_day",
            "attendance_percentage", "academic_exam_score", "literacy_proficiency_level"
        ]
        for col in required_cols:
            self.assertIn(col, df.columns)
            
        self.assertTrue((df["academic_exam_score"] >= 0).all())
        self.assertTrue((df["academic_exam_score"] <= 100).all())

    def test_forecasting_summary_json(self):
        fpath = os.path.join(PROCESSED_DIR, "forecasting_results_summary.json")
        self.assertTrue(os.path.exists(fpath))
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertIn("timeline_data", data)
        self.assertIn("model_performance_backtest", data)
        
        # Ensure 2026 prediction is between 99.0 and 100.0%
        pred_2026 = [d for d in data["timeline_data"] if d["year"] == 2026][0]
        self.assertTrue(99.0 <= pred_2026["pred_asymptotic"] <= 100.0)


if __name__ == "__main__":
    unittest.main()
