def run(df, config):
    stop_pct = config.get("custom_stop_loss_pct", 5)

    if len(df) < 30:
        return _neutral("Insufficient data for breakout analysis")

    close = df["close"].iloc[-1]
    today_vol = df["volume"].iloc[-1]
    high_52w = df["high"].tail(252).max()
    avg_vol_20 = df["volume"].tail(20).mean()

    pct_from_high = (high_52w - close) / high_52w

    stop_loss = round(close * (1 - stop_pct / 100), 2)
    t1 = round(high_52w * 1.03, 2)
    t2 = round(high_52w * 1.08, 2)

    if pct_from_high <= 0.02 and today_vol > avg_vol_20 * 1.5:
        return {
            "signal": "BUY",
            "reason": f"Price ₹{close:.2f} within 2% of 52w high ₹{high_52w:.2f} with {today_vol/avg_vol_20:.1f}x avg volume",
            "entry_zone": [round(close * 0.99, 2), round(close, 2)],
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }

    if 0.05 <= pct_from_high <= 0.10:
        return {
            "signal": "WATCH",
            "reason": f"Price {pct_from_high*100:.1f}% below 52w high ₹{high_52w:.2f} — approaching breakout zone",
            "entry_zone": None,
            "stop_loss": stop_loss,
            "target_1": t1,
            "target_2": t2,
        }

    if pct_from_high > 0.15:
        return _avoid(f"Price {pct_from_high*100:.1f}% below 52w high ₹{high_52w:.2f} — far from breakout")

    return _neutral(f"Price {pct_from_high*100:.1f}% below 52w high — no breakout signal")


def _avoid(reason):
    return {"signal": "AVOID", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
