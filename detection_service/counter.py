from datetime import datetime
import numpy as np
from detection_service.config import CAMERAS, COUNTER_API_URl

class PeopleCounter:
    def __init__(self, camera_id: str):
        """Инициализация с учетом exclusion_zones для конкретной камеры"""
        config = CAMERAS[camera_id]
        from .detector import PeopleDetector
        self.detector = PeopleDetector(
            api_url=COUNTER_API_URl,
            exclusion_zones=config.get("exclusion_zones", [])
        )

    def process_frame(self, frame: np.ndarray) -> dict:
        """Обработка кадра с учетом exclusion_zones"""
        count = self.detector.detect(frame)
        return {
            "count": count,
            # "annotated_frame": annotated_frame,
            "timestamp": datetime.now()
        }