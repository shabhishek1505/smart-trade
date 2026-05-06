import ta


def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    close = df["close"]
    macd_ind = ta.trend.MACD(close=close, window_slow=26, window_fast=12, window_sign=9)

    macd_line   = macd_ind.macd()
    signal_line = macd_ind.macd_signal()
    histogram   = macd_ind.macd_diff()

    if macd_line.isna().all():
        return _neutral("Insufficient data for MACD calculation")

    macd_curr = macd_line.iloc[-1]
    macd_prev = macd_line.iloc[-2]
    sig_curr  = signal_line.iloc[-1]
    sig_prev  = signal_line.iloc[-2]
    hist_curr = histogram.iloc[-1]
    hist_prev = histogram.iloc[-2]
    close_val = close.iloc[-1]

    indicators = {
        "MACD Line": round(macd_curr, 4),
        "Signal Line": round(sig_curr, 4),
        "Histogram": round(hist_curr, 4),
        "Prev Histogram": round(hist_prev, 4),
        "Crossover": "Golden ▲" if macd_curr > sig_curr else "Death ▼",
    }

    stop_loss = round(close_val * (1 - stop_pct / 100), 2)
    t1 = round(close_val * 1.08, 2)
    t2 = round(close_val * 1.15, 2)

    golden_cross = macd_prev < sig_prev and macd_curr > sig_curr
    if golden_cross and hist_curr > 0:
        return {
            "signal": "BUY",
            "reason": f"MACD golden cross — histogram positive ({hist_curr:.4f})",
            "entry_zone": [round(close_val * 0.99, 2), round(close_val, 2)],
            "stop_loss": stop_loss, "target_1": t1, "target_2": t2,
            "indicators": indicators,
        }

    if macd_curr > sig_curr and abs(hist_curr) < abs(hist_prev):
        return {
            "signal": "WATCH",
            "reason": f"MACD above signal but histogram shrinking ({hist_curr:.4f}) — momentum fading",
            "entry_zone": None, "stop_loss": stop_loss, "target_1": t1, "target_2": None,
            "indicators": indicators,
        }

    if macd_curr < sig_curr:
        return {**_avoid(f"MACD death cross — line below signal ({macd_curr:.4f} < {sig_curr:.4f})"), "indicators": indicators}

    return {**_neutral(f"MACD {macd_curr:.4f} — no crossover signal"), "indicators": indicators}


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}

def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
