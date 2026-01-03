from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .models import VehicleStatus, WorkOrderStatus

# --- Vehicle Schemas ---
class VehicleBase(BaseModel):
    plate: str
    brand: str
    model: str
    status: VehicleStatus = VehicleStatus.ACTIVE

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Inventory Schemas ---
class InventoryItemBase(BaseModel):
    name: str
    sku: str
    quantity: int
    critical_level: int = 5

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItem(InventoryItemBase):
    id: int

    class Config:
        from_attributes = True

# --- WorkOrder Schemas ---
class WorkOrderBase(BaseModel):
    description: str
    technician_id: Optional[int] = None
    status: WorkOrderStatus = WorkOrderStatus.PENDING

class WorkOrderCreate(WorkOrderBase):
    vehicle_plate: str # Pass plate instead of ID for convenience

class WorkOrder(WorkOrderBase):
    id: int
    vehicle_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_labor_seconds: int = 0
    last_started_at: Optional[datetime] = None

    class Config:
        from_attributes = True
