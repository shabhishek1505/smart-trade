import pandas_ta as ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    df = df.copy()
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.rsi(length=14, append=True)

    lower_col = "BBL_20_2.0"
    upper_col = "BBU_20_2.0"
    bw_col = "BBB_20_2.0"
    rsi_col = "RSI_14"

    missing = [c for c in [lower_col, upper_col, bw_col, rsi_col] if c not in df.columns]
    if missing:
        return _neutral("Insufficient data for Bollinger Band calculation")

    close = df["close"].iloc[-1]
    lower = df[lower_col].iloc[-1]
    upper = df[upper_col].iloc[-1]
    rsi = df[rsi_col].iloc[-1]
    bw_curr = df[bw_col].iloc[-1]
    bw_mean = df[bw_col].tail(20).mean()

    stop_loss = round(lower * (1 - stop_pct / 100), 2)
    t1 = round(close * 1.08, 2)
    t2 = round(close * 1.15, 2)

    if close <= lower and rsi < 35:
        return {
            "signal": "BUY",
            "reason": f"Price ₹{close:.2f} at/below lower BB ₹{lower:.2f} with RSI {rsi:.1f} (oversold)",
            "entry_zone": [round(lower, 2), round(close, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }

    squeeze = bw_curr < bw_mean * 0.8
    if squeeze:
        return {
            "signal": "WATCH",
            "reason": f"Bollinger squeeze detected — bandwidth {bw_curr:.2f} below 20-day avg {bw_mean:.2f} (breakout imminent)",
            "entry_zone": None,
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }

    if close >= upper and rsi > 65:
        return _avoid(f"Price at upper BB ₹{upper:.2f} with RSI {rsi:.1f} — overbought")

    return _neutral(f"Price ₹{close:.2f} within bands ({lower:.2f}–{upper:.2f}), RSI {rsi:.1f}")


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
