from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base

class VehicleStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class WorkOrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, unique=True, index=True)
    brand = Column(String)
    model = Column(String)
    status = Column(SqlEnum(VehicleStatus), default=VehicleStatus.ACTIVE)
    
    work_orders = relationship("WorkOrder", back_populates="vehicle")

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    technician_id = Column(Integer, nullable=True) # ID of the user/technician
    description = Column(String)
    status = Column(SqlEnum(WorkOrderStatus), default=WorkOrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Labor Tracking
    total_labor_seconds = Column(Integer, default=0)
    last_started_at = Column(DateTime(timezone=True), nullable=True)

    vehicle = relationship("Vehicle", back_populates="work_orders")
    items = relationship("WorkOrderItem", back_populates="work_order")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=0)
    critical_level = Column(Integer, default=5)

class WorkOrderItem(Base):
    __tablename__ = "work_order_items"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))
    quantity_used = Column(Integer)

    work_order = relationship("WorkOrder", back_populates="items")
    inventory_item = relationship("InventoryItem")

class TrafficDensity(Base):
    __tablename__ = "traffic_density"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String, index=True)
    longitude = Column(String, index=True)
    density_score = Column(Integer)  # 0-100 scale
    vehicle_count = Column(Integer)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    satellite_image_id = Column(String, nullable=True)  # Sentinel Hub image reference

class SatelliteImage(Base):
    __tablename__ = "satellite_images"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String, unique=True, index=True)  # Sentinel Hub ID
    bbox = Column(String)  # Bounding box coordinates (JSON string)
    capture_time = Column(DateTime(timezone=True))
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    vehicle_detections = Column(Integer, default=0)
