import time
import threading
from pathlib import Path
from datetime import datetime
from clickhouse_driver import Client
from ultralytics import YOLO
from detection_service.config import CAMERAS, CLICKHOUSE_CONFIG

class DetectionScheduler:
    def __init__(self):
        self.ch_client = Client(**CLICKHOUSE_CONFIG)
        self.stop_event = threading.Event()
        self.processors = {}

    def init_camera_processor(self, camera_id: str):
        """Инициализация обработчика для конкретной камеры"""
        from .hls_client import HLSCamera
        config = CAMERAS[camera_id]
        
        self.processors[camera_id] = {
            "camera": HLSCamera(config["url"]),
            "model": YOLO(config["model_path"]),
            "config": config,
            "output_dir": Path(f"storage/snapshots/{camera_id}")
        }
        self.processors[camera_id]["output_dir"].mkdir(parents=True, exist_ok=True)

    def process_frame(self, camera_id: str):
        """Обработка одного кадра с сохранением результатов"""
        proc = self.processors[camera_id]
        try:
            # Захват кадра
            frame_path = proc["camera"].capture_frame(str(proc["output_dir"]))
            
            # Детекция людей
            results = proc["model"](frame_path, classes=[0], conf=0.5)
            count = len(results[0].boxes)
            
            # Сохранение в ClickHouse
            self.ch_client.execute(
                """INSERT INTO people_count VALUES""",
                [{
                    'user_id': proc["config"]["user_id"],
                    'camera_id': camera_id,
                    'hall_name': proc["config"]["hall_name"],
                    'timestamp': datetime.now(),
                    'people_count': count
                }]
            )
            
            print(f"[{proc['config']['hall_name']}] Обнаружено людей: {count}")
            return True
            
        except Exception as e:
            print(f"[{camera_id}] Ошибка обработки: {str(e)}")
            return False

    def start_monitoring(self, interval: int = 30):
        """Запуск мониторинга для всех камер"""
        for camera_id in CAMERAS.keys():
            self.init_camera_processor(camera_id)
            
            threading.Thread(
                target=self._monitor_worker,
                args=(camera_id, interval),
                daemon=True
            ).start()

    def _monitor_worker(self, camera_id: str, interval: int):
        """Поток мониторинга для отдельной камеры"""
        while not self.stop_event.is_set():
            self.process_frame(camera_id)
            time.sleep(interval)

    def stop(self):
        """Корректная остановка всех процессов"""
        self.stop_event.set()
        self.ch_client.disconnect()