# backend/services/notifier_service.py
from backend.config import settings
import logging
import yagmail
import requests
from backend.services.mongodb_service import get_db, get_user_by_id

CARRIER_GATEWAYS = {
    # India
    "airtel": "airtelmail.com",
    "jio": "jio.com",
    "vi": "vims.net",
    # US
    "att": "txt.att.net",
    "tmobile": "tmomail.net",
    "verizon": "vtext.com",
    "sprint": "messaging.sprintpcs.com",
    "uscellular": "email.uscc.net",
}

def send_email_notification(contact: dict, user: dict, incident: dict):
    """
    Sends an SMS notification via an email-to-SMS gateway using yagmail.
    """
    to_email = contact.get("email")
    logging.info(f"Notifier: send_email_notification - Processing contact: {contact.get('name')}, provided email: {to_email}")

    if not to_email:       
        logging.warning(f"Notifier: No email address found for contact {contact.get('name')}. Attempting SMS fallback.")
        phone_number = contact.get("phone")
        carrier = contact.get("carrier", "").lower()
        gateway = CARRIER_GATEWAYS.get(carrier)
        if not gateway:
            logging.warning(f"Notifier: Unsupported carrier for contact {contact.get('name')}: {carrier}. Cannot send SMS.")
            return
        to_email = f"{phone_number}@{gateway}"
        logging.info(f"Notifier: Falling back to SMS gateway email: {to_email}")
    
    subject = f"Distress Alert from {user.get('name', 'N/A')}"
    
    lat = incident.get("latitude")
    lon = incident.get("longitude")
    location_url = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "Location not available."
    
    address = "Address not available."
    logging.info(f"Checking for Google API Key. Found: '{settings.GOOGLE_GEOCODING_API_KEY}'")
    if lat and lon and settings.GOOGLE_GEOCODING_API_KEY and settings.GOOGLE_GEOCODING_API_KEY != "AIzaSyDH3QzDTAF-R_k7NE96it65Hk_QKumWbb4":
        logging.info("Attempting to call Google Geocoding API...")
        try:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={settings.GOOGLE_GEOCODING_API_KEY}"
            logging.info(f"Calling Google Geocoding API: {url}")
            response = requests.get(url)
            data = response.json()
            logging.info(f"Google Geocoding API response: {data}")
            if data["status"] == "OK":
                address = data["results"][0]["formatted_address"]
            else:
                logging.error(f"Google Geocoding API error: {data.get('error_message', data['status'])}")
        except Exception as e:
            logging.error(f"Google Geocoding API request failed: {e}")

    severity = incident.get("final_severity", "N/A")
    llm_reason = (incident.get("llm_response", {}) or {}).get("reason", "")

    body = (
        f"Distress alert from {user.get('name', 'N/A')}.\n"
        f"Message: {incident.get('transcript', 'No transcript available.')}\n"
        f"Severity: {severity}\n"
        f"Reason: {llm_reason}\n\n"
        f"--- LOCATION DETAILS ---\n"
        f"Exact Location (Google Maps): {location_url}\n"
    )

    logging.info(f"Preparing to send email to: {to_email}")
    logging.info(f"Subject: {subject}")

    try:
        yag = yagmail.SMTP(settings.SMTP_USER, settings.SMTP_PASSWORD)
        yag.send(
            to=to_email,
            subject=subject,
            contents=body
        )
        logging.info(f"Successfully sent SMS to {contact.get('name')} via yagmail.")
    except yagmail.error.YagmailSMTPError as e:
        logging.error(f"Yagmail SMTP error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending email: {e}")

def notify_contacts(incident: dict):
    """
    Fetches user's emergency contacts and sends notifications based on the configured mode.
    """
    db = get_db()
    user_id_raw = incident.get("user_id")
    # Clean the user_id to remove any potential leading/trailing quotes or whitespace
    user_id = user_id_raw.strip().strip("'\"") if isinstance(user_id_raw, str) else user_id_raw
    logging.info(f"Notifier: Cleaned user_id from '{user_id_raw}' to '{user_id}'")
    user = get_user_by_id(db, user_id)

    if not user:
        logging.error(f"Notifier: Could not find user with ID {user_id}")
        return False

    if not user.get("emergency_contacts"):
        logging.warning(f"Notifier: User {user_id} has no emergency contacts configured.")
        return False

    logging.info(f"Notifier: Processing {len(user['emergency_contacts'])} emergency contacts for user {user_id}.")

    for i, contact in enumerate(user["emergency_contacts"]):
        contact_name = contact.get("name", f"Contact {i+1}")
        logging.info(f"Notifier: Attempting to notify contact {i+1}: {contact_name}")

        if settings.NOTIFIER_MODE == "email":
            send_email_notification(contact, user, incident)
        else:  # Default to mock/logging
            contact_phone = contact.get("phone")
            lat = incident.get("latitude")
            lon = incident.get("longitude")
            location_info = f"Lat: {lat}, Lon: {lon}" if lat and lon else "Unknown location."
            
            message = (
                f"** SIMULATING NOTIFICATION to {contact_name} at {contact_phone} **\n"
                f"  - Your contact, {user.get('name', 'N/A')}, has triggered a distress alert.\n"
                f"  - Severity: {incident.get('final_severity', 'N/A')}\n"
                f"  - Message: '{incident.get('transcript', 'No transcript available.')}'\n"
                f"  - Last known location: {location_info}\n"
                f"****************************************************************"
            )
            print(message)
            logging.info(f"Notifier: Simulated notification for user {user_id} to contact {contact_name}")

    return True
