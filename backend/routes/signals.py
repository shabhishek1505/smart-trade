import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from flask import Blueprint, jsonify, current_app

signals_bp = Blueprint("signals", __name__)

GITHUB_API  = "https://api.github.com/repos/shabhishek1505/smart-trade"
BRANCH      = "stock-monitor-app"
WORKFLOW_FILE = "daily_analyse.yml"


def _gh_headers():
    pat = os.getenv("GITHUB_PAT")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if pat:
        h["Authorization"] = f"Bearer {pat}"
    return h


def _fetch_file(path):
    """Fetch file content via GitHub API — always returns latest commit, no CDN cache."""
    resp = requests.get(
        f"{GITHUB_API}/contents/{path}?ref={BRANCH}",
        headers=_gh_headers(),
        timeout=8,
    )
    resp.raise_for_status()
    content_b64 = resp.json()["content"]
    return json.loads(base64.b64decode(content_b64).decode())


@signals_bp.get("/results")
def get_results():
    try:
        return jsonify(_fetch_file("config/results.json"))
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
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        return jsonify({"error": "GITHUB_PAT not configured on server"}), 500

    resp = requests.post(
        f"{GITHUB_API}/actions/workflows/{WORKFLOW_FILE}/dispatches",
        json={"ref": BRANCH},
        headers=_gh_headers(),
        timeout=10,
    )
    if resp.status_code == 204:
        return jsonify({"status": "triggered", "message": "Analysis started — results ready in ~3 minutes"})
    return jsonify({"error": f"GitHub API returned {resp.status_code}", "detail": resp.text}), 500


@signals_bp.get("/run/status")
def run_status():
    try:
        resp = requests.get(
            f"{GITHUB_API}/actions/workflows/{WORKFLOW_FILE}/runs?per_page=1&branch={BRANCH}",
            headers=_gh_headers(),
            timeout=8,
        )
        runs = resp.json().get("workflow_runs", [])
        if runs:
            latest = runs[0]
            return jsonify({
                "status":     latest["status"],
                "conclusion": latest.get("conclusion"),
                "started_at": latest.get("run_started_at"),
                "html_url":   latest.get("html_url"),
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"status": "unknown"})
