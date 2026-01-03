"""
Traffic Analysis Router
API endpoints for satellite-based traffic density analysis
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import numpy as np

from .. import models, schemas, database
from ..services.sentinel_service import SentinelHubService
from ..services.yolo_service import VehicleDetectionService


router = APIRouter(
    prefix="/traffic",
    tags=["traffic-analysis"],
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize services (will be loaded on first use)
sentinel_service = None
yolo_service = None


def get_sentinel_service():
    """Lazy load Sentinel Hub service"""
    global sentinel_service
    if sentinel_service is None:
        try:
            sentinel_service = SentinelHubService()
        except ValueError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Sentinel Hub service initialization failed: {str(e)}"
            )
    return sentinel_service


def get_yolo_service():
    """Lazy load YOLO service"""
    global yolo_service
    if yolo_service is None:
        yolo_service = VehicleDetectionService(model_name="yolov8n.pt")
    return yolo_service


@router.get("/density/latest", response_model=List[schemas.TrafficDensity])
def get_latest_traffic_density(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get the most recent traffic density data

    Args:
        limit: Maximum number of records to return
    """
    densities = (
        db.query(models.TrafficDensity)
        .order_by(models.TrafficDensity.analyzed_at.desc())
        .limit(limit)
        .all()
    )

    return densities


