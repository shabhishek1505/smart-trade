from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, stock_symbol: str, params: dict):
        self.stock_symbol = stock_symbol
        self.params = params

    @abstractmethod
    def evaluate(self) -> dict:
        pass
