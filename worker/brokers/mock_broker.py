from worker.brokers.base_broker import BrokerClient, OrderResponse, OrderStatus, Position, PriceData
from common.db.models.broker_credentials import BrokerCredentials
from common.utils.logger import init_logger
from datetime import datetime
from typing import List, Optional, Dict
import uuid

logger = init_logger("mock-broker")


class MockBrokerClient(BrokerClient):
    """Mock broker client for testing and development"""

    def __init__(self, credentials: BrokerCredentials):
        """Initialize mock broker client"""
        self.credentials = credentials
        self.user_id = credentials.user_id
        self.is_authenticated = False
        self.orders = {}  # Simulated order storage
        self.positions = {}  # Simulated positions
        self.available_capital = 100000.0  # Simulated account balance
        self.price_data = {}  # Simulated price data

    def authenticate(self) -> bool:
        """Mock authentication"""
        logger.info(f"Mock: Authenticated for user {self.user_id}")
        self.is_authenticated = True
        return True

    def place_order(
        self,
        symbol: str,
        action: str,
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        sl_price: Optional[float] = None,
        target_price: Optional[float] = None,
    ) -> OrderResponse:
        """Mock order placement"""
        if not self.is_authenticated:
            return OrderResponse(
                order_id="",
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                status="REJECTED",
                message="Not authenticated"
            )

        # Generate mock order ID
        order_id = f"MOCK_{uuid.uuid4().hex[:8].upper()}"

        # Get current price (mock)
        current_price = self.price_data.get(symbol, 100.0)

        # Calculate filled price
        if order_type == "MARKET":
            filled_price = current_price
        elif order_type == "LIMIT" and price:
            filled_price = price
        else:
            filled_price = current_price

        # Update available capital
        self.available_capital -= filled_price * quantity

        # Store order
        self.orders[order_id] = {
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "status": "FILLED",
            "filled_quantity": quantity,
            "filled_price": filled_price,
            "timestamp": datetime.now(),
        }

        # Update positions
        if symbol not in self.positions:
            self.positions[symbol] = {"quantity": 0, "avg_price": 0.0}

        if action.upper() == "BUY":
            self.positions[symbol]["quantity"] += quantity
            self.positions[symbol]["avg_price"] = filled_price
        elif action.upper() == "SELL":
            self.positions[symbol]["quantity"] -= quantity

        logger.info(f"Mock: Order placed {order_id} - {action} {quantity} {symbol}")

        return OrderResponse(
            order_id=order_id,
            symbol=symbol,
            action=action,
            quantity=quantity,
            price=price,
            status="FILLED",
            filled_quantity=quantity,
            filled_price=filled_price,
            message="Mock order filled successfully",
            timestamp=datetime.now(),
        )

    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """Get mock order status"""
        if order_id in self.orders:
            order = self.orders[order_id]
            return OrderStatus(
                order_id=order_id,
                status=order["status"],
                filled_quantity=order.get("filled_quantity", 0),
                filled_price=order.get("filled_price"),
                updated_at=order.get("timestamp", datetime.now())
            )
        return None

    def cancel_order(self, order_id: str) -> bool:
        """Mock order cancellation"""
        if order_id in self.orders:
            self.orders[order_id]["status"] = "CANCELLED"
            logger.info(f"Mock: Order cancelled {order_id}")
            return True
        return False

    def get_live_price(self, symbol: str) -> Optional[PriceData]:
        """Get mock price"""
        price = self.price_data.get(symbol, 100.0)
        return PriceData(
            symbol=symbol,
            price=price,
            bid=price - 0.5,
            ask=price + 0.5,
            timestamp=datetime.now(),
        )

    def set_mock_price(self, symbol: str, price: float):
        """Set mock price for testing"""
        self.price_data[symbol] = price

    def get_positions(self) -> List[Position]:
        """Get mock positions"""
        positions = []
        for symbol, data in self.positions.items():
            if data["quantity"] != 0:
                current_price = self.price_data.get(symbol, 100.0)
                unrealized_pnl = (current_price - data["avg_price"]) * data["quantity"]
                positions.append(Position(
                    symbol=symbol,
                    quantity=data["quantity"],
                    avg_price=data["avg_price"],
                    current_price=current_price,
                    unrealized_pnl=unrealized_pnl
                ))
        return positions

    def get_available_capital(self) -> float:
        """Get mock available capital"""
        return self.available_capital

    def get_holdings(self) -> Dict[str, Dict]:
        """Get mock holdings"""
        holdings = {}
        for symbol, data in self.positions.items():
            if data["quantity"] > 0:
                current_price = self.price_data.get(symbol, 100.0)
                holdings[symbol] = {
                    "quantity": data["quantity"],
                    "price": data["avg_price"],
                    "current_price": current_price,
                }
        return holdings

    def disconnect(self):
        """Mock disconnect"""
        logger.info("Mock: Disconnected")
        self.is_authenticated = False
