import time
import logging
from utils.analysis_view import refresh_analysis_view

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("view_refresher")

def refresh_view():
    """Refresh the analysis summary view every hour."""
    while True:
        try:
            logger.info("Refreshing analysis summary view...")
            refresh_analysis_view()
            logger.info("View refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing view: {str(e)}")
        
        # Wait for 1 hour
        time.sleep(3600)

if __name__ == '__main__':
    refresh_view()
