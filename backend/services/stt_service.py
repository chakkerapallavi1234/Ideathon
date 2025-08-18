# backend/services/stt_service.py
"""
Simple Whisper STT wrapper.
Requires 'openai-whisper' package and ffmpeg installed (for some formats).
"""

import io
from backend.config import settings
import logging

try:
    import whisper
    WHISPER_MODEL = whisper.load_model(settings.WHISPER_MODEL)
except Exception as e:
    WHISPER_MODEL = None
    logging.warning(f"Whisper model not loaded: {e}")

def transcribe_audio(audio_bytes: bytes) -> str:
    if not WHISPER_MODEL:
        # fallback mock
        return "transcription not available (whisper not loaded)"
    # write bytes to temp file-like object
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        f.write(audio_bytes)
        f.flush()
        result = WHISPER_MODEL.transcribe(f.name)
        return result.get("text", "")
