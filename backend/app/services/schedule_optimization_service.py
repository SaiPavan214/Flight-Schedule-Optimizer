import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from ..services.data_service import data_service

class ScheduleOptimizationService:
    def __init__(self):
        self.data_service = data_service
    
    def find_optimal_takeoff_landing_times(self, airport_code: str = "BOM") -> Dict[str, Any]:
        """
        Find the best times for takeoff/landing to minimize delays
        """
        if self.data_service.data.empty:
            return {}
        
        # Filter data for the specific airport
        airport_data = self.data_service.data[
            self.data_service.data['Route'].str.contains(airport_code, na=False)
        ]
        
        if airport_data.empty:
            return {}
        
        # Analyze delays by hour
        hourly_delays = airport_data.groupby('Hour_of_Day').agg({
            'Departure_Delay_Minutes': 'mean',
            'Arrival_Delay_Minutes': 'mean',
            'Flight_Number': 'count'
        }).rename(columns={'Flight_Number': 'flight_count'})
        
        # Find best times (lowest delays) - get top 3
        best_departure_hours = hourly_delays.nsmallest(3, 'Departure_Delay_Minutes').index.tolist()
        best_arrival_hours = hourly_delays.nsmallest(3, 'Arrival_Delay_Minutes').index.tolist()
        
        # Find worst times (highest delays) - get top 3
        worst_departure_hours = hourly_delays.nlargest(3, 'Departure_Delay_Minutes').index.tolist()
        worst_arrival_hours = hourly_delays.nlargest(3, 'Arrival_Delay_Minutes').index.tolist()
        
        return {
            "optimal_times": {
                "best_departure_hours": [int(hour) for hour in best_departure_hours],
                "best_arrival_hours": [int(hour) for hour in best_arrival_hours],
                "worst_departure_hours": [int(hour) for hour in worst_departure_hours],
                "worst_arrival_hours": [int(hour) for hour in worst_arrival_hours]
            },
            "hourly_analysis": hourly_delays.to_dict(orient='index'),
            "recommendations": [
                f"Schedule departures around {best_departure_hours[0]:02d}:00 for minimal delays",
                f"Schedule arrivals around {best_arrival_hours[0]:02d}:00 for minimal delays",
                f"Avoid departures around {worst_departure_hours[0]:02d}:00 due to high delays",
                f"Avoid arrivals around {worst_arrival_hours[0]:02d}:00 due to high delays"
            ]
        }
    
    def identify_busy_time_slots(self, airport_code: str = "BOM") -> Dict[str, Any]:
        """
        Identify the busiest time slots to avoid for scheduling
        """
        if self.data_service.data.empty:
            return {}
        
        # Filter data for the specific airport
        airport_data = self.data_service.data[
            self.data_service.data['Route'].str.contains(airport_code, na=False)
        ]
        
        if airport_data.empty:
            return {}
        
        # Analyze traffic by hour
        hourly_traffic = airport_data.groupby('Hour_of_Day').agg({
            'Flight_Number': 'count',
            'Departure_Delay_Minutes': 'mean',
            'Arrival_Delay_Minutes': 'mean'
        }).rename(columns={'Flight_Number': 'flight_count'})
        
        # Calculate congestion score (traffic + delays)
        hourly_traffic['congestion_score'] = (
            hourly_traffic['flight_count'] * 0.6 + 
            hourly_traffic['Departure_Delay_Minutes'] * 0.4
        )
        
        # Find peak hours (top 25% congestion)
        peak_threshold = hourly_traffic['congestion_score'].quantile(0.75)
        peak_hours = hourly_traffic[hourly_traffic['congestion_score'] >= peak_threshold]
        
        # Find quiet hours (bottom 25% congestion)
        quiet_threshold = hourly_traffic['congestion_score'].quantile(0.25)
        quiet_hours = hourly_traffic[hourly_traffic['congestion_score'] <= quiet_threshold]
        
        # Create congestion score dictionary for all 24 hours
        congestion_score = {}
        for hour in range(24):
            if hour in hourly_traffic.index:
                congestion_score[hour] = hourly_traffic.loc[hour, 'congestion_score']
            else:
                congestion_score[hour] = 0.0
        
        return {
            "busy_time_slots": {
                "peak_hours": [int(hour) for hour in peak_hours.index],
                "quiet_hours": [int(hour) for hour in quiet_hours.index],
                "congestion_score": congestion_score,
                "recommendations": [
                    f"Peak hours to avoid: {', '.join([f'{int(hour):02d}:00' for hour in peak_hours.index])}",
                    f"Quiet hours for scheduling: {', '.join([f'{int(hour):02d}:00' for hour in quiet_hours.index])}",
                    "Schedule flights during quiet hours to minimize delays and congestion"
                ]
            }
        }
    
    def optimize_flight_schedule(self, flight_number: str, new_departure_time: str) -> Dict[str, Any]:
        """
        Model to tune schedule time for a flight and see impact on delays
        """
        if self.data_service.data.empty:
            return {}
        
        # Find the flight
        flight_data = self.data_service.data[
            self.data_service.data['Flight_Number'] == flight_number
        ]
        
        if flight_data.empty:
            return {"error": f"Flight {flight_number} not found"}
        
        # Get current delay patterns
        current_delays = flight_data['Departure_Delay_Minutes'].mean()
        current_hour = flight_data['Hour_of_Day'].iloc[0]
        
        # Parse new departure time
        try:
            new_hour = int(new_departure_time.split(':')[0])
        except:
            return {"error": "Invalid time format. Use HH:MM"}
        
        # Analyze delays at the new time slot
        new_time_delays = self.data_service.data[
            self.data_service.data['Hour_of_Day'] == new_hour
        ]['Departure_Delay_Minutes'].mean()
        
        # Calculate impact
        delay_improvement = current_delays - new_time_delays
        
        # Check runway capacity at new time
        new_time_capacity = len(self.data_service.data[
            self.data_service.data['Hour_of_Day'] == new_hour
        ])
        
        return {
            "flight_number": flight_number,
            "current_schedule": {
                "hour": int(current_hour),
                "avg_delay": round(current_delays, 1),
                "time_slot": f"{int(current_hour):02d}:00"
            },
            "proposed_schedule": {
                "hour": new_hour,
                "avg_delay": round(new_time_delays, 1),
                "time_slot": f"{new_hour:02d}:00"
            },
            "impact_analysis": {
                "delay_improvement": round(delay_improvement, 1),
                "runway_capacity_at_new_time": new_time_capacity,
                "recommendation": "Schedule change recommended" if delay_improvement > 0 else "Keep current schedule"
            }
        }
    
    def analyze_cascading_delays(self, min_cascade_impact: int = 30) -> Dict[str, Any]:
        """
        Model to isolate flights with biggest cascading impact on schedule delays
        """
        if self.data_service.data.empty:
            return {}
        
        # Group flights by route and time proximity
        cascading_analysis = []
        
        # Analyze each route
        for route in self.data_service.data['Route'].unique():
            route_data = self.data_service.data[
                self.data_service.data['Route'] == route
            ].sort_values('STD_DateTime')
            
            if len(route_data) < 2:
                continue
            
            # Calculate cascading impact
            for i in range(len(route_data) - 1):
                current_flight = route_data.iloc[i]
                next_flight = route_data.iloc[i + 1]
                
                # Calculate time gap between flights
                time_gap = (next_flight['STD_DateTime'] - current_flight['STD_DateTime']).total_seconds() / 60
                
                # Calculate cascading impact
                if current_flight['Departure_Delay_Minutes'] > 0 and time_gap < 120:  # 2 hours
                    cascade_impact = current_flight['Departure_Delay_Minutes'] * (120 - time_gap) / 120
                    
                    if cascade_impact >= min_cascade_impact:
                        cascading_analysis.append({
                            "route": route,
                            "flight_number": current_flight['Flight_Number'],
                            "date": current_flight['Date'],
                            "delay_minutes": current_flight['Departure_Delay_Minutes'],
                            "time_gap_minutes": time_gap,
                            "cascade_impact": round(cascade_impact, 1),
                            "next_flight": next_flight['Flight_Number'],
                            "next_flight_time": next_flight['STD_DateTime']
                        })
        
        # Sort by cascade impact
        cascading_analysis.sort(key=lambda x: x['cascade_impact'], reverse=True)
        
        return {
            "high_impact_flights": cascading_analysis[:20],  # Top 20
            "total_cascading_flights": len(cascading_analysis),
            "recommendations": [
                "Increase buffer time between flights on high-impact routes",
                "Prioritize on-time departure for flights with high cascade potential",
                "Consider alternative scheduling for routes with frequent cascading delays"
            ]
        }
    
    def get_runway_capacity_analysis(self, airport_code: str = "BOM") -> Dict[str, Any]:
        """
        Analyze runway capacity constraints and optimization opportunities
        """
        if self.data_service.data.empty:
            return {}
        
        # Filter data for the specific airport
        airport_data = self.data_service.data[
            self.data_service.data['Route'].str.contains(airport_code, na=False)
        ]
        
        if airport_data.empty:
            return {}
        
        # Analyze capacity by hour
        hourly_capacity = airport_data.groupby('Hour_of_Day').agg({
            'Flight_Number': 'count',
            'Departure_Delay_Minutes': 'mean'
        }).rename(columns={'Flight_Number': 'flight_count'})
        
        # Calculate capacity utilization
        max_capacity_per_hour = 60  # Maximum flights per hour
        hourly_capacity['utilization_percent'] = (hourly_capacity['flight_count'] / max_capacity_per_hour) * 100
        
        # Identify bottlenecks
        bottlenecks = hourly_capacity[hourly_capacity['utilization_percent'] > 80]
        underutilized = hourly_capacity[hourly_capacity['utilization_percent'] < 40]
        
        # Convert to frontend-expected format
        bottlenecks_list = []
        for hour, row in bottlenecks.iterrows():
            bottlenecks_list.append({
                "hour": int(hour),
                "utilization": round(row['utilization_percent'], 1),
                "flight_count": int(row['flight_count'])
            })
        
        underutilized_list = []
        for hour, row in underutilized.iterrows():
            underutilized_list.append({
                "hour": int(hour),
                "utilization": round(row['utilization_percent'], 1),
                "flight_count": int(row['flight_count'])
            })
        
        return {
            "bottlenecks": bottlenecks_list,
            "underutilized_slots": underutilized_list,
            "optimization_opportunities": [
                f"Redistribute flights from bottleneck hours: {', '.join([f'{int(hour):02d}:00' for hour in bottlenecks.index])}",
                f"Utilize underutilized slots: {', '.join([f'{int(hour):02d}:00' for hour in underutilized.index])}",
                "Implement dynamic scheduling based on real-time capacity"
            ]
        }

# Global instance
schedule_optimization_service = ScheduleOptimizationService()
