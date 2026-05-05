import json
import logging
import os
import re
import time
from datetime import datetime, timezone

log = logging.getLogger("llm_analyser")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
MAX_RETRIES = 2


def _build_prompt(stock_result: dict) -> str:
    ticker = stock_result["ticker"]
    name = stock_result["display_name"]
    price = stock_result["last_price"]
    chg = stock_result["day_change_pct"]
    overall = stock_result["overall_signal"]
    strategies = stock_result.get("strategy_results", {})
    notes = stock_result.get("notes", "")

    signal_lines = []
    for strat, res in strategies.items():
        signal_lines.append(f"  - {strat}: {res['signal']} — {res.get('reason', '')}")
    signals_text = "\n".join(signal_lines) if signal_lines else "  (none)"

    notes_line = f"\nAnalyst note: {notes}" if notes else ""

    return f"""You are a stock market analyst specialising in NSE India equities.

Stock: {name} ({ticker})
Current price: ₹{price:,.2f} ({'+' if chg >= 0 else ''}{chg:.2f}% today)
Technical verdict: {overall}

Technical strategy signals:
{signals_text}{notes_line}

Based on these technical signals AND your knowledge of this company's business, sector trends, and broader Indian market context, give your independent analysis.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "verdict": "BULLISH" | "BEARISH" | "NEUTRAL",
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "reasoning": "<2-3 sentences combining technical + fundamental context>",
  "market_context": "<one concise line about sector/macro backdrop>"
}}"""


def _parse_response(text: str) -> dict:
    text = re.sub(r"```(?:json)?", "", text).strip()
    data = json.loads(text)
    allowed_verdicts = {"BULLISH", "BEARISH", "NEUTRAL"}
    allowed_confidence = {"HIGH", "MEDIUM", "LOW"}
    if data.get("verdict") not in allowed_verdicts:
        data["verdict"] = "NEUTRAL"
    if data.get("confidence") not in allowed_confidence:
        data["confidence"] = "MEDIUM"
    return {
        "verdict": data["verdict"],
        "confidence": data["confidence"],
        "reasoning": str(data.get("reasoning", ""))[:400],
        "market_context": str(data.get("market_context", ""))[:200],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def analyse(stock_result: dict) -> dict | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log.warning("GEMINI_API_KEY not set — skipping LLM analysis")
        return None

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = _build_prompt(stock_result)
        ticker = stock_result.get("ticker", "?")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = client.models.generate_content(model=MODEL, contents=prompt)
                return _parse_response(response.text)
            except Exception as e:
                err = str(e)
                # Extract suggested retry delay from 429 error
                retry_match = re.search(r"retry_delay\s*\{\s*seconds:\s*(\d+)", err)
                if "429" in err and retry_match and attempt < MAX_RETRIES:
                    wait = int(retry_match.group(1)) + 2
                    log.warning(f"{ticker}: rate limited — waiting {wait}s before retry {attempt}")
                    time.sleep(wait)
                else:
                    raise
    except Exception as e:
        log.error(f"Gemini error for {stock_result.get('ticker')}: {e}")
        return None
