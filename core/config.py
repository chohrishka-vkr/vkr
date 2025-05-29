from dotenv import load_dotenv
import os

load_dotenv()

CAMERAS = {
    "cam_117": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-117/api/stream.m3u8?src=camera-117&mp4=flac",
        "hall_name": "gym", 
        "exclusion_zones": [[0, 0], [1279, 0], [0, 1139], [0, 0], [1279, 0],
                     [1667, 5], [2363, 1517], [2685, 1517], [2687, 0],
                     [1349, 0], [1361, 119], [1281, 163], [1189, 89]],
        "zones": {
            "strength_training_1": [[945, 942], [934, 354], [449, 254], [0, 820], [0, 941], [945, 942]],
            "strength_training_2": [[934, 425], [939, 49], [580, 0], [468, 265], [913, 391]],
        }
    },
    "cam_119": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-119/api/stream.m3u8?src=camera-119&mp4=flac",
        "hall_name": "gym",
        "exclusion_zones": [[0, 0], [1261, 0], [1261, 115], [1040, 181], [0, 1519], [0, 0], [1261, 0],
                     [1595, 0], [1707, 209], [1733, 119], [2685, 1313], [2685, 0], [1595, 0]],
        "zones": {
            "weights_right": [[1663, 943], [903, 943], [886, 331], [831, 246], [873, 0], [1665, 0], [1663, 943]],
            "weights_left": [[0, 943], [903, 943], [886, 331], [831, 246], [873, 0], [0, 0], [0, 943]],
        }
    },
    "cam_120": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-120/api/stream.m3u8?src=camera-120&mp4=flac",
        "hall_name": "gym", 
        "exclusion_zones": [[0, 0], [1233, 0], [370, 500], [245, 875], [0, 945], [0, 0], [1233, 0],
                     [1285, 17], [1527, 20], [1527, 95], [1331, 75], [1285, 17]],
        "zones": {
            "cardio": [[1468, 943], [1353, 689], [1136, 617], [944, 163], [1130, 0], [1667, 0], [1667, 943], [1468, 943]],
            "fitness": [[1468, 943], [1353, 689], [1136, 617], [1060, 434], [340, 452], [0, 645], [0, 944], [1468, 943]],
            "training": [[1060, 434], [340, 452], [246, 309], [740, 33], [917, 74], [1060, 434]],
        }
    },
    "cam_121": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-121/api/stream.m3u8?src=camera-121&mp4=flac",
        "hall_name": "functional_training_hall",
        "zones": {
            "training": [[182, 459], [132, 0], [874, 0], [880, 323], [182, 459]],
            "green_carpet": [[1667, 665], [757, 271], [909, 0], [1666, 0], [1667, 665]],
            "functional_training": [[0, 363], [860, 306], [1666, 661], [1668, 940], [0, 942], [0, 363]],
        }
    },
    "cam_118": {
        "url": "https://techvision.dvfu.ru/cameras/go2rtc-118/api/stream.m3u8?src=camera-118&mp4=flac",
        "hall_name": "group_program_room",
        "exclusion_zones": [[1153, 145], [1551, 228], [1533, 388], [1156, 290], [1153, 145],
                     [1551, 228], [1398, 945], [1671, 945], [1671, 370], [1551, 228]]
    },
}


CLICKHOUSE_CONFIG = {
    "host": os.getenv('DATABASE_HOST'),
    "port": os.getenv('DATABASE_PORT'),
    "user": os.getenv('DATABASE_USER'),
    "password": os.getenv('DATABASE_PASSWORD'),
    "database": os.getenv('DATABASE_NAME')
}

COUNTER_API_URL = os.getenv('COUNTER_API_URL')
   

