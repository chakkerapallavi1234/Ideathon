# backend/services/mongodb_service.py
from pymongo import MongoClient
from backend.config import settings
from datetime import datetime
from bson.objectid import ObjectId

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client[settings.MONGO_DB]

def insert_incident(db, incident: dict):
    if isinstance(incident, dict):
        incident["created_at"] = datetime.utcnow()
    res = db.incidents.insert_one(incident)
    return res.inserted_id

def update_user_location(db, user_id: str, lat: float, lon: float):
    db.users.update_one({"user_id": user_id}, {"$push": {"location_history": {"lat": lat, "lon": lon, "ts": datetime.utcnow()}}}, upsert=True)

def get_user_by_id(db, user_id: str):
    return db.users.find_one({"user_id": user_id})
