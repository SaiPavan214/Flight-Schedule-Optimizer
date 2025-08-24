from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas import Flight, FlightCreate, FlightUpdate, FlightSearchQuery, APIResponse
from ..services.flight_service import FlightService
from ..services.data_service import data_service
from ..models import FlightStatus
from datetime import datetime

router = APIRouter(prefix="/flights", tags=["flights"])

@router.get("/", response_model=List[dict])
async def get_flights(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    airline: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get flights with optional filters"""
    try:
        # Use data service to get flights from CSV
        flights = data_service.get_all_flights()
        
        # Apply filters
        if origin:
            flights = [f for f in flights if origin.upper() in f.get('Route', '')]
        if destination:
            flights = [f for f in flights if destination.upper() in f.get('Route', '')]
        if airline:
            flights = [f for f in flights if airline.upper() in f.get('Flight_Number', '')]
        if status:
            if status.lower() == 'delayed':
                flights = [f for f in flights if f.get('Departure_Delay_Minutes', 0) > 0]
            elif status.lower() == 'on time':
                flights = [f for f in flights if f.get('Departure_Delay_Minutes', 0) == 0]
        
        # Apply pagination
        total_flights = len(flights)
        flights = flights[skip:skip + limit]
        
        return flights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")

@router.get("/{flight_id}", response_model=dict)
async def get_flight(flight_id: str, db: Session = Depends(get_db)):
    """Get a specific flight by ID (Flight_Number + Date combination)"""
    try:
        flights = data_service.get_all_flights()
        # Find flight by Flight_Number and Date combination
        for flight in flights:
            if f"{flight['Flight_Number']}_{flight['Date']}" == flight_id:
                return flight
        
        raise HTTPException(status_code=404, detail="Flight not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching flight: {str(e)}")

@router.post("/search/nlp", response_model=List[dict])
async def search_flights_nlp(
    search_query: FlightSearchQuery,
    db: Session = Depends(get_db)
):
    """Search flights using natural language processing"""
    try:
        # Use data service for NLP search
        flights = data_service.search_flights_nlp(search_query.query)
        return flights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching flights: {str(e)}")

@router.get("/statistics/overview", response_model=dict)
async def get_flight_statistics(db: Session = Depends(get_db)):
    """Get flight statistics"""
    try:
        return data_service.get_flight_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@router.get("/upcoming/{hours}", response_model=List[dict])
async def get_upcoming_flights(
    hours: int,
    db: Session = Depends(get_db)
):
    """Get flights departing in the next N hours"""
    try:
        return data_service.get_recent_flights(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching upcoming flights: {str(e)}")

@router.get("/delayed/all", response_model=List[dict])
async def get_delayed_flights(db: Session = Depends(get_db)):
    """Get all delayed flights"""
    try:
        return data_service.get_delayed_flights()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching delayed flights: {str(e)}")

@router.get("/recent/today", response_model=List[dict])
async def get_today_flights(db: Session = Depends(get_db)):
    """Get all flights for today"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        flights = data_service.get_all_flights()
        today_flights = [f for f in flights if f.get('Date') == today]
        return today_flights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching today's flights: {str(e)}")
