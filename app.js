/**
 * app.js
 * Interactive logic, Chart.js visualizations, and real-time ML simulator
 * for Taiwan Literacy Rate & Educational Dynamics (2019-2026).
 */

let charts = {};

document.addEventListener("DOMContentLoaded", () => {
  if (typeof window.PROJECT_DATA === "undefined") {
    console.warn("PROJECT_DATA not found on window, attempting to fetch data_bundle.json...");
    fetch("data_bundle.json")
      .then(res => res.json())
      .then(data => {
        window.PROJECT_DATA = data;
        initDashboard();
      })
      .catch(err => console.error("Failed to load data:", err));
  } else {
    initDashboard();
  }
});

function initDashboard() {
  const data = window.PROJECT_DATA;
  if (!data) return;

  renderNationalTable(data.national_timeline);
  initMacroTrendChart(data.national_timeline);
  initAgeCohortChart(data.age_cohorts);
  initGenderGapChart(data.national_timeline);
  initEducationalAttainmentChart(data.educational_attainment);
  initRegionalChart(data.counties, "2026", "All");
  initForecastComparisonChart(data.forecasting);
  initStudentHabitsCharts(data.student_habits_analysis, data.student_habits_sample);
  runSimulator(); // Initial simulator calculation
}

// ==========================================
// Tab Switching Logic
// ==========================================
function switchTab(tabId) {
  const tabs = ["macro", "equity", "regional", "forecast", "micro", "report"];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-${t}`);
    const panel = document.getElementById(`panel-${t}`);
    if (t === tabId) {
      panel.classList.remove("hidden");
      btn.classList.add("bg-blue-600/20", "text-blue-400", "border", "border-blue-500/30");
      btn.classList.remove("text-slate-300");
    } else {
      panel.classList.add("hidden");
      btn.classList.remove("bg-blue-600/20", "text-blue-400", "border", "border-blue-500/30");
      btn.classList.add("text-slate-300");
    }
  });

  // Trigger chart resize if needed
  window.dispatchEvent(new Event('resize'));
}

// ==========================================
// National Timeseries Table
// ==========================================
function renderNationalTable(records) {
  const tbody = document.getElementById("national-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  records.forEach(r => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50/80 transition-colors";

    const statusBadge = r.status.includes("Historical") 
      ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800">Official</span>`
      : `<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-100 text-indigo-800">Projected</span>`;

    tr.innerHTML = `
      <td class="px-6 py-4 font-semibold text-slate-900">${r.year} (${r.roc_year})</td>
      <td class="px-6 py-4">${Number(r.pop_15_plus).toLocaleString()}</td>
      <td class="px-6 py-4 text-emerald-700 font-medium">${Number(r.literate_pop).toLocaleString()}</td>
      <td class="px-6 py-4 font-bold text-slate-900">${r.overall_literacy_rate.toFixed(2)}%</td>
      <td class="px-6 py-4 text-blue-600 font-medium">${r.male_literacy_rate.toFixed(2)}%</td>
      <td class="px-6 py-4 text-purple-600 font-medium">${r.female_literacy_rate.toFixed(2)}%</td>
      <td class="px-6 py-4 text-rose-600 font-semibold">${r.gender_gap.toFixed(2)}%</td>
      <td class="px-6 py-4">${statusBadge}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ==========================================
// Chart 1: Macro National Trends (Line)
// ==========================================
function initMacroTrendChart(records) {
  const ctx = document.getElementById("macroTrendChart").getContext("2d");
  const labels = records.map(r => `${r.year} (${r.roc_year})`);
  
  const overall = records.map(r => r.overall_literacy_rate);
  const male = records.map(r => r.male_literacy_rate);
  const female = records.map(r => r.female_literacy_rate);

  charts.macro = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Overall Literacy Rate (%)",
          data: overall,
          borderColor: "#2563eb",
          backgroundColor: "rgba(37, 99, 235, 0.08)",
          fill: true,
          tension: 0.3,
          borderWidth: 3,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: "#2563eb",
          segment: {
            borderDash: ctx => ctx.p0DataIndex >= 5 ? [6, 6] : undefined
          }
        },
        {
          label: "Male Literacy (%)",
          data: male,
          borderColor: "#10b981",
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: "#10b981",
          segment: {
            borderDash: ctx => ctx.p0DataIndex >= 5 ? [6, 6] : undefined
          }
        },
        {
          label: "Female Literacy (%)",
          data: female,
          borderColor: "#9333ea",
          borderWidth: 2,
          tension: 0.3,
          pointRadius: 4,
          pointBackgroundColor: "#9333ea",
          segment: {
            borderDash: ctx => ctx.p0DataIndex >= 5 ? [6, 6] : undefined
          }
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "top",
          labels: { font: { family: "'Plus Jakarta Sans'", size: 12 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.toFixed(2)}%`
          }
        }
      },
      scales: {
        y: {
          min: 98.0,
          max: 100.0,
          ticks: {
            callback: v => v.toFixed(1) + "%",
            font: { size: 11 }
          },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });
}

