# backend/models/user.py
from pydantic import BaseModel, Field
from typing import List, Optional

class EmergencyContact(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    relation: Optional[str] = None
    carrier: Optional[str] = None

class User(BaseModel):
    user_id: str
    name: str
    age: Optional[int] = None
    phone: str
    email: Optional[str] = None
    emergency_contacts: List[EmergencyContact] = Field(default_factory=list)
    medical_history: Optional[str] = None
    consent: dict = Field(default_factory=lambda: {"listening": False, "share_location": False})
