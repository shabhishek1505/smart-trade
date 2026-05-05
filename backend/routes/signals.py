import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from flask import Blueprint, jsonify, current_app

signals_bp = Blueprint("signals", __name__)


@signals_bp.get("/results")
def get_results():
    path = current_app.config["RESULTS_PATH"]
    try:
        with open(path) as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
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
