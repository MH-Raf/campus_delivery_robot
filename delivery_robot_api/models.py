from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

class CreateOrderRequest(BaseModel):
    address: str
    delivery_window: str

class OrderResponse(BaseModel):
    address: str
    delivery_window: str
    confirmation_code: str
    status: str
    eta: Optional[datetime]
    delivered_at: Optional[datetime]

class DeliverOrderRequest(BaseModel):
    confirmation_code: str

class SensorResponse(BaseModel):
    data: Dict[str, Any]

class ActuatorResponse(BaseModel):
    data: Dict[str, Any]

class StatusResponse(BaseModel):
    status: str  # idle, running, error

class ScenarioRequest(BaseModel):
    scenario: str  # 'A' или 'B'