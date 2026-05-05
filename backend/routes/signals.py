import json
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Blueprint, jsonify, current_app

signals_bp = Blueprint("signals", __name__)

GITHUB_RAW = "https://raw.githubusercontent.com/shabhishek1505/smart-trade/stock-monitor-app"


def _fetch_github(path):
    url = f"{GITHUB_RAW}/{path}"
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    return resp.json()


@signals_bp.get("/results")
def get_results():
    try:
        return jsonify(_fetch_github("config/results.json"))
    except Exception:
        try:
            with open(current_app.config["RESULTS_PATH"]) as f:
                return jsonify(json.load(f))
        except Exception:
            return jsonify({"last_run": None, "stocks": []})


@signals_bp.get("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@signals_bp.post("/run")
def run_now():
    analyser_path = Path(current_app.config["ANALYSER_PATH"]) / "analyse.py"
    try:
        subprocess.Popen(
            [sys.executable, str(analyser_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
