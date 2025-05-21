import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from typing import Optional, Tuple

class PeopleDetector:
    def __init__(self, model_path: str = "yolo11m.pt"):
        self.model = YOLO(model_path)  # Загрузка модели YOLO
        self.class_id = 0              # ID класса "person" в COCO

    def detect(self, image_path: Path) -> Tuple[int, Optional[np.ndarray]]:
        """Детектирует людей на изображении и возвращает их количество + аннотированный кадр."""
        if not image_path.exists():
            raise FileNotFoundError(f"Файл {image_path} не найден")

        img = cv2.imread(str(image_path))
        results = self.model.predict(img, classes=[self.class_id], conf=0.6)

        count = len(results[0].boxes)  # Количество людей
        annotated_img = results[0].plot()  # Аннотированное изображение

        return count, annotated_img