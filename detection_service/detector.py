import numpy as np
from ultralytics import YOLO

class PeopleDetector:
    def __init__(self, model_path: str = "yolov11m.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray) -> tuple[int, np.ndarray]:
        """Детекция людей в кадре"""
        results = self.model(frame, classes=[0], conf=0.6)
        count = len(results[0].boxes)
        annotated_frame = results[0].plot()
        return count, annotated_frame