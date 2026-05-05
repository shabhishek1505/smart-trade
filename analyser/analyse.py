import json
import os
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

import yfinance as yf
from dotenv import load_dotenv

from strategies import STRATEGY_REGISTRY
import notifier

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
)
log = logging.getLogger("analyser")

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "stocks.json"
RESULTS_PATH = ROOT / "config" / "results.json"
IST = timezone(timedelta(hours=5, minutes=30))


def calculate_overall_signal(strategy_results):
    buy_count = sum(1 for r in strategy_results.values() if r["signal"] == "BUY")
    watch_count = sum(1 for r in strategy_results.values() if r["signal"] == "WATCH")
    avoid_count = sum(1 for r in strategy_results.values() if r["signal"] == "AVOID")

    if buy_count >= 2:
        return "🟢 STRONG BUY"
    if buy_count == 1:
        return "🟢 BUY SIGNAL"
    if watch_count >= 2:
        return "🟡 WATCH"
    if avoid_count >= 2:
        return "🔴 AVOID"
    return "⚪ NEUTRAL"


def pick_best_levels(strategy_results):
    for res in strategy_results.values():
        if res.get("signal") == "BUY" and res.get("entry_zone"):
            return {
                "best_entry_zone": res.get("entry_zone"),
                "best_stop_loss": res.get("stop_loss"),
                "best_target_1": res.get("target_1"),
                "best_target_2": res.get("target_2"),
            }
    return {"best_entry_zone": None, "best_stop_loss": None, "best_target_1": None, "best_target_2": None}


def analyse_stock(stock_cfg):
    ticker = stock_cfg["ticker"]
    log.info(f"Fetching {ticker}")

    df = yf.download(ticker, period="1y", auto_adjust=True, progress=False)
    if df.empty or len(df) < 30:
        log.warning(f"{ticker}: insufficient data")
        return None

    df.columns = [c.lower() for c in df.columns]
    df = df.dropna()

    close = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])
    day_change_pct = round((close - prev_close) / prev_close * 100, 2)

    strategy_results = {}
    for strat_name in stock_cfg.get("strategies", []):
        module = STRATEGY_REGISTRY.get(strat_name)
        if not module:
            log.warning(f"Unknown strategy: {strat_name}")
            continue
        try:
            result = module.run(df, stock_cfg)
            strategy_results[strat_name] = result
        except Exception as e:
            log.error(f"{ticker}/{strat_name} error: {e}")
            strategy_results[strat_name] = {
                "signal": "NEUTRAL",
                "reason": f"Error: {e}",
                "entry_zone": None,
                "stop_loss": None,
                "target_1": None,
                "target_2": None,
            }

    overall = calculate_overall_signal(strategy_results)
    levels = pick_best_levels(strategy_results)

    return {
        "ticker": ticker,
        "display_name": stock_cfg.get("display_name", ticker),
        "last_price": round(close, 2),
        "day_change_pct": day_change_pct,
        "overall_signal": overall,
        "strategy_results": strategy_results,
        "notes": stock_cfg.get("notes", ""),
        "run_at": datetime.now(IST).isoformat(),
        **levels,
    }


def main():
    log.info("Loading config")
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    settings = config.get("settings", {})
    stocks = [s for s in config.get("stocks", []) if s.get("active", True)]
    log.info(f"Analysing {len(stocks)} active stocks")

    results = []
    for stock in stocks:
        try:
            result = analyse_stock(stock)
            if result:
                results.append(result)
        except Exception as e:
            log.error(f"{stock['ticker']} failed: {e}")
        time.sleep(1)  # avoid Yahoo Finance rate limits

    output = {
        "last_run": datetime.now(IST).isoformat(),
        "stocks": results,
    }

    tmp_path = RESULTS_PATH.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(output, f, indent=2)
    os.replace(tmp_path, RESULTS_PATH)
    log.info(f"Results written to {RESULTS_PATH}")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        log.info("Sending Telegram notifications")
        notifier.send_daily_report(results, settings, token)
    else:
        log.warning("TELEGRAM_BOT_TOKEN not set — skipping notifications")

    log.info("Done")


if __name__ == "__main__":
    main()
