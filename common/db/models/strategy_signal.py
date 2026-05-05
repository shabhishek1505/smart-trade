# common/db/models/strategy_signal.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from common.db.base import Base

class StrategySignal(Base):
    __tablename__ = "strategy_signals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    strategy_id = Column(Integer, nullable=False)
    plan_id = Column(Integer, nullable=False)
    stock_symbol = Column(String(20), nullable=False)
    signal_type = Column(String(10), nullable=False)  # BUY / SELL / HOLD
    confidence = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=True)
    lower_bound = Column(Float, nullable=True)
    reason = Column(String, nullable=True)
    status = Column(String(20), default="PENDING")  # PENDING, EXECUTED, CANCELLED
    timestamp = Column(DateTime, default=datetime.utcnow)
    executed = Column(Boolean, default=False)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
