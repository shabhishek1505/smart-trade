import json
import os
import threading

import requests
from flask import Blueprint, request, jsonify, current_app

stocks_bp = Blueprint("stocks", __name__)
_lock = threading.Lock()

GITHUB_RAW = "https://raw.githubusercontent.com/shabhishek1505/smart-trade/stock-monitor-app"


def _read_github():
    resp = requests.get(f"{GITHUB_RAW}/config/stocks.json", timeout=8)
    resp.raise_for_status()
    return resp.json()


def _read_local():
    with open(current_app.config["STOCKS_PATH"]) as f:
        return json.load(f)


def _read():
    try:
        return _read_github()
    except Exception:
        return _read_local()


def _write(data):
    path = current_app.config["STOCKS_PATH"]
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


@stocks_bp.get("/stocks")
def get_stocks():
    return jsonify(_read())


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
        _write(data)

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
        _write(data)
        updated = data["stocks"][idx]

    return jsonify(updated)


@stocks_bp.delete("/stocks/<ticker>")
def delete_stock(ticker):
    ticker_upper = ticker.upper()

    with _lock:
        data = _read()
        before = len(data["stocks"])
        data["stocks"] = [s for s in data["stocks"] if s["ticker"].upper() != ticker_upper]
        if len(data["stocks"]) == before:
            return jsonify({"error": "Stock not found"}), 404
        _write(data)

    return jsonify({"deleted": ticker_upper})


@stocks_bp.put("/settings")
def update_settings():
    body = request.get_json(force=True)
    allowed = {"telegram_group_chat_id", "telegram_private_chat_id", "run_time_utc", "notify_on"}

    with _lock:
        data = _read()
        for key in allowed:
            if key in body:
                data["settings"][key] = body[key]
        _write(data)

    return jsonify(data["settings"])
