from fastapi import APIRouter
import logging
from typing import Dict, List, Any

# Import from the webapp-specific repositories
from database.repositories import CronRepository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/cronjobs")
def read_cronjobs() -> List[Dict[str, Any]]:
    """
    Get all scheduled cronjobs.
    
    Returns:
        List of cronjob records
    """
    return CronRepository.get_all_cronjobs()
