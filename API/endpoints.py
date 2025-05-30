from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from clickhouse_driver import Client
from datetime import datetime
from core.utils import CLICKHOUSE_CONFIG
from core.config import CAMERAS
from .schemas import AnalyticsRequest, ZoneAnalyticsHourlyResponse
import cv2
from rtsp_capture.hls_client import HLSCamera
import base64
from typing import List

router = APIRouter(prefix="/api")

def get_ch_client():
    client = Client(**CLICKHOUSE_CONFIG)
    try:
        yield client
    finally:
        client.disconnect()

@router.get("/people-count/{hall_name}/")
@router.get("/people-count/camera/{camera_id}/")
async def get_current_people(
    hall_name: str = None,
    camera_id: str = None,
    client: Client = Depends(get_ch_client)
):
    try:
        if camera_id:
            query = """
            SELECT 
                people_count as count,
                timestamp
            FROM people_count
            WHERE camera_id = %(camera_id)s
            ORDER BY timestamp DESC
            LIMIT 1
            """
            result = client.execute(query, {"camera_id": camera_id})
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for camera {camera_id}"
                )
            
            return {
                "count": result[0][0],
                "last_updated": result[0][1].strftime("%Y-%m-%d %H:%M:%S")
            }
        
        elif hall_name:
            query = """
            WITH latest_entries AS (
                SELECT 
                    camera_id,
                    people_count as count,
                    timestamp,
                    ROW_NUMBER() OVER (PARTITION BY camera_id ORDER BY timestamp DESC) as rn
                FROM people_count
                WHERE hall_name = %(hall_name)s
            )
            SELECT 
                SUM(count) as count,
                MAX(timestamp) as last_updated
            FROM latest_entries
            WHERE rn = 1
            """
            result = client.execute(query, {"hall_name": hall_name})
            
            if not result or result[0][0] is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No data found for specified parameters"
                )

            return {
                "count": result[0][0],
                "last_updated": result[0][1].strftime("%Y-%m-%d %H:%M:%S")
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Please specify either hall_name or camera_id"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/people-analytics/{hall_name}/{date_from}/{date_to}/")
async def get_analytics(
    request: AnalyticsRequest = Depends(),
    client: Client = Depends(get_ch_client)
):
    try:
        query = """
        SELECT 
            timestamp,
            SUM(people_count) as count
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
        
        results: List[tuple] = client.execute(query, params)
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No analytics data found for the specified parameters"
            )
        
        return {
            "data": [{
                "timestamp": row[0].strftime("%Y-%m-%d %H:%M:%S"),
                "count": row[1]
            } for row in results]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/hall_frames/{hall_name}")
async def get_hall_screenshots(hall_name: str):
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

@router.get("/peak-hours/{hall_name}/{date_from}/{date_to}/")
async def get_peak_hours(
    hall_name: str,
    date_from: str,
    date_to: str,
    client: Client = Depends(get_ch_client)
):
    try:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            if dt_to < dt_from:
                raise HTTPException(400, "End date must be after start date")
        except ValueError:
            raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

        query = """
        SELECT 
            toHour(timestamp) as hour,
            AVG(people_count) as count
        FROM (
            SELECT 
                timestamp,
                SUM(people_count) as people_count
            FROM people_count
            WHERE hall_name = %(hall_name)s
              AND timestamp >= %(date_from)s
              AND timestamp <= %(date_to)s
            GROUP BY timestamp
        )
        GROUP BY hour
        ORDER BY hour
        """
        
        result = client.execute(query, {
            "hall_name": hall_name,
            "date_from": date_from,
            "date_to": date_to
        })
        
        if not result:
            raise HTTPException(404, "No data available for the selected period")
            
        return {
            "hall": hall_name,
            "period": f"{date_from} to {date_to}",
            "hourly_stats": [{"hour": row[0], "count": round(row[1], 1)} for row in result]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")
    
@router.get("/zone-analytics-hourly/{hall_name}/{date_from}/{date_to}/", response_model=List[ZoneAnalyticsHourlyResponse])
async def get_zone_analytics_hourly(
    hall_name: str,
    date_from: str,
    date_to: str,
    client: Client = Depends(get_ch_client)
):
    try:
        try:
            dt_from = datetime.strptime(date_from, "%Y-%m-%d")
            dt_to = datetime.strptime(date_to, "%Y-%m-%d")
            if dt_to < dt_from:
                raise HTTPException(400, "End date must be after start date")
        except ValueError:
            raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")

        query = """
        SELECT 
            zone as zone_name,
            toStartOfHour(timestamp) as hour,
            SUM(people_count) as count
        FROM people_count
        WHERE hall_name = %(hall_name)s
          AND timestamp >= %(date_from)s
          AND timestamp <= %(date_to)s
          AND zone != ''
        GROUP BY zone_name, hour
        ORDER BY zone_name, hour
        """
        
        result = client.execute(query, {
            "hall_name": hall_name,
            "date_from": date_from,
            "date_to": date_to
        })
        
        if not result:
            raise HTTPException(404, "No zone data available for the selected period")
            
        analytics = {}
        for row in result:
            zone_name = row[0]
            if zone_name not in analytics:
                analytics[zone_name] = []
            analytics[zone_name].append({
                "hour": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                "count": row[2]
            })
        
        return [{
            "zone_name": zone,
            "hourly_data": data
        } for zone, data in analytics.items()]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")