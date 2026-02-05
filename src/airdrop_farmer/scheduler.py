"""
Cron-based scheduler for automated farming
"""
import time
import schedule
from datetime import datetime
from typing import Optional

from .farmer import AirdropFarmer
from .utils.logger import setup_logger
from .config import config

logger = setup_logger()


class FarmingScheduler:
    """Scheduler for automated airdrop farming"""

    def __init__(self, interval_hours: Optional[int] = None):
        """
        Initialize scheduler

        Args:
            interval_hours: Interval between runs in hours
        """
        self.interval_hours = interval_hours or config.RUN_INTERVAL_HOURS
        self.farmer = AirdropFarmer()
        self.is_running = False

        logger.info(f"Scheduler initialized with {self.interval_hours} hour interval")

    def run_farming_job(self):
        """Execute a single farming run"""
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Scheduled farming job started at {datetime.utcnow().isoformat()}")
        logger.info(f"{'=' * 80}\n")

        try:
            results = self.farmer.run_farming_activities()

            if results["status"] == "success":
                logger.info("Scheduled farming job completed successfully")
            else:
                logger.warning("Scheduled farming job completed with errors")

            return results

        except Exception as e:
            logger.error(f"Scheduled farming job failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def start(self, run_immediately: bool = True):
        """
        Start the scheduler

        Args:
            run_immediately: Whether to run farming immediately on start
        """
        logger.info("Starting farming scheduler...")

        # Setup wallets if needed
        try:
            self.farmer.setup_wallets()
        except Exception as e:
            logger.error(f"Failed to setup wallets: {e}")

        # Run immediately if requested
        if run_immediately:
            logger.info("Running initial farming cycle...")
            self.run_farming_job()

        # Schedule recurring jobs
        schedule.every(self.interval_hours).hours.do(self.run_farming_job)

        logger.info(f"Scheduler started. Next run in {self.interval_hours} hours")
        logger.info("Press Ctrl+C to stop")

        self.is_running = True

        # Run the scheduler loop
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
            self.stop()

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.is_running = False
        self.farmer.cleanup()
        logger.info("Scheduler stopped")

    def run_once(self):
        """Run farming activities once without scheduling"""
        logger.info("Running farming activities (single run)...")

        # Setup wallets if needed
        try:
            self.farmer.setup_wallets()
        except Exception as e:
            logger.error(f"Failed to setup wallets: {e}")

        # Run farming
        results = self.run_farming_job()

        # Cleanup
        self.farmer.cleanup()

        return results


def main():
    """Main entry point for scheduled farming"""
    try:
        # Validate configuration
        config.validate()

        # Create and start scheduler
        scheduler = FarmingScheduler()

        if config.ENABLE_CRON:
            # Run with scheduling
            scheduler.start(run_immediately=True)
        else:
            # Run once and exit
            scheduler.run_once()

    except Exception as e:
        logger.error(f"Scheduler failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
