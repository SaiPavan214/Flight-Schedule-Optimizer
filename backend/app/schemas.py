from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .models import FlightStatus, AlertType

# Flight Schemas
class FlightBase(BaseModel):
    flight_number: str = Field(..., min_length=1, max_length=20)
    airline: str = Field(..., min_length=1, max_length=100)
    origin: str = Field(..., min_length=1, max_length=10)
    destination: str = Field(..., min_length=1, max_length=10)
    departure_time: datetime
    arrival_time: datetime
    status: FlightStatus = FlightStatus.ON_TIME
    gate: str = Field(..., min_length=1, max_length=10)
    terminal: str = Field(..., min_length=1, max_length=10)
    aircraft: str = Field(..., min_length=1, max_length=50)
    price: Optional[float] = None

class FlightCreate(FlightBase):
    pass

class FlightUpdate(BaseModel):
    flight_number: Optional[str] = Field(None, min_length=1, max_length=20)
    airline: Optional[str] = Field(None, min_length=1, max_length=100)
    origin: Optional[str] = Field(None, min_length=1, max_length=10)
    destination: Optional[str] = Field(None, min_length=1, max_length=10)
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    status: Optional[FlightStatus] = None
    gate: Optional[str] = Field(None, min_length=1, max_length=10)
    terminal: Optional[str] = Field(None, min_length=1, max_length=10)
    aircraft: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[float] = None

class Flight(FlightBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alert Schemas
class AlertBase(BaseModel):
    type: AlertType
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    resolved: bool = False

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    type: Optional[AlertType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    message: Optional[str] = Field(None, min_length=1)
    resolved: Optional[bool] = None

class Alert(AlertBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Runway Metric Schemas
class RunwayMetricBase(BaseModel):
    runway: str = Field(..., min_length=1, max_length=10)
    utilization: float = Field(..., ge=0, le=100)
    capacity: int = Field(..., ge=0)
    delays: int = Field(0, ge=0)
    conflicts: int = Field(0, ge=0)

class RunwayMetricCreate(RunwayMetricBase):
    pass

class RunwayMetricUpdate(BaseModel):
    runway: Optional[str] = Field(None, min_length=1, max_length=10)
    utilization: Optional[float] = Field(None, ge=0, le=100)
    capacity: Optional[int] = Field(None, ge=0)
    delays: Optional[int] = Field(None, ge=0)
    conflicts: Optional[int] = Field(None, ge=0)

class RunwayMetric(RunwayMetricBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Search and Query Schemas
class FlightSearchQuery(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    limit: Optional[int] = Field(10, ge=1, le=100)

class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, description="User message for chatbot")
    context: Optional[str] = Field(None, description="Additional context for the conversation")

class ChatResponse(BaseModel):
    response: str
    confidence: float = Field(..., ge=0, le=1)
    sources: Optional[List[str]] = None

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int
