from .sma_rsi_macd import SmaRsiMacdStrategy

STRATEGY_MAP = {
    "sma_rsi_macd": SmaRsiMacdStrategy
}

def get_strategy(strategy_name: str):
    return STRATEGY_MAP.get(strategy_name)
