from pydantic import BaseModel

class DetectionResult(BaseModel):
    count: int
    original_path: str
    annotated_path: str
    timestamp: str