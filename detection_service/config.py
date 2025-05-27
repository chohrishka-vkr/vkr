from pathlib import Path

MODEL_PATH = Path("models/yolo11m.pt")

CAMERAS = {
    "cam_117": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-117/api/stream.m3u8?src=camera-117&mp4=flac",
        "hall_name": "gym", 
        "user_id": 1,
        "model_path": "yolo11m.pt",
        "exclusion_zones": [[0, 0], [1279, 0], [0, 1139], [0, 0], [1279, 0],
                     [1667, 5], [2363, 1517], [2685, 1517], [2687, 0],
                     [1349, 0], [1361, 119], [1281, 163], [1189, 89]]
    },
    "cam_119": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-119/api/stream.m3u8?src=camera-119&mp4=flac",
        "hall_name": "gym",
        "user_id": 1,
        "model_path": "yolo11m.pt",
        "exclusion_zones": [[0, 0], [1261, 0], [1261, 115], [1040, 181], [0, 1519], [0, 0], [1261, 0],
                     [1595, 0], [1707, 209], [1733, 119], [2685, 1313], [2685, 0], [1595, 0]]
    },
    "cam_120": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-120/api/stream.m3u8?src=camera-120&mp4=flac",
        "hall_name": "gym", 
        "user_id": 1,
        "model_path": "yolo11m.pt",
        "exclusion_zones": [[0, 0], [1233, 0], [370, 500], [245, 875], [0, 945], [0, 0], [1233, 0],
                     [1285, 17], [1527, 20], [1527, 95], [1331, 75], [1285, 17]]
    },
    "cam_121": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-121/api/stream.m3u8?src=camera-121&mp4=flac",
        "hall_name": "functional_training_hall",
        "user_id": 1,
        "model_path": "yolo11m.pt"
    },
    "cam_118": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-118/api/stream.m3u8?src=camera-118&mp4=flac",
        "hall_name": "group_program_room",
        "user_id": 1,
        "model_path": "yolo11m.pt",
        "exclusion_zones": [[1153, 145], [1551, 228], [1533, 388], [1156, 290], [1153, 145],
                     [1551, 228], [1398, 945], [1671, 945], [1671, 370], [1551, 228]]
    },
}

CLICKHOUSE_CONFIG = {
    "host": "localhost",
    "port": 9000,
    "user": "default",
    "password": "njhnbr",
    "database": "fitness_analytics"
}