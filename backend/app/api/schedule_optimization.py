from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.schedule_optimization_service import schedule_optimization_service

router = APIRouter(prefix="/schedule-optimization")

@router.get("/optimal-times/{airport_code}")
async def get_optimal_takeoff_landing_times(airport_code: str = "BOM"):
    """Get optimal takeoff/landing times for an airport"""
    try:
        result = schedule_optimization_service.find_optimal_takeoff_landing_times(airport_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for airport {airport_code}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/busy-time-slots/{airport_code}")
async def get_busy_time_slots(airport_code: str = "BOM"):
    """Get busy time slots to avoid for scheduling"""
    try:
        result = schedule_optimization_service.identify_busy_time_slots(airport_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for airport {airport_code}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize-flight/{flight_number}")
async def optimize_flight_schedule(
    flight_number: str,
    new_departure_time: str = Query(..., description="New departure time in HH:MM format")
):
    """Optimize schedule time for a specific flight"""
    try:
        result = schedule_optimization_service.optimize_flight_schedule(flight_number, new_departure_time)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cascading-delays")
async def get_cascading_delays(
    min_cascade_impact: int = Query(30, description="Minimum cascade impact threshold")
):
    """Analyze flights with biggest cascading impact on delays"""
    try:
        result = schedule_optimization_service.analyze_cascading_delays(min_cascade_impact)
        if not result:
            raise HTTPException(status_code=404, detail="No cascading delay data found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runway-capacity/{airport_code}")
async def get_runway_capacity_analysis(airport_code: str = "BOM"):
    """Analyze runway capacity constraints and optimization opportunities"""
    try:
        result = schedule_optimization_service.get_runway_capacity_analysis(airport_code)
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for airport {airport_code}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{airport_code}")
async def get_schedule_optimization_summary(airport_code: str = "BOM"):
    """Get comprehensive schedule optimization summary for an airport"""
    try:
        # Get all optimization data
        optimal_times = schedule_optimization_service.find_optimal_takeoff_landing_times(airport_code)
        busy_slots = schedule_optimization_service.identify_busy_time_slots(airport_code)
        capacity_analysis = schedule_optimization_service.get_runway_capacity_analysis(airport_code)
        cascading_delays = schedule_optimization_service.analyze_cascading_delays()
        
        return {
            "airport_code": airport_code,
            "optimal_times": optimal_times.get("optimal_times", {}),
            "busy_time_slots": busy_slots.get("busy_time_slots", {}),
            "capacity_analysis": capacity_analysis.get("bottlenecks", {}),
            "cascading_delays_count": cascading_delays.get("total_cascading_flights", 0),
            "recommendations": {
                "timing": optimal_times.get("recommendations", []),
                "avoidance": busy_slots.get("recommendations", []),
                "capacity": capacity_analysis.get("optimization_opportunities", []),
                "cascading": cascading_delays.get("recommendations", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
