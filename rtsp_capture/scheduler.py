import time
import threading
from pathlib import Path
from .hls_client import HLSCamera

def start_capture_scheduler(camera: HLSCamera, interval: int = 120):
    """Запуск периодического захвата кадров в отдельном потоке"""
    
    def capture_worker():
        while True:
            try:
                filepath = camera.capture_frame()
                print(f"Скриншот сохранен: {filepath}")
            except Exception as e:
                print(f"Ошибка захвата: {e}")
            time.sleep(interval)
    
    thread = threading.Thread(target=capture_worker, daemon=True)
    thread.start()
    