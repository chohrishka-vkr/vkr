from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List

class AnalyticsRequest(BaseModel):
    hall_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class CameraStatus(BaseModel):
    camera_id: str
    people_count: int
    last_update: datetime
    hall_name: str
    
class ZoneHourlyData(BaseModel):
    hour: str
    count: int  

class ZoneAnalyticsHourlyResponse(BaseModel):
    zone_name: str
    hourly_data: List[ZoneHourlyData]