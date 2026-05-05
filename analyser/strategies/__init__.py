from . import rsi_ema, macd, breakout, bollinger, volume_surge

STRATEGY_REGISTRY = {
    "rsi_ema": rsi_ema,
    "macd": macd,
    "breakout": breakout,
    "bollinger": bollinger,
    "volume_surge": volume_surge,
}
