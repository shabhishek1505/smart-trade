from common.db.repository.base_repository import BaseRepository
from common.db.models.price_data import PriceData
from datetime import datetime, timedelta
from typing import List, Optional


class PriceDataRepository(BaseRepository):
    """Repository for PriceData model"""

    def __init__(self, session):
        super().__init__(session, PriceData)

    def get_by_symbol_and_date(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "5M"
    ) -> List[PriceData]:
        """Get prices for a symbol within date range

        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            interval: Time interval

        Returns:
            List of PriceData
        """
        return self.session.query(PriceData).filter(
            PriceData.symbol == symbol,
            PriceData.interval == interval,
            PriceData.timestamp >= start_date,
            PriceData.timestamp <= end_date
        ).order_by(PriceData.timestamp).all()

    def get_latest_by_symbol(self, symbol: str, interval: str = "5M") -> Optional[PriceData]:
        """Get latest price for a symbol

        Args:
            symbol: Stock symbol
            interval: Time interval

        Returns:
            Latest PriceData or None
        """
        return self.session.query(PriceData).filter(
            PriceData.symbol == symbol,
            PriceData.interval == interval
        ).order_by(PriceData.timestamp.desc()).first()

    def get_ohlc_data(
        self,
        symbol: str,
        days: int = 30,
        interval: str = "5M"
    ) -> List[PriceData]:
        """Get OHLC data for charting

        Args:
            symbol: Stock symbol
            days: Number of days
            interval: Time interval

        Returns:
            List of PriceData
        """
        start_date = datetime.now() - timedelta(days=days)
        return self.get_by_symbol_and_date(symbol, start_date, datetime.now(), interval)

    def cleanup_old_data(self, days: int = 365):
        """Delete price data older than specified days

        Args:
            days: Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        self.session.query(PriceData).filter(
            PriceData.timestamp < cutoff_date
        ).delete()
        self.session.commit()
