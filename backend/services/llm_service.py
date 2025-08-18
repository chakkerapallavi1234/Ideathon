# backend/services/llm_service.py
"""
Gemini 2.0 Pro integration wrapper.
This is a simple prompt wrapper that returns a JSON-like dict with 'urgency' (0..1) and 'reason'.

You must set GEMINI_API_KEY in environment variables or config.
"""
from backend.config import settings
import json
import logging
from backend.services.mongodb_service import get_db, get_user_by_id

try:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception:
    genai = None
    logging.warning("google.generativeai not available or not configured; using mock LLM responses.")

def assess_urgency(user_id: str, transcript: str, audio_events: list, sensor_data: dict) -> dict:
    """
    Assess urgency using a context-aware LLM prompt.
    Includes user's profile information for more nuanced assessment.
    """
    db = get_db()
    user = get_user_by_id(db, user_id) or {}

    prompt = f"""
You are an emergency response dispatcher. Your task is to assess the urgency of a situation based on the provided data.
Respond ONLY with a valid JSON object. Do not include any other text, explanations, or markdown formatting.

The JSON object must have the following keys:
- "urgency": a float between 0.0 and 1.0.
- "reason": a brief explanation for the urgency score.
- "recommended_actions": a list of strings.

**User Profile:**
- Name: {user.get('name', 'N/A')}
- Age: {user.get('age', 'N/A')}
- Medical History: {user.get('medical_history', 'None provided')}

**Incident Data:**
- User transcript: "{transcript}"
- Detected audio events: {audio_events}
- Sensor data: {sensor_data}

Analyze all the information and provide your assessment.
"""
    if genai:
        try:
            # Using the new GenerativeModel API
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(prompt)
            raw = resp.text
            # attempt to parse JSON from LLM answer
            try:
                # Attempt to parse the entire response as JSON
                parsed = json.loads(raw)
                return parsed
            except json.JSONDecodeError:
                # If that fails, try to extract a JSON block from the response
                try:
                    json_block = raw[raw.find('{') : raw.rfind('}')+1]
                    parsed = json.loads(json_block)
                    return parsed
                except Exception:
                    # If all else fails, use the heuristic
                    return {"urgency": 0.9 if "help" in transcript.lower() or audio_events else 0.2,
                            "reason": f"LLM response parsing failed: {raw[:200]}", "recommended_actions": ["notify_contacts"]}
        except Exception as e:
            return {"urgency": 0.5, "reason": f"gemini_err:{e}", "recommended_actions": []}
    else:
        # Rule-based fallback
        score = 0.0
        text = transcript.lower() if transcript else ""
        if any(k in text for k in ["help", "emergency", "attack", "follow", "please help"]):
            score += 0.7
        if audio_events:
            score += 0.2
        hr = sensor_data.get("heart_rate") or 0
        if hr and hr > 120:
            score += 0.1
        score = min(1.0, score)
        reason = "rule-based detection"
        return {"urgency": round(score, 2), "reason": reason, "recommended_actions": ["notify_contacts"] if score > 0.6 else ["ask_clarify"]}
