import cv2
import numpy as np
from datetime import datetime
from typing import Tuple

class HLSCamera:
    def __init__(self, hls_url: str):
        self.hls_url = hls_url
        self.cap = cv2.VideoCapture(hls_url)
        if not self.cap.isOpened():
            raise ConnectionError(f"Couldn't connect to {hls_url}")

    def capture_frame(self) -> Tuple[np.ndarray, datetime]:
        """Capturing a frame into RAM"""
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Couldn't get a frame")
        return frame, datetime.now()

    def release(self):
        """Freeing up resources"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()