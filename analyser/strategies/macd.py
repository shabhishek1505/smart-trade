import pandas_ta as ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    df = df.copy()
    df.ta.macd(fast=12, slow=26, signal=9, append=True)

    macd_col = "MACD_12_26_9"
    hist_col = "MACDh_12_26_9"
    sig_col = "MACDs_12_26_9"

    if macd_col not in df.columns or df[macd_col].isna().all():
        return _neutral("Insufficient data for MACD calculation")

    close = df["close"].iloc[-1]
    macd_curr = df[macd_col].iloc[-1]
    macd_prev = df[macd_col].iloc[-2]
    sig_curr = df[sig_col].iloc[-1]
    sig_prev = df[sig_col].iloc[-2]
    hist_curr = df[hist_col].iloc[-1]
    hist_prev = df[hist_col].iloc[-2]

    stop_loss = round(close * (1 - stop_pct / 100), 2)
    t1 = round(close * 1.08, 2)
    t2 = round(close * 1.15, 2)

    golden_cross = macd_prev < sig_prev and macd_curr > sig_curr
    hist_positive = hist_curr > 0

    if golden_cross and hist_positive:
        return {
            "signal": "BUY",
            "reason": f"MACD golden cross — line crossed above signal, histogram positive ({hist_curr:.4f})",
            "entry_zone": [round(close * 0.99, 2), round(close, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }

    hist_flattening = macd_curr > sig_curr and abs(hist_curr) < abs(hist_prev)
    if hist_flattening:
        return {
            "signal": "WATCH",
            "reason": f"MACD above signal but histogram shrinking ({hist_curr:.4f}) — momentum fading",
            "entry_zone": None,
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": None,
        }

    if macd_curr < sig_curr:
        return _avoid(f"MACD death cross — line below signal ({macd_curr:.4f} < {sig_curr:.4f})")

    return _neutral(f"MACD {macd_curr:.4f} — no crossover signal")


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
