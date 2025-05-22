from pathlib import Path

# Пути по умолчанию
MODEL_PATH = Path("models/yolo11m.pt")
OUTPUT_DIR = Path("storage/detections")

CAMERAS = {
    "cam_35": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-35/api/stream.m3u8?src=camera-35&mp4=flac",
        "hall_name": "Тренажерный зал",
        "user_id": 1,
        "model_path": "yolo11m.pt"
    },
    "cam_32": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-32/api/stream.m3u8?src=camera-32&mp4=flac",
        "hall_name": "Тренажерный зал", 
        "user_id": 1,
        "model_path": "yolo11m.pt"
    },
    "cam_34": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-34/api/stream.m3u8?src=camera-34&mp4=flac",
        "hall_name": "Тренажерный зал",
        "user_id": 1,
        "model_path": "yolo11m.pt"
    },
    "cam_36": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-36/api/stream.m3u8?src=camera-36&mp4=flac",
        "hall_name": "зал функционального тренинга",
        "user_id": 1,
        "model_path": "yolo11m.pt"
    }
}

CLICKHOUSE_CONFIG = {
    "host": "localhost",
    "port": 9000,
    "user": "default",
    "password": "njhnbr",
    "database": "fitness_analytics"
}