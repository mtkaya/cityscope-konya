from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from .. import models, schemas, database

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
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == item.sku).first()
    if db_item:
        raise HTTPException(status_code=400, detail="Item with this SKU already exists")
    
    new_item = models.InventoryItem(
        name=item.name,
        sku=item.sku,
        quantity=item.quantity,
        critical_level=item.critical_level
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.get("/", response_model=List[schemas.InventoryItem])
def read_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.InventoryItem).offset(skip).limit(limit).all()
    return items

@router.post("/movement", response_model=schemas.InventoryItem)
def stock_movement(movement: StockMovement, db: Session = Depends(get_db)):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.sku == movement.sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    new_qty = item.quantity + movement.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock for this operation")
        
    item.quantity = new_qty
    db.commit()
    db.refresh(item)
    return item
