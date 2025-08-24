#!/usr/bin/env python3
"""
Database seeding script for Airport Operations API
Populates the database with initial mock data for testing and development
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Flight, Alert, RunwayMetric, FlightStatus, AlertType
from app.database import Base

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        print("🌱 Seeding database...")
        
        # Check if data already exists
        if db.query(Flight).count() > 0:
            print("⚠️  Database already contains data. Skipping seeding.")
            return
        
        # Seed Flights
        print("✈️  Seeding flights...")
        flights_data = [
            {
                "flight_number": "BA123",
                "airline": "British Airways",
                "origin": "LHR",
                "destination": "JFK",
                "departure_time": datetime.now() + timedelta(hours=2),
                "arrival_time": datetime.now() + timedelta(hours=8),
                "status": FlightStatus.ON_TIME,
                "gate": "A12",
                "terminal": "T1",
                "aircraft": "Boeing 777",
                "price": 899.0
            },
            {
                "flight_number": "LH456",
                "airline": "Lufthansa",
                "origin": "FRA",
                "destination": "CDG",
                "departure_time": datetime.now() + timedelta(hours=1),
                "arrival_time": datetime.now() + timedelta(hours=2.5),
                "status": FlightStatus.BOARDING,
                "gate": "B7",
                "terminal": "T2",
                "aircraft": "Airbus A320",
                "price": 245.0
            },
            {
                "flight_number": "AA789",
                "airline": "American Airlines",
                "origin": "LAX",
                "destination": "ORD",
                "departure_time": datetime.now() + timedelta(hours=3),
                "arrival_time": datetime.now() + timedelta(hours=8.5),
                "status": FlightStatus.DELAYED,
                "gate": "C15",
                "terminal": "T3",
                "aircraft": "Boeing 737",
                "price": 456.0
            },
            {
                "flight_number": "EK101",
                "airline": "Emirates",
                "origin": "DXB",
                "destination": "LHR",
                "departure_time": datetime.now() - timedelta(hours=2),
                "arrival_time": datetime.now() + timedelta(hours=2),
                "status": FlightStatus.DEPARTED,
                "gate": "A1",
                "terminal": "T1",
                "aircraft": "Airbus A380",
                "price": 1299.0
            },
            {
                "flight_number": "AF202",
                "airline": "Air France",
                "origin": "CDG",
                "destination": "NRT",
                "departure_time": datetime.now() + timedelta(hours=5),
                "arrival_time": datetime.now() + timedelta(hours=24),
                "status": FlightStatus.ON_TIME,
                "gate": "D8",
                "terminal": "T2",
                "aircraft": "Boeing 787",
                "price": 1150.0
            }
        ]
        
        for flight_data in flights_data:
            flight = Flight(**flight_data)
            db.add(flight)
        
        # Seed Alerts
        print("🚨 Seeding alerts...")
        alerts_data = [
            {
                "type": AlertType.CRITICAL,
                "title": "Runway 27L Closure",
                "message": "Runway 27L is temporarily closed due to maintenance work. Expected reopening at 17:00.",
                "timestamp": datetime.now() - timedelta(minutes=30),
                "resolved": False
            },
            {
                "type": AlertType.WARNING,
                "title": "Weather Advisory",
                "message": "Strong crosswinds expected between 15:00-18:00. Possible flight delays.",
                "timestamp": datetime.now() - timedelta(hours=1),
                "resolved": False
            },
            {
                "type": AlertType.INFO,
                "title": "Ground Services Update",
                "message": "Ground services on standby for Flight AZ123 at Gate B12.",
                "timestamp": datetime.now() - timedelta(minutes=45),
                "resolved": True
            }
        ]
        
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            db.add(alert)
        
        # Seed Runway Metrics
        print("🛫 Seeding runway metrics...")
        runways = ["27L", "27R", "09L", "09R"]
        
        for runway in runways:
            # Create multiple metrics for each runway over the last 24 hours
            for i in range(24):
                timestamp = datetime.now() - timedelta(hours=23-i)
                metric = RunwayMetric(
                    runway=runway,
                    utilization=random.uniform(60, 95),
                    capacity=100,
                    delays=random.randint(0, 20),
                    conflicts=random.randint(0, 5),
                    timestamp=timestamp
                )
                db.add(metric)
        
        # Commit all changes
        db.commit()
        print("✅ Database seeded successfully!")
        print(f"📊 Added {len(flights_data)} flights, {len(alerts_data)} alerts, and {len(runways) * 24} runway metrics")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
