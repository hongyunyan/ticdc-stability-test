import schedule
import time
import logging
import sys
from datetime import datetime
from stability_test import StabilityTest

class StabilityTestScheduler:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_stability_test_job(self):
        """Job function to run stability test"""
        self.logger.info("Scheduled stability test job started")
        
        try:
            stability_test = StabilityTest()
            stability_test.run_stability_test()
            self.logger.info("Scheduled stability test job completed successfully")
        except Exception as e:
            self.logger.error(f"Scheduled stability test job failed: {e}")
            # Don't raise the exception to prevent scheduler from stopping
    
    def schedule_daily_test(self, hour: int = 20, minute: int = 0):
        """Schedule daily stability test at specified time (UTC+8)"""
        # Schedule job to run daily at specified time
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.run_stability_test_job)
        
        self.logger.info(f"Scheduled daily stability test at {hour:02d}:{minute:02d} (UTC+8)")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        self.logger.info("Starting stability test scheduler")
        self.logger.info("Press Ctrl+C to stop the scheduler")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
            raise

def main():
    """Main entry point for scheduler"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "run-now":
            # Run test immediately
            scheduler = StabilityTestScheduler()
            scheduler.run_stability_test_job()
        elif sys.argv[1] == "schedule":
            # Run scheduler
            scheduler = StabilityTestScheduler()
            # Schedule for 8 PM UTC+8 (which is 12 PM UTC)
            scheduler.schedule_daily_test(hour=12, minute=0)
            scheduler.run_scheduler()
        else:
            print("Usage:")
            print("  python scheduler.py run-now  - Run stability test immediately")
            print("  python scheduler.py schedule - Start the daily scheduler")
    else:
        print("Usage:")
        print("  python scheduler.py run-now  - Run stability test immediately")
        print("  python scheduler.py schedule - Start the daily scheduler")

if __name__ == "__main__":
    main()
