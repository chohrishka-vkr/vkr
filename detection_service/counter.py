from datetime import datetime
from .detector import PeopleDetector
import numpy as np

class PeopleCounter:
    def __init__(self):
        self.detector = PeopleDetector()

    def process_frame(self, frame: np.ndarray) -> dict:
        """Обработка кадра в памяти"""
        count, annotated_frame = self.detector.detect(frame)
        return {
            "count": count,
            "annotated_frame": annotated_frame,
            "timestamp": datetime.now()
        }