# streamlit_ui/components/alert_table.py
import streamlit as st
import pandas as pd

def render_table(incidents):
    if not incidents:
        st.info("No incidents to display.")
        return
    rows = []
    for inc in incidents:
        rows.append({
            "incident_id": inc.get("_id"),
            "user_id": inc.get("user_id"),
            "ts": inc.get("timestamp"),
            "severity": inc.get("final_severity"),
            "status": inc.get("status")
        })
    st.table(pd.DataFrame(rows))
