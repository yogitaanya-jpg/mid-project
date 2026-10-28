"""
student_habits_analysis.py
Exploratory Data Analysis and Machine Learning modeling on the Kaggle
'student-study-habits' dataset (Preksha Dewoolkar schema).
Investigates the micro-level behavioral drivers of academic performance and literacy.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def analyze_student_habits():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "student_study_habits_processed.csv"))
    
    # 1. Summary Statistics
    summary_stats = {
        "total_students": len(df),
        "mean_study_hours": round(float(df["study_hours_per_week"].mean()), 2),
        "mean_sleep_hours": round(float(df["sleep_hours_per_day"].mean()), 2),
        "mean_attendance": round(float(df["attendance_percentage"].mean()), 2),
        "mean_social_media_hours": round(float(df["social_media_hours_per_day"].mean()), 2),
        "mean_exam_score": round(float(df["academic_exam_score"].mean()), 2),
        "literacy_distribution": df["literacy_proficiency_level"].value_counts().to_dict()
    }
    
    # 2. Correlation Matrix with Exam Score
    numeric_cols = [
        "study_hours_per_week",
        "sleep_hours_per_day",
        "attendance_percentage",
        "social_media_hours_per_day",
        "academic_exam_score"
    ]
    corr_matrix = df[numeric_cols].corr().round(4).to_dict()
    
    # 3. Machine Learning Modeling
    # Feature engineering & encoding
    X = df[[
        "study_hours_per_week",
        "sleep_hours_per_day",
        "attendance_percentage",
        "social_media_hours_per_day",
        "tutoring_attendance",
        "parental_education_level"
    ]].copy()
    
    y = df["academic_exam_score"]
    
    # Encode categoricals
    X["tutoring_encoded"] = (X["tutoring_attendance"] == "Yes").astype(int)
    edu_map = {
        "High School": 1,
        "Associate/Junior College": 2,
        "Bachelor's Degree": 3,
        "Master's Degree": 4,
        "Doctorate": 5
    }
    X["parental_edu_encoded"] = X["parental_education_level"].map(edu_map)
    
    feature_names = [
        "study_hours_per_week",
        "sleep_hours_per_day",
        "attendance_percentage",
        "social_media_hours_per_day",
        "tutoring_encoded",
        "parental_edu_encoded"
    ]
    
    X_features = X[feature_names]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_features, y, test_size=0.2, random_state=42
    )
    
    # Model 1: Multiple Linear Regression
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_r2 = float(r2_score(y_test, lr_pred))
    lr_rmse = float(np.sqrt(mean_squared_error(y_test, lr_pred)))
    lr_mae = float(mean_absolute_error(y_test, lr_pred))
    
    # Model 2: Random Forest Regressor
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_r2 = float(r2_score(y_test, rf_pred))
    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_pred)))
    rf_mae = float(mean_absolute_error(y_test, rf_pred))
    
    # Feature Importance from Random Forest
    importances = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in zip(feature_names, rf.feature_importances_)
    ]
    importances.sort(key=lambda x: x["importance"], reverse=True)
    
    # Grouped comparisons
    parental_edu_comparison = df.groupby("parental_education_level")["academic_exam_score"].mean().round(2).to_dict()
    tutoring_comparison = df.groupby("tutoring_attendance")["academic_exam_score"].mean().round(2).to_dict()
    
    results = {
        "summary": summary_stats,
        "correlations": corr_matrix,
        "models": {
            "linear_regression": {
                "r2_score": round(lr_r2, 4),
                "rmse": round(lr_rmse, 3),
                "mae": round(lr_mae, 3),
                "coefficients": {
                    name: round(float(coef), 3) for name, coef in zip(feature_names, lr.coef_)
                },
                "intercept": round(float(lr.intercept_), 3)
            },
            "random_forest": {
                "r2_score": round(rf_r2, 4),
                "rmse": round(rf_rmse, 3),
                "mae": round(rf_mae, 3),
                "feature_importance": importances
            }
        },
        "group_analysis": {
            "parental_education_mean_score": parental_edu_comparison,
            "tutoring_mean_score": tutoring_comparison
        }
    }
    
    out_file = os.path.join(PROCESSED_DIR, "student_habits_analysis.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Student study habits ML analysis completed. Results saved to {out_file}")
    print(f"Linear Regression R^2: {lr_r2:.4f}, RMSE: {lr_rmse:.3f}")
    print(f"Random Forest R^2:     {rf_r2:.4f}, RMSE: {rf_rmse:.3f}")
    return results


if __name__ == "__main__":
    analyze_student_habits()
