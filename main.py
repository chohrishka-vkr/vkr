from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import time
from rtsp_capture.scheduler import DetectionScheduler
from detection_service.config import CLICKHOUSE_CONFIG
from clickhouse_driver import Client

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
        print("🚀 Запуск системы мониторинга для всех камер...")
        scheduler.start_monitoring(interval=30)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки мониторинга")
        scheduler.stop()
        print("✅ Все процессы мониторинга корректно остановлены")

def run_web_server():
    """Функция для запуска веб-сервера"""
    import uvicorn
    print("🚀 Запуск веб-сервера API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    try:
        test_client = Client(**CLICKHOUSE_CONFIG)
        test_client.execute("SELECT 1")
        test_client.disconnect()
        print("✅ Проверка подключения к ClickHouse успешна")

        monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        
        monitoring_thread.start()
        web_thread.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки приложения")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации: {str(e)}")
    finally:
        print("✅ Приложение корректно остановлено")