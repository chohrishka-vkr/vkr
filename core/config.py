import os
import sys
from typing import Dict, Any
from core.utils import get_ch_client, load_camera_configs, init_camera_config_table, seed_initial_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_camera_configs() -> Dict[str, Any]:
    """Initializes the camera configuration from the database"""
    client = get_ch_client()
    
    try:
        init_camera_config_table(client)
        
        configs = load_camera_configs(client)
        
        if not configs:
            logger.warning("No camera configs found in DB, seeding initial data")
            seed_initial_data(client)
            configs = load_camera_configs(client)
            
        return configs
    except Exception as e:
        logger.critical(f"Fatal error initializing camera configs: {str(e)}")
        sys.exit(1)
    finally:
        client.disconnect()
        
CAMERAS = initialize_camera_configs()

COUNTER_API_URL = os.getenv('COUNTER_API_URL')
   

