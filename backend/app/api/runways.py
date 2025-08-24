from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..database import get_db
from ..schemas import RunwayMetric, RunwayMetricCreate, RunwayMetricUpdate, APIResponse
from ..services.runway_service import RunwayService
from ..services.data_service import data_service
from datetime import datetime

router = APIRouter(prefix="/runways", tags=["runways"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_runway_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    runway: Optional[str] = None,
    hours: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get runway metrics with optional filters"""
    try:
        # Get runway analytics from data service
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return []
        
        # Convert to runway metrics format
        hourly_data = analytics.get('hourly_analysis', {})
        runway_metrics = []
        
        # Create runway metrics for each hour
        for hour in range(24):
            if hour in hourly_data:
                data = hourly_data[hour]
                # Calculate realistic utilization for each hour (capped at 100%)
                max_capacity_per_hour = 60  # Maximum flights per hour
                flight_count = data.get('flight_count', 0)
                utilization = min(100, (flight_count / max_capacity_per_hour) * 100)
                
                metric = {
                    "id": f"hour_{hour}",
                    "runway": f"Hour {hour:02d}:00",
                    "utilization": round(utilization, 1),
                    "capacity": max_capacity_per_hour,
                    "delays": round(data.get('Departure_Delay_Minutes', 0), 1),
                    "conflicts": 0,  # Not available in CSV data
                    "timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "flight_count": flight_count
                }
                runway_metrics.append(metric)
            else:
                # Add empty hour with 0 utilization
                metric = {
                    "id": f"hour_{hour}",
                    "runway": f"Hour {hour:02d}:00",
                    "utilization": 0.0,
                    "capacity": 60,
                    "delays": 0.0,
                    "conflicts": 0,
                    "timestamp": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "flight_count": 0
                }
                runway_metrics.append(metric)
        
        # Apply filters
        if runway:
            runway_metrics = [r for r in runway_metrics if runway.lower() in r['runway'].lower()]
        
        # Apply pagination
        total_metrics = len(runway_metrics)
        runway_metrics = runway_metrics[skip:skip + limit]
        
        return runway_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching runway metrics: {str(e)}")

@router.get("/status/current", response_model=List[Dict[str, Any]])
async def get_current_runway_status(db: Session = Depends(get_db)):
    """Get current status of all runways"""
    try:
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return []
        
        current_hour = datetime.now().hour
        hourly_data = analytics.get('hourly_analysis', {})
        
        if current_hour in hourly_data:
            current_data = hourly_data[current_hour]
            return [{
                "runway": f"Current Hour ({current_hour}:00)",
                "flight_count": current_data.get('flight_count', 0),
                "avg_departure_delay": current_data.get('Departure_Delay_Minutes', 0),
                "avg_arrival_delay": current_data.get('Arrival_Delay_Minutes', 0),
                "utilization_percentage": min(100, (current_data.get('flight_count', 0) / 50) * 100)
            }]
        
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching current runway status: {str(e)}")

@router.get("/statistics/overview", response_model=Dict[str, Any])
async def get_runway_statistics(db: Session = Depends(get_db)):
    """Get comprehensive runway statistics"""
    try:
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return {}
        
        hourly_data = analytics.get('hourly_analysis', {})
        daily_data = analytics.get('daily_analysis', {})
        
        # Calculate runway utilization statistics
        total_flights = sum(data.get('flight_count', 0) for data in hourly_data.values())
        avg_delays = sum(data.get('Departure_Delay_Minutes', 0) for data in hourly_data.values()) / len(hourly_data) if hourly_data else 0
        
        # Calculate average utilization
        max_capacity_per_hour = 60
        total_utilization = 0
        hours_with_flights = 0
        
        for data in hourly_data.values():
            flight_count = data.get('flight_count', 0)
            if flight_count > 0:
                utilization = min(100, (flight_count / max_capacity_per_hour) * 100)
                total_utilization += utilization
                hours_with_flights += 1
        
        average_utilization = total_utilization / hours_with_flights if hours_with_flights > 0 else 0
        
        # Find peak hours
        peak_hours = analytics.get('peak_hours', {})
        peak_hour_info = [f"{hour}:00 ({data.get('flight_count', 0)} flights)" for hour, data in peak_hours.items()]
        
        return {
            "total_flights": total_flights,
            "average_delays": round(avg_delays, 1),
            "average_utilization": round(average_utilization, 1),
            "peak_hours": peak_hour_info,
            "total_flights_today": analytics.get('total_flights_today', 0),
            "avg_delays_today": analytics.get('avg_delays_today', 0),
            "hourly_distribution": hourly_data,
            "daily_distribution": daily_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching runway statistics: {str(e)}")

@router.get("/optimization/recommendations", response_model=Dict[str, Any])
async def get_optimization_recommendations(db: Session = Depends(get_db)):
    """Get AI optimization recommendations"""
    try:
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return {
                "analysis": "No runway data available for analysis",
                "recommendations": [],
                "efficiency_score": 0,
                "bottlenecks": []
            }
        
        hourly_data = analytics.get('hourly_analysis', {})
        peak_hours = analytics.get('peak_hours', {})
        
        # Analyze bottlenecks
        bottlenecks = []
        if len(peak_hours) > 3:
            bottlenecks.append("Multiple peak hours detected - consider flight redistribution")
        
        # Calculate efficiency score
        total_delays = sum(data.get('Departure_Delay_Minutes', 0) for data in hourly_data.values())
        total_flights = sum(data.get('flight_count', 0) for data in hourly_data.values())
        
        if total_flights > 0:
            delay_ratio = total_delays / total_flights
            efficiency_score = max(0, 100 - (delay_ratio * 10))  # Convert delay ratio to 0-100 score
        else:
            efficiency_score = 100
        
        # Generate recommendations
        recommendations = []
        
        if efficiency_score < 70:
            recommendations.append({
                "type": "immediate",
                "action": "Review and optimize flight scheduling during peak hours",
                "impact": "Reduce delays and improve on-time performance",
                "priority": "high"
            })
        
        if len(peak_hours) > 2:
            recommendations.append({
                "type": "strategic",
                "action": "Implement flight time spreading to reduce congestion",
                "impact": "Better runway utilization and reduced conflicts",
                "priority": "medium"
            })
        
        if total_delays > 100:
            recommendations.append({
                "type": "immediate",
                "action": "Investigate causes of frequent delays",
                "impact": "Identify and resolve systemic issues",
                "priority": "high"
            })
        
        return {
            "analysis": f"Current runway efficiency score: {efficiency_score:.1f}%. Analysis based on {total_flights} flights with {total_delays:.1f} total delay minutes.",
            "recommendations": recommendations,
            "efficiency_score": efficiency_score,
            "bottlenecks": bottlenecks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating optimization recommendations: {str(e)}")

@router.get("/{runway}/trends", response_model=List[Dict[str, Any]])
async def get_runway_utilization_trends(
    runway: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get utilization trends for a specific runway"""
    try:
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return []
        
        hourly_data = analytics.get('hourly_analysis', {})
        
        # Convert to trend format
        trends = []
        for hour, data in hourly_data.items():
            trends.append({
                "hour": hour,
                "flight_count": data.get('flight_count', 0),
                "utilization_percentage": min(100, (data.get('flight_count', 0) / 50) * 100),
                "avg_delays": data.get('Departure_Delay_Minutes', 0)
            })
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching runway trends: {str(e)}")

@router.get("/{runway}/peak-hours", response_model=List[Dict[str, Any]])
async def get_peak_hours_analysis(
    runway: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Analyze peak hours for a specific runway"""
    try:
        analytics = data_service.get_runway_analytics()
        
        if not analytics:
            return []
        
        peak_hours = analytics.get('peak_hours', {})
        
        # Convert to peak hours format
        peak_analysis = []
        for hour, data in peak_hours.items():
            peak_analysis.append({
                "hour": hour,
                "flight_count": data.get('flight_count', 0),
                "avg_departure_delay": data.get('Departure_Delay_Minutes', 0),
                "avg_arrival_delay": data.get('Arrival_Delay_Minutes', 0),
                "congestion_level": "high" if data.get('flight_count', 0) > 40 else "medium" if data.get('flight_count', 0) > 25 else "low"
            })
        
        return peak_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching peak hours analysis: {str(e)}")
