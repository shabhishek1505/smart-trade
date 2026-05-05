from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, Boolean, ForeignKey, Float
from common.db.base import Base
from datetime import datetime
from sqlalchemy.orm import relationship


class StrategyMaster(Base):
    __tablename__ = "strategy_master"

    strategy_id = Column(Integer, primary_key=True)
    strategy_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    default_cron = Column(String(50), nullable=False)
    default_params = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-many relationship to StrategyPlan
    plans = relationship("StrategyPlan", back_populates="strategy_master")


class StrategyPlan(Base):
    __tablename__ = "strategy_plan"

    plan_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    strategy_id = Column(Integer, ForeignKey("strategy_master.strategy_id"), nullable=False)
    stock_symbol = Column(String(20), nullable=False)
    enabled = Column(Boolean, default=True)
    override_cron = Column(String(50), nullable=True)
    override_params = Column(JSON, nullable=True)
    total_signals = Column(Integer, default=0)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    last_executed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    #relationships
    strategy_master = relationship("StrategyMaster", back_populates="plans")

