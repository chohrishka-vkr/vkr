from clickhouse_driver import Client
from typing import Dict, Any
import logging
from dotenv import load_dotenv
import os

load_dotenv()

CLICKHOUSE_CONFIG = {
    "host": os.getenv('DATABASE_HOST'),
    "port": os.getenv('DATABASE_PORT'),
    "user": os.getenv('DATABASE_USER'),
    "password": os.getenv('DATABASE_PASSWORD'),
    "database": os.getenv('DATABASE_NAME')
}

logger = logging.getLogger(__name__)

def get_ch_client() -> Client:
    """Returns connection to ClickHouse"""
    return Client(**CLICKHOUSE_CONFIG)

def init_camera_config_table(client: Client) -> None:
    """Creates camera configuration table if not exists"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS camera_configurations (
        camera_id String,
        url String,
        hall_name String,
        exclusion_zones Array(Array(Tuple(Int32, Int32))) DEFAULT [],
        zones Map(String, Array(Array(Tuple(Int32, Int32)))) DEFAULT map()
    ) ENGINE = MergeTree()
    ORDER BY (camera_id)
    """
    client.execute(create_table_query)
    logger.info("Camera configurations table initialized")

    
def load_camera_configs(client: Client) -> Dict[str, Any]:
    """Loads the camera configuration from ClickHouse"""
    query = "SELECT * FROM camera_configurations"
    try:
        result = client.execute(query)
        return {
            row[0]: {
                "url": row[1],
                "hall_name": row[2],
                "exclusion_zones": row[3],
                "zones": row[4]
            }
            for row in result
        }
    except Exception as e:
        logger.error(f"Error loading camera configs: {str(e)}")
        return {}

def save_camera_config(client: Client, camera_id: str, config: Dict[str, Any]) -> None:
    """Saves the camera configuration in ClickHouse"""
    query = """
    INSERT INTO camera_configurations 
    (camera_id, url, hall_name, exclusion_zones, zones)
    VALUES
    """
    data = {
        'camera_id': camera_id,
        'url': config['url'],
        'hall_name': config['hall_name'],
        'exclusion_zones': config.get('exclusion_zones', []),
        'zones': config.get('zones', {})
    }
    client.execute(query, [data])

def seed_initial_data(client: Client) -> None:
    """Fills the table with initial camera configurations with correct data structure"""
    initial_configs = {
        "cam_117": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-117/api/stream.m3u8?src=camera-117&mp4=flac",
            "hall_name": "gym",
            "exclusion_zones": [
                [(0, 0), (1279, 0), (0, 1139), (0, 0), (1279, 0),
                (1667, 5), (2363, 1517), (2685, 1517), (2687, 0),
                (1349, 0), (1361, 119), (1281, 163), (1189, 89)]
            ],
            "zones": {
                "strength_training_near": [
                    [(945, 942), (934, 354), (449, 254), (0, 820), (0, 941), (945, 942)]
                ],
                "strength_training_farther": [
                    [(934, 425), (939, 49), (580, 0), (468, 265), (913, 391)]
                ]
            }
        },
        "cam_119": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-119/api/stream.m3u8?src=camera-119&mp4=flac",
            "hall_name": "gym",
            "exclusion_zones": [
                [(0, 0), (1261, 0), (1261, 115), (1040, 181), (0, 1519), (0, 0), (1261, 0),
                (1595, 0), (1707, 209), (1733, 119), (2685, 1313), (2685, 0), (1595, 0)]
            ],
            "zones": {
                "weights_right": [
                    [(1663, 943), (903, 943), (886, 331), (831, 246), (873, 0), (1665, 0), (1663, 943)]
                ],
                "weights_left": [
                    [(0, 943), (903, 943), (886, 331), (831, 246), (873, 0), (0, 0), (0, 943)]
                ]
            }
        },
        "cam_120": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-120/api/stream.m3u8?src=camera-120&mp4=flac",
            "hall_name": "gym",
            "exclusion_zones": [
                [(0, 0), (1233, 0), (370, 500), (245, 875), (0, 945), (0, 0), (1233, 0),
                (1285, 17), (1527, 20), (1527, 95), (1331, 75), (1285, 17)]
            ],
            "zones": {
                "cardio": [
                    [(1468, 943), (1353, 689), (1136, 617), (944, 163), (1130, 0), (1667, 0), (1667, 943), (1468, 943)]
                ],
                "fitness": [
                    [(1468, 943), (1353, 689), (1136, 617), (1060, 434), (340, 452), (0, 645), (0, 944), (1468, 943)]
                ],
                "training": [
                    [(1060, 434), (340, 452), (246, 309), (740, 33), (917, 74), (1060, 434)]
                ]
            }
        },
        "cam_121": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-121/api/stream.m3u8?src=camera-121&mp4=flac",
            "hall_name": "functional_training_hall",
            "exclusion_zones": [],
            "zones": {
                "training": [
                    [(182, 459), (132, 0), (874, 0), (880, 323), (182, 459)]
                ],
                "green_carpet": [
                    [(1667, 665), (757, 271), (909, 0), (1666, 0), (1667, 665)]
                ],
                "functional_training": [
                    [(0, 363), (860, 306), (1666, 661), (1668, 940), (0, 942), (0, 363)]
                ]
            }
        },
        "cam_118": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-118/api/stream.m3u8?src=camera-118&mp4=flac",
            "hall_name": "group_program_room",
            "exclusion_zones": [
                [(1153, 145), (1551, 228), (1533, 388), (1156, 290), (1153, 145),
                (1551, 228), (1398, 945), (1671, 945), (1671, 370), (1551, 228)]
            ],
            "zones": {
                "weights": [
                    [(0, 531), (1126, 317), (1158, 0), (0, 0), (0, 531)]
                ]
            }
        }
    }

    try:
        client.execute("TRUNCATE TABLE camera_configurations")
        
        for camera_id, config in initial_configs.items():
            try:
                data = {
                    'camera_id': camera_id,
                    'url': config['url'],
                    'hall_name': config['hall_name'],
                    'exclusion_zones': config['exclusion_zones'],
                    'zones': config['zones']
                }
                
                query = """
                INSERT INTO camera_configurations 
                (camera_id, url, hall_name, exclusion_zones, zones)
                VALUES
                """
                client.execute(query, [data])
                logger.info(f"Successfully seeded config for camera {camera_id}")
            except Exception as e:
                logger.error(f"Failed to seed camera {camera_id}: {str(e)}")
                continue
        
        logger.info(f"Successfully seeded initial data for {len(initial_configs)} cameras")
        
    except Exception as e:
        logger.critical(f"Fatal error during initial data seeding: {str(e)}")
        raise