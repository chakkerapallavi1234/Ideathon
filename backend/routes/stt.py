# backend/routes/stt.py
from fastapi import APIRouter, UploadFile, File
from backend.services.stt_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save to temp and transcribe
    audio_bytes = await file.read()
    text = transcribe_audio(audio_bytes)
    return {"transcript": text}
