from fastapi import APIRouter
import logging
from typing import List
from database.repositories import AnalysisRepository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/api/analysed_coins")
def get_analysed_coins() -> List[str]:
    """
    Returns a list of all analyzed coin symbols from the analysis_summary table.
    """
    return AnalysisRepository.get_analysed_coins()
