from common.db.session import get_session
from common.db.models.price_data import PriceData
from common.db.repository.price_data_repository import PriceDataRepository
from common.db.models.broker_credentials import BrokerCredentials
from worker.brokers.factory import BrokerFactory
from common.utils.logger import init_logger
from datetime import datetime, timedelta
from typing import List, Optional
import threading
import time

logger = init_logger("price-service")


class PriceService:
    """Service for managing price data"""

    def __init__(self):
        self.session = None
        self.repository = None

    def _ensure_session(self):
        """Ensure database session is initialized"""
        if self.session is None:
            self.session = get_session()
            self.repository = PriceDataRepository(self.session)

    def fetch_and_store_prices(
        self,
        user_id: int,
        symbols: List[str],
        interval: str = "5M",
        days: int = 30
    ) -> bool:
        """Fetch historical prices from Angel One and store in database

        Args:
            user_id: User ID (for credential lookup)
            symbols: List of stock symbols
            interval: Time interval (5M, 15M, 1H, 1D)
            days: Number of days of history to fetch

        Returns:
            True if successful, False otherwise
        """
        self._ensure_session()

        try:
            # Get user's Angel One credentials
            credentials = self.session.query(BrokerCredentials).filter(
                BrokerCredentials.user_id == user_id,
                BrokerCredentials.broker_type == "angel_one",
                BrokerCredentials.is_active == True
            ).first()

            if not credentials:
                logger.warning(f"No active Angel One credentials for user {user_id}")
                return False

            # Create broker client
            broker = BrokerFactory.create_broker("angel_one", credentials)
            if not broker.authenticate():
                logger.error(f"Failed to authenticate broker for user {user_id}")
                return False

            # Fetch prices for each symbol
            start_date = datetime.now() - timedelta(days=days)
            success_count = 0

            for symbol in symbols:
                try:
                    # Fetch historical data from broker
                    # Note: This is a simplified implementation
                    # Actual implementation depends on Angel One API capabilities
                    prices = self._fetch_symbol_history(broker, symbol, interval, start_date)

                    if prices:
                        # Store in database
                        for price_data in prices:
                            self.repository.create(price_data)
                        success_count += 1
                        logger.info(f"Stored {len(prices)} price records for {symbol}")
                except Exception as e:
                    logger.error(f"Error fetching prices for {symbol}: {str(e)}")

            logger.info(f"Price fetch completed: {success_count}/{len(symbols)} symbols")
            return success_count > 0

        except Exception as e:
            logger.error(f"Error in fetch_and_store_prices: {str(e)}")
            return False
        finally:
            broker.disconnect()

    def _fetch_symbol_history(self, broker, symbol: str, interval: str, start_date: datetime) -> List[PriceData]:
        """Fetch historical prices for a symbol

        Note: This is a placeholder. Actual implementation depends on Angel One API.
        Angel One may have limitations on historical data retrieval.

        Args:
            broker: BrokerClient instance
            symbol: Stock symbol
            interval: Time interval
            start_date: Start date for history

        Returns:
            List of PriceData objects
        """
        prices = []

        try:
            # Placeholder: In production, call broker's historical data API
            # For now, we'll create mock data for testing
            current_price = 100.0
            current_date = start_date

            while current_date <= datetime.now():
                # Create OHLC data
                open_price = current_price
                close_price = current_price + (1.0 if current_price % 2 == 0 else -1.0)
                high_price = max(open_price, close_price) + 2.0
                low_price = min(open_price, close_price) - 2.0

                price_data = PriceData(
                    symbol=symbol,
                    open_price=open_price,
                    high_price=high_price,
                    low_price=low_price,
                    close_price=close_price,
                    volume=100000,
                    interval=interval,
                    timestamp=current_date,
                )
                prices.append(price_data)

                # Move to next interval
                if interval == "5M":
                    current_date += timedelta(minutes=5)
                elif interval == "15M":
                    current_date += timedelta(minutes=15)
                elif interval == "1H":
                    current_date += timedelta(hours=1)
                elif interval == "1D":
                    current_date += timedelta(days=1)

                current_price = close_price

        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {str(e)}")

        return prices

    def get_cached_prices(
        self,
        symbol: str,
        days: int = 30,
        interval: str = "5M"
    ) -> List[PriceData]:
        """Get cached prices from database

        Args:
            symbol: Stock symbol
            days: Number of days to fetch
            interval: Time interval

        Returns:
            List of PriceData objects
        """
        self._ensure_session()

        try:
            start_date = datetime.now() - timedelta(days=days)
            prices = self.session.query(PriceData).filter(
                PriceData.symbol == symbol,
                PriceData.interval == interval,
                PriceData.timestamp >= start_date
            ).order_by(PriceData.timestamp).all()

            return prices
        except Exception as e:
            logger.error(f"Error fetching cached prices: {str(e)}")
            return []

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest close price for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Latest close price or None
        """
        self._ensure_session()

        try:
            latest = self.session.query(PriceData).filter(
                PriceData.symbol == symbol
            ).order_by(PriceData.timestamp.desc()).first()

            if latest:
                return latest.close_price
        except Exception as e:
            logger.error(f"Error fetching latest price: {str(e)}")

        return None

    def subscribe_live_prices(self, user_id: int, symbols: List[str]):
        """Subscribe to live prices via broker WebSocket

        Args:
            user_id: User ID
            symbols: List of symbols to subscribe
        """
        try:
            credentials = self.session.query(BrokerCredentials).filter(
                BrokerCredentials.user_id == user_id,
                BrokerCredentials.broker_type == "angel_one",
                BrokerCredentials.is_active == True
            ).first()

            if not credentials:
                logger.warning(f"No credentials for user {user_id}")
                return

            broker = BrokerFactory.create_broker("angel_one", credentials)
            if broker.authenticate():
                logger.info(f"Subscribed to live prices for {len(symbols)} symbols")
            else:
                logger.error("Failed to authenticate for live prices")

        except Exception as e:
            logger.error(f"Error subscribing to live prices: {str(e)}")

    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
            self.session = None
