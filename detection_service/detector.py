import numpy as np
import cv2
from ultralytics import YOLO
from typing import Tuple, List

class PeopleDetector:
    def __init__(self, model_path: str = "yolo11m.pt", exclusion_zones: List[List[Tuple[int, int]]] = None):
        self.model = YOLO(model_path)
        self.exclusion_zones = exclusion_zones or []
    
    def _apply_mask(self, frame: np.ndarray) -> np.ndarray:
        """Создает маску исключенных зон"""
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for zone in self.exclusion_zones:
            pts = np.array(zone, np.int32).reshape((-1,1,2))
            cv2.fillPoly(mask, [pts], 255)
        return mask

    def detect(self, frame: np.ndarray):
        """Детекция людей с исключением заданных зон"""
        mask = self._apply_mask(frame)
        results = self.model(frame, classes=[0], conf=0.6)
        print(len(results[0].boxes))

        return len(results)