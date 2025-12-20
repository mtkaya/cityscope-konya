from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from pydantic import BaseModel
from .. import models, schemas, database

router = APIRouter(
    prefix="/work-orders",
    tags=["work-orders"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PartRequest(BaseModel):
    inventory_item_id: int
    quantity: int

@router.post("/", response_model=schemas.WorkOrder)
def create_work_order(work_order: schemas.WorkOrderCreate, db: Session = Depends(get_db)):
    vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == work_order.vehicle_plate).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    new_wo = models.WorkOrder(
        vehicle_id=vehicle.id,
        technician_id=work_order.technician_id,
        description=work_order.description,
        status=models.WorkOrderStatus.PENDING
    )
    db.add(new_wo)
    
    vehicle.status = models.VehicleStatus.MAINTENANCE
    
    db.commit()
    db.refresh(new_wo)
    return new_wo

@router.get("/", response_model=List[schemas.WorkOrder])
def read_work_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    wos = db.query(models.WorkOrder).offset(skip).limit(limit).all()
    return wos

@router.put("/{wo_id}/status", response_model=schemas.WorkOrder)
def update_work_order_status(wo_id: int, status: schemas.WorkOrderStatus, db: Session = Depends(get_db)):
    wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    wo.status = status
    if status == models.WorkOrderStatus.COMPLETED:
        wo.completed_at = datetime.now()
        wo.vehicle.status = models.VehicleStatus.ACTIVE
    
    db.commit()
    db.refresh(wo)
    return wo

@router.post("/{wo_id}/start", response_model=schemas.WorkOrder)
def start_work_order(wo_id: int, db: Session = Depends(get_db)):
    wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if wo.status == models.WorkOrderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot start completed job")
        
    wo.status = models.WorkOrderStatus.IN_PROGRESS
    wo.last_started_at = datetime.now()
    
    db.commit()
    db.refresh(wo)
    return wo

@router.post("/{wo_id}/stop", response_model=schemas.WorkOrder)
def stop_work_order(wo_id: int, db: Session = Depends(get_db)):
    wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
    
    if wo.last_started_at:
        delta = datetime.now() - wo.last_started_at
        wo.total_labor_seconds += int(delta.total_seconds())
        wo.last_started_at = None
    
    db.commit()
    db.refresh(wo)
    return wo

@router.post("/{wo_id}/parts", response_model=schemas.WorkOrder)
def add_part_to_work_order(wo_id: int, part_req: PartRequest, db: Session = Depends(get_db)):
    wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")
        
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == part_req.inventory_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if item.quantity < part_req.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
        
    # Deduct stock
    item.quantity -= part_req.quantity
    
    # Add to relation
    wo_item = models.WorkOrderItem(
        work_order_id=wo.id,
        inventory_item_id=item.id,
        quantity_used=part_req.quantity
    )
    db.add(wo_item)
    
    db.commit()
    db.refresh(wo)
    return wo
