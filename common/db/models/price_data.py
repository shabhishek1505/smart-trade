from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from common.db.base import Base


class PriceData(Base):
    __tablename__ = "price_data"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)

    # OHLC data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    # Metadata
    interval = Column(String(10), default="5M")  # 5M, 15M, 1H, 1D, etc.
    source = Column(String(20), default="ANGEL_ONE")
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Index for fast lookups
    __table_args__ = (
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_symbol_interval', 'symbol', 'interval'),
    )

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume,
            "interval": self.interval,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