// ==========================================
// Chart 2: Age Cohorts (Bar)
// ==========================================
function initAgeCohortChart(ageRecords) {
  const ctx = document.getElementById("ageCohortChart").getContext("2d");
  const years = [2019, 2021, 2024, 2026];
  const cohorts = ["15-24", "25-44", "45-64", "65+"];
  
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"];
  
  const datasets = cohorts.map((cohort, idx) => {
    return {
      label: `Age ${cohort}`,
      data: years.map(y => {
        const item = ageRecords.find(r => r.year === y && r.age_cohort === cohort);
        return item ? item.literacy_rate : null;
      }),
      backgroundColor: colors[idx],
      borderRadius: 6
    };
  });

  charts.age = new Chart(ctx, {
    type: "bar",
    data: {
      labels: years.map(y => y >= 2025 ? `${y} (Proj)` : `${y}`),
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.raw.toFixed(2)}%`
          }
        }
      },
      scales: {
        y: {
          min: 92.0,
          max: 100.0,
          ticks: { callback: v => v + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ==========================================
// Chart 3: Gender Gap (Area)
// ==========================================
function initGenderGapChart(records) {
  const ctx = document.getElementById("genderGapChart").getContext("2d");
  const labels = records.map(r => r.year);
  const gaps = records.map(r => r.gender_gap);

  charts.genderGap = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Gender Literacy Gap (Male - Female %)",
          data: gaps,
          borderColor: "#e11d48",
          backgroundColor: "rgba(225, 29, 72, 0.12)",
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointRadius: 5,
          pointBackgroundColor: "#e11d48",
          segment: {
            borderDash: ctx => ctx.p0DataIndex >= 5 ? [6, 6] : undefined
          }
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: ctx => `Gap: ${ctx.raw.toFixed(2)} percentage points`
          }
        }
      },
      scales: {
        y: {
          min: 0.0,
          max: 1.6,
          ticks: { callback: v => v.toFixed(2) + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ==========================================
// Chart 4: Educational Attainment Progression
// ==========================================
function initEducationalAttainmentChart(eduRecords) {
  const ctx = document.getElementById("educationalAttainmentChart").getContext("2d");
  const labels = eduRecords.map(r => r.year);

  charts.edu = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Higher Education (Tertiary)",
          data: eduRecords.map(r => r.higher_education_pct),
          backgroundColor: "#2563eb",
          stack: "stack0"
        },
        {
          label: "Senior High / Vocational",
          data: eduRecords.map(r => r.senior_high_vocational_pct),
          backgroundColor: "#38bdf8",
          stack: "stack0"
        },
        {
          label: "Junior High School",
          data: eduRecords.map(r => r.junior_high_pct),
          backgroundColor: "#fbbf24",
          stack: "stack0"
        },
        {
          label: "Primary School",
          data: eduRecords.map(r => r.primary_school_pct),
          backgroundColor: "#f87171",
          stack: "stack0"
        },
        {
          label: "Self-Taught / Illiterate",
          data: eduRecords.map(r => r.self_taught_and_illiterate_pct),
          backgroundColor: "#94a3b8",
          stack: "stack0"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.raw.toFixed(1)}%`
          }
        }
      },
      scales: {
        y: {
          stacked: true,
          max: 100,
          ticks: { callback: v => v + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        x: {
          stacked: true,
          grid: { display: false }
        }
      }
    }
  });
}

