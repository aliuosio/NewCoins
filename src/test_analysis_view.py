from utils.analysis_view import refresh_analysis_view, get_latest_analysis
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Test the analysis view creation and refresh.
    """
    try:
        # Refresh the view
        refresh_analysis_view()
        
        # Get latest analysis for SOL
        sol_analysis = get_latest_analysis("SOL")
        
        if sol_analysis:
            logger.info("Latest analysis for SOL:")
            logger.info(f"Total Score: {sol_analysis['total_score']}")
            logger.info(f"Score Percentage: {sol_analysis['score_percentage']}%")
            logger.info(f"Recommendation: {sol_analysis['recommendation']}")
        else:
            logger.warning("No analysis found for SOL")
            
    except Exception as e:
        logger.error(f"Error in test script: {str(e)}")

if __name__ == "__main__":
    main()
