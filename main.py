from rtsp_capture.scheduler import DetectionScheduler
import time

def main():
    scheduler = DetectionScheduler()
    
    try:
        print("🚀 Запуск системы мониторинга для всех камер...")
        scheduler.start_monitoring(interval=30)  # Интервал в секундах
        
        # Основной цикл
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки")
        scheduler.stop()
        print("✅ Все процессы корректно остановлены")

if __name__ == "__main__":
    main()