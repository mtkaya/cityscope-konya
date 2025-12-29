from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from pydantic import BaseModel
import logging
from .. import models, schemas, database

logger = logging.getLogger(__name__)

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
    try:
        vehicle = db.query(models.Vehicle).filter(models.Vehicle.plate == work_order.vehicle_plate).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle with plate '{work_order.vehicle_plate}' not found")

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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating work order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create work order due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating work order: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating work order")

@router.get("/", response_model=List[schemas.WorkOrder])
def read_work_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        wos = db.query(models.WorkOrder).offset(skip).limit(limit).all()
        return wos
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching work orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve work orders from database")
    except Exception as e:
        logger.error(f"Unexpected error fetching work orders: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching work orders")

@router.put("/{wo_id}/status", response_model=schemas.WorkOrder)
def update_work_order_status(wo_id: int, status: schemas.WorkOrderStatus, db: Session = Depends(get_db)):
    try:
        wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work Order with ID {wo_id} not found")

        wo.status = status
        if status == models.WorkOrderStatus.COMPLETED:
            wo.completed_at = datetime.now()
            if wo.vehicle:
                wo.vehicle.status = models.VehicleStatus.ACTIVE
            else:
                logger.warning(f"Work order {wo_id} has no associated vehicle")

        db.commit()
        db.refresh(wo)
        return wo
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating work order {wo_id} status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update work order status due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating work order {wo_id} status: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating work order status")

@router.post("/{wo_id}/start", response_model=schemas.WorkOrder)
def start_work_order(wo_id: int, db: Session = Depends(get_db)):
    try:
        wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work Order with ID {wo_id} not found")

        if wo.status == models.WorkOrderStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Cannot start a completed work order")

        wo.status = models.WorkOrderStatus.IN_PROGRESS
        wo.last_started_at = datetime.now()

        db.commit()
        db.refresh(wo)
        return wo
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error starting work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start work order due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error starting work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while starting work order")

@router.post("/{wo_id}/stop", response_model=schemas.WorkOrder)
def stop_work_order(wo_id: int, db: Session = Depends(get_db)):
    try:
        wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work Order with ID {wo_id} not found")

        if wo.last_started_at:
            try:
                delta = datetime.now() - wo.last_started_at
                wo.total_labor_seconds += int(delta.total_seconds())
                wo.last_started_at = None
            except (TypeError, ValueError) as e:
                logger.error(f"Error calculating time delta for work order {wo_id}: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to calculate work duration")
        else:
            logger.warning(f"Attempted to stop work order {wo_id} that was not started")

        db.commit()
        db.refresh(wo)
        return wo
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error stopping work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop work order due to database error")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error stopping work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while stopping work order")

@router.post("/{wo_id}/parts", response_model=schemas.WorkOrder)
def add_part_to_work_order(wo_id: int, part_req: PartRequest, db: Session = Depends(get_db)):
    try:
        # Validate quantity is positive
        if part_req.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")

        wo = db.query(models.WorkOrder).filter(models.WorkOrder.id == wo_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work Order with ID {wo_id} not found")

        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == part_req.inventory_item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Inventory item with ID {part_req.inventory_item_id} not found")

        if item.quantity < part_req.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{item.name}'. Available: {item.quantity}, Requested: {part_req.quantity}"
            )

        # Deduct stock and add to work order in a single transaction
        item.quantity -= part_req.quantity

        wo_item = models.WorkOrderItem(
            work_order_id=wo.id,
            inventory_item_id=item.id,
            quantity_used=part_req.quantity
        )
        db.add(wo_item)

        db.commit()
        db.refresh(wo)
        logger.info(f"Added {part_req.quantity} units of '{item.name}' to work order {wo_id}")
        return wo
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error adding part to work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add part to work order due to database error. Stock has been rolled back.")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error adding part to work order {wo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while adding part to work order")
