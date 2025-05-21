import cv2
import os
from datetime import datetime
from pathlib import Path

class HLSCamera:
    def __init__(self, hls_url: str):
        self.hls_url = hls_url
        self.output_dir = Path(__file__).parent / "storage/snapshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture_frame(self) -> Path:
        """Захват кадра из HLS-потока"""
        cap = cv2.VideoCapture(self.hls_url)
        if not cap.isOpened():
            raise ConnectionError(f"Не удалось подключиться к {self.hls_url}")

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError("Не удалось получить кадр")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.jpg"
        filepath = self.output_dir / filename

        cv2.imwrite(str(filepath), frame)
        return filepath

    def get_latest_snapshot(self) -> Path:
        """Получение последнего скриншота"""
        files = list(self.output_dir.glob("*.jpg"))
        if not files:
            raise FileNotFoundError("Нет доступных скриншотов")
        return max(files, key=lambda f: f.stat().st_mtime)