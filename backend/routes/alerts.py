# backend/routes/alerts.py
from fastapi import APIRouter, Depends
from pymongo.database import Database
from backend.services.mongodb_service import get_db
from bson import json_util
import json

router = APIRouter()

@router.get("/")
def get_all_alerts(db: Database = Depends(get_db)):
    """
    Retrieves the 50 most recent alerts from the database.
    """
    alerts = db.incidents.find().sort("timestamp", -1).limit(50)
    # Use json_util to handle MongoDB's specific data types (like ObjectId)
    return json.loads(json_util.dumps(list(alerts)))
