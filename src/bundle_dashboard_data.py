"""
bundle_dashboard_data.py
Consolidates all processed CSVs and analytical JSON summaries into a single
dashboard-ready JSON & JS payload, ensuring 100% offline and file:// compatibility.
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

os.makedirs(DASHBOARD_DIR, exist_ok=True)


def bundle():
    # Load all processed tables
    national_df = pd.read_csv(os.path.join(PROCESSED_DIR, "taiwan_literacy_national_2019_2026.csv"))
    age_df = pd.read_csv(os.path.join(PROCESSED_DIR, "taiwan_literacy_age_cohorts_2019_2026.csv"))
    counties_df = pd.read_csv(os.path.join(PROCESSED_DIR, "taiwan_literacy_counties_2019_2026.csv"))
    edu_df = pd.read_csv(os.path.join(PROCESSED_DIR, "taiwan_educational_attainment_2019_2026.csv"))
    students_df = pd.read_csv(os.path.join(PROCESSED_DIR, "student_study_habits_processed.csv"))
    
    with open(os.path.join(PROCESSED_DIR, "forecasting_results_summary.json"), "r", encoding="utf-8") as f:
        forecasting_json = json.load(f)
        
    with open(os.path.join(PROCESSED_DIR, "student_habits_analysis.json"), "r", encoding="utf-8") as f:
        students_analysis_json = json.load(f)
        
    bundle_data = {
        "metadata": {
            "project_name": "Taiwan Literacy Rate & Educational Attainment Analytics (2019-2026)",
            "subtitle": "Bridging Macro Demographics with Micro Student Study Habits",
            "kaggle_source": "https://www.kaggle.com/datasets/prekshad2166/student-study-habits",
            "gov_source": "Ministry of the Interior & Ministry of Education, ROC (Taiwan)",
            "generated_at": "2026-10-28"
        },
        "national_timeline": national_df.to_dict(orient="records"),
        "age_cohorts": age_df.to_dict(orient="records"),
        "counties": counties_df.to_dict(orient="records"),
        "educational_attainment": edu_df.to_dict(orient="records"),
        "forecasting": forecasting_json,
        "student_habits_sample": students_df.head(100).to_dict(orient="records"),
        "student_habits_analysis": students_analysis_json
    }
    
    # 1. Save JSON
    json_path = os.path.join(DASHBOARD_DIR, "data_bundle.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bundle_data, f, ensure_ascii=False, indent=2)
        
    # 2. Save JS wrapper for seamless local file:// opening
    js_path = os.path.join(DASHBOARD_DIR, "data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.PROJECT_DATA = " + json.dumps(bundle_data, ensure_ascii=False, indent=2) + ";\n")
        
    print(f"Data bundled successfully into:\n- {json_path}\n- {js_path}")


if __name__ == "__main__":
    bundle()
