#!/usr/bin/env python
"""Initialize broker integration tables in database"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.db.base import Base
from common.db.session import engine
from common.db.models import (
    BrokerCredentials,
    PriceData,
    BrokerOrder,
    StrategyPerformance,
)
from common.utils.logger import init_logger

logger = init_logger("init-broker-tables")


def create_tables():
    """Create all broker-related tables"""
    try:
        logger.info("Creating broker integration tables...")

        # Create all tables
        Base.metadata.create_all(engine)

        logger.info("✓ BrokerCredentials table created")
        logger.info("✓ PriceData table created")
        logger.info("✓ BrokerOrder table created")
        logger.info("✓ StrategyPerformance table created")

        logger.info("All tables created successfully!")
        return True

    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False


def drop_tables():
    """Drop all broker-related tables (use with caution!)"""
    try:
        logger.warning("Dropping all broker integration tables...")

        Base.metadata.drop_all(engine)

        logger.warning("All tables dropped!")
        return True

    except Exception as e:
        logger.error(f"Error dropping tables: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("⚠️  Are you sure you want to DROP all broker tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Cancelled.")
    else:
        create_tables()
