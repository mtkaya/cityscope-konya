from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from pydantic import BaseModel
import logging
from .. import models, schemas, database

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class StockMovement(BaseModel):
    sku: str
    quantity_change: int # Can be negative for removal

@router.post("/", response_model=schemas.InventoryItem)
def create_item(item: schemas.InventoryItemCreate, db: Session = Depends(get_db)):
    try:
        # Validate input
        if item.quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        if item.critical_level < 0:
            raise HTTPException(status_code=400, detail="Critical level cannot be negative")

        db_item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == item.sku).first()
        if db_item:
            raise HTTPException(status_code=400, detail=f"Item with SKU '{item.sku}' already exists")

        new_item = models.InventoryItem(
            name=item.name,
            sku=item.sku,
            quantity=item.quantity,
            critical_level=item.critical_level
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        logger.info(f"Created new inventory item: {item.name} (SKU: {item.sku})")
        return new_item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating inventory item: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create inventory item due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating inventory item: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating inventory item")

@router.get("/", response_model=List[schemas.InventoryItem])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        items = db.query(models.InventoryItem).offset(skip).limit(limit).all()
        return items
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve inventory from database")
    except Exception as e:
        logger.error(f"Unexpected error fetching inventory: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching inventory")

@router.post("/movement", response_model=schemas.InventoryItem)
def stock_movement(movement: StockMovement, db: Session = Depends(get_db)):
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == movement.sku).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Item with SKU '{movement.sku}' not found")

        new_qty = item.quantity + movement.quantity_change
        if new_qty < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for this operation. Current: {item.quantity}, Requested change: {movement.quantity_change}"
            )

        item.quantity = new_qty
        db.commit()
        db.refresh(item)

        operation_type = "added" if movement.quantity_change > 0 else "removed"
        logger.info(f"Stock movement: {abs(movement.quantity_change)} units {operation_type} for '{item.name}' (SKU: {movement.sku})")
        return item
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error processing stock movement for SKU {movement.sku}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process stock movement due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error processing stock movement: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing stock movement")
