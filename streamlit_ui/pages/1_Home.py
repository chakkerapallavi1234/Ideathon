# streamlit_ui/pages/1_Home.py
import streamlit as st
import requests
import os
from urllib.parse import urljoin
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import numpy as np
from streamlit_geolocation import streamlit_geolocation
import base64

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
        # Ensure user_id is stripped of any leading/trailing whitespace or quotes
        clean_user_id = user_id.strip().strip("'\"")
        resp = requests.post(urljoin(BACKEND_URL, f"/distress/panic?user_id={clean_user_id}&latitude={lat}&longitude={lon}"))
        if resp.status_code == 200:
            st.success("✅ Panic alert sent successfully! Emergency contacts have been notified.")
            st.json(resp.json())
        else:
            st.error(f"❌ Error sending panic alert: {resp.text}")
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

# --- Detailed Alert Triggers ---
st.header("3. Detailed Alert Triggers")

with st.expander("✍️ Send a Text-based Alert"):
    text_message = st.text_area("Enter distress message here:")
    if st.button("Send Text Alert"):
        if text_message:
            # Ensure user_id is stripped of any leading/trailing whitespace or quotes
            clean_user_id = user_id.strip().strip("'\"")
            payload = {
                "user_id": clean_user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "signal_type": "text",
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

    # Diagnostics: show WebRTC states to help surface why Start button may not render
    with st.expander("WebRTC diagnostics", expanded=False):
        st.write({
            "state": getattr(webrtc_ctx.state, "name", str(webrtc_ctx.state)),
            "signaling_state": getattr(webrtc_ctx, "signaling_state", None),
            "ice_connection_state": getattr(webrtc_ctx, "ice_connection_state", None),
            "peer_connection": str(getattr(webrtc_ctx, "peer_connection", None)),
        })

    if not webrtc_ctx.state.playing:
        st.info("Recorder is off. Click 'Start' to begin recording.")
        st.warning("If recording does not start, please check your browser's microphone permissions.")
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
                    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
                    # Ensure user_id is stripped of any leading/trailing whitespace or quotes
                    clean_user_id = user_id.strip().strip("'\"")
                    payload = {
                        "user_id": clean_user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "signal_type": "voice",
                        "audio_bytes": audio_b64,
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

    # Fallback uploader
    st.divider()
    st.caption("Fallback: upload an audio file if the Start button isn't visible")
    uploaded_audio = st.file_uploader("Upload audio (wav/mp3/m4a/ogg)", type=["wav", "mp3", "m4a", "ogg"]) 
    if uploaded_audio is not None:
        if st.button("Send Uploaded Audio"):
            try:
                file_bytes = uploaded_audio.read()
                if not file_bytes:
                    st.warning("Uploaded file is empty.")
                else:
                    clean_user_id = user_id.strip().strip("'\"")
                    file_b64 = base64.b64encode(file_bytes).decode("ascii")
                    payload = {
                        "user_id": clean_user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "audio_bytes": file_b64,
                        "latitude": lat,
                        "longitude": lon,
                    }
                    resp = requests.post(urljoin(BACKEND_URL, "/distress/analyze"), json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Uploaded audio alert sent successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Error sending uploaded audio: {resp.text}")
            except Exception as e:
                st.error(f"Error sending uploaded audio: {e}")

    # Fallback 2: Simple Start/Stop mic recorder button (requires streamlit-mic-recorder)
    try:
        from st_mic_recorder import mic_recorder
        st.caption("Fallback: use the Start Recording button below (no WebRTC)")
        mic_audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", use_container_width=True, key="mic_fallback")
        if mic_audio is not None:
            # mic_recorder returns a dict with 'bytes' key
            audio_bytes2 = mic_audio.get("bytes") if isinstance(mic_audio, dict) else mic_audio
            if audio_bytes2:
                # Auto-send immediately on stop
                try:
                    clean_user_id = user_id.strip().strip("'\"")
                    b64_2 = base64.b64encode(audio_bytes2).decode("ascii")
                    payload = {
                        "user_id": clean_user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "signal_type": "voice",
                        "audio_bytes": b64_2,
                        "latitude": lat,
                        "longitude": lon,
                    }
                    resp = requests.post(urljoin(BACKEND_URL, "/distress/analyze"), json=payload)
                    if resp.status_code == 200:
                        st.success("✅ Mic recording sent successfully!")
                        st.json(resp.json())
                    else:
                        st.error(f"❌ Error sending mic recording: {resp.text}")
                except Exception as e:
                    st.error(f"Error sending mic recording: {e}")
            else:
                st.warning("No audio captured from mic recorder.")
    except Exception:
        st.caption("Optional: install 'streamlit-mic-recorder' for a simple Start/Stop button: pip install streamlit-mic-recorder")
