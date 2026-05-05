from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrderResponse:
    """Response from order placement"""
    order_id: str
    symbol: str
    action: str
    quantity: int
    price: Optional[float]
    status: str
    message: str = ""
    filled_quantity: int = 0
    filled_price: Optional[float] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "symbol": self.symbol,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "status": self.status,
            "message": self.message,
            "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class OrderStatus:
    """Order status details"""
    order_id: str
    status: str  # PENDING, FILLED, PARTIALLY_FILLED, REJECTED, CANCELLED
    filled_quantity: int
    filled_price: Optional[float]
    updated_at: datetime


@dataclass
class Position:
    """Current position"""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    unrealized_pnl: float


@dataclass
class PriceData:
    """Price data"""
    symbol: str
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[int] = None
    timestamp: Optional[datetime] = None


class BrokerClient(ABC):
    """Abstract base class for broker integrations"""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with broker"""
        pass

    @abstractmethod
    def place_order(
        self,
        symbol: str,
        action: str,  # "BUY" or "SELL"
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        sl_price: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> OrderResponse:
        """Place an order on the broker

        Args:
            symbol: Stock symbol (e.g., "INFY")
            action: "BUY" or "SELL"
            quantity: Number of shares
            order_type: "MARKET", "LIMIT", "STOPLOSS"
            price: Entry price for LIMIT orders
            sl_price: Stop-loss price
            target_price: Take-profit price

        Returns:
            OrderResponse with order details
        """
        pass

    @abstractmethod
    def get_order_status(self, order_id: str) -> OrderStatus:
        """Get status of an order"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass

    @abstractmethod
    def get_live_price(self, symbol: str) -> PriceData:
        """Get current price for a symbol"""
        pass

    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get all current positions"""
        pass

    @abstractmethod
    def get_available_capital(self) -> float:
        """Get available capital/cash balance"""
        pass

    @abstractmethod
    def get_holdings(self) -> Dict[str, Dict]:
        """Get current holdings with details"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from broker"""
        pass
