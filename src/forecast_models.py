"""
forecast_models.py
Statistical forecasting and time-series modeling of Taiwan literacy rates (2019-2026).
Implements Asymptotic Logistic Decay, Holt's Exponential Smoothing, and Linear Trend.
"""

import os
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")


def asymptotic_decay(t, i0, k):
    """
    Models illiteracy rate decay: I(t) = i0 * exp(-k * t).
    Literacy rate = 100 - I(t).
    Guarantees predictions never exceed 100.0%.
    """
    return i0 * np.exp(-k * t)


def holt_linear_trend(series, alpha=0.6, beta=0.3, n_ahead=2):
    """
    Holt's double exponential smoothing for trending series.
    """
    y = np.array(series, dtype=float)
    n = len(y)
    level = np.zeros(n)
    trend = np.zeros(n)
    
    # Initialize
    level[0] = y[0]
    trend[0] = y[1] - y[0]
    
    for t in range(1, n):
        level[t] = alpha * y[t] + (1 - alpha) * (level[t - 1] + trend[t - 1])
        trend[t] = beta * (level[t] - level[t - 1]) + (1 - beta) * trend[t - 1]
        
    forecasts = []
    for h in range(1, n_ahead + 1):
        forecasts.append(level[-1] + h * trend[-1])
        
    return level, trend, forecasts


