from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime
from common.db.base import Base


class BrokerOrder(Base):
    __tablename__ = "broker_orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    signal_id = Column(Integer, nullable=True)  # Reference to StrategySignal

    # Order identifiers
    broker_order_id = Column(String(100), nullable=False, unique=True)  # Angel One order ID
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY or SELL

    # Order details
    order_type = Column(String(20), nullable=False)  # MARKET, LIMIT, STOPLOSS
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)  # For LIMIT orders
    sl_price = Column(Float, nullable=True)  # Stop-loss price
    target_price = Column(Float, nullable=True)  # Take-profit price

    # Execution details
    status = Column(String(20), nullable=False)  # PENDING, FILLED, PARTIALLY_FILLED, REJECTED, CANCELLED
    filled_quantity = Column(Integer, default=0)
    filled_price = Column(Float, nullable=True)  # Average fill price
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime, nullable=True)

    # Index for fast lookups
    __table_args__ = (
        Index('idx_user_symbol', 'user_id', 'symbol'),
        Index('idx_status', 'status'),
        Index('idx_broker_order_id', 'broker_order_id'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "signal_id": self.signal_id,
            "broker_order_id": self.broker_order_id,
            "symbol": self.symbol,
            "action": self.action,
            "order_type": self.order_type,
            "quantity": self.quantity,
            "price": self.price,
            "sl_price": self.sl_price,
            "target_price": self.target_price,
            "status": self.status,
            "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
        }
