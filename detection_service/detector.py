import requests
import cv2
import numpy as np
from typing import List, Tuple

class PeopleDetector:
    def __init__(self, api_url: str, exclusion_zones: List[List[Tuple[int, int]]] = None):
        self.api_url = api_url
        self.exclusion_zones = exclusion_zones or []
    
    def _apply_mask(self, frame: np.ndarray) -> np.ndarray:
        """Создает маску исключенных зон и применяет ее к изображению"""
        if not self.exclusion_zones:
            return frame
            
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for zone in self.exclusion_zones:
            pts = np.array(zone, np.int32).reshape((-1,1,2))
            cv2.fillPoly(mask, [pts], 255)
        
        # Применяем маску к изображению
        masked_frame = cv2.bitwise_and(frame, frame, mask=~mask)
        return masked_frame

    def detect(self, frame: np.ndarray) -> int:
        """Отправляет изображение на внешний сервис для детекции людей"""
        # Применяем маску исключенных зон
        processed_frame = self._apply_mask(frame)
        
        # Конвертируем кадр в JPEG для отправки
        _, img_encoded = cv2.imencode('.jpg', processed_frame)
        files = {'image': ('image.jpg', img_encoded.tobytes(), 'image/jpeg')}
        
        try:
            response = requests.post(self.api_url, files=files)
            response.raise_for_status()
            result = response.json()
            return result.get('count', 0)
        except requests.exceptions.RequestException as e:
            print(f"Error sending request to detection service: {e}")
            return 0
