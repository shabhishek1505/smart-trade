from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.jobs import load_and_schedule_jobs
from common.utils.config import REFRESH_INTERVAL
import time
import logging

logger = logging.getLogger("strategy-scheduler.manager")

def start_scheduler_loop():
    scheduler = BackgroundScheduler()
    scheduler.start()
    logger.info("Strategy Scheduler started")

    # Initial job loading
    load_and_schedule_jobs(scheduler)

    try:
        while True:
            time.sleep(REFRESH_INTERVAL)
            logger.info("Refreshing job schedules...")
            load_and_schedule_jobs(scheduler)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down.")
