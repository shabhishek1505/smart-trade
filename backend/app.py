import json
import logging
import os
from pathlib import Path

import requests as req
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from routes.stocks import stocks_bp
from routes.signals import signals_bp

load_dotenv()

log = logging.getLogger("scheduler")

GITHUB_API = "https://api.github.com/repos/shabhishek1505/smart-trade"
WORKFLOW_FILE = "daily_analyse.yml"
BRANCH = "stock-monitor-app"


def trigger_analysis():
    pat = os.getenv("GITHUB_PAT")
    if not pat:
        log.warning("GITHUB_PAT not set — cannot trigger scheduled analysis")
        return
    try:
        resp = req.post(
            f"{GITHUB_API}/actions/workflows/{WORKFLOW_FILE}/dispatches",
            json={"ref": BRANCH},
            headers={
                "Authorization": f"Bearer {pat}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10,
        )
        if resp.status_code == 204:
            log.info("Scheduled analysis triggered successfully")
        else:
            log.error(f"Trigger failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Scheduler trigger error: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    # 9:30 AM IST, Mon–Fri
    scheduler.add_job(trigger_analysis, CronTrigger(day_of_week="mon-fri", hour=9, minute=30, timezone="Asia/Kolkata"))
    # 2:30 PM IST, Mon–Fri
    scheduler.add_job(trigger_analysis, CronTrigger(day_of_week="mon-fri", hour=14, minute=30, timezone="Asia/Kolkata"))
    scheduler.start()
    log.info("Scheduler started — jobs: 9:30 AM and 2:30 PM IST (Mon–Fri)")
    return scheduler


app = Flask(__name__)
CORS(app, origins="*")

ROOT = Path(__file__).resolve().parent.parent
app.config["STOCKS_PATH"] = ROOT / "config" / "stocks.json"
app.config["RESULTS_PATH"] = ROOT / "config" / "results.json"
app.config["ANALYSER_PATH"] = ROOT / "analyser"

app.register_blueprint(stocks_bp, url_prefix="/api")
app.register_blueprint(signals_bp, url_prefix="/api")

# Start the background scheduler (skipped during testing/reloads)
import os as _os
if not _os.environ.get("WERKZEUG_RUN_MAIN"):
    _scheduler = start_scheduler()


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
