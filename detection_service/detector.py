import requests
import cv2
import numpy as np
from typing import List, Tuple

class PeopleDetector:
    def __init__(self, api_url: str, exclusion_zones: List[List[Tuple[int, int]]] = None):
        self.api_url = api_url
        self.exclusion_zones = exclusion_zones or []
    
    def _apply_mask(self, frame: np.ndarray) -> np.ndarray:
        """Creates a mask of excluded zones and applies it to the image"""
        if not self.exclusion_zones:
            return frame
            
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for zone in self.exclusion_zones:
            pts = np.array(zone, np.int32).reshape((-1,1,2))
            cv2.fillPoly(mask, [pts], 255)
        
        masked_frame = cv2.bitwise_and(frame, frame, mask=~mask)
        return masked_frame

    def detect(self, frame: np.ndarray) -> int:
        """Sends the image to an external service for detecting people"""
        processed_frame = self._apply_mask(frame)
        
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
