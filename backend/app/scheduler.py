from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.feed_fetcher import FeedFetcher
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def fetch_all_feeds_job():
    """Background job to fetch all feeds"""
    db: Session = SessionLocal()
    try:
        fetcher = FeedFetcher(db)
        results = fetcher.fetch_all_feeds()
        logger.info(f"Feed fetch job completed. Results: {results}")
    except Exception as e:
        logger.error(f"Error in feed fetch job: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Run every 30 minutes
        scheduler.add_job(
            fetch_all_feeds_job,
            trigger=IntervalTrigger(minutes=30),
            id='fetch_all_feeds',
            name='Fetch all feeds',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

