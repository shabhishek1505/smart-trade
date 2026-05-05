import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from routes.stocks import stocks_bp
from routes.signals import signals_bp

load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")

ROOT = Path(__file__).resolve().parent.parent
app.config["STOCKS_PATH"] = ROOT / "config" / "stocks.json"
app.config["RESULTS_PATH"] = ROOT / "config" / "results.json"
app.config["ANALYSER_PATH"] = ROOT / "analyser"

app.register_blueprint(stocks_bp, url_prefix="/api")
app.register_blueprint(signals_bp, url_prefix="/api")


@app.post("/webhook")
def telegram_webhook():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", {})
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not chat_id:
        return jsonify({"ok": True})

    def reply(msg):
        import requests as req
        req.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"},
            timeout=5,
        )

    if text.startswith("/start"):
        reply("👋 Welcome to <b>Stock Monitor</b>! You'll receive daily NSE signals here. Use /status to check the last run time.")
    elif text.startswith("/status"):
        try:
            with open(app.config["RESULTS_PATH"]) as f:
                results = json.load(f)
            last_run = results.get("last_run", "Never")
            reply(f"✅ Last analysis: <b>{last_run}</b>\nStocks monitored: {len(results.get('stocks', []))}")
        except Exception:
            reply("⚠️ No results yet. Run the analyser first.")
    elif text.startswith("/today"):
        import subprocess, sys
        analyser = app.config["ANALYSER_PATH"] / "analyse.py"
        subprocess.Popen([sys.executable, str(analyser)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        reply("⏳ Analysis started — results will be posted shortly.")
    elif text.startswith("/stop"):
        reply("⏸ Daily reports paused. Edit the cron in GitHub Actions to re-enable.")
    else:
        reply("Commands: /status /today /stop")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
