"""
Traffic Analysis Scheduler
Runs hourly satellite image analysis automatically
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

from ..database import SessionLocal
from .sentinel_service import SentinelHubService
from .yolo_service import VehicleDetectionService
from .. import models
import json


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrafficAnalysisScheduler:
    """Scheduler for automated hourly traffic analysis"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.sentinel_service = None
        self.yolo_service = None

    def start(self):
        """Start the scheduler with hourly trigger"""
        # Schedule job to run every hour
        self.scheduler.add_job(
            func=self.run_traffic_analysis,
            trigger=IntervalTrigger(hours=1),
            id="hourly_traffic_analysis",
            name="Analyze traffic from satellite imagery",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("🚀 Traffic analysis scheduler started - will run every hour")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("🛑 Traffic analysis scheduler stopped")

    def run_traffic_analysis(self):
        """
        Main analysis function that runs hourly
        Fetches satellite imagery and performs vehicle detection
        """
        logger.info(f"🛰️ Starting scheduled traffic analysis at {datetime.now()}")

        db = SessionLocal()

        try:
            # Initialize services if not already done
            if self.sentinel_service is None:
                logger.info("Initializing Sentinel Hub service...")
                self.sentinel_service = SentinelHubService()

            if self.yolo_service is None:
                logger.info("Initializing YOLO service...")
                self.yolo_service = VehicleDetectionService(model_name="yolov8n.pt")

            # Fetch latest satellite image
            logger.info("Fetching satellite image from Sentinel Hub...")
            image_array, image_id, capture_time = self.sentinel_service.get_latest_image()

            # Create satellite image record
            sat_image = models.SatelliteImage(
                image_id=image_id,
                bbox=json.dumps(self.sentinel_service.get_konya_bbox().bbox),
                capture_time=capture_time,
                processing_status="processing"
            )
            db.add(sat_image)
            db.commit()

            logger.info(f"Processing satellite image: {image_id}")

            # Detect vehicles using YOLO
            logger.info("Running YOLO vehicle detection...")
            detections, vehicle_count = self.yolo_service.detect_vehicles(
                image_array,
                confidence_threshold=0.25
            )

            logger.info(f"Detected {vehicle_count} vehicles")

            # Calculate density score (assuming 1 km² area for Konya center)
            density_score = self.yolo_service.calculate_density_score(
                vehicle_count,
                image_area_km2=1.0,
                max_vehicles_per_km2=500
            )

            # Update satellite image record
            sat_image.vehicle_detections = vehicle_count
            sat_image.processing_status = "completed"
            db.commit()

            # Get bbox center for traffic density location
            bbox = self.sentinel_service.get_konya_bbox().bbox
            center_lon = (bbox[0] + bbox[2]) / 2
            center_lat = (bbox[1] + bbox[3]) / 2

            # Create traffic density record
            traffic_density = models.TrafficDensity(
                latitude=str(center_lat),
                longitude=str(center_lon),
                density_score=density_score,
                vehicle_count=vehicle_count,
                satellite_image_id=image_id
            )
            db.add(traffic_density)
            db.commit()

            logger.info(
                f"✅ Traffic analysis completed successfully!\n"
                f"   - Vehicles detected: {vehicle_count}\n"
                f"   - Density score: {density_score}/100\n"
                f"   - Location: ({center_lat:.4f}, {center_lon:.4f})\n"
                f"   - Image ID: {image_id}"
            )

        except Exception as e:
            logger.error(f"❌ Traffic analysis failed: {str(e)}")

            # Mark satellite image as failed if it exists
            try:
                if 'sat_image' in locals() and sat_image:
                    sat_image.processing_status = "failed"
                    db.commit()
            except:
                pass

            # Don't crash the scheduler - just log the error
            logger.exception("Full error traceback:")

        finally:
            db.close()

    def run_now(self):
        """Run analysis immediately (for testing)"""
        logger.info("▶️ Running traffic analysis immediately (manual trigger)")
        self.run_traffic_analysis()


# Global scheduler instance
scheduler_instance = None


def get_scheduler() -> TrafficAnalysisScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = TrafficAnalysisScheduler()
    return scheduler_instance


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """Stop the global scheduler"""
    global scheduler_instance
    if scheduler_instance:
        scheduler_instance.stop()
        scheduler_instance = None
