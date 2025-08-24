from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum
from sqlalchemy.sql import func
from .database import Base
import enum

class FlightStatus(str, enum.Enum):
    ON_TIME = "On Time"
    DELAYED = "Delayed"
    BOARDING = "Boarding"
    CANCELLED = "Cancelled"
    DEPARTED = "Departed"

class AlertType(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class Flight(Base):
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(20), nullable=False, index=True)
    airline = Column(String(100), nullable=False)
    origin = Column(String(10), nullable=False, index=True)
    destination = Column(String(10), nullable=False, index=True)
    departure_time = Column(DateTime, nullable=False, index=True)
    arrival_time = Column(DateTime, nullable=False)
    status = Column(Enum(FlightStatus), nullable=False, default=FlightStatus.ON_TIME)
    gate = Column(String(10), nullable=False)
    terminal = Column(String(10), nullable=False)
    aircraft = Column(String(50), nullable=False)
    price = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(AlertType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RunwayMetric(Base):
    __tablename__ = "runway_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    runway = Column(String(10), nullable=False, index=True)
    utilization = Column(Float, nullable=False)  # Percentage
    capacity = Column(Integer, nullable=False)
    delays = Column(Integer, default=0)
    conflicts = Column(Integer, default=0)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
