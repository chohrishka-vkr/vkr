import time
import threading
from datetime import datetime
from clickhouse_driver import Client
import numpy as np
from detection_service.config import CAMERAS, CLICKHOUSE_CONFIG

class DetectionScheduler:
    def __init__(self):
        self.ch_client = Client(**CLICKHOUSE_CONFIG)
        self.stop_event = threading.Event()
        self.processors = {}

    def init_camera_processor(self, camera_id: str):
        """Инициализация обработчика камеры"""
        from .hls_client import HLSCamera
        from detection_service.counter import PeopleCounter
        
        config = CAMERAS[camera_id]
        
        self.processors[camera_id] = {
            "camera": HLSCamera(config["url"]),
            "counter": PeopleCounter(camera_id),
            "config": config
        }

    def process_frame(self, camera_id: str):
        """Обработка кадра в памяти"""
        proc = self.processors[camera_id]
        try:
            # Захват кадра в память
            frame, timestamp = proc["camera"].capture_frame()
            
            # Детекция людей
            result = proc["counter"].process_frame(frame)
            
            # Сохранение в ClickHouse
            self.ch_client.execute(
                """INSERT INTO people_count VALUES""",
                [{
                    'user_id': proc["config"]["user_id"],
                    'camera_id': camera_id,
                    'hall_name': proc["config"]["hall_name"],
                    'timestamp': timestamp,
                    'people_count': result["count"]
                }]
            )
            
            print(f"[{proc['config']['hall_name']}, {camera_id}] Обнаружено людей: {result['count']}")
            return True
            
        except Exception as e:
            print(f"[{camera_id}] Ошибка обработки: {str(e)}")
            return False

    def start_monitoring(self, interval: int = 30):
        """Запуск мониторинга"""
        for camera_id in CAMERAS.keys():
            self.init_camera_processor(camera_id)
            
            threading.Thread(
                target=self._monitor_worker,
                args=(camera_id, interval),
                daemon=True
            ).start()

    def _monitor_worker(self, camera_id: str, interval: int):
        """Поток обработки камеры"""
        while not self.stop_event.is_set():
            self.process_frame(camera_id)
            time.sleep(interval)

    def stop(self):
        """Остановка системы"""
        self.stop_event.set()
        for proc in self.processors.values():
            proc["camera"].release()
        self.ch_client.disconnect()