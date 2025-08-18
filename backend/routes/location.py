# backend/routes/location.py
from fastapi import APIRouter
from backend.services.mongodb_service import get_db, update_user_location

router = APIRouter()

@router.post("/update")
async def update_location(user_id: str, lat: float, lon: float):
    db = get_db()
    update_user_location(db, user_id, lat, lon)
    return {"status": "ok"}
