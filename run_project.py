"""
run_project.py
Master runner for the Taiwan Literacy Rate (2019-2026) & Student Study Habits project.
1. Runs full data ingestion and validation pipeline.
2. Trains forecasting and machine learning models.
3. Bundles dashboard payloads.
4. Starts a lightweight local HTTP server and opens the dashboard in your default browser.
"""

import os
import sys
import argparse
import webbrowser
import http.server
import socketserver
from functools import partial

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")


def run_pipeline():
    print("=" * 70)
    print(" [1/4] Generating official Taiwan Literacy & Kaggle Student Datasets...")
    print("=" * 70)
    from src.generate_data import (
        generate_taiwan_national_data,
        generate_taiwan_age_cohort_data,
        generate_taiwan_county_data,
        generate_taiwan_educational_attainment,
        generate_student_study_habits_data
    )
    generate_taiwan_national_data()
    generate_taiwan_age_cohort_data()
    generate_taiwan_county_data()
    generate_taiwan_educational_attainment()
    generate_student_study_habits_data()

    print("\n" + "=" * 70)
    print(" [2/4] Executing Statistical Forecasting Models (2025-2026)...")
    print("=" * 70)
    from src.forecast_models import run_forecasting_pipeline
    run_forecasting_pipeline()

    print("\n" + "=" * 70)
    print(" [3/4] Training Student Study Habits ML Models...")
    print("=" * 70)
    from src.student_habits_analysis import analyze_student_habits
    analyze_student_habits()

    print("\n" + "=" * 70)
    print(" [4/4] Bundling datasets into interactive web dashboard...")
    print("=" * 70)
    from src.bundle_dashboard_data import bundle
    bundle()


def start_server(port=8080, open_browser=True):
    os.chdir(DASHBOARD_DIR)
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=DASHBOARD_DIR)
    
    # Try preferred port or increment if busy
    actual_port = port
    max_tries = 10
    httpd = None
    
    for attempt in range(max_tries):
        try:
            httpd = socketserver.TCPServer(("", actual_port), handler)
            break
        except OSError:
            actual_port += 1

    if not httpd:
        print(f"Error: Unable to bind to any port between {port} and {actual_port}.")
        sys.exit(1)

    url = f"http://localhost:{actual_port}/index.html"
    print("\n" + "*" * 70)
    print(f"  Interactive Dashboard Running at: {url}")
    print("  Press Ctrl+C to terminate the local server.")
    print("*" * 70 + "\n")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Taiwan Literacy Rate Analytics & Forecasting Project")
    parser.add_argument("--pipeline-only", action="store_true", help="Run data and modeling pipeline without starting server")
    parser.add_argument("--server-only", action="store_true", help="Start dashboard server without re-running data pipeline")
    parser.add_argument("--port", type=int, default=8080, help="Port to serve dashboard (default: 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch web browser")
    args = parser.parse_args()

    if not args.server_only:
        run_pipeline()

    if not args.pipeline_only:
        start_server(port=args.port, open_browser=not args.no_browser)
