from sqlalchemy.orm import Session
from common.dto.signal import StrategySignalData
from common.db.models.positional import PositionConfig
from common.db.models.broker_credentials import BrokerCredentials
from common.db.models.trade_history import TradeHistory
from common.db.models.strategy_signal import StrategySignal
from common.db.repository.position_repository import PositionRepository
from common.db.repository.trade_history_repository import TradeHistoryRepository
from common.db.repository.strategy_signal_repository import StrategySignalRepository
from common.db.repository.broker_order_repository import BrokerOrderRepository
from common.db.repository.broker_credentials_repository import BrokerCredentialsRepository
from common.db.models.broker_order import BrokerOrder
from worker.brokers.factory import BrokerFactory
from common.utils.logger import init_logger
from datetime import datetime

logger = init_logger("signal-service")


class SignalService:
    """Service for executing trading signals"""

    def __init__(self, db: Session):
        self.db = db
        self.position_repo = PositionRepository(db)
        self.trade_repo = TradeHistoryRepository(db)
        self.signal_repo = StrategySignalRepository(db)
        self.order_repo = BrokerOrderRepository(db)
        self.credentials_repo = BrokerCredentialsRepository(db)

    def execute_signal(self, signal: StrategySignalData) -> dict:
        """Execute a trading signal

        Args:
            signal: StrategySignalData object

        Returns:
            Dictionary with execution result
        """
        stock = signal.stock_symbol
        user_id = signal.user_id
        broker_type = signal.broker_type or "angel_one"

        logger.info(f"Executing signal: {signal.signal} {stock} for user {user_id}")

        try:
            # 1. Validate signal
            if signal.signal.upper() not in ["BUY", "SELL", "HOLD"]:
                logger.error(f"Invalid signal action: {signal.signal}")
                return {"status": "REJECTED", "message": "Invalid signal action"}

            if signal.signal.upper() == "HOLD":
                logger.info(f"HOLD signal, no action taken")
                return {"status": "SKIPPED", "message": "HOLD signal"}

            # 2. Get user’s broker credentials
            credentials = self.credentials_repo.get_by_user_and_broker(user_id, broker_type)
            if not credentials:
                logger.error(f"No {broker_type} credentials for user {user_id}")
                return {"status": "REJECTED", "message": f"No {broker_type} credentials"}

            # 3. Create broker client
            broker = BrokerFactory.create_broker(broker_type, credentials)
            if not broker.authenticate():
                logger.error(f"Failed to authenticate broker for user {user_id}")
                return {"status": "REJECTED", "message": "Broker authentication failed"}

            # 4. Get live price and validate bounds
            live_price = broker.get_live_price(stock)
            if not live_price:
                logger.warning(f"Could not fetch live price for {stock}")
                # Use signal price if live price unavailable
                current_price = signal.price
            else:
                current_price = live_price.price

            # Validate price bounds
            if signal.upper_bound_price and current_price > signal.upper_bound_price:
                logger.warning(f"Price {current_price} exceeds upper bound {signal.upper_bound_price}")
                return {"status": "REJECTED", "message": "Price exceeds upper bound"}

            if signal.lower_bound_price and current_price < signal.lower_bound_price:
                logger.warning(f"Price {current_price} below lower bound {signal.lower_bound_price}")
                return {"status": "REJECTED", "message": "Price below lower bound"}

            # 5. Calculate quantity
            available_capital = broker.get_available_capital()
            quantity = self._calculate_quantity(current_price, signal, available_capital)

            if not quantity or quantity <= 0:
                logger.warning(f"Invalid quantity calculated: {quantity}")
                return {"status": "REJECTED", "message": "Invalid quantity"}

            # 6. Place broker order
            order_type = signal.order_type or "MARKET"
            price = current_price if order_type == "MARKET" else signal.price
            sl_price = signal.lower_bound_price if order_type != "MARKET" else None
            target_price = signal.upper_bound_price if order_type != "MARKET" else None

            order_response = broker.place_order(
                symbol=stock,
                action=signal.signal.upper(),
                quantity=quantity,
                order_type=order_type,
                price=price if order_type == "LIMIT" else None,
                sl_price=sl_price,
                target_price=target_price
            )

            if order_response.status in ["REJECTED", "CANCELLED"]:
                logger.error(f"Order rejected: {order_response.message}")
                return {"status": "REJECTED", "message": order_response.message}

            # 7. Store broker order in database
            broker_order = BrokerOrder(
                user_id=user_id,
                signal_id=signal.plan_id,
                broker_order_id=order_response.order_id,
                symbol=stock,
                action=signal.signal.upper(),
                order_type=order_type,
                quantity=quantity,
                price=price if order_type == "LIMIT" else None,
                sl_price=sl_price,
                target_price=target_price,
                status=order_response.status,
                filled_quantity=order_response.filled_quantity,
                filled_price=order_response.filled_price,
            )
            self.order_repo.create(broker_order)

            # 8. Log trade in trade history
            trade = TradeHistory(
                stock_symbol=stock,
                action=signal.signal.upper(),
                quantity=quantity,
                price=current_price,
                strategy_name=signal.strategy_name
            )
            self.trade_repo.create(trade)

            logger.info(f"Order placed successfully: {order_response.order_id}")

            return {
                "status": "EXECUTED",
                "order_id": order_response.order_id,
                "quantity": quantity,
                "price": current_price,
                "message": order_response.message
            }

        except Exception as e:
            logger.error(f"Error executing signal: {str(e)}")
            return {"status": "ERROR", "message": str(e)}
        finally:
            if ‘broker’ in locals():
                broker.disconnect()

    def _calculate_quantity(self, price: float, signal: StrategySignalData, available_capital: float) -> int:
        """Calculate order quantity based on signal and available capital

        Args:
            price: Current price
            signal: StrategySignalData
            available_capital: Available capital in account

        Returns:
            Quantity to order
        """
        try:
            # Simple strategy: use 5% of capital per trade
            trade_capital = available_capital * 0.05
            quantity = int(trade_capital / price)
            return max(1, quantity)  # At least 1 share
        except Exception as e:
            logger.error(f"Error calculating quantity: {str(e)}")
            return 0

    def get_live_price(self, stock: str) -> float:
        """Get live price for a stock

        Args:
            stock: Stock symbol

        Returns:
            Current price
        """
        try:
            # This would fetch from broker or cache
            # For now, return signal price as fallback
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching live price: {str(e)}")
            return 0.0

