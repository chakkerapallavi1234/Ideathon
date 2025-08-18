# backend/main.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import alerts, stt, distress, location
import uvicorn
from backend.routes import profile

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Guardian Angel BOT - Backend (PoC)")

# CORS for local Streamlit access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(stt.router, prefix="/stt", tags=["stt"])
app.include_router(distress.router, prefix="/distress", tags=["distress"])
app.include_router(location.router, prefix="/location", tags=["location"])
app.include_router(profile.router)
@app.get("/")
def read_root():
    return {"ok": True, "service": "guardian-angel-bot-backend"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