// ==========================================
// Chart 5: 22 Counties & Cities (Horizontal Bar)
// ==========================================
function initRegionalChart(countiesData, selectedYear = "2026", categoryFilter = "All") {
  const ctx = document.getElementById("regionalBarChart").getContext("2d");

  let filtered = countiesData.filter(c => c.year === parseInt(selectedYear));
  if (categoryFilter !== "All") {
    filtered = filtered.filter(c => c.category === categoryFilter);
  }

  // Sort descending by literacy rate
  filtered.sort((a, b) => b.literacy_rate - a.literacy_rate);

  const labels = filtered.map(c => `${c.county_en} (${c.county_zh})`);
  const values = filtered.map(c => c.literacy_rate);

  const colors = filtered.map(c => {
    if (c.category === "Special Municipality") return "#2563eb";
    if (c.category === "Provincial City") return "#06b6d4";
    if (c.category === "Offshore Island") return "#8b5cf6";
    return "#10b981";
  });

  if (charts.regional) {
    charts.regional.destroy();
  }

  charts.regional = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: `Literacy Rate in ${selectedYear} (%)`,
          data: values,
          backgroundColor: colors,
          borderRadius: 6
        }
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `Literacy Rate: ${ctx.raw.toFixed(2)}%`
          }
        }
      },
      scales: {
        x: {
          min: 97.0,
          max: 100.0,
          ticks: { callback: v => v.toFixed(1) + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        y: {
          ticks: { font: { size: 11, weight: "500" } },
          grid: { display: false }
        }
      }
    }
  });
}

function updateRegionalChart() {
  const yr = document.getElementById("regionalYearSelect").value;
  const cat = document.getElementById("regionalCategorySelect").value;
  if (window.PROJECT_DATA && window.PROJECT_DATA.counties) {
    initRegionalChart(window.PROJECT_DATA.counties, yr, cat);
  }
}

