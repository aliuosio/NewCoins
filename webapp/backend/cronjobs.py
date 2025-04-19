from fastapi import APIRouter
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.utils.cron_db import get_cronjobs

router = APIRouter()

@router.get("/api/cronjobs")
def read_cronjobs():
    rows = get_cronjobs()
    # Return as a list of dicts for easy frontend consumption
    return [
        {
            "id": row[0],
            "schedule": row[1],
            "command": row[2],
            "created_at": row[3].isoformat() if row[3] else None
        } for row in rows
    ]
