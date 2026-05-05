import base64
import json
import os
import threading

import requests
from flask import Blueprint, request, jsonify, current_app

stocks_bp = Blueprint("stocks", __name__)
_lock = threading.Lock()

GITHUB_RAW = "https://raw.githubusercontent.com/shabhishek1505/smart-trade/stock-monitor-app"
GITHUB_API = "https://api.github.com/repos/shabhishek1505/smart-trade"
STOCKS_PATH = "config/stocks.json"
BRANCH = "stock-monitor-app"


def _gh_headers():
    pat = os.getenv("GITHUB_PAT")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if pat:
        h["Authorization"] = f"Bearer {pat}"
    return h


def _read():
    resp = requests.get(f"{GITHUB_RAW}/{STOCKS_PATH}", timeout=8)
    resp.raise_for_status()
    return resp.json()


def _write(data, message):
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        # fall back to local write only (no persistence across deploys)
        path = current_app.config["STOCKS_PATH"]
        with open(str(path) + ".tmp", "w") as f:
            json.dump(data, f, indent=2)
        os.replace(str(path) + ".tmp", path)
        return

    # get current file SHA (required by GitHub API to update)
    meta = requests.get(
        f"{GITHUB_API}/contents/{STOCKS_PATH}?ref={BRANCH}",
        headers=_gh_headers(),
        timeout=8,
    ).json()
    sha = meta["sha"]

    content_b64 = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    resp = requests.put(
        f"{GITHUB_API}/contents/{STOCKS_PATH}",
        headers=_gh_headers(),
        json={"message": message, "content": content_b64, "sha": sha, "branch": BRANCH},
        timeout=10,
    )
    resp.raise_for_status()


@stocks_bp.get("/stocks")
def get_stocks():
    try:
        return jsonify(_read())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stocks_bp.post("/stocks")
def add_stock():
    body = request.get_json(force=True)
    if not body.get("ticker") or not body.get("display_name"):
        return jsonify({"error": "ticker and display_name are required"}), 400

    with _lock:
        data = _read()
        existing = [s["ticker"].upper() for s in data["stocks"]]
        if body["ticker"].upper() in existing:
            return jsonify({"error": "Ticker already exists"}), 409

        new_stock = {
            "ticker": body["ticker"].upper(),
            "display_name": body["display_name"],
            "active": body.get("active", True),
            "strategies": body.get("strategies", ["rsi_ema"]),
            "custom_stop_loss_pct": body.get("custom_stop_loss_pct", 5),
            "notes": body.get("notes", ""),
        }
        data["stocks"].append(new_stock)
        _write(data, f"feat: add {new_stock['ticker']} via UI")

    return jsonify(new_stock), 201


@stocks_bp.put("/stocks/<ticker>")
def update_stock(ticker):
    body = request.get_json(force=True)
    ticker_upper = ticker.upper()

    with _lock:
        data = _read()
        idx = next((i for i, s in enumerate(data["stocks"]) if s["ticker"].upper() == ticker_upper), None)
        if idx is None:
            return jsonify({"error": "Stock not found"}), 404

        data["stocks"][idx].update(body)
        _write(data, f"feat: update {ticker_upper} via UI")

    return jsonify(data["stocks"][idx])


@stocks_bp.delete("/stocks/<ticker>")
def delete_stock(ticker):
    ticker_upper = ticker.upper()

    with _lock:
        data = _read()
        before = len(data["stocks"])
        data["stocks"] = [s for s in data["stocks"] if s["ticker"].upper() != ticker_upper]
        if len(data["stocks"]) == before:
            return jsonify({"error": "Stock not found"}), 404
        _write(data, f"feat: remove {ticker_upper} via UI")

    return jsonify({"deleted": ticker_upper})


@stocks_bp.put("/settings")
def update_settings():
    allowed = {"telegram_group_chat_id", "telegram_private_chat_id", "run_time_utc", "notify_on"}
    body = request.get_json(force=True)

    with _lock:
        data = _read()
        for key in allowed:
            if key in body:
                data["settings"][key] = body[key]
        _write(data, "feat: update settings via UI")

    return jsonify(data["settings"])
