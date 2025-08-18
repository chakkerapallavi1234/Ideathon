# backend/services/stt_service.py
"""
Simple Faster-Whisper STT wrapper.
Requires 'faster-whisper' package.
"""

import io
from backend.config import settings
import logging

try:
    from faster_whisper import WhisperModel
    WHISPER_MODEL = WhisperModel(settings.WHISPER_MODEL, device="cpu", compute_type="int8")
except Exception as e:
    WHISPER_MODEL = None
    logging.warning(f"Faster-Whisper model not loaded: {e}")

def transcribe_audio(audio_bytes: bytes) -> str:
    if not WHISPER_MODEL:
        # fallback mock
        return "transcription not available (whisper not loaded)"
    
    # Use an in-memory buffer instead of a temporary file
    audio_buffer = io.BytesIO(audio_bytes)
    
    segments, info = WHISPER_MODEL.transcribe(audio_buffer, beam_size=5)
    
    # Combine the transcribed segments
    transcription = "".join(segment.text for segment in segments)
    return transcription
