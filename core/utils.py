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
                    [(0, 1519),  
                     (0, 1397),   
                     (689, 431),    
                     (1685, 509),     
                     (1893, 1519),    
                     (0, 1519)]  
                ],
                "strength_training_farther": [
                    [(689, 431),   
                     (1685, 509),    
                     (1567, 79),      
                     (1163, 69),    
                     (689, 431)]  
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
                    [(0, 1519),  
                     (0, 0),  
                     (1417, 0),   
                     (1417, 1519),   
                     (0, 1519),] 
                ],
                "weights_left": [
                    [(2687, 1519),     
                     (1411, 1473),  
                     (1384, 517),  
                     (1298, 384),   
                     (1364, 0),     
                     (0, 0),       
                     (0, 1473)]    
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
                    [(2371, 1519),  
                     (2167, 1055),  
                     (1800, 1025),  
                     (1523, 263),   
                     (1525, 0),     
                     (2685, 0),     
                     (2685, 1519),  
                     (2371, 1519)]  
                ],
                "fitness": [
                    [(2371, 1519),  
                     (2167, 1055),  
                     (1800, 1025),   
                     (527, 727),   
                     (0, 1033),    
                     (0, 1519),     
                     (2371, 1519)]  
                ],
                "training": [
                    [(1800, 1025),   
                     (527, 727),    
                     (0, 1033),    
                     (1135, 0),    
                     (1525, 0),   
                     (1523, 263),
                     (1800, 1025)]   
                ]
            }
        },
        "cam_121": {
            "url": "https://techvision.dvfu.ru/cameras/go2rtc-121/api/stream.m3u8?src=camera-121&mp4=flac",
            "hall_name": "functional_training_hall",
            "exclusion_zones": [],
            "zones": {
                "training": [
                    [(1217, 439),    
                     (1457, 0),     
                     (0, 671),     
                     (1217, 439)]    
                ],
                "green_carpet": [
                    [(2688, 1089),  
                     (1217, 439),   
                     (1457, 0),     
                     (2687, 0),     
                     (2688, 1089)]  
                ],
                "functional_training": [
                    [(2688, 1089),      
                     (1217, 439),   
                     (0, 671),  
                     (0, 1515),  
                     (2687, 1519),     
                     (2688, 1089)]      
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
                    [(0, 830),      # 0 * 1.5625 = 0, 531 * 1.5625 = 830
                     (1759, 495),   # 1126 * 1.5625 = 1759, 317 * 1.5625 = 495
                     (1809, 0),     # 1158 * 1.5625 = 1809, 0 * 1.5625 = 0
                     (0, 0),        # 0 * 1.5625 = 0, 0 * 1.5625 = 0
                     (0, 830)]      # 0 * 1.5625 = 0, 531 * 1.5625 = 830
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