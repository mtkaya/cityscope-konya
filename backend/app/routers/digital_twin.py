from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import random
import math
from datetime import datetime
from .. import models, database

router = APIRouter(
    prefix="/digital-twin",
    tags=["digital-twin"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock Konya Coordinates (Center approx)
KONYA_LAT = 37.8716
KONYA_LON = 32.4851

@router.get("/vehicles")
def get_live_vehicles(db: Session = Depends(get_db)):
    """
    Returns vehicles with simulated GPS coordinates and status.
    """
    vehicles = db.query(models.Vehicle).filter(models.Vehicle.status == models.VehicleStatus.ACTIVE).all()
    
    response = []
    for v in vehicles:
        # Simulate semi-random positions around Konya center
        # Deterministic randomness based on ID + Minute so they move slowly
        time_seed = int(datetime.utcnow().timestamp() / 10) # Changes every 10 seconds
        
        offset_lat = (math.sin(v.id + time_seed) * 0.05)
        offset_lon = (math.cos(v.id + time_seed) * 0.05)
        
        response.append({
            "id": v.id,
            "plate": v.plate,
            "lat": KONYA_LAT + offset_lat,
            "lng": KONYA_LON + offset_lon,
            "speed": abs(int(offset_lat * 1000)) % 90, # Fake speed
            "status": "Moving" if (v.id % 2 == 0) else "Stopped"
        })
    return response

@router.get("/telemetry/{vehicle_id}")
def get_vehicle_telemetry(vehicle_id: int):
    """
    Simulates real-time IoT sensor data stream.
    """
    # Random but realistic-looking values
    return {
        "timestamp": datetime.now(),
        "engine_temp": random.randint(80, 110),
        "rpm": random.randint(1000, 3500),
        "fuel_level": random.randint(10, 100),
        "battery_voltage": round(random.uniform(12.0, 14.5), 1)
    }

@router.get("/prediction/{vehicle_id}")
def get_ai_prediction(vehicle_id: int):
    """
    Stub for AI Predictive Maintenance model.
    """
    risk_score = random.randint(0, 100)
    
    if risk_score > 80:
        return {
            "risk_level": "High",
            "score": risk_score,
            "message": "⚠️ CRITICAL: Transmission failure predicted within 500km.",
            "action": "Schedule immediate maintenance."
        }
    elif risk_score > 50:
         return {
            "risk_level": "Medium",
            "score": risk_score,
            "message": "⚠️ Warning: Brake pad wear detected.",
            "action": "Check in next service."
        }
    else:
         return {
            "risk_level": "Low",
            "score": risk_score,
            "message": "✅ System healthy.",
            "action": "No action needed."
        }
