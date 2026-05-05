import ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    close = df["close"]
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()
    ema20 = ta.trend.EMAIndicator(close=close, window=20).ema_indicator()
    ema50 = ta.trend.EMAIndicator(close=close, window=50).ema_indicator()

    rsi_val = rsi.iloc[-1]
    ema20_val = ema20.iloc[-1]
    ema50_val = ema50.iloc[-1]
    close_val = close.iloc[-1]

    if any(v != v for v in [rsi_val, ema20_val, ema50_val]):
        return _neutral("Insufficient data for RSI/EMA calculation")

    stop_loss = round(ema50_val * (1 - stop_pct / 100), 2)
    t1 = round(close_val * 1.08, 2)
    t2 = round(close_val * 1.15, 2)

    if 40 <= rsi_val <= 55 and close_val > ema50_val:
        return {
            "signal": "BUY",
            "reason": f"RSI {rsi_val:.1f} in entry zone (40–55) and price above EMA50 ({ema50_val:.2f})",
            "entry_zone": [round(ema50_val, 2), round(close_val, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }
    if 55 < rsi_val <= 65 and close_val > ema20_val:
        return {
            "signal": "WATCH",
            "reason": f"RSI {rsi_val:.1f} elevated, price above EMA20 ({ema20_val:.2f}) — wait for pullback",
            "entry_zone": [round(ema20_val, 2), round(close_val, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }
    if rsi_val > 70 or close_val < ema50_val:
        reason = f"RSI {rsi_val:.1f} overbought" if rsi_val > 70 else f"Price below EMA50 ({ema50_val:.2f})"
        return _avoid(reason)

    return _neutral(f"RSI {rsi_val:.1f} — no clear signal")


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
