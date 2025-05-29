import time
import threading
from clickhouse_driver import Client
from core.config import CAMERAS, CLICKHOUSE_CONFIG
from .hls_client import HLSCamera
from detection_service.counter import PeopleCounter
import cv2
import numpy as np

class DetectionScheduler:
    def __init__(self):
        self.ch_client = Client(**CLICKHOUSE_CONFIG)
        self.stop_event = threading.Event()
        self.processors = {}

    def init_camera_processor(self, camera_id: str):
        """Initializing the camera handler"""
        
        config = CAMERAS[camera_id]
        
        self.processors[camera_id] = {
            "camera": HLSCamera(config["url"]),
            "counter": PeopleCounter(camera_id),
            "config": config
        }

    def process_frame(self, camera_id: str):
        """Обработка кадра с сохранением данных по зонам"""
        proc = self.processors[camera_id]
        try:
            # Захват кадра
            frame, timestamp = proc["camera"].capture_frame()
            
            # Получаем результат детекции
            result = proc["counter"].process_frame(frame)
            
            # Получаем зоны для текущей камеры
            zones = proc["config"].get("zones", {})
            
            if zones:
                # Если есть зоны - обрабатываем каждую отдельно
                for zone_name, zone_coords in zones.items():
                    # Создаем маску для текущей зоны
                    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                    pts = np.array(zone_coords, np.int32).reshape((-1,1,2))
                    cv2.fillPoly(mask, [pts], 255)
                    
                    # Применяем маску к кадру
                    zone_frame = cv2.bitwise_and(frame, frame, mask=mask)
                    
                    # Детекция людей в зоне
                    zone_count = proc["counter"].detector.detect(zone_frame)
                    
                    # Сохраняем данные по зоне
                    self.ch_client.execute(
                        """INSERT INTO people_count VALUES""",
                        [{
                            'camera_id': camera_id,
                            'hall_name': proc["config"]["hall_name"],
                            'zone': zone_name,
                            'timestamp': timestamp,
                            'people_count': zone_count
                        }]
                    )
                    
                    print(f"[{zone_name}] People count: {zone_count}")
            else:
                # Если зон нет - сохраняем общий счетчик
                self.ch_client.execute(
                    """INSERT INTO people_count VALUES""",
                    [{
                        'camera_id': camera_id,
                        'hall_name': proc["config"]["hall_name"],
                        'zone': 'general',
                        'timestamp': timestamp,
                        'people_count': result["count"]
                    }]
                )
            
            print(f"[{proc['config']['hall_name']}, {camera_id}] Total people: {result['count']}")
            return True
            
        except Exception as e:
            print(f"[{camera_id}] Processing error: {str(e)}")
            return False

    def start_monitoring(self, interval: int = 30):
        """Launching monitoring"""
        for camera_id in CAMERAS.keys():
            self.init_camera_processor(camera_id)
            
            threading.Thread(
                target=self._monitor_worker,
                args=(camera_id, interval),
                daemon=True
            ).start()

    def _monitor_worker(self, camera_id: str, interval: int):
        """Camera Processing Flow"""
        while not self.stop_event.is_set():
            self.process_frame(camera_id)
            time.sleep(interval)

    def stop(self):
        """System shutdown"""
        self.stop_event.set()
        for proc in self.processors.values():
            proc["camera"].release()
        self.ch_client.disconnect()