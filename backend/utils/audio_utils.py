# backend/utils/audio_utils.py
import io
import wave

def save_wav_bytes(path: str, audio_bytes: bytes):
    with open(path, "wb") as f:
        f.write(audio_bytes)
    return path
