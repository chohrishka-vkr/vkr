from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from clickhouse_driver import Client
from datetime import datetime, timedelta
from detection_service.config import CLICKHOUSE_CONFIG
from .schemas import AnalyticsRequest
import cv2
from fastapi.responses import Response
import numpy as np
from detection_service.config import CAMERAS
from rtsp_capture.hls_client import HLSCamera


router = APIRouter()

def get_ch_client():
    client = Client(**CLICKHOUSE_CONFIG)
    try:
        yield client
    finally:
        client.disconnect()

@router.get("/current_people")
async def get_current_people(camera_id: str, client: Client = Depends(get_ch_client)):
    """Получение текущего количества людей для камеры"""
    try:
        result = client.execute(
            """
            SELECT people_count FROM people_count
            WHERE camera_id = %(camera_id)s
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            {"camera_id": camera_id}
        )
        return {"count": result[0][0] if result else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics(
    request: AnalyticsRequest = Depends(),
    client: Client = Depends(get_ch_client)
):
    """Получение аналитики с фильтрацией"""
    try:
        query = """
        SELECT 
            toStartOfHour(timestamp) as hour,
            people_count as people,
        FROM people_count
        WHERE 1=1
        """
        
        params = {}
        filters = []
        
        if request.hall_name:
            filters.append("hall_name = %(hall_name)s")
            params["hall_name"] = request.hall_name
        
        if request.date_from:
            filters.append("timestamp >= %(date_from)s")
            params["date_from"] = request.date_from
        
        if request.date_to:
            filters.append("timestamp <= %(date_to)s")
            params["date_to"] = request.date_to
        
        if filters:
            query += " AND " + " AND ".join(filters)
        
        query += " GROUP BY hour, hall_name ORDER BY hour"
        
        results = client.execute(query, params)
        
        return {
            "data": [{
                "hour": row[0].strftime("%Y-%m-%d %H:%M:%S"),
                "avg_people": float(row[1]),
                "hall_name": row[2]
            } for row in results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/frame")
async def get_camera_screenshot(camera_id: str):
    """Получение чистого скриншота с камеры без визуализации исключенных зон"""
    try:
        # Проверяем, что камера существует в конфигурации
        if camera_id not in CAMERAS:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        # Получаем конфигурацию камеры
        config = CAMERAS[camera_id]
        
        # Создаем временный экземпляр камеры для захвата кадра
        camera = HLSCamera(config["url"])
        frame, _ = camera.capture_frame()
        camera.release()
        
        # Конвертируем кадр в JPEG (без добавления exclusion_zones)
        _, img_encoded = cv2.imencode('.jpg', frame)
        
        return Response(content=img_encoded.tobytes(), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
