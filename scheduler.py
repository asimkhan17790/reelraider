from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from main import run_pipeline


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, CronTrigger(hour=9, minute=0))
    print("[scheduler] running daily at 09:00. Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("[scheduler] stopped.")
