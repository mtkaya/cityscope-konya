"""
YOLO Vehicle Detection Service
Detects vehicles in satellite imagery using YOLOv8
"""
import numpy as np
from typing import List, Dict, Tuple
from ultralytics import YOLO
import cv2
from pathlib import Path


class VehicleDetectionService:
    """Service for detecting vehicles in satellite images using YOLO"""

    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        Initialize YOLO model

        Args:
            model_name: YOLO model variant (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
                       'n' = nano (fastest, least accurate)
                       's' = small
                       'm' = medium
                       'l' = large
                       'x' = extra large (slowest, most accurate)
        """
        self.model = YOLO(model_name)

        # Vehicle class IDs in COCO dataset
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.vehicle_classes = [2, 3, 5, 7]

    def detect_vehicles(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ) -> Tuple[List[Dict], int]:
        """
        Detect vehicles in the given image

        Args:
            image: Numpy array of the image (RGB)
            confidence_threshold: Minimum confidence for detection
            iou_threshold: IoU threshold for NMS (Non-Maximum Suppression)

        Returns:
            Tuple of (detections_list, vehicle_count)
            detections_list: List of dicts with bbox, confidence, class_name
        """
        # Run inference
        results = self.model(
            image,
            conf=confidence_threshold,
            iou=iou_threshold,
            classes=self.vehicle_classes,
            verbose=False
        )

        detections = []
        vehicle_count = 0

        # Process results
        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Get confidence and class
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                # Map class ID to name
                class_name = self._get_vehicle_type(class_id)

                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": confidence,
                    "class": class_name,
                    "class_id": class_id
                })

                vehicle_count += 1

        return detections, vehicle_count

    def _get_vehicle_type(self, class_id: int) -> str:
        """Map COCO class ID to vehicle type"""
        vehicle_map = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck"
        }
        return vehicle_map.get(class_id, "vehicle")

    def calculate_density_score(
        self,
        vehicle_count: int,
        image_area_km2: float,
        max_vehicles_per_km2: int = 500
    ) -> int:
        """
        Calculate traffic density score (0-100)

        Args:
            vehicle_count: Number of detected vehicles
            image_area_km2: Area of the image in square kilometers
            max_vehicles_per_km2: Maximum expected vehicles per km2 for normalization

        Returns:
            Density score from 0 to 100
        """
        if image_area_km2 == 0:
            return 0

        vehicles_per_km2 = vehicle_count / image_area_km2

        # Normalize to 0-100 scale
        density_score = min(100, int((vehicles_per_km2 / max_vehicles_per_km2) * 100))

        return density_score

    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Dict]
    ) -> np.ndarray:
        """
        Draw bounding boxes on image

        Args:
            image: Original image
            detections: List of detections from detect_vehicles()

        Returns:
            Image with drawn bounding boxes
        """
        output_image = image.copy()

        for det in detections:
            x1, y1, x2, y2 = [int(coord) for coord in det["bbox"]]
            confidence = det["confidence"]
            class_name = det["class"]

            # Draw rectangle
            cv2.rectangle(output_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(
                output_image,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return output_image

    def analyze_traffic_by_grid(
        self,
        image: np.ndarray,
        grid_size: Tuple[int, int] = (4, 4)
    ) -> List[Dict]:
        """
        Divide image into grid and analyze traffic density in each cell

        Args:
            image: Input image
            grid_size: (rows, cols) for grid division

        Returns:
            List of grid cells with vehicle counts and density scores
        """
        height, width = image.shape[:2]
        rows, cols = grid_size

        cell_height = height // rows
        cell_width = width // cols

        grid_results = []

        for i in range(rows):
            for j in range(cols):
                # Extract cell
                y1 = i * cell_height
                y2 = (i + 1) * cell_height if i < rows - 1 else height
                x1 = j * cell_width
                x2 = (j + 1) * cell_width if j < cols - 1 else width

                cell_image = image[y1:y2, x1:x2]

                # Detect vehicles in cell
                detections, vehicle_count = self.detect_vehicles(cell_image)

                # Estimate cell area (rough approximation)
                # This would need proper geospatial calculation in production
                cell_area_km2 = 0.1  # Placeholder

                density_score = self.calculate_density_score(
                    vehicle_count,
                    cell_area_km2
                )

                grid_results.append({
                    "row": i,
                    "col": j,
                    "bbox": [x1, y1, x2, y2],
                    "vehicle_count": vehicle_count,
                    "density_score": density_score,
                    "detections": detections
                })

        return grid_results
