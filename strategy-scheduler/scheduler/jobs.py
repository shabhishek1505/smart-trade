from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from common.db.session import SessionLocal
from common.db.repository import get_enabled_strategy_plans
from kafka.producer import send_strategy_eval_message
import logging

from common.dto.strategy import StrategyTriggerData

logger = logging.getLogger("strategy-scheduler.jobs")


def job_runner(job_data: StrategyTriggerData):
    logger.info(f"[Job Triggered] PlanID={job_data.plan_id}, StrategyID={job_data.strategy_id}, Stock={job_data.stock_symbol}")
    send_strategy_eval_message(job_data)


def load_and_schedule_jobs(scheduler):
    logger.info("Loading strategy plans from DB...")

    with SessionLocal() as db:
        rows = get_enabled_strategy_plans(db)
    scheduler.remove_all_jobs()

    for row in rows:
        cron_expr = row.override_cron or row.strategy_master.default_cron

        job_data = StrategyTriggerData(
            plan_id=row.plan_id,
            strategy_id=row.strategy_id,
            strategy_name=row.strategy_master.strategy_name,
            stock_symbol=row.stock_symbol,
            override_params=row.override_params
        )
        

        if not cron_expr:
            logger.warning(f"[Skipping] No cron for PlanID={job_data.plan_id}")
            continue

        try:
            trigger = CronTrigger.from_crontab(cron_expr)
            scheduler.add_job(
                func=job_runner,
                trigger=trigger,
                args=[job_data],
                id=str(job_data.plan_id),
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            logger.info(f"[Scheduled] PlanID={job_data.plan_id}, Stock={job_data.stock_symbol}, Cron={cron_expr}")
        except Exception as e:
            logger.error(f"[Error] Failed to schedule PlanID={job_data.plan_id}: {e}")
