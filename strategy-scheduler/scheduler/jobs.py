from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from common.db.session import SessionLocal
from common.db.repository import get_enabled_strategy_plans
from kafka.producer import send_strategy_eval_message
import logging

logger = logging.getLogger("strategy-scheduler.jobs")


def job_runner(plan_id, strategy_id, stock_symbol):
    logger.info(f"[Job Triggered] PlanID={plan_id}, StrategyID={strategy_id}, Stock={stock_symbol}")
    send_strategy_eval_message(plan_id, strategy_id, stock_symbol)


def load_and_schedule_jobs(scheduler):
    logger.info("Loading strategy plans from DB...")

    with SessionLocal() as db:
        rows = get_enabled_strategy_plans(db)
    scheduler.remove_all_jobs()

    for row in rows:
        plan_id = row.plan_id
        strategy_id = row.strategy_id
        stock_symbol = row.stock_symbol
        cron_expr = row.override_cron or row.strategy_master.default_cron

        if not cron_expr:
            logger.warning(f"[Skipping] No cron for PlanID={plan_id}")
            continue

        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            scheduler.add_job(
                func=job_runner,
                trigger=trigger,
                args=[plan_id, strategy_id, stock_symbol],
                id=str(plan_id),
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            logger.info(f"[Scheduled] PlanID={plan_id}, Stock={stock_symbol}, Cron={cron_expr}")
        except Exception as e:
            logger.error(f"[Error] Failed to schedule PlanID={plan_id}: {e}")
