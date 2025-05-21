from datetime import datetime
from pathlib import Path
from .detector import PeopleDetector
import cv2

class PeopleCounter:
    def __init__(self, output_dir: str = "storage/detections"):
        self.detector = PeopleDetector()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, image_path: Path) -> dict:
        """Обрабатывает скриншот: детектирует людей и сохраняет результат."""
        count, annotated_img = self.detector.detect(image_path)

        # Сохранение аннотированного изображения
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"detected_{timestamp}.jpg"
        cv2.imwrite(str(output_path), annotated_img)

        return {
            "count": count,
            "original_path": str(image_path),
            "annotated_path": str(output_path),
            "timestamp": timestamp
        }