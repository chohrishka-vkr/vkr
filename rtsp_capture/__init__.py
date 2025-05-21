from .hls_client import HLSCamera
from .scheduler import start_capture_scheduler

__all__ = ['HLSCamera', 'start_capture_scheduler']
__version__ = '0.1.0'

def init_module(rtsp_url: str, interval: int = 120):
    """Инициализация модуля с настройками по умолчанию"""
    camera = HLSCamera(rtsp_url)
    start_capture_scheduler(camera, interval)
    return camera