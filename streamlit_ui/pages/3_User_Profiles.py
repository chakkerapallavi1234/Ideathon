# streamlit_ui/pages/3_User_Profiles.py
import streamlit as st
import requests
import os
from urllib.parse import urljoin
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Guardian Angel - User Profiles", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("👤 User Profile Management")

# --- User Selection and Creation ---
st.header("1. Select or Create User")
user_id = st.text_input("Enter User ID", "user_test_01")

# --- Fetch existing user data ---
user_data = None
if user_id:
    try:
        resp = requests.get(urljoin(BACKEND_URL, f"/profile/{user_id}"))
        if resp.status_code == 200:
            user_data = resp.json()
            st.success(f"Loaded profile for **{user_id}**")
        else:
            st.info(f"No profile found for **{user_id}**. You can create one below.")
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

# --- Profile Editor ---
st.header("2. Edit Profile")

with st.form(key="profile_form"):
    name = st.text_input("Name", value=user_data.get("name", "") if user_data else "")
    email = st.text_input("Email", value=user_data.get("email", "") if user_data else "")
    age = st.number_input("Age", min_value=0, max_value=120, value=user_data.get("age", 30) if user_data else 30)
    phone = st.text_input("Phone", value=user_data.get("phone", "") if user_data else "")
    medical_history = st.text_area("Medical History", value=user_data.get("medical_history", "") if user_data else "None")

    st.subheader("Location")
    location = streamlit_geolocation()
    st.write(location)

    st.subheader("Privacy & Consent")
    consent_data = user_data.get("consent", {}) if user_data else {}
    allow_listening = st.checkbox("Allow ambient listening for distress signals", value=consent_data.get("listening", False))
    share_location = st.checkbox("Share location with emergency responders", value=consent_data.get("share_location", False))

    st.subheader("Emergency Contacts")
    st.info("To enable SMS alerts, you must select a mobile carrier for each emergency contact.")
    
    contacts = user_data.get("emergency_contacts", []) if user_data else []
    
    # Create lists to store the values from the input widgets
    contact_names = []
    contact_phones = []
    contact_emails = []
    contact_relations = []
    contact_carriers = []
    
    # Carrier options for the dropdown
    carrier_options = ["", "airtel", "jio", "vi", "att", "tmobile", "verizon", "sprint", "uscellular"]

    # For simplicity, we'll manage a small, fixed number of contacts in the UI
    for i in range(2):
        st.markdown(f"---")
        st.markdown(f"**Contact {i+1}**")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        default_name = contacts[i]["name"] if len(contacts) > i else ""
        default_phone = contacts[i]["phone"] if len(contacts) > i else ""
        default_email = contacts[i].get("email", "") if len(contacts) > i else ""
        default_relation = contacts[i]["relation"] if len(contacts) > i else ""
        default_carrier = contacts[i].get("carrier", "") if len(contacts) > i else ""

        contact_names.append(col1.text_input(f"Name {i+1}", value=default_name, key=f"name_{i}"))
        contact_phones.append(col2.text_input(f"Phone {i+1}", value=default_phone, key=f"phone_{i}"))
        contact_emails.append(col3.text_input(f"Email {i+1}", value=default_email, key=f"email_{i}"))
        contact_relations.append(col4.text_input(f"Relation {i+1}", value=default_relation, key=f"relation_{i}"))
        st.info("The carrier field below is for SMS notifications, which may be unreliable. Email is recommended.")
        contact_carriers.append(st.selectbox(f"Carrier {i+1}", options=carrier_options, key=f"carrier_{i}", index=carrier_options.index(default_carrier) if default_carrier in carrier_options else 0, help="Select the mobile carrier for this contact to receive SMS alerts."))

    submit_button = st.form_submit_button(label="Save Profile")

    if submit_button:
        new_contacts = []
        # Correctly build the list of contacts from the form inputs
        for i in range(len(contact_names)):
            if contact_names[i] and contact_phones[i]:
                new_contacts.append({
                    "name": contact_names[i],
                    "phone": contact_phones[i],
                    "email": contact_emails[i],
                    "relation": contact_relations[i],
                    "carrier": contact_carriers[i]
                })

        payload = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "age": age,
            "phone": phone,
            "medical_history": medical_history,
            "emergency_contacts": new_contacts,
            "consent": {
                "listening": allow_listening,
                "share_location": share_location
            },
            "location": {
                "latitude": location['latitude'],
                "longitude": location['longitude']
            } if location else None
        }
        try:
            resp = requests.post(urljoin(BACKEND_URL, "/profile/"), json=payload)
            if resp.status_code == 200:
                st.success("Profile saved successfully!")
                st.json(resp.json())
                st.rerun() # Rerun to show the updated data
            else:
                st.error(f"Error saving profile: {resp.text}")
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
