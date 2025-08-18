# backend/routes/profile.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from backend.services.mongodb_service import get_db
from backend.models.user import User
from bson import json_util
import json

router = APIRouter(prefix="/profile", tags=["profile"])

@router.post("/")
def create_or_update_user(user: User, db: Database = Depends(get_db)):
    """
    Create or update a user profile.
    """
    user_data = jsonable_encoder(user)
    db.users.update_one(
        {"user_id": user.user_id},
        {"$set": user_data},
        upsert=True
    )
    return user

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str, db: Database = Depends(get_db)):
    """
    Retrieve a user profile by user_id.
    """
    user = db.users.find_one({"user_id": user_id})
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")
