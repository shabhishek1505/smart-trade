from scheduler.manager import start_scheduler_loop
from common.utils.logger import init_logger
from common.utils.config import DB_URL

init_logger("strategy-scheduler")

if __name__ == "__main__":
    start_scheduler_loop()
