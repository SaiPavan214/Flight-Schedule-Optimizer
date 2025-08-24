import pandas as pd
import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

class DataService:
    def __init__(self):
        self.csv_path = "flight_data.csv"
        self.data = None
        self.load_data()
    
    def copy_csv_to_backend(self):
        """Copy the CSV file to the backend directory if it exists in the root"""
        try:
            # Check if CSV exists in root workspace
            root_csv = os.path.join(os.path.dirname(__file__), "..", "..", "..", "flight_data.csv")
            if os.path.exists(root_csv):
                backend_csv = os.path.join(os.path.dirname(__file__), "..", "..", "flight_data.csv")
                shutil.copy2(root_csv, backend_csv)
                print(f"Copied flight_data.csv to backend directory: {backend_csv}")
                return True
        except Exception as e:
            print(f"Error copying CSV file: {e}")
        return False
    
    def load_data(self):
        """Load flight data from CSV file"""
        try:
            # First try to copy the CSV to backend directory
            self.copy_csv_to_backend()
            
            # Try to load from current directory first
            if os.path.exists(self.csv_path):
                self.data = pd.read_csv(self.csv_path)
                print(f"Loaded from current directory: {os.path.abspath(self.csv_path)}")
            else:
                # Try to load from parent directory (root workspace)
                parent_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", self.csv_path)
                if os.path.exists(parent_path):
                    self.data = pd.read_csv(parent_path)
                    print(f"Loaded from root workspace: {parent_path}")
                else:
                    # Try alternative path
                    alt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", self.csv_path)
                    if os.path.exists(alt_path):
                        self.data = pd.read_csv(alt_path)
                        print(f"Loaded from alternative path: {alt_path}")
                    else:
                        print(f"Warning: Could not find {self.csv_path}")
                        print(f"Tried paths: {self.csv_path}, {parent_path}, {alt_path}")
                        self.data = pd.DataFrame()
            
            if not self.data.empty:
                # Convert datetime columns
                datetime_columns = ['STD_DateTime', 'ATD_DateTime', 'STA_DateTime', 'ATA_DateTime']
                for col in datetime_columns:
                    if col in self.data.columns:
                        self.data[col] = pd.to_datetime(self.data[col])
                
                print(f"Successfully loaded {len(self.data)} flight records from {self.csv_path}")
                print(f"Columns: {list(self.data.columns)}")
                print(f"Sample data: {self.data.head(2).to_dict()}")
                
                # Print some basic statistics
                print(f"Date range: {self.data['Date'].min()} to {self.data['Date'].max()}")
                print(f"Total routes: {self.data['Route'].nunique()}")
                print(f"Total airlines: {self.data['Flight_Number'].str[:2].nunique()}")
            else:
                print("No flight data loaded")
        except Exception as e:
            print(f"Error loading flight data: {e}")
            import traceback
            traceback.print_exc()
            self.data = pd.DataFrame()
    
    def get_all_flights(self) -> List[Dict[str, Any]]:
        """Get all flights as a list of dictionaries"""
        if self.data.empty:
            return []
        
        return self.data.to_dict(orient='records')
    
    def get_recent_flights(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get flights from the last N hours"""
        if self.data.empty:
            return []
        
        now = datetime.now()
        cutoff_time = now - timedelta(hours=hours)
        
        recent_data = self.data[self.data['STD_DateTime'] >= cutoff_time]
        return recent_data.to_dict(orient='records')
    
    def get_flights_by_route(self, origin: str = None, destination: str = None) -> List[Dict[str, Any]]:
        """Get flights filtered by route"""
        if self.data.empty:
            return []
        
        filtered_data = self.data.copy()
        
        if origin:
            filtered_data = filtered_data[filtered_data['Route'].str.contains(f"^{origin}-", na=False)]
        
        if destination:
            filtered_data = filtered_data[filtered_data['Route'].str.contains(f"-{destination}$", na=False)]
        
        return filtered_data.to_dict(orient='records')
    
    def get_delayed_flights(self, min_delay: int = 15) -> List[Dict[str, Any]]:
        """Get flights with delays above threshold"""
        if self.data.empty:
            return []
        
        delayed_data = self.data[
            (self.data['Departure_Delay_Minutes'] >= min_delay) | 
            (self.data['Arrival_Delay_Minutes'] >= min_delay)
        ]
        return delayed_data.to_dict(orient='records')
    
    def get_flight_statistics(self) -> Dict[str, Any]:
        """Get comprehensive flight statistics"""
        if self.data.empty:
            return {}
        
        stats = {
            "total_flights": len(self.data),
            "total_delays": len(self.data[self.data['Departure_Delay_Minutes'] > 0]),
            "avg_departure_delay": self.data['Departure_Delay_Minutes'].mean(),
            "avg_arrival_delay": self.data['Arrival_Delay_Minutes'].mean(),
            "avg_flight_duration": self.data['Flight_Duration_Minutes'].mean(),
            "weekend_flights": len(self.data[self.data['Weekend'] == True]),
            "peak_time_flights": len(self.data[self.data['Peak_Time'] == True]),
            "routes": self.data['Route'].value_counts().to_dict(),
            "airlines": self.data['Flight_Number'].str[:2].value_counts().to_dict()
        }
        
        return stats
    
    def get_runway_analytics(self) -> Dict[str, Any]:
        """Get runway utilization and performance analytics"""
        if self.data.empty:
            return {}
        
        # Analyze by hour of day
        hourly_stats = self.data.groupby('Hour_of_Day').agg({
            'Flight_Number': 'count',
            'Departure_Delay_Minutes': 'mean',
            'Arrival_Delay_Minutes': 'mean'
        }).rename(columns={'Flight_Number': 'flight_count'})
        
        # Analyze by day of week
        daily_stats = self.data.groupby('Day_of_Week').agg({
            'Flight_Number': 'count',
            'Departure_Delay_Minutes': 'mean',
            'Arrival_Delay_Minutes': 'mean'
        }).rename(columns={'Flight_Number': 'flight_count'})
        
        # Peak hours analysis
        peak_hours = hourly_stats[hourly_stats['flight_count'] > hourly_stats['flight_count'].quantile(0.75)]
        
        # Calculate realistic runway utilization
        # Assume maximum capacity of 60 flights per hour (1 flight per minute)
        max_capacity_per_hour = 60
        total_flights = len(self.data)
        total_hours = 24  # 24-hour period
        
        # Calculate average utilization across all hours
        avg_flights_per_hour = total_flights / total_hours
        avg_utilization = min(100, (avg_flights_per_hour / max_capacity_per_hour) * 100)
        
        # Calculate peak hour utilization (capped at 100%)
        if not hourly_stats.empty:
            max_flights_in_hour = hourly_stats['flight_count'].max()
            peak_utilization = min(100, (max_flights_in_hour / max_capacity_per_hour) * 100)
        else:
            peak_utilization = 0
        
        return {
            "hourly_analysis": hourly_stats.to_dict(orient='index'),
            "daily_analysis": daily_stats.to_dict(orient='index'),
            "peak_hours": peak_hours.to_dict(orient='index'),
            "total_flights_today": len(self.data[self.data['Date'] == datetime.now().strftime('%Y-%m-%d')]),
            "avg_delays_today": self.data[self.data['Date'] == datetime.now().strftime('%Y-%m-%d')]['Departure_Delay_Minutes'].mean(),
            "utilization_metrics": {
                "average_utilization": round(avg_utilization, 1),
                "peak_utilization": round(peak_utilization, 1),
                "max_capacity_per_hour": max_capacity_per_hour,
                "total_flights": total_flights,
                "avg_flights_per_hour": round(avg_flights_per_hour, 1)
            }
        }
    
    def search_flights_nlp(self, query: str) -> List[Dict[str, Any]]:
        """Search flights using natural language query"""
        if self.data.empty:
            return []
        
        query_lower = query.lower()
        results = []
        
        # Simple keyword-based search
        for _, flight in self.data.iterrows():
            score = 0
            
            # Route matching
            if any(airport in query_lower for airport in flight['Route'].split('-')):
                score += 10
            
            # Flight number matching
            if flight['Flight_Number'].lower() in query_lower:
                score += 8
            
            # Time-based matching
            if 'morning' in query_lower and flight['Hour_of_Day'] < 12:
                score += 5
            elif 'afternoon' in query_lower and 12 <= flight['Hour_of_Day'] < 18:
                score += 5
            elif 'evening' in query_lower and flight['Hour_of_Day'] >= 18:
                score += 5
            
            # Date matching
            if 'today' in query_lower and flight['Date'] == datetime.now().strftime('%Y-%m-%d'):
                score += 7
            elif 'tomorrow' in query_lower and flight['Date'] == (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'):
                score += 7
            
            if score > 0:
                flight_dict = flight.to_dict()
                flight_dict['search_score'] = score
                results.append(flight_dict)
        
        # Sort by relevance score
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results[:20]  # Return top 20 results
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Generate alerts based on flight data"""
        if self.data.empty:
            return []
        
        alerts = []
        
        # Check for significant delays
        significant_delays = self.data[
            (self.data['Departure_Delay_Minutes'] > 30) | 
            (self.data['Arrival_Delay_Minutes'] > 30)
        ]
        
        for _, flight in significant_delays.iterrows():
            if flight['Departure_Delay_Minutes'] > 30:
                alert_type = "critical" if flight['Departure_Delay_Minutes'] > 60 else "warning"
                alerts.append({
                    "id": f"delay_{flight['Flight_Number']}_{flight['Date']}",
                    "type": alert_type,
                    "title": f"Flight {flight['Flight_Number']} Departure Delay",
                    "message": f"Flight {flight['Flight_Number']} from {flight['Route']} is delayed by {flight['Departure_Delay_Minutes']} minutes",
                    "timestamp": flight['STD_DateTime'].isoformat() if pd.notna(flight['STD_DateTime']) else datetime.now().isoformat(),
                    "resolved": False,
                    "severity": alert_type,
                    "category": "delay"
                })
            
            if flight['Arrival_Delay_Minutes'] > 30:
                alert_type = "critical" if flight['Arrival_Delay_Minutes'] > 60 else "warning"
                alerts.append({
                    "id": f"arrival_delay_{flight['Flight_Number']}_{flight['Date']}",
                    "type": alert_type,
                    "title": f"Flight {flight['Flight_Number']} Arrival Delay",
                    "message": f"Flight {flight['Flight_Number']} to {flight['Route']} is delayed by {flight['Arrival_Delay_Minutes']} minutes",
                    "timestamp": flight['STA_DateTime'].isoformat() if pd.notna(flight['STA_DateTime']) else datetime.now().isoformat(),
                    "resolved": False,
                    "severity": alert_type,
                    "category": "delay"
                })
        
        # Check for peak hour congestion
        hourly_flight_counts = self.data.groupby('Hour_of_Day')['Flight_Number'].count()
        peak_hours = hourly_flight_counts[hourly_flight_counts > 20]
        
        for hour, count in peak_hours.items():
            alerts.append({
                "id": f"congestion_{hour}",
                "type": "warning",
                "title": "Peak Hour Congestion",
                "message": f"High traffic volume detected at {int(hour):02d}:00 with {count} flights",
                "timestamp": datetime.now().isoformat(),
                "resolved": False,
                "severity": "warning",
                "category": "congestion"
            })
        
        # Check for runway capacity issues
        max_capacity_per_hour = 60
        for hour, count in hourly_flight_counts.items():
            if count > max_capacity_per_hour * 0.8:  # Over 80% capacity
                alerts.append({
                    "id": f"capacity_{hour}",
                    "type": "critical" if count > max_capacity_per_hour * 0.9 else "warning",
                    "title": "Runway Capacity Warning",
                    "message": f"Runway utilization at {int(hour):02d}:00 is {min(100, (count / max_capacity_per_hour) * 100):.1f}% ({count} flights)",
                    "timestamp": datetime.now().isoformat(),
                    "resolved": False,
                    "severity": "critical" if count > max_capacity_per_hour * 0.9 else "warning",
                    "category": "capacity"
                })
        
        return alerts
    
    def get_chat_response(self, message: str) -> str:
        """Generate intelligent chat responses based on flight data"""
        if self.data.empty:
            return "I don't have access to flight data at the moment. Please try again later."
        
        message_lower = message.lower()
        
        # Flight status queries
        if any(word in message_lower for word in ['status', 'delay', 'on time']):
            delayed_count = len(self.data[self.data['Departure_Delay_Minutes'] > 0])
            total_today = len(self.data[self.data['Date'] == datetime.now().strftime('%Y-%m-%d')])
            if total_today > 0:
                delay_percentage = (delayed_count / total_today) * 100
                return f"Current flight status: {delayed_count} out of {total_today} flights today have delays ({delay_percentage:.1f}%). You can check the Alerts page for specific delay information."
            else:
                return "I don't have flight data for today yet. Please check back later."
        
        # Route queries
        if any(word in message_lower for word in ['route', 'destination', 'origin']):
            routes = self.data['Route'].value_counts().head(5)
            route_info = ", ".join([f"{route} ({count} flights)" for route, count in routes.items()])
            return f"Top 5 busiest routes: {route_info}. You can search for specific routes on the Flight Search page."
        
        # Time-based queries
        if any(word in message_lower for word in ['morning', 'afternoon', 'evening', 'peak']):
            peak_hours = self.data.groupby('Hour_of_Day')['Flight_Number'].count().sort_values(ascending=False).head(3)
            peak_info = ", ".join([f"{hour}:00 ({count} flights)" for hour, count in peak_hours.items()])
            return f"Peak hours with highest flight volume: {peak_info}. Consider this when planning your travel."
        
        # Statistics queries
        if any(word in message_lower for word in ['statistics', 'stats', 'numbers', 'total']):
            stats = self.get_flight_statistics()
            return f"Flight statistics: Total flights: {stats['total_flights']}, Average departure delay: {stats['avg_departure_delay']:.1f} minutes, Weekend flights: {stats['weekend_flights']}, Peak time flights: {stats['peak_time_flights']}."
        
        # General help
        if any(word in message_lower for word in ['help', 'assist', 'what can you do']):
            return "I can help you with flight information, delays, routes, and statistics based on real flight data. Ask me about flight status, delays, routes, peak hours, or general statistics. For detailed information, check the Dashboard, Analytics, or Alerts pages."
        
        # Default response
        return "I can help you with flight information from our database. Try asking about flight status, delays, routes, or statistics. For specific searches, use the Flight Search page."

# Global instance
data_service = DataService()