def run_forecasting_pipeline():
    df = pd.read_csv(os.path.join(PROCESSED_DIR, "taiwan_literacy_national_2019_2026.csv"))
    
    # Historical ground truth: 2019-2024
    hist = df[df["status"] == "Official Historical"].copy()
    hist_years = hist["year"].values
    t_hist = hist_years - 2019
    overall_lit = hist["overall_literacy_rate"].values
    male_lit = hist["male_literacy_rate"].values
    female_lit = hist["female_literacy_rate"].values
    illit_overall = 100.0 - overall_lit
    
    # Target forecasting years: 2025 and 2026
    proj_years = np.array([2025, 2026])
    t_all = np.array(range(8)) # 2019..2026
    all_years = np.array(range(2019, 2027))
    
    # -------------------------------------------------------------
    # Model 1: Asymptotic Logistic Decay (Bounded Ceiling)
    # -------------------------------------------------------------
    popt, _ = curve_fit(asymptotic_decay, t_hist, illit_overall, p0=[illit_overall[0], 0.08])
    pred_illit_asymp = asymptotic_decay(t_all, *popt)
    pred_lit_asymp = np.round(100.0 - pred_illit_asymp, 3)
    
    # -------------------------------------------------------------
    # Model 2: Linear Trend Regression (OLS)
    # -------------------------------------------------------------
    poly_coeff = np.polyfit(t_hist, overall_lit, deg=1)
    pred_lit_linear = np.round(np.polyval(poly_coeff, t_all), 3)
    
    # -------------------------------------------------------------
    # Model 3: Holt's Double Exponential Smoothing
    # -------------------------------------------------------------
    _, _, holt_future = holt_linear_trend(overall_lit, alpha=0.55, beta=0.25, n_ahead=2)
    pred_lit_holt = np.concatenate([overall_lit, np.round(holt_future, 3)])
    
    # -------------------------------------------------------------
    # Model Backtesting & Evaluation (Train: 2019-2022, Test: 2023-2024)
    # -------------------------------------------------------------
    train_mask = hist_years <= 2022
    test_mask = hist_years >= 2023
    t_train = hist_years[train_mask] - 2019
    t_test = hist_years[test_mask] - 2019
    y_train = overall_lit[train_mask]
    y_test = overall_lit[test_mask]
    
    # Evaluate Asymptotic
    popt_train, _ = curve_fit(asymptotic_decay, t_train, 100.0 - y_train, p0=[1.0, 0.08])
    test_pred_asymp = 100.0 - asymptotic_decay(t_test, *popt_train)
    rmse_asymp = float(np.sqrt(mean_squared_error(y_test, test_pred_asymp)))
    mae_asymp = float(mean_absolute_error(y_test, test_pred_asymp))
    
    # Evaluate Linear
    poly_train = np.polyfit(t_train, y_train, deg=1)
    test_pred_linear = np.polyval(poly_train, t_test)
    rmse_linear = float(np.sqrt(mean_squared_error(y_test, test_pred_linear)))
    mae_linear = float(mean_absolute_error(y_test, test_pred_linear))
    
    # Evaluate Holt
    _, _, holt_test = holt_linear_trend(y_train, n_ahead=2)
    rmse_holt = float(np.sqrt(mean_squared_error(y_test, holt_test)))
    mae_holt = float(mean_absolute_error(y_test, holt_test))
    
    # -------------------------------------------------------------
    # Gender Gap Convergence Projections
    # -------------------------------------------------------------
    gap_hist = hist["gender_gap"].values
    gap_poly = np.polyfit(t_hist, gap_hist, deg=1)
    gap_projected = np.round(np.clip(np.polyval(gap_poly, t_all), 0.0, 5.0), 3)
    
    # Female literacy projection (closing the historical gap)
    popt_f, _ = curve_fit(asymptotic_decay, t_hist, 100.0 - female_lit, p0=[1.6, 0.09])
    pred_lit_female = np.round(100.0 - asymptotic_decay(t_all, *popt_f), 3)
    
    # Male literacy projection
    popt_m, _ = curve_fit(asymptotic_decay, t_hist, 100.0 - male_lit, p0=[0.3, 0.12])
    pred_lit_male = np.round(100.0 - asymptotic_decay(t_all, *popt_m), 3)
    
    results = {
        "metadata": {
            "title": "Taiwan Literacy Rate Forecasting (2019-2026)",
            "historical_range": "2019-2024 (ROC 108-113)",
            "forecast_range": "2025-2026 (ROC 114-115)",
            "unit": "Percentage of population aged 15 and over (%)",
            "source": "Ministry of the Interior, Republic of China (Taiwan)"
        },
        "model_performance_backtest": {
            "asymptotic_logistic": {
                "rmse": round(rmse_asymp, 4),
                "mae": round(mae_asymp, 4),
                "r2_fit_overall": round(float(r2_score(overall_lit, pred_lit_asymp[:6])), 4),
                "notes": "Optimal for demographic saturation; mathematically guarantees predictions never exceed 100%."
            },
            "linear_regression": {
                "rmse": round(rmse_linear, 4),
                "mae": round(mae_linear, 4),
                "r2_fit_overall": round(float(r2_score(overall_lit, pred_lit_linear[:6])), 4),
                "notes": "Standard benchmark, but lacks upper-bound asymptotic constraints."
            },
            "holt_exponential_smoothing": {
                "rmse": round(rmse_holt, 4),
                "mae": round(mae_holt, 4),
                "r2_fit_overall": round(float(r2_score(overall_lit, pred_lit_holt[:6])), 4),
                "notes": "Adapts dynamically to recent year-over-year momentum."
            }
        },
        "timeline_data": []
    }
    
    for i, yr in enumerate(all_years):
        results["timeline_data"].append({
            "year": int(yr),
            "roc_year": int(yr - 1911),
            "is_forecast": bool(yr >= 2025),
            "actual_overall": float(overall_lit[i]) if yr <= 2024 else None,
            "pred_asymptotic": float(pred_lit_asymp[i]),
            "pred_linear": float(pred_lit_linear[i]),
            "pred_holt": float(pred_lit_holt[i]),
            "male_literacy": float(male_lit[i]) if yr <= 2024 else float(pred_lit_male[i]),
            "female_literacy": float(female_lit[i]) if yr <= 2024 else float(pred_lit_female[i]),
            "gender_gap": float(gap_hist[i]) if yr <= 2024 else float(gap_projected[i])
        })
        
    out_file = os.path.join(PROCESSED_DIR, "forecasting_results_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Forecasting pipeline completed. Results written to {out_file}")
    print(f"2026 Forecast (Asymptotic Model): {pred_lit_asymp[-1]}%")
    print(f"2026 Forecast (Linear Model):     {pred_lit_linear[-1]}%")
    print(f"2026 Forecast (Holt Model):       {pred_lit_holt[-1]}%")
    print(f"2026 Forecast Gender Gap:         {gap_projected[-1]}%")
    return results


if __name__ == "__main__":
    run_forecasting_pipeline()
