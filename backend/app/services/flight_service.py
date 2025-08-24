from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models import Flight, FlightStatus
from ..schemas import FlightCreate, FlightUpdate
from .gemini_service import gemini_service

class FlightService:
    
    @staticmethod
    async def create_flight(db: Session, flight: FlightCreate) -> Flight:
        """Create a new flight"""
        db_flight = Flight(**flight.dict())
        db.add(db_flight)
        db.commit()
        db.refresh(db_flight)
        return db_flight
    
    @staticmethod
    def get_flight(db: Session, flight_id: int) -> Optional[Flight]:
        """Get a flight by ID"""
        return db.query(Flight).filter(Flight.id == flight_id).first()
    
    @staticmethod
    def get_flights(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        airline: Optional[str] = None,
        status: Optional[FlightStatus] = None
    ) -> List[Flight]:
        """Get flights with optional filters"""
        query = db.query(Flight)
        
        if origin:
            query = query.filter(Flight.origin.ilike(f"%{origin}%"))
        if destination:
            query = query.filter(Flight.destination.ilike(f"%{destination}%"))
        if airline:
            query = query.filter(Flight.airline.ilike(f"%{airline}%"))
        if status:
            query = query.filter(Flight.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    async def search_flights_nlp(db: Session, query: str, limit: int = 10) -> List[Flight]:
        """Search flights using natural language processing"""
        # Parse the query using Gemini AI
        parsed_params = await gemini_service.parse_flight_query(query)
        
        # Build database query based on parsed parameters
        db_query = db.query(Flight)
        
        if parsed_params.get('origin'):
            db_query = db_query.filter(Flight.origin.ilike(f"%{parsed_params['origin']}%"))
        
        if parsed_params.get('destination'):
            db_query = db_query.filter(Flight.destination.ilike(f"%{parsed_params['destination']}%"))
        
        if parsed_params.get('airline'):
            db_query = db_query.filter(Flight.airline.ilike(f"%{parsed_params['airline']}%"))
        
        if parsed_params.get('date'):
            # Convert date string to datetime range
            try:
                search_date = datetime.strptime(parsed_params['date'], '%Y-%m-%d')
                start_of_day = search_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                db_query = db_query.filter(
                    and_(
                        Flight.departure_time >= start_of_day,
                        Flight.departure_time < end_of_day
                    )
                )
            except ValueError:
                pass  # Skip date filtering if parsing fails
        
        if parsed_params.get('time'):
            # Filter by time if date is also specified
            if parsed_params.get('date'):
                try:
                    search_date = datetime.strptime(parsed_params['date'], '%Y-%m-%d')
                    time_str = parsed_params['time']
                    
                    if ':' in time_str:
                        hour, minute = map(int, time_str.split(':'))
                        target_time = search_date.replace(hour=hour, minute=minute)
                        # Allow 2 hours before and after the target time
                        time_range_start = target_time - timedelta(hours=2)
                        time_range_end = target_time + timedelta(hours=2)
                        
                        db_query = db_query.filter(
                            and_(
                                Flight.departure_time >= time_range_start,
                                Flight.departure_time <= time_range_end
                            )
                        )
                except ValueError:
                    pass
        
        if parsed_params.get('max_price'):
            try:
                max_price = float(parsed_params['max_price'])
                db_query = db_query.filter(Flight.price <= max_price)
            except (ValueError, TypeError):
                pass
        
        # Order by departure time (closest first)
        db_query = db_query.order_by(Flight.departure_time)
        
        return db_query.limit(limit).all()
    
    @staticmethod
    def update_flight(db: Session, flight_id: int, flight_update: FlightUpdate) -> Optional[Flight]:
        """Update a flight"""
        db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not db_flight:
            return None
        
        update_data = flight_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_flight, field, value)
        
        db.commit()
        db.refresh(db_flight)
        return db_flight
    
    @staticmethod
    def delete_flight(db: Session, flight_id: int) -> bool:
        """Delete a flight"""
        db_flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not db_flight:
            return False
        
        db.delete(db_flight)
        db.commit()
        return True
    
    @staticmethod
    def get_flight_statistics(db: Session) -> Dict[str, Any]:
        """Get flight statistics"""
        total_flights = db.query(Flight).count()
        active_flights = db.query(Flight).filter(Flight.status != FlightStatus.DEPARTED).count()
        
        # Status distribution
        status_counts = db.query(
            Flight.status,
            func.count(Flight.id).label('count')
        ).group_by(Flight.status).all()
        
        # Airline distribution
        airline_counts = db.query(
            Flight.airline,
            func.count(Flight.id).label('count')
        ).group_by(Flight.airline).order_by(func.count(Flight.id).desc()).limit(10).all()
        
        # Recent flights (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_flights = db.query(Flight).filter(Flight.departure_time >= yesterday).count()
        
        return {
            "total_flights": total_flights,
            "active_flights": active_flights,
            "recent_flights": recent_flights,
            "status_distribution": {status: count for status, count in status_counts},
            "top_airlines": {airline: count for airline, count in airline_counts}
        }
    
    @staticmethod
    def get_upcoming_flights(db: Session, hours: int = 24) -> List[Flight]:
        """Get flights departing in the next N hours"""
        now = datetime.now()
        future_time = now + timedelta(hours=hours)
        
        return db.query(Flight).filter(
            and_(
                Flight.departure_time >= now,
                Flight.departure_time <= future_time
            )
        ).order_by(Flight.departure_time).all()
    
    @staticmethod
    def get_delayed_flights(db: Session) -> List[Flight]:
        """Get all delayed flights"""
        return db.query(Flight).filter(Flight.status == FlightStatus.DELAYED).all()
