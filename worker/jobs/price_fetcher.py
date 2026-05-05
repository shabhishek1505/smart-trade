from worker.services.price_service import PriceService
from common.db.session import get_session
from common.db.models.broker_credentials import BrokerCredentials
from common.utils.logger import init_logger
from datetime import datetime, timedelta
import traceback

logger = init_logger("price-fetcher-job")


def fetch_prices_for_all_users():
    """Fetch prices for all active users"""
    try:
        session = get_session()
        service = PriceService()
        service.session = session

        # Get all active broker credentials
        credentials_list = session.query(BrokerCredentials).filter(
            BrokerCredentials.is_active == True,
            BrokerCredentials.broker_type == "angel_one"
        ).all()

        if not credentials_list:
            logger.info("No active credentials found")
            return

        logger.info(f"Found {len(credentials_list)} active users")

        # Symbols to fetch (can be configured)
        symbols = [
            "INFY", "TCS", "RELIANCE", "HDFC", "ICICIBANK",
            "WIPRO", "LT", "MARUTI", "BAJAJFINSV", "HCLTECH"
        ]

        success_count = 0
        for credentials in credentials_list:
            try:
                user_id = credentials.user_id
                logger.info(f"Fetching prices for user {user_id}")

                if service.fetch_and_store_prices(
                    user_id=user_id,
                    symbols=symbols,
                    interval="5M",
                    days=30
                ):
                    success_count += 1
                    logger.info(f"Successfully fetched prices for user {user_id}")
                else:
                    logger.warning(f"Failed to fetch prices for user {user_id}")

            except Exception as e:
                logger.error(f"Error processing user {credentials.user_id}: {str(e)}")
                traceback.print_exc()

        logger.info(f"Price fetch job completed: {success_count}/{len(credentials_list)} users")

    except Exception as e:
        logger.error(f"Critical error in price fetcher job: {str(e)}")
        traceback.print_exc()
    finally:
        service.close()
        session.close()


def fetch_prices_for_user(user_id: int, symbols: list = None):
    """Fetch prices for a specific user

    Args:
        user_id: User ID
        symbols: List of symbols (optional)
    """
    try:
        session = get_session()
        service = PriceService()
        service.session = session

        if symbols is None:
            symbols = [
                "INFY", "TCS", "RELIANCE", "HDFC", "ICICIBANK",
                "WIPRO", "LT", "MARUTI", "BAJAJFINSV", "HCLTECH"
            ]

        logger.info(f"Fetching prices for user {user_id}: {symbols}")

        if service.fetch_and_store_prices(user_id, symbols):
            logger.info(f"Successfully fetched prices for user {user_id}")
        else:
            logger.warning(f"Failed to fetch prices for user {user_id}")

    except Exception as e:
        logger.error(f"Error fetching prices for user {user_id}: {str(e)}")
        traceback.print_exc()
    finally:
        service.close()
        session.close()


def schedule_price_fetcher():
    """Schedule price fetcher job with APScheduler

    This should be called from the main application startup
    """
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BackgroundScheduler()

        # Schedule to run every 5 minutes
        scheduler.add_job(
            fetch_prices_for_all_users,
            trigger=IntervalTrigger(minutes=5),
            id='price_fetcher',
            name='Fetch prices for all users',
            replace_existing=True,
            misfire_grace_time=30,  # Grace period if job is delayed
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("Price fetcher scheduler started")

        return scheduler

    except Exception as e:
        logger.error(f"Error scheduling price fetcher: {str(e)}")
        traceback.print_exc()
        return None
