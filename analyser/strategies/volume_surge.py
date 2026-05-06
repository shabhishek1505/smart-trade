def run(df, config):
    if len(df) < 21:
        return _neutral("Insufficient data for volume analysis")

    today_vol = df["volume"].iloc[-1]
    avg_vol   = df["volume"].tail(21).iloc[:-1].mean()

    if avg_vol == 0:
        return _neutral("No volume data available")

    ratio      = today_vol / avg_vol
    close_curr = df["close"].iloc[-1]
    close_prev = df["close"].iloc[-2]
    day_chg    = (close_curr - close_prev) / close_prev * 100
    direction  = "📈" if day_chg >= 0 else "📉"

    def _fmt_vol(v):
        if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
        if v >= 1_000:     return f"{v/1_000:.0f}K"
        return str(int(v))

    indicators = {
        "Today Volume": _fmt_vol(today_vol),
        "20D Avg Volume": _fmt_vol(avg_vol),
        "Volume Ratio": f"{ratio:.1f}x",
        "Day Change": f"{'+' if day_chg >= 0 else ''}{day_chg:.2f}%",
    }

    if ratio >= 3.0:
        return {
            "signal": "ALERT",
            "reason": f"Volume surge {ratio:.1f}x avg — {direction} {abs(day_chg):.1f}% — institutional activity detected",
            "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None,
            "indicators": indicators,
        }

    return {**_neutral(f"Volume {ratio:.1f}x avg — no surge"), "indicators": indicators}


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
