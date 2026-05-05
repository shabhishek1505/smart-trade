from common.db.repository.base_repository import BaseRepository
from common.db.models.broker_order import BrokerOrder
from datetime import datetime, timedelta
from typing import Optional, List


class BrokerOrderRepository(BaseRepository):
    """Repository for BrokerOrder model"""

    def __init__(self, session):
        super().__init__(session, BrokerOrder)

    def get_by_broker_id(self, broker_order_id: str) -> Optional[BrokerOrder]:
        """Get order by broker order ID

        Args:
            broker_order_id: Broker's order ID

        Returns:
            BrokerOrder or None
        """
        return self.session.query(BrokerOrder).filter(
            BrokerOrder.broker_order_id == broker_order_id
        ).first()

    def get_by_user_and_symbol(self, user_id: int, symbol: str) -> List[BrokerOrder]:
        """Get all orders for user and symbol

        Args:
            user_id: User ID
            symbol: Stock symbol

        Returns:
            List of BrokerOrder
        """
        return self.session.query(BrokerOrder).filter(
            BrokerOrder.user_id == user_id,
            BrokerOrder.symbol == symbol
        ).order_by(BrokerOrder.created_at.desc()).all()

    def get_pending_orders(self, user_id: int) -> List[BrokerOrder]:
        """Get all pending orders for user

        Args:
            user_id: User ID

        Returns:
            List of pending BrokerOrder
        """
        return self.session.query(BrokerOrder).filter(
            BrokerOrder.user_id == user_id,
            BrokerOrder.status.in_(["PENDING", "PARTIALLY_FILLED"])
        ).all()

    def get_filled_orders(self, user_id: int, days: int = 30) -> List[BrokerOrder]:
        """Get filled orders for user in last N days

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            List of filled BrokerOrder
        """
        start_date = datetime.now() - timedelta(days=days)
        return self.session.query(BrokerOrder).filter(
            BrokerOrder.user_id == user_id,
            BrokerOrder.status == "FILLED",
            BrokerOrder.created_at >= start_date
        ).order_by(BrokerOrder.created_at.desc()).all()

    def update_status(self, broker_order_id: str, status: str, filled_quantity: int = None, filled_price: float = None) -> bool:
        """Update order status

        Args:
            broker_order_id: Broker order ID
            status: New status
            filled_quantity: Filled quantity
            filled_price: Filled price

        Returns:
            True if successful
        """
        try:
            order = self.get_by_broker_id(broker_order_id)
            if order:
                order.status = status
                if filled_quantity is not None:
                    order.filled_quantity = filled_quantity
                if filled_price is not None:
                    order.filled_price = filled_price
                if status == "FILLED":
                    order.filled_at = datetime.now()
                order.updated_at = datetime.now()
                self.session.commit()
                return True
        except Exception as e:
            self.session.rollback()
            raise e
        return False

    def get_order_count_by_status(self, user_id: int) -> dict:
        """Get order counts by status

        Args:
            user_id: User ID

        Returns:
            Dictionary with status counts
        """
        from sqlalchemy import func

        results = self.session.query(
            BrokerOrder.status,
            func.count(BrokerOrder.id)
        ).filter(
            BrokerOrder.user_id == user_id
        ).group_by(BrokerOrder.status).all()

        return {status: count for status, count in results}
