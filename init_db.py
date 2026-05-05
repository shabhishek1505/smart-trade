#!/usr/bin/env python
"""
Initialize the database schema
"""

from common.db.base import Base
from common.db.session import engine
from common.db.models import (
    user, trade_history, position, strategy_signal,
    strategy, broker_credentials, user_settings
)
from common.utils.logger import init_logger

logger = init_logger("db-init")

if __name__ == "__main__":
    try:
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully!")
        logger.info("All tables created.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
