# backend/routes/distress.py
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.services.llm_service import assess_urgency
from backend.services.mongodb_service import get_db, insert_incident
from backend.services.milvus_service import upsert_embedding
from backend.services.stt_service import transcribe_audio
from backend.models.distress_event import DistressEventCreate
from backend.services.notifier_service import notify_contacts
from datetime import datetime
import asyncio

router = APIRouter()

DISTRESS_PHRASES = [
    "help me", "i can't breathe", "emergency", "angel code 9",
    "gunshot", "scream", "screaming", "i'm scared", "don't hurt me"
]

@router.post("/analyze")
async def analyze_event(event: DistressEventCreate, background_tasks: BackgroundTasks):
    db = get_db()
    # If audio provided as bytes in this PoC, process it (or expect transcript)
    transcript = event.transcript
    if event.audio_bytes:
        transcript = transcribe_audio(event.audio_bytes)

    # Call LLM to assess urgency
    llm_resp = assess_urgency(event.user_id, transcript, event.audio_events or [], event.sensor_data or {})
    severity = llm_resp.get("urgency", 0.0)

    incident_doc = {
        "user_id": event.user_id,
        "timestamp": event.timestamp,
        "transcript": transcript,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "audio_events": event.audio_events or [],
        "sensor_data": event.sensor_data or {},
        "llm_response": llm_resp,
        "final_severity": severity,
        "status": "pending"
    }

    inserted = insert_incident(db, incident_doc)

    # background upsert to milvus
    background_tasks.add_task(upsert_embedding, str(inserted), transcript)

    # If urgency is high, trigger notification as a background task
    if severity > 0.7:
        background_tasks.add_task(notify_contacts, incident_doc)

    return {"incident_id": str(inserted), "severity": severity, "llm": llm_resp}


@router.post("/wearable_trigger")
async def wearable_trigger(user_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None):
    """
    A dedicated endpoint for a wearable device's panic button.
    """
    db = get_db()
    incident_doc = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "transcript": "WEARABLE PANIC BUTTON ACTIVATED",
        "latitude": latitude,
        "longitude": longitude,
        "final_severity": 1.0,
        "status": "confirmed"
    }
    inserted = insert_incident(db, incident_doc)
    notify_contacts(incident_doc)
    return {"incident_id": str(inserted), "status": "confirmed"}


@router.post("/fall_detection")
async def fall_detection(user_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None):
    """
    Endpoint for fall detection from a wearable device.
    """
    db = get_db()
    incident_doc = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "transcript": "FALL DETECTED BY WEARABLE DEVICE",
        "latitude": latitude,
        "longitude": longitude,
        "final_severity": 0.9,
        "status": "confirmed"
    }
    inserted = insert_incident(db, incident_doc)
    notify_contacts(incident_doc)
    return {"incident_id": str(inserted), "status": "confirmed"}


@router.post("/listen")
async def listen_for_distress(event: DistressEventCreate):
    """
    Analyzes a short audio clip for distress phrases.
    This is designed to be called in a continuous stream from the frontend.
    """
    if not event.audio_bytes:
        raise HTTPException(status_code=400, detail="No audio data provided.")

    transcript = transcribe_audio(event.audio_bytes).lower()
    
    for phrase in DISTRESS_PHRASES:
        if phrase in transcript:
            # If a distress phrase is found, create a high-severity incident
            db = get_db()
            incident_doc = {
                "user_id": event.user_id,
                "timestamp": datetime.utcnow(),
                "transcript": f"DISTRESS PHRASE DETECTED: '{transcript}'",
                "latitude": event.latitude,
                "longitude": event.longitude,
                "final_severity": 0.9,
                "status": "confirmed"
            }
            inserted = insert_incident(db, incident_doc)
            notify_contacts(incident_doc)
            return {"status": "distress_detected", "incident_id": str(inserted)}

    return {"status": "no_distress_detected"}


@router.post("/panic")
async def panic_button(user_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None):
    """
    A simple, dedicated endpoint for a "panic button" feature.
    Immediately triggers a high-severity alert.
    """
    db = get_db()
    incident_doc = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "transcript": "PANIC BUTTON ACTIVATED",
        "latitude": latitude,
        "longitude": longitude,
        "audio_events": [],
        "sensor_data": {},
        "llm_response": {"urgency": 1.0, "reason": "Panic button"},
        "final_severity": 1.0,
        "status": "confirmed"
    }
    inserted = insert_incident(db, incident_doc)

    # Immediately trigger notification
    notify_contacts(incident_doc)

    return {"incident_id": str(inserted), "status": "confirmed", "severity": 1.0}


@router.post("/sms_trigger")
async def sms_trigger(event: DistressEventCreate, background_tasks: BackgroundTasks):
    """
    Triggers an alert based on an incoming SMS message.
    Checks for a safety phrase or uses LLM to assess urgency.
    """
    db = get_db()
    transcript = event.transcript.lower()

    # Check for safety phrase
    for phrase in DISTRESS_PHRASES:
        if phrase in transcript:
            incident_doc = {
                "user_id": event.user_id,
                "timestamp": datetime.utcnow(),
                "transcript": f"SMS TRIGGER (SAFETY PHRASE): '{transcript}'",
                "latitude": event.latitude,
                "longitude": event.longitude,
                "final_severity": 1.0,
                "status": "confirmed"
            }
            inserted = insert_incident(db, incident_doc)
            background_tasks.add_task(notify_contacts, incident_doc)
            return {"status": "distress_detected", "incident_id": str(inserted)}

    # If no safety phrase, use LLM to assess urgency
    llm_resp = assess_urgency(event.user_id, transcript, [], {})
    severity = llm_resp.get("urgency", 0.0)

    incident_doc = {
        "user_id": event.user_id,
        "timestamp": event.timestamp,
        "transcript": f"SMS TRIGGER (ANALYSIS): '{transcript}'",
        "latitude": event.latitude,
        "longitude": event.longitude,
        "llm_response": llm_resp,
        "final_severity": severity,
        "status": "pending"
    }

    inserted = insert_incident(db, incident_doc)

    if severity > 0.7:
        background_tasks.add_task(notify_contacts, incident_doc)

    return {"incident_id": str(inserted), "severity": severity, "llm": llm_resp}
