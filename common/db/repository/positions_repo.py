from common.db.models import Position
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
import logging

logger = logging.getLogger("strategy.worker.repo")

def log_position(db: Session, stock: str, quantity: int, action: str, price: float):
    position = Position(
        stock_symbol=stock,
        quantity=quantity,
        action=action.upper(),
        executed_price=price,
        executed_at=datetime.utcnow()
    )
    db.add(position)
    db.commit()
    logger.info(f"[DB] Logged {action.upper()} for {quantity}x {stock} @ {price}")
