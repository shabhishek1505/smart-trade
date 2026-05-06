import ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    close = df["close"]
    bb  = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    rsi = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    lower     = bb.bollinger_lband().iloc[-1]
    upper     = bb.bollinger_hband().iloc[-1]
    mid       = bb.bollinger_mavg().iloc[-1]
    wband     = bb.bollinger_wband()
    rsi_val   = rsi.iloc[-1]
    close_val = close.iloc[-1]

    wband_curr = wband.iloc[-1]
    wband_mean = wband.tail(20).mean()

    indicators = {
        "Upper Band": round(upper, 2),
        "Middle Band": round(mid, 2),
        "Lower Band": round(lower, 2),
        "Bandwidth": round(wband_curr, 2),
        "Avg Bandwidth (20)": round(wband_mean, 2),
        "RSI (14)": round(rsi_val, 1),
    }

    stop_loss = round(lower * (1 - stop_pct / 100), 2)
    t1 = round(close_val * 1.08, 2)
    t2 = round(close_val * 1.15, 2)

    if close_val <= lower and rsi_val < 35:
        return {
            "signal": "BUY",
            "reason": f"Price ₹{close_val:.2f} at/below lower BB ₹{lower:.2f} with RSI {rsi_val:.1f} (oversold)",
            "entry_zone": [round(lower, 2), round(close_val, 2)],
            "stop_loss": stop_loss, "target_1": t1, "target_2": t2,
            "indicators": indicators,
        }

    if wband_curr < wband_mean * 0.8:
        return {
            "signal": "WATCH",
            "reason": f"Bollinger squeeze — bandwidth {wband_curr:.2f} below avg {wband_mean:.2f} (breakout imminent)",
            "entry_zone": None, "stop_loss": stop_loss, "target_1": t1, "target_2": t2,
            "indicators": indicators,
        }

    if close_val >= upper and rsi_val > 65:
        return {**_avoid(f"Price at upper BB ₹{upper:.2f} with RSI {rsi_val:.1f} — overbought"), "indicators": indicators}

    return {**_neutral(f"Price ₹{close_val:.2f} within bands ({lower:.2f}–{upper:.2f}), RSI {rsi_val:.1f}"), "indicators": indicators}


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}

def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