// ==========================================
// Chart 6: ML Forecasting Comparison
// ==========================================
function initForecastComparisonChart(forecastingData) {
  const ctx = document.getElementById("forecastComparisonChart").getContext("2d");
  const timeline = forecastingData.timeline_data;
  const labels = timeline.map(t => `${t.year} (${t.roc_year})`);

  const actuals = timeline.map(t => t.actual_overall);
  const asymp = timeline.map(t => t.pred_asymptotic);
  const linear = timeline.map(t => t.pred_linear);
  const holt = timeline.map(t => t.pred_holt);

  charts.forecast = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Historical Census (Ground Truth)",
          data: actuals,
          borderColor: "#0f172a",
          backgroundColor: "#0f172a",
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8
        },
        {
          label: "Asymptotic Logistic Decay (Bounded)",
          data: asymp,
          borderColor: "#4f46e5",
          borderWidth: 2.5,
          borderDash: [5, 5],
          pointRadius: 4,
          pointBackgroundColor: "#4f46e5",
          tension: 0.3
        },
        {
          label: "Linear OLS Trend",
          data: linear,
          borderColor: "#0284c7",
          borderWidth: 2,
          borderDash: [2, 4],
          pointRadius: 3,
          tension: 0.1
        },
        {
          label: "Holt's Double Exponential Smoothing",
          data: holt,
          borderColor: "#10b981",
          borderWidth: 2,
          borderDash: [8, 4],
          pointRadius: 3,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.raw ? ctx.raw.toFixed(3) + '%' : 'N/A'}`
          }
        }
      },
      scales: {
        y: {
          min: 98.8,
          max: 99.6,
          ticks: { callback: v => v.toFixed(2) + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

// ==========================================
// Chart 7 & 8: Student Habits Lab (Kaggle)
// ==========================================
function initStudentHabitsCharts(analysis, sample) {
  // Feature Importance
  const ctxFeat = document.getElementById("featureImportanceChart").getContext("2d");
  const feats = analysis.models.random_forest.feature_importance;

  charts.feats = new Chart(ctxFeat, {
    type: "bar",
    data: {
      labels: feats.map(f => f.feature.replace(/_/g, ' ')),
      datasets: [
        {
          label: "Feature Importance (%)",
          data: feats.map(f => (f.importance * 100).toFixed(1)),
          backgroundColor: "#3b82f6",
          borderRadius: 6
        }
      ]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          ticks: { callback: v => v + "%" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        y: { grid: { display: false } }
      }
    }
  });

  // Scatter Plot
  const ctxScatter = document.getElementById("studentScatterChart").getContext("2d");
  const scatterData = sample.map(s => {
    let color = "#3b82f6";
    if (s.literacy_proficiency_level === "Advanced Literacy") color = "#10b981";
    if (s.literacy_proficiency_level === "Basic Literacy") color = "#ef4444";

    return {
      x: s.study_hours_per_week,
      y: s.academic_exam_score,
      level: s.literacy_proficiency_level,
      color: color
    };
  });

  charts.scatter = new Chart(ctxScatter, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Students",
          data: scatterData,
          backgroundColor: scatterData.map(d => d.color),
          pointRadius: 5,
          pointHoverRadius: 7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `Study: ${ctx.raw.x}h/wk | Score: ${ctx.raw.y} | ${ctx.raw.level}`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: "Study Hours per Week" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        },
        y: {
          min: 30,
          max: 105,
          title: { display: true, text: "Academic Exam Score (0-100)" },
          grid: { color: "rgba(226, 232, 240, 0.8)" }
        }
      }
    }
  });
}

// ==========================================
// Real-time ML Student Performance Simulator
// ==========================================
function runSimulator() {
  const study = parseFloat(document.getElementById("sim-study").value);
  const att = parseFloat(document.getElementById("sim-attendance").value);
  const sleep = parseFloat(document.getElementById("sim-sleep").value);
  const social = parseFloat(document.getElementById("sim-social").value);
  const parent = parseInt(document.getElementById("sim-parent").value);
  const tutor = document.getElementById("sim-tutor").checked;

  // Update dynamic labels
  document.getElementById("val-study").innerText = `${study} hrs`;
  document.getElementById("val-attendance").innerText = `${att}%`;
  document.getElementById("val-sleep").innerText = `${sleep.toFixed(1)} hrs`;
  document.getElementById("val-social").innerText = `${social.toFixed(1)} hrs`;

  // Score formula derived from the Multiple Linear Regression model:
  // Base intercept ~ 45
  let parentScore = (parent - 1) * 3.0;
  let tutorScore = tutor ? 5.0 : 0.0;
  let sleepBonus = (sleep >= 7.0 && sleep <= 8.5) ? 3.5 : (sleep < 5.5 ? -3.5 : 0.0);

  let predicted = 45.0 + (study * 1.15) + (att * 0.25) + parentScore + tutorScore - (social * 2.2) + sleepBonus;
  predicted = Math.max(35.0, Math.min(100.0, predicted));

  const scoreEl = document.getElementById("sim-output-score");
  const badgeEl = document.getElementById("sim-output-badge");
  const tipEl = document.getElementById("sim-output-tip");

  scoreEl.innerText = predicted.toFixed(1);

  if (predicted >= 85) {
    badgeEl.className = "inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800";
    badgeEl.innerHTML = `<i class="fa-solid fa-award mr-1.5"></i> Advanced Literacy & Honors`;
    tipEl.innerText = "Exceptional academic performance! High probability of admission to premier research universities.";
  } else if (predicted >= 65) {
    badgeEl.className = "inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800";
    badgeEl.innerHTML = `<i class="fa-solid fa-certificate mr-1.5"></i> Proficient Literacy`;
    tipEl.innerText = "Solid academic performance with high probability of advancing to standard university programs.";
  } else {
    badgeEl.className = "inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800";
    badgeEl.innerHTML = `<i class="fa-solid fa-triangle-exclamation mr-1.5"></i> Basic Literacy / At-Risk`;
    tipEl.innerText = "Recommend structured tutoring, increased study hours, and capping daily screen time.";
  }
}

// ==========================================
// Export CSV Utilities
// ==========================================
function exportCSV(type) {
  if (!window.PROJECT_DATA) return;
  let csvContent = "data:text/csv;charset=utf-8,";
  let filename = "taiwan_literacy_data.csv";

  if (type === "national") {
    filename = "taiwan_literacy_national_2019_2026.csv";
    csvContent += "Year,ROC_Year,15+_Pop,Literate_Pop,Literacy_Rate,Male_Rate,Female_Rate,Gender_Gap,Status\n";
    window.PROJECT_DATA.national_timeline.forEach(r => {
      csvContent += `${r.year},${r.roc_year},${r.pop_15_plus},${r.literate_pop},${r.overall_literacy_rate},${r.male_literacy_rate},${r.female_literacy_rate},${r.gender_gap},${r.status}\n`;
    });
  } else {
    filename = "taiwan_literacy_county_2019_2026.csv";
    csvContent += "Year,County_Code,County_EN,County_ZH,Category,Literacy_Rate\n";
    window.PROJECT_DATA.counties.forEach(c => {
      csvContent += `${c.year},${c.county_code},${c.county_en},${c.county_zh},${c.category},${c.literacy_rate}\n`;
    });
  }

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
