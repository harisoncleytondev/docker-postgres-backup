from apscheduler.schedulers.blocking import BlockingScheduler
from scripts.drive_upload import upload

scheduler = BlockingScheduler()

def start():
    scheduler.add_job(upload, 'cron', hour=3, minute=0)
    scheduler.start()
