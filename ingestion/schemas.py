from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class AdEvent(BaseModel):
    event_id: str
    ts: datetime
    user_id: str
    ad_id: int
    device: Literal["mobile", "desktop", "console", "tablet"]
    geo: str # e.g., "US-NY"
    event_type: Literal["impression", "click", "conversion"]
    revenue: Optional[float] = Field(default=0.0, ge=0.0)
    
    