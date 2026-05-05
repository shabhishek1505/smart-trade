# common/db/models/trade_history.py
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from common.db.base import Base

class TradeHistory(Base):
    __tablename__ = "trade_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY / SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=False)
    pnl = Column(Float, nullable=True, default=0.0)
    status = Column(String(20), default="OPEN")  # OPEN, CLOSED
    strategy = Column(String(100), nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
