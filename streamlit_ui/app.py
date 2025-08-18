# streamlit_ui/app.py
import streamlit as st
import requests
import os
from urllib.parse import urljoin
st.set_page_config(page_title="Guardian Angel - Monitor", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Guardian Angel - Live Monitor (PoC)")

st.sidebar.header("Controls")
if st.sidebar.button("Refresh incidents"):
    st.rerun()

st.header("Recent Incidents")
try:
    resp = requests.get(urljoin(BACKEND_URL, "/incidents"))
    incidents = resp.json() if resp.status_code == 200 else []
except Exception:
    incidents = []
    st.error("Could not reach backend. Is it running?")

if incidents:
    import pandas as pd
    rows = []
    for inc in incidents:
        rows.append({
            "incident_id": inc.get("_id", {}).get("$oid") if isinstance(inc.get("_id"), dict) else inc.get("_id"),
            "user_id": inc.get("user_id"),
            "ts": inc.get("timestamp"),
            "severity": inc.get("final_severity"),
            "status": inc.get("status")
        })
    st.table(pd.DataFrame(rows))
else:
    st.info("No incidents found (or backend not reachable).")

st.sidebar.markdown("---")
st.sidebar.write("Backend URL:")
st.sidebar.text_input("backend url", value=BACKEND_URL)
