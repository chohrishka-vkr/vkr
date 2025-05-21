from rtsp_capture.hls_client import HLSCamera
from rtsp_capture.scheduler import start_capture_scheduler
from detection_service.counter import PeopleCounter
from ultralytics import YOLO
from pathlib import Path
import threading
import time

class VideoProcessor:
    def __init__(self):
        self.stop_event = threading.Event()
        self.camera = HLSCamera(
            "https://techvision.dvfu.ru/cameras/go2rtc-35/api/stream.m3u8?src=camera-35&mp4=flac"
        )
        self.counter = PeopleCounter()
        self.model = YOLO("yolo11m.pt")
        self.screenshots_dir = Path("c:/Users/admin/Desktop/fitnes_vkr/rtsp_capture/storage/snapshots")

    def process_snapshot(self, image_path: Path):
        """Обработка каждого нового скриншота"""
        # Детекция людей через detection_service
        result = self.counter.process_image(image_path)
        print(f"Найдено людей: {result['count']}. Результат сохранён в {result['annotated_path']}")
        
        # Дополнительная обработка через YOLO напрямую
        self.process_with_yolo(image_path)

    def process_with_yolo(self, image_path: Path):
        """Прямая обработка YOLO (дополнительная)"""
        results = self.model.predict(image_path, classes=[0], conf=0.5)
        count = len(results[0].boxes)
        print(f"YOLO: На скриншоте {image_path.name} найдено людей: {count}")
        
        annotated_path = image_path.parent.parent / "detections" / f"yolo_{image_path.name}"
        annotated_path.parent.mkdir(exist_ok=True)
        results[0].save(filename=str(annotated_path))

    def start_capture(self):
        """Запуск захвата в отдельном потоке"""
        self.capture_thread = threading.Thread(
            target=self._capture_worker,
            daemon=True
        )
        self.capture_thread.start()

    def _capture_worker(self):
        """Фоновый поток для захвата кадров"""
        while not self.stop_event.is_set():
            try:
                filepath = self.camera.capture_frame()
                print(f"Скриншот сохранен: {filepath}")
                self.process_snapshot(filepath)
            except Exception as e:
                print(f"Ошибка захвата: {e}")
            time.sleep(30)

    def stop(self):
        """Остановка захвата"""
        self.stop_event.set()
        self.capture_thread.join(timeout=5)
        print("Захват остановлен")

def main():
    processor = VideoProcessor()
    print("Запуск системы мониторинга...")
    processor.start_capture()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки")
        processor.stop()

if __name__ == "__main__":
    main()