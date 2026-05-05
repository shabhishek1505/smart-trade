from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from common.db.base import Base


class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    strategy_name = Column(String(100), nullable=False)

    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)  # 0.0 to 1.0

    # P&L metrics
    total_pnl = Column(Float, default=0.0)
    avg_profit = Column(Float, default=0.0)
    avg_loss = Column(Float, default=0.0)
    max_profit = Column(Float, default=0.0)
    max_loss = Column(Float, default=0.0)

    # Risk metrics
    max_drawdown = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)  # Gross profit / Gross loss
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)

    # Signal metrics
    total_signals = Column(Integer, default=0)
    executed_signals = Column(Integer, default=0)
    signal_accuracy = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for fast lookups
    __table_args__ = (
        Index('idx_user_strategy', 'user_id', 'strategy_name'),
        Index('idx_strategy_name', 'strategy_name'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "strategy_name": self.strategy_name,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "total_pnl": self.total_pnl,
            "avg_profit": self.avg_profit,
            "avg_loss": self.avg_loss,
            "max_profit": self.max_profit,
            "max_loss": self.max_loss,
            "max_drawdown": self.max_drawdown,
            "profit_factor": self.profit_factor,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "total_signals": self.total_signals,
            "executed_signals": self.executed_signals,
            "signal_accuracy": self.signal_accuracy,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
