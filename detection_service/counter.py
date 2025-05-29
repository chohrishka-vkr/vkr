from datetime import datetime
import numpy as np
from core.config import CAMERAS, COUNTER_API_URL

class PeopleCounter:
    def __init__(self, camera_id: str):
        """Initialization based on exclusion_zones for a specific camera"""
        config = CAMERAS[camera_id]
        from .detector import PeopleDetector
        self.detector = PeopleDetector(
            api_url=COUNTER_API_URL,
            exclusion_zones=config.get("exclusion_zones", [])
        )

    def process_frame(self, frame: np.ndarray) -> dict:
        """Frame processing based on exclusion_zones"""
        count = self.detector.detect(frame)
        return {
            "count": count,
            "timestamp": datetime.now()
        }