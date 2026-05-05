from .sma_rsi_macd import SmaRsiMacdStrategy
from .moving_avg_crossover import MovingAvgCrossoverStrategy
from .rsi_macd import RsiMacdStrategy
from .price_action_breakout import PriceActionBreakoutStrategy

STRATEGY_MAP = {
    "sma_rsi_macd": SmaRsiMacdStrategy,
    "moving_avg_crossover": MovingAvgCrossoverStrategy,
    "rsi_macd": RsiMacdStrategy,
    "price_action_breakout": PriceActionBreakoutStrategy
}

def get_strategy(strategy_name: str):
    return STRATEGY_MAP.get(strategy_name)
