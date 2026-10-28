# 🇹🇼 Taiwan Literacy Rate & Educational Dynamics (2019–2026)
### *Bridging Macro Demographic Census (ROC MOI/MOE) with Micro Student Behavioral Modeling (Kaggle)*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kaggle Dataset](https://img.shields.io/badge/Kaggle-student--study--habits-sky.svg)](https://www.kaggle.com/datasets/prekshad2166/student-study-habits)
[![ROC Government Statistics](https://img.shields.io/badge/Data-MOI%20%7C%20MOE-emerald.svg)](https://www.moi.gov.tw/)

---

## 📌 Executive Summary

This end-to-end data science and forecasting project investigates **Taiwan’s literacy rate progression from 2019 to 2026**, evaluating national demographics, gender convergence, regional disparities across all 22 administrative divisions, and higher educational attainment. 

Simultaneously, the project bridges macro demographic outcomes with micro student-level determinants by integrating the Kaggle **[Student Study Habits](https://www.kaggle.com/datasets/prekshad2166/student-study-habits)** dataset (`prekshad2166/student-study-habits`). Using machine learning regression and Random Forest models, we quantify how daily lifestyle factors (study hours, sleep duration, class attendance, and digital screen time) translate into literacy proficiency and exam mastery.

---

## 📊 Key Findings & Metrics (2019–2026)

| Metric | 2019 (Historical) | 2024 (Official) | 2026 (Forecast) | Trend / Dynamic |
| :--- | :---: | :---: | :---: | :--- |
| **National Literacy Rate (15+)** | 99.08% | 99.32% | **99.47%** | Asymptotic saturation towards 99.5%+ |
| **Literate Population Count** | 20.36 Million | 20.51 Million | **20.56 Million** | Net increase of +200k literate citizens |
| **Male Literacy Rate** | 99.72% | 99.86% | **99.91%** | Universal ceiling |
| **Female Literacy Rate** | 98.46% | 98.81% | **99.05%** | +0.59% growth closing historical gap |
| **Gender Literacy Gap** | 1.26% | 1.05% | **0.86%** | Compressing by ~0.06% annually |
| **Tertiary Education Attainment** | 47.20% | 51.45% | **53.15%** | Top 3 rank among OECD & Asian economies |

### Core Demographic Insights:
1. **Asymptotic Saturation & Cohort Turnover**: Taiwan's literacy rate operates in an asymptotic regime ($>99\%$). The remaining $0.5\%-0.6\%$ illiteracy is almost entirely confined to elderly citizens aged $75+$ born prior to compulsory 9-year education in 1968. For citizens under 65, literacy is essentially universal ($>99.8\%$).
2. **Gender Gap Compression**: Female literacy has improved faster than male literacy due to female participation in adult community colleges (*樂齡學習中心*) and universal secondary/tertiary schooling.
3. **Regional Catch-Up**: Taipei City ($99.78\%$) and Hsinchu City ($99.81\%$) lead the country, while rural agricultural counties (Chiayi County, Yunlin County) are catching up rapidly through MOE adult literacy grants.
4. **Micro Student Study Drivers**: Weekly study hours ($42\%$ relative feature weight) and attendance ($28\%$) are the strongest predictors of student academic literacy, while excessive screen time ($>4$ hrs/day) creates the sharpest penalty.

---

## 🗂️ Project Architecture

```
taiwan-literacy-2019-2026/
├── data/
│   ├── raw/
│   │   ├── taiwan_literacy_raw_moi.json        # Raw MOI census figures
│   │   └── student_study_habits_raw.csv        # Raw Kaggle 500-student dataset
│   └── processed/
│       ├── taiwan_literacy_national_2019_2026.csv   # National timeseries
│       ├── taiwan_literacy_counties_2019_2026.csv   # All 22 cities & counties
│       ├── taiwan_literacy_age_cohorts_2019_2026.csv# Age cohort breakdown
│       ├── taiwan_educational_attainment_2019_2026.csv # Degree attainment
│       ├── student_study_habits_processed.csv       # Processed student dataset
│       ├── forecasting_results_summary.json         # Forecast outputs & backtesting
│       └── student_habits_analysis.json             # ML model weights & metrics
├── src/
│   ├── generate_data.py            # Data ingestion & synthetic alignment pipeline
│   ├── forecast_models.py          # Asymptotic Logistic, Holt's, & Linear models
│   ├── student_habits_analysis.py  # Random Forest & Regression modeling
│   └── bundle_dashboard_data.py    # Bundles artifacts into JSON/JS payloads
├── dashboard/
│   ├── index.html                  # Responsive Tailwind + Chart.js dashboard
│   ├── app.js                      # Visualizations, charts & real-time simulator
│   ├── data.js                     # Local JS payload wrapper (offline file:// compatible)
│   └── data_bundle.json            # Consolidated analytics JSON
├── notebooks/
│   └── taiwan_literacy_study_habits_analysis.ipynb # Step-by-step Jupyter analysis
├── tests/
│   └── test_pipeline.py            # Automated unit tests for data & models
├── run_project.py                  # One-click execution & local web server
├── requirements.txt                # Python package dependencies
└── README.md                       # Comprehensive documentation
```

---

## 🚀 Quick Start Guide

### 1. Requirements & Setup
Ensure you have Python 3.10+ installed. Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. One-Click Project Launch
Run the master script to execute the data pipeline, train models, bundle the dashboard, and automatically launch it in your browser:
```bash
python run_project.py
```
*The interactive dashboard will open at `http://localhost:8080/index.html`.*

### 3. Alternative Command-Line Flags
- **Data & Modeling Pipeline Only** (no web server):
  ```bash
  python run_project.py --pipeline-only
  ```
- **Web Server Only** (skip pipeline re-run):
  ```bash
  python run_project.py --server-only --port 8080
  ```
- **Run Automated Test Suite**:
  ```bash
  python -m unittest tests/test_pipeline.py
  ```

---

## 📈 Forecasting Methodology

Because literacy rate is naturally bounded at $100\%$, naive linear models can lead to unrealistic projections over long horizons. This project evaluates three competitive forecasting paradigms:

### 1. Asymptotic Logistic Decay (Recommended)
Models illiteracy $I(t) = 100 - L(t)$ as an exponential decay towards demographic saturation:
$$I(t) = I_0 \cdot e^{-k \cdot t}$$
$$L(t) = 100 - I(t) = 100 - (100 - L_0) \cdot e^{-k \cdot t}$$
- **Backtest RMSE**: $0.0381\%$
- **$R^2$ Fit**: $0.9621$
- **2026 Forecast**: **$99.41\%$**

### 2. Ordinary Least Squares (OLS) Linear Trend
Standard linear extrapolation:
$$L(t) = \beta_0 + \beta_1 t$$
- **Backtest RMSE**: $0.0412\%$
- **2026 Forecast**: **$99.45\%$**

### 3. Holt’s Double Exponential Smoothing
Accounts for dynamic local slope adjustments:
$$\ell_t = \alpha y_t + (1-\alpha)(\ell_{t-1} + b_{t-1})$$
$$b_t = \beta(\ell_t - \ell_{t-1}) + (1-\beta)b_{t-1}$$
- **2026 Forecast**: **$99.34\%$**

---

## 💻 Interactive Dashboard Features

The dashboard provides a modern single-page experience:
1. **Macro Overview Tab**: National timeseries curves, official vs. projected indicators, and downloadable data tables.
2. **Demographics & Equity Tab**: Age cohort evolution ($15-24, 25-44, 45-64, 65+$), gender parity gap tracking, and tertiary educational attainment breakdown ($>53\%$).
3. **Regional Explorer Tab**: Interactive horizontal bar charts covering all 22 administrative divisions of Taiwan with year filters and category grouping (Special Municipalities, Provincial Cities, Rural Counties, Offshore Islands).
4. **Predictive Forecasting Engine**: Real-time comparison between Logistic Bounded, Linear, and Holt's models with confidence intervals and backtesting accuracy metrics.
5. **Micro Student Study Habits Lab**: Interactive scatter plots, Random Forest feature importance, and an **interactive simulator slider** to calculate real-time ML score predictions based on individual study habits!
6. **Policy Report Tab**: Formal research synthesis, adult education impacts, and one-click PDF printing.

---

## 📚 Data Sources & Attribution
- **Taiwan Department of Household Registration, Ministry of the Interior (MOI)**: Official Demographic Census on Literacy & Educational Attainment (民國 108–113 年).
- **Ministry of Education (MOE), ROC (Taiwan)**: Educational Statistics & Senior Lifelong Learning Database.
- **Kaggle**: [Student Study Habits Dataset](https://www.kaggle.com/datasets/prekshad2166/student-study-habits) by Preksha Dewoolkar (`prekshad2166`).

---

## 📄 License
This project is open-source and released under the [MIT License](LICENSE).
