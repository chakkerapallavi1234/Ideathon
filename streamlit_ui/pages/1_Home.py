# streamlit_ui/pages/1_Home.py
import streamlit as st
import requests
import os
from urllib.parse import urljoin
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import numpy as np
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Guardian Angel - Home", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("👼 Guardian Angel - User Simulation")

# --- User Selection & Location ---
st.header("1. User and Location Setup")
user_id = st.text_input("Enter a User ID to simulate", "user_test_01")

st.subheader("Your Location")
st.info("Your browser's location will be sent with any alert. You can also manually enter coordinates below.")
location = streamlit_geolocation()

lat_manual = st.number_input("Manual Latitude (Optional)", value=location.get('latitude', 0.0), format="%.6f")
lon_manual = st.number_input("Manual Longitude (Optional)", value=location.get('longitude', 0.0), format="%.6f")

# Use browser location if available, otherwise fall back to manual input
lat = location.get('latitude', lat_manual)
lon = location.get('longitude', lon_manual)


if not user_id:
    st.warning("Please enter a User ID to proceed.")
    st.stop()

st.info(f"Simulating actions for **{user_id}** at Latitude: **{lat}**, Longitude: **{lon}**")

# --- Panic Button (Most Important) ---
st.header("2. Immediate Distress Signal")
if st.button("🚨 ACTIVATE PANIC BUTTON 🚨", key="panic_button", help="Click here for immediate, high-priority assistance."):
    try:
        resp = requests.post(urljoin(BACKEND_URL, f"/distress/panic?user_id={user_id}&latitude={lat}&longitude={lon}"))
        if resp.status_code == 200:
            st.success("✅ Panic alert sent successfully! Emergency contacts have been notified.")
            st.json(resp.json())
        else:
            st.error(f"❌ Error sending panic alert: {resp.text}")
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

# --- Detailed Alert Triggers ---
st.header("3. Detailed Alert Triggers")

with st.expander("🎤 Enable Ambient Listening"):
    st.info("When enabled, the application will listen for distress phrases and automatically trigger an alert.")
    ambient_listening = st.toggle("Enable Ambient Listening", key="ambient_listening")

    if ambient_listening:
        st.success("Ambient listening is now active.")
        webrtc_streamer(
            key="ambient-listener",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            media_stream_constraints={"video": False, "audio": True},
            async_processing=True,
            audio_frame_callback=lambda frame: asyncio.run(send_audio_chunk(frame))
        )

async def send_audio_chunk(frame):
    """Sends a chunk of audio to the backend for analysis."""
    sound_chunk = np.concatenate([af.to_ndarray() for af in frame])
    audio_bytes = sound_chunk.tobytes()
    payload = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "audio_bytes": audio_bytes.hex(),
        "latitude": lat,
        "longitude": lon,
    }
    requests.post(urljoin(BACKEND_URL, "/distress/listen"), json=payload)

with st.expander("✍️ Send a Text-based Alert"):
    text_message = st.text_area("Enter distress message here:")
    if st.button("Send Text Alert"):
        if text_message:
            payload = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "transcript": text_message,
                "latitude": lat,
                "longitude": lon,
            }
            try:
                resp = requests.post(urljoin(BACKEND_URL, "/distress/analyze"), json=payload)
                if resp.status_code == 200:
                    st.success("✅ Text alert sent successfully!")
                    st.json(resp.json())
                else:
                    st.error(f"❌ Error sending alert: {resp.text}")
            except Exception as e:
                st.error(f"Could not connect to backend: {e}")
        else:
            st.warning("Please enter a message.")

with st.expander("🎤 Send a Voice-based Alert"):
    st.write("Click 'start' to record audio from your microphone.")
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"video": False, "audio": True},
    )

    if not webrtc_ctx.state.playing:
        st.info("Recorder is off.")
    else:
        st.success("🔴 Recording... Speak now.")

    if st.button("Send Recorded Audio"):
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if not audio_frames:
                    st.warning("No audio received. Please record something first.")
                else:
                    sound_chunk = np.concatenate([af.to_ndarray() for af in audio_frames])
                    audio_bytes = sound_chunk.tobytes()
                    payload = {
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "audio_bytes": audio_bytes.hex(),
                        "latitude": lat,
                        "longitude": lon,
                    }
                    resp = requests.post(urljoin(BACKEND_URL, "/distress/analyze"), json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Audio alert sent successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Error sending audio alert: {resp.text}")
            except Exception as e:
                st.error(f"Error processing audio: {e}")
        else:
            st.warning("Audio receiver not available. Is the recorder running?")
