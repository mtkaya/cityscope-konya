from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import logging
from .. import models, schemas, database

logger = logging.getLogger(__name__)

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
    try:
        # Validate plate is not empty
        if not vehicle.plate or not vehicle.plate.strip():
            raise HTTPException(status_code=400, detail="Vehicle plate cannot be empty")

        db_vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == vehicle.plate).first()
        if db_vehicle:
            raise HTTPException(status_code=400, detail=f"Vehicle with plate '{vehicle.plate}' is already registered")

        new_vehicle = models.Vehicle(
            plate=vehicle.plate,
            brand=vehicle.brand,
            model=vehicle.model,
            status=vehicle.status
        )
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        logger.info(f"Created new vehicle: {vehicle.brand} {vehicle.model} (Plate: {vehicle.plate})")
        return new_vehicle
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating vehicle: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create vehicle due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating vehicle: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating vehicle")

@router.get("/", response_model=List[schemas.Vehicle])
def read_vehicles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        vehicles = db.query(models.Vehicle).offset(skip).limit(limit).all()
        return vehicles
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching vehicles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vehicles from database")
    except Exception as e:
        logger.error(f"Unexpected error fetching vehicles: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching vehicles")

@router.get("/{plate}", response_model=schemas.Vehicle)
def read_vehicle(plate: str, db: Session = Depends(get_db)):
    try:
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == plate).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle with plate '{plate}' not found")
        return vehicle
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching vehicle {plate}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vehicle from database")
    except Exception as e:
        logger.error(f"Unexpected error fetching vehicle {plate}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching vehicle")
