# common/db/models/position.py
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from common.db.base import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False, default=0.0)
    invested_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False, default=0.0)
    strategy = Column(String(100), nullable=True)
    entry_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
