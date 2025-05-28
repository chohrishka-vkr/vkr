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
import base64
import json
from fastapi.responses import HTMLResponse

router = APIRouter()

def get_ch_client():
    client = Client(**CLICKHOUSE_CONFIG)
    try:
        yield client
    finally:
        client.disconnect()

@router.get("/current_people")
async def get_current_people(
    hall_name: str = None, 
    camera_id: str = None,
    client: Client = Depends(get_ch_client)
):
    """
    Получение текущего количества людей (по камере или сумма по всем камерам зала)
    Возвращает только количество и время последнего обновления
    """
    try:
        if camera_id:
            # Если указана конкретная камера - возвращаем её данные
            query = """
            SELECT 
                people_count,
                timestamp
            FROM people_count
            WHERE camera_id = %(camera_id)s
            ORDER BY timestamp DESC
            LIMIT 1
            """
            result = client.execute(query, {"camera_id": camera_id})
        elif hall_name:
            # Если указан зал - суммируем по всем его камерам
            query = """
            WITH latest_entries AS (
                SELECT 
                    camera_id,
                    people_count,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY camera_id ORDER BY timestamp DESC) as rn
                FROM people_count
                WHERE hall_name = %(hall_name)s
            )
            SELECT 
                SUM(people_count) as total_people,
                MAX(timestamp) as last_updated
            FROM latest_entries
            WHERE rn = 1
            """
            result = client.execute(query, {"hall_name": hall_name})
        else:
            # Если не указаны параметры - возвращаем 0
            return {"count": 0}
        
        if not result or result[0][0] is None:
            return {"count": 0}
        
        return {
            "count": result[0][0],
            "last_updated": result[0][1].strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics(
    request: AnalyticsRequest = Depends(),
    client: Client = Depends(get_ch_client)
):
    """Получение суммарной аналитики по всем камерам зала (без детализации по камерам)"""
    try:
        query = """
        SELECT 
            timestamp,
            SUM(people_count) as total_people
        FROM people_count
        WHERE hall_name = %(hall_name)s
        """
        
        params = {"hall_name": request.hall_name}
        
        if request.date_from:
            query += " AND timestamp >= %(date_from)s"
            params["date_from"] = request.date_from
        
        if request.date_to:
            query += " AND timestamp <= %(date_to)s"
            params["date_to"] = request.date_to
        
        query += """
        GROUP BY timestamp
        ORDER BY timestamp
        """
        
        results = client.execute(query, params)
        
        return {
            "hall_name": request.hall_name,
            "data": [{
                "timestamp": row[0].strftime("%Y-%m-%d %H:%M:%S"),
                "total_people": row[1]
            } for row in results]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
import base64
from fastapi.responses import JSONResponse

@router.get("/hall_frames")
async def get_hall_screenshots(hall_name: str):
    """Получение скриншотов с камер зала — все по отдельности в JSON base64"""
    try:
        hall_cameras = [
            config for config in CAMERAS.values() 
            if config.get("hall_name") == hall_name
        ]
        
        if not hall_cameras:
            raise HTTPException(status_code=404, detail="No cameras found for this hall")
        
        images_b64 = []
        for config in hall_cameras:
            try:
                camera = HLSCamera(config["url"])
                frame, _ = camera.capture_frame()
                camera.release()
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_b64 = base64.b64encode(img_encoded).decode('utf-8')
                images_b64.append(img_b64)
            except Exception as e:
                print(f"Error processing camera: {str(e)}")
        
        if not images_b64:
            raise HTTPException(status_code=404, detail="No frames captured")
        
        return JSONResponse(content={"images": images_b64})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/show_images", response_class=HTMLResponse)
async def show_images_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Frames</title>
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
                overflow: hidden;
                background: #f0f0f0;
                display: flex;
                justify-content: center;
                align-items: center;
                box-sizing: border-box;
            }
            body {
                flex-direction: column;
            }
            .container {
                width: 95vw;
                max-height: 95vh;
                display: flex;
                flex-direction: column;
                gap: 15px;
                box-sizing: border-box;
            }
            .row {
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: nowrap;
            }
            .row img {
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                object-fit: contain;
                max-height: 40vh;
                max-width: 45vw;
                width: auto;
            }
            /* Если одно изображение — оно крупнее */
            .single-row img {
                max-width: 90vw;
                max-height: 90vh;
            }
        </style>
    </head>
    <body>
        <div class="container" id="container">
            <!-- Верхний ряд -->
            <div class="row" id="top-row"></div>
            <!-- Нижний ряд -->
            <div class="row" id="bottom-row"></div>
        </div>

        <script>
            function getQueryParam(param) {
                const urlParams = new URLSearchParams(window.location.search);
                return urlParams.get(param);
            }

            const hallName = getQueryParam('hall_name');
            const topRow = document.getElementById('top-row');
            const bottomRow = document.getElementById('bottom-row');
            const container = document.getElementById('container');

            if (!hallName) {
                container.textContent = 'Parameter hall_name is required in the URL.';
            } else {
                fetch(`/api/v1/hall_frames?hall_name=${encodeURIComponent(hallName)}`)
                    .then(res => {
                        if (!res.ok) throw new Error('Network response was not ok');
                        return res.json();
                    })
                    .then(data => {
                        if (!data.images || data.images.length === 0) {
                            container.textContent = 'No images found for this hall.';
                            return;
                        }

                        const images = data.images;

                        if (images.length === 1) {
                            // Один кадр — в один ряд, увеличенный размер
                            container.innerHTML = '';  // очистить
                            const img = document.createElement('img');
                            img.src = 'data:image/jpeg;base64,' + images[0];
                            img.alt = 'Camera 1';
                            img.style.maxWidth = '90vw';
                            img.style.maxHeight = '90vh';
                            img.style.border = '1px solid #ccc';
                            img.style.borderRadius = '4px';
                            img.style.background = 'white';
                            container.classList.add('single-row');
                            container.appendChild(img);
                        } else {
                            // Несколько кадров
                            container.classList.remove('single-row');
                            // первые два в верхний ряд
                            for (let i = 0; i < 2 && i < images.length; i++) {
                                const img = document.createElement('img');
                                img.src = 'data:image/jpeg;base64,' + images[i];
                                img.alt = `Camera ${i + 1}`;
                                topRow.appendChild(img);
                            }
                            // остальные — в нижний ряд
                            for (let i = 2; i < images.length; i++) {
                                const img = document.createElement('img');
                                img.src = 'data:image/jpeg;base64,' + images[i];
                                img.alt = `Camera ${i + 1}`;
                                bottomRow.appendChild(img);
                            }
                        }
                    })
                    .catch(err => {
                        container.textContent = 'Error loading images: ' + err.message;
                        console.error(err);
                    });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
