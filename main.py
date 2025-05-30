import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from rtsp_capture.scheduler import DetectionScheduler
from core.utils import CLICKHOUSE_CONFIG
from clickhouse_driver import Client
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fitness Analytics Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from API.endpoints import router as api_router
app.include_router(api_router)

def run_monitoring():
    scheduler = DetectionScheduler()
    
    try:
        logger.info("🚀 Launching a monitoring system for all cameras...")
        scheduler.start_monitoring(interval=30)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Monitoring stop signal received")
        scheduler.stop()
        logger.info("✅ All monitoring processes have been stopped correctly")
    except Exception as e:
        logger.error(f"Error in monitoring: {str(e)}", exc_info=True)

def run_web_server():
    """A function for launching a web server"""
    logger.info("🚀 Launching the API Web Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)

if __name__ == "__main__":
    try:
        test_client = Client(**CLICKHOUSE_CONFIG)
        test_client.execute("SELECT 1")
        test_client.disconnect()
        logger.info("✅ Verification of connection to ClickHouse is successful")

        monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        
        monitoring_thread.start()
        web_thread.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 An application stop signal has been received")
    except Exception as e:
        logger.error(f"⚠️ Initialization error: {str(e)}", exc_info=True)
    finally:
        logger.info("✅ The application was stopped correctly")