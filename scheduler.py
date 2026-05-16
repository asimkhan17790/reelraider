import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from main import run_pipeline

logger = logging.getLogger(__name__)


def _run_pipeline_safe():
    try:
        run_pipeline()
    except Exception as e:
        logger.exception("Pipeline run failed: %s", e)


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(_run_pipeline_safe, CronTrigger(hour=9, minute=0))
    logger.info("Scheduler running — daily at 09:00. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
