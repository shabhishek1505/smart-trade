import pandas_ta as ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    df = df.copy()
    df.ta.rsi(length=14, append=True)
    df.ta.ema(length=20, append=True)
    df.ta.ema(length=50, append=True)

    close = df["close"].iloc[-1]
    rsi = df["RSI_14"].iloc[-1]
    ema20 = df["EMA_20"].iloc[-1]
    ema50 = df["EMA_50"].iloc[-1]

    if any(v != v for v in [rsi, ema20, ema50]):  # NaN check
        return _neutral("Insufficient data for RSI/EMA calculation")

    stop_loss = round(ema50 * (1 - stop_pct / 100), 2)
    t1 = round(close * 1.08, 2)
    t2 = round(close * 1.15, 2)

    if 40 <= rsi <= 55 and close > ema50:
        return {
            "signal": "BUY",
            "reason": f"RSI {rsi:.1f} in entry zone (40–55) and price above EMA50 ({ema50:.2f})",
            "entry_zone": [round(ema50, 2), round(close, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }
    if 55 < rsi <= 65 and close > ema20:
        return {
            "signal": "WATCH",
            "reason": f"RSI {rsi:.1f} elevated, price above EMA20 ({ema20:.2f}) — wait for pullback",
            "entry_zone": [round(ema20, 2), round(close, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }
    if rsi > 70 or close < ema50:
        reason = f"RSI {rsi:.1f} overbought" if rsi > 70 else f"Price below EMA50 ({ema50:.2f})"
        return _avoid(reason)

    return _neutral(f"RSI {rsi:.1f} — no clear signal")


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
