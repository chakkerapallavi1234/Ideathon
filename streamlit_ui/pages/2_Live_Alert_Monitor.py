# streamlit_ui/pages/2_Live_Alert_Monitor.py
import streamlit as st
import requests
import os
from urllib.parse import urljoin
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Guardian Angel - Live Monitor", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("🔴 Live Alert Monitor")

# --- Auto-refresh control ---
refresh_rate = st.slider("Refresh rate (seconds)", 1, 10, 3)

placeholder = st.empty()

def get_alerts():
    try:
        # This endpoint needs to be created in the backend
        resp = requests.get(urljoin(BACKEND_URL, "/alerts/"))
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []

def format_severity(severity):
    if severity > 0.8:
        return f"🔥 HIGH ({severity:.2f})"
    elif severity > 0.5:
        return f"⚠️ MEDIUM ({severity:.2f})"
    else:
        return f"⚪ LOW ({severity:.2f})"

while True:
    alerts = get_alerts()
    with placeholder.container():
        if not alerts:
            st.info("No recent alerts found (or backend not reachable).")
        else:
            rows = []
            for alert in alerts:
                rows.append({
                    "Timestamp": alert.get("timestamp"),
                    "User ID": alert.get("user_id"),
                    "Severity": format_severity(alert.get("final_severity", 0)),
                    "Status": alert.get("status"),
                    "Message": alert.get("transcript", "N/A"),
                    "LLM Reason": alert.get("llm_response", {}).get("reason", "N/A"),
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

        st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    time.sleep(refresh_rate)
