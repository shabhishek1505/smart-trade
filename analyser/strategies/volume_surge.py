def run(df, config):
    if len(df) < 21:
        return _neutral("Insufficient data for volume analysis")

    today_vol = df["volume"].iloc[-1]
    avg_vol_20 = df["volume"].tail(21).iloc[:-1].mean()  # exclude today

    if avg_vol_20 == 0:
        return _neutral("No volume data available")

    ratio = today_vol / avg_vol_20
    close_curr = df["close"].iloc[-1]
    close_prev = df["close"].iloc[-2]
    day_chg = (close_curr - close_prev) / close_prev * 100
    direction = "📈" if day_chg >= 0 else "📉"

    if ratio >= 3.0:
        return {
            "signal": "ALERT",
            "reason": f"Volume surge {ratio:.1f}x avg — {direction} {abs(day_chg):.1f}% — institutional activity detected",
            "entry_zone": None,
            "stop_loss": None,
            "target_1": None,
            "target_2": None,
        }

    return _neutral(f"Volume {ratio:.1f}x avg — no surge")


def _neutral(reason):
    return {"signal": "NEUTRAL", "reason": reason, "entry_zone": None, "stop_loss": None, "target_1": None, "target_2": None}
