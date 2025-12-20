from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(
    prefix="/vehicles",
    tags=["vehicles"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Vehicle)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == vehicle.plate).first()
    if db_vehicle:
        raise HTTPException(status_code=400, detail="Vehicle with this plate already registered")
    
    new_vehicle = models.Vehicle(
        plate=vehicle.plate,
        brand=vehicle.brand,
        model=vehicle.model,
        status=vehicle.status
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return new_vehicle

@router.get("/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vehicles = db.query(models.Vehicle).offset(skip).limit(limit).all()
    return vehicles

@router.get("/{plate}", response_model=schemas.Vehicle)
def read_vehicle(plate: str, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == plate).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
