import time
import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[notifier] Failed to send to {chat_id}: {e}")


def build_summary(results, run_at):
    date_str = run_at.strftime("%d %b %Y | %H:%M IST")
    counts = {"BUY": 0, "WATCH": 0, "AVOID": 0, "NEUTRAL": 0}
    for r in results:
        sig = r.get("overall_signal", "")
        if "BUY" in sig:
            counts["BUY"] += 1
        elif "WATCH" in sig:
            counts["WATCH"] += 1
        elif "AVOID" in sig:
            counts["AVOID"] += 1
        else:
            counts["NEUTRAL"] += 1

    return (
        f"📊 <b>DAILY REPORT — {date_str}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 BUY signals:   {counts['BUY']}\n"
        f"🟡 WATCH signals: {counts['WATCH']}\n"
        f"🔴 AVOID:         {counts['AVOID']}\n"
        f"⚪ NEUTRAL:      {counts['NEUTRAL']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Total monitored: {len(results)} stocks"
    )


def _llm_line(r):
    """Return a compact AI verdict line, or empty string if not available."""
    llm = r.get("llm_verdict")
    if not llm:
        return ""
    icons = {"BULLISH": "🤖▲", "BEARISH": "🤖▼", "NEUTRAL": "🤖◆"}
    icon = icons.get(llm["verdict"], "🤖")
    conf = llm.get("confidence", "")
    return f"{icon} AI: <b>{llm['verdict']}</b> ({conf})"


def build_buy_message(buys, run_at):
    date_str = run_at.strftime("%d %b %Y")
    lines = [f"🟢 <b>BUY SIGNALS — {date_str}</b>\n"]
    for r in buys:
        lines.append(f"━━━━━━━━━━━━━━━━━━━")
        chg = r.get("day_change_pct", 0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        lines.append(f"<b>{r['display_name']}</b> — ₹{r['last_price']:.2f} ({chg_str})")

        tags = []
        for strat, res in r.get("strategy_results", {}).items():
            sig = res.get("signal", "")
            icon = "✅" if sig == "BUY" else ("🔔" if sig == "ALERT" else "")
            label = strat.upper().replace("_", "+")
            tags.append(f"[{label}] {sig} {icon}")
        lines.append("  ".join(tags))

        entry = r.get("best_entry_zone")
        sl = r.get("best_stop_loss")
        t1 = r.get("best_target_1")
        t2 = r.get("best_target_2")
        if entry:
            parts = [f"Entry: ₹{entry[0]}–{entry[1]}"]
            if sl:
                parts.append(f"SL: ₹{sl}")
            if t1:
                parts.append(f"T1: ₹{t1}")
            if t2:
                parts.append(f"T2: ₹{t2}")
            lines.append(" | ".join(parts))

        ai = _llm_line(r)
        if ai:
            lines.append(ai)
        lines.append("")
    return "\n".join(lines)


def build_watch_message(watches, run_at):
    date_str = run_at.strftime("%d %b %Y")
    lines = [f"🟡 <b>WATCH LIST — {date_str}</b>\n"]
    for r in watches:
        lines.append(f"━━━━━━━━━━━━━━━━━━━")
        chg = r.get("day_change_pct", 0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        lines.append(f"<b>{r['display_name']}</b> — ₹{r['last_price']:.2f} ({chg_str})")

        for strat, res in r.get("strategy_results", {}).items():
            if res.get("signal") == "WATCH":
                lines.append(f"  {res.get('reason', '')}")

        ai = _llm_line(r)
        if ai:
            lines.append(ai)
        lines.append("")
    return "\n".join(lines)


def build_private_detail(results, run_at):
    date_str = run_at.strftime("%d %b %Y | %H:%M IST")
    lines = [f"🔒 <b>PRIVATE NOTES — {date_str}</b>\n"]
    for r in results:
        lines.append(f"━━━━━━━━━━━━━━━━━━━")
        chg = r.get("day_change_pct", 0)
        chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
        lines.append(f"<b>{r['display_name']}</b> ({r['ticker']}) — ₹{r['last_price']:.2f} ({chg_str})")
        lines.append(f"Signal: {r.get('overall_signal', '⚪ NEUTRAL')}")

        for strat, res in r.get("strategy_results", {}).items():
            lines.append(f"  [{strat}] {res.get('signal')} — {res.get('reason', '')}")

        llm = r.get("llm_verdict")
        if llm:
            icons = {"BULLISH": "▲", "BEARISH": "▼", "NEUTRAL": "◆"}
            icon = icons.get(llm["verdict"], "◆")
            lines.append(
                f"🤖 AI {icon} <b>{llm['verdict']}</b> ({llm.get('confidence', '')}) — {llm.get('reasoning', '')}"
            )
            ctx = llm.get("market_context", "").strip()
            if ctx:
                lines.append(f"   <i>{ctx}</i>")

        notes = r.get("notes", "").strip()
        if notes:
            lines.append(f"📝 {notes}")
        lines.append("")
    return "\n".join(lines)


def send_daily_report(results, settings, token):
    run_at = datetime.now(IST)
    group_id = settings.get("telegram_group_chat_id")
    private_id = settings.get("telegram_private_chat_id")
    notify_on = settings.get("notify_on", ["BUY", "WATCH"])

    send_message(token, group_id, build_summary(results, run_at))
    time.sleep(1)

    buys = [r for r in results if "BUY" in r.get("overall_signal", "") and
            any(n in r.get("overall_signal", "") for n in notify_on)]
    if buys:
        send_message(token, group_id, build_buy_message(buys, run_at))
        time.sleep(1)

    watches = [r for r in results if "WATCH" in r.get("overall_signal", "") and "WATCH" in notify_on]
    if watches:
        send_message(token, group_id, build_watch_message(watches, run_at))
        time.sleep(1)

    send_message(token, private_id, build_private_detail(results, run_at))
