# backend/models/distress_event.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class DistressEventCreate(BaseModel):
    user_id: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    signal_type: Optional[str] = "voice"  # voice | text | sensor
    transcript: Optional[str] = None
    audio_events: Optional[List[str]] = None
    sensor_data: Optional[dict] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # For PoC we can accept base64/bytes, but FastAPI File uploads are simpler
    audio_bytes: Optional[bytes] = None