@router.get("/density/area")
def get_traffic_density_by_area(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get traffic density data for a specific area and time range

    Args:
        min_lon, min_lat, max_lon, max_lat: Bounding box coordinates
        hours: Hours of historical data to retrieve
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    densities = (
        db.query(models.TrafficDensity)
        .filter(
            models.TrafficDensity.analyzed_at >= cutoff_time,
            models.TrafficDensity.longitude >= str(min_lon),
            models.TrafficDensity.longitude <= str(max_lon),
            models.TrafficDensity.latitude >= str(min_lat),
            models.TrafficDensity.latitude <= str(max_lat),
        )
        .all()
    )

    return densities


@router.get("/satellite/images", response_model=List[schemas.SatelliteImage])
def get_satellite_images(
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of processed satellite images

    Args:
        limit: Maximum number of records
        status: Filter by processing status (pending, processing, completed, failed)
    """
    query = db.query(models.SatelliteImage)

    if status:
        query = query.filter(models.SatelliteImage.processing_status == status)

    images = query.order_by(models.SatelliteImage.processed_at.desc()).limit(limit).all()

    return images


@router.post("/analyze/trigger")
async def trigger_traffic_analysis(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger traffic analysis from satellite imagery
    This will run in the background
    """
    # Add background task
    background_tasks.add_task(
        process_satellite_image,
        db_session=db
    )

    return {
        "status": "started",
        "message": "Traffic analysis has been triggered and will run in the background"
    }


@router.post("/analyze/custom")
async def analyze_custom_area(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze traffic in a custom area

    Args:
        min_lon, min_lat, max_lon, max_lat: Bounding box coordinates
    """
    background_tasks.add_task(
        process_custom_area,
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
        db_session=db
    )

    return {
        "status": "started",
        "message": f"Analyzing area: [{min_lon}, {min_lat}, {max_lon}, {max_lat}]",
        "bbox": [min_lon, min_lat, max_lon, max_lat]
    }


@router.get("/stats/summary")
def get_traffic_summary(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for traffic analysis

    Args:
        hours: Time range for statistics
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    # Get recent densities
    densities = (
        db.query(models.TrafficDensity)
        .filter(models.TrafficDensity.analyzed_at >= cutoff_time)
        .all()
    )

    if not densities:
        return {
            "message": "No traffic data available",
            "total_records": 0
        }

    # Calculate statistics
    density_scores = [d.density_score for d in densities]
    vehicle_counts = [d.vehicle_count for d in densities]

    return {
        "time_range_hours": hours,
        "total_records": len(densities),
        "avg_density_score": sum(density_scores) / len(density_scores),
        "max_density_score": max(density_scores),
        "min_density_score": min(density_scores),
        "total_vehicles_detected": sum(vehicle_counts),
        "avg_vehicles_per_area": sum(vehicle_counts) / len(vehicle_counts),
    }


# Background task functions
def process_satellite_image(db_session: Session):
    """
    Background task to fetch and analyze satellite imagery
    """
    try:
        # Get services
        sentinel = get_sentinel_service()
        yolo = get_yolo_service()

        # Fetch satellite image
        image_array, image_id, capture_time = sentinel.get_latest_image()

        # Create satellite image record
        sat_image = models.SatelliteImage(
            image_id=image_id,
            bbox=json.dumps(sentinel.get_konya_bbox().bbox),
            capture_time=capture_time,
            processing_status="processing"
        )
        db_session.add(sat_image)
        db_session.commit()

        # Detect vehicles
        detections, vehicle_count = yolo.detect_vehicles(image_array)

        # Calculate density score
        # Konya area approximately 1 km²
        density_score = yolo.calculate_density_score(vehicle_count, 1.0)

        # Update satellite image record
        sat_image.vehicle_detections = vehicle_count
        sat_image.processing_status = "completed"

        # Create traffic density record
        bbox = sentinel.get_konya_bbox().bbox
        center_lon = (bbox[0] + bbox[2]) / 2
        center_lat = (bbox[1] + bbox[3]) / 2

        traffic_density = models.TrafficDensity(
            latitude=str(center_lat),
            longitude=str(center_lon),
            density_score=density_score,
            vehicle_count=vehicle_count,
            satellite_image_id=image_id
        )
        db_session.add(traffic_density)
        db_session.commit()

        print(f"✅ Traffic analysis complete: {vehicle_count} vehicles, density score: {density_score}")

    except Exception as e:
        # Mark as failed
        if 'sat_image' in locals():
            sat_image.processing_status = "failed"
            db_session.commit()
        print(f"❌ Traffic analysis failed: {str(e)}")
        raise


def process_custom_area(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    db_session: Session
):
    """
    Background task to analyze custom area
    """
    try:
        sentinel = get_sentinel_service()
        yolo = get_yolo_service()

        # Fetch image for custom bbox
        image_array, image_id, capture_time = sentinel.get_image_for_bbox(
            min_lon, min_lat, max_lon, max_lat
        )

        # Create satellite image record
        sat_image = models.SatelliteImage(
            image_id=image_id,
            bbox=json.dumps([min_lon, min_lat, max_lon, max_lat]),
            capture_time=capture_time,
            processing_status="processing"
        )
        db_session.add(sat_image)
        db_session.commit()

        # Analyze by grid
        grid_results = yolo.analyze_traffic_by_grid(image_array, grid_size=(4, 4))

        # Store results for each grid cell
        total_vehicles = 0
        for cell in grid_results:
            # Calculate cell center coordinates
            # This is a simplified calculation - production should use proper geospatial transform
            cell_lon = min_lon + (max_lon - min_lon) * (cell["col"] + 0.5) / 4
            cell_lat = min_lat + (max_lat - min_lat) * (cell["row"] + 0.5) / 4

            traffic_density = models.TrafficDensity(
                latitude=str(cell_lat),
                longitude=str(cell_lon),
                density_score=cell["density_score"],
                vehicle_count=cell["vehicle_count"],
                satellite_image_id=image_id
            )
            db_session.add(traffic_density)
            total_vehicles += cell["vehicle_count"]

        # Update satellite image
        sat_image.vehicle_detections = total_vehicles
        sat_image.processing_status = "completed"
        db_session.commit()

        print(f"✅ Custom area analysis complete: {total_vehicles} vehicles in {len(grid_results)} cells")

    except Exception as e:
        if 'sat_image' in locals():
            sat_image.processing_status = "failed"
            db_session.commit()
        print(f"❌ Custom area analysis failed: {str(e)}")
        raise
