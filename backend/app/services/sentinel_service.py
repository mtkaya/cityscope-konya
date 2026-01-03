"""
Sentinel Hub API Integration Service
Fetches satellite imagery for traffic analysis
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
import numpy as np
from sentinelhub import (
    SHConfig,
    CRS,
    BBox,
    DataCollection,
    SentinelHubRequest,
    MimeType,
    bbox_to_dimensions,
)
from PIL import Image
import io


class SentinelHubService:
    """Service for fetching satellite images from Sentinel Hub"""

    def __init__(self):
        """Initialize Sentinel Hub configuration"""
        self.config = SHConfig()

        # Load credentials from environment variables
        self.config.sh_client_id = os.getenv("SENTINEL_CLIENT_ID", "")
        self.config.sh_client_secret = os.getenv("SENTINEL_CLIENT_SECRET", "")

        if not self.config.sh_client_id or not self.config.sh_client_secret:
            raise ValueError(
                "Sentinel Hub credentials not found. "
                "Set SENTINEL_CLIENT_ID and SENTINEL_CLIENT_SECRET environment variables."
            )

    def get_konya_bbox(self) -> BBox:
        """
        Returns bounding box for Konya city center
        Can be adjusted for different areas
        """
        # Konya center coordinates (approximate)
        # Format: [min_lon, min_lat, max_lon, max_lat]
        konya_coords = [32.4351, 37.8216, 32.5351, 37.9216]

        return BBox(bbox=konya_coords, crs=CRS.WGS84)

    def get_latest_image(
        self,
        bbox: Optional[BBox] = None,
        resolution: int = 10,  # meters per pixel
        max_cloud_coverage: float = 0.3  # 30% max cloud coverage
    ) -> Tuple[np.ndarray, str, datetime]:
        """
        Fetch the latest satellite image for the given area

        Args:
            bbox: Bounding box, defaults to Konya center
            resolution: Image resolution in meters per pixel
            max_cloud_coverage: Maximum acceptable cloud coverage (0-1)

        Returns:
            Tuple of (image_array, image_id, capture_time)
        """
        if bbox is None:
            bbox = self.get_konya_bbox()

        # Calculate image dimensions based on resolution
        size = bbox_to_dimensions(bbox, resolution=resolution)

        # Define time range (last 7 days to ensure we get recent imagery)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        # Define evalscript for RGB image
        evalscript = """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B04", "B03", "B02", "SCL"],
                    units: "DN"
                }],
                output: {
                    bands: 3,
                    sampleType: "AUTO"
                }
            };
        }

        function evaluatePixel(sample) {
            // Return RGB (True Color)
            return [sample.B04 / 3000, sample.B03 / 3000, sample.B02 / 3000];
        }
        """

        # Create request
        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(start_date, end_date),
                    maxcc=max_cloud_coverage,
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
            bbox=bbox,
            size=size,
            config=self.config,
        )

        # Get image
        image_data = request.get_data()[0]

        # Convert to numpy array
        image_array = np.array(Image.open(io.BytesIO(image_data)))

        # Generate image ID (timestamp-based)
        image_id = f"konya_sentinel_{end_date.strftime('%Y%m%d_%H%M%S')}"

        return image_array, image_id, end_date

    def get_image_for_bbox(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        resolution: int = 10
    ) -> Tuple[np.ndarray, str, datetime]:
        """
        Fetch satellite image for custom bounding box

        Args:
            min_lon, min_lat, max_lon, max_lat: Bounding box coordinates
            resolution: Image resolution in meters per pixel

        Returns:
            Tuple of (image_array, image_id, capture_time)
        """
        bbox = BBox(bbox=[min_lon, min_lat, max_lon, max_lat], crs=CRS.WGS84)
        return self.get_latest_image(bbox=bbox, resolution=resolution)

    def save_image(self, image_array: np.ndarray, filepath: str) -> None:
        """
        Save image array to disk

        Args:
            image_array: Numpy array of image data
            filepath: Path to save the image
        """
        Image.fromarray(image_array).save(filepath)
