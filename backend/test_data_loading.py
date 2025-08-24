#!/usr/bin/env python3
"""
Test script to verify data service can load flight_data.csv
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from services.data_service import data_service
    
    print("=== Data Service Test ===")
    print(f"Data loaded: {not data_service.data.empty}")
    
    if not data_service.data.empty:
        print(f"Total flights: {len(data_service.data)}")
        print(f"Columns: {list(data_service.data.columns)}")
        print(f"Date range: {data_service.data['Date'].min()} to {data_service.data['Date'].max()}")
        print(f"Total routes: {data_service.data['Route'].nunique()}")
        print(f"Sample flight: {data_service.data.iloc[0].to_dict()}")
        
        # Test statistics
        stats = data_service.get_flight_statistics()
        print(f"\nFlight Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test runway analytics
        analytics = data_service.get_runway_analytics()
        print(f"\nRunway Analytics:")
        print(f"  Hourly analysis keys: {list(analytics.get('hourly_analysis', {}).keys())}")
        print(f"  Utilization metrics: {analytics.get('utilization_metrics', {})}")
        
        # Test alerts
        alerts = data_service.get_alerts()
        print(f"\nAlerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"  {alert['type']}: {alert['title']}")
            
    else:
        print("No data loaded!")
        print(f"CSV path tried: {data_service.csv_path}")
        print(f"Current working directory: {os.getcwd()}")
        
except Exception as e:
    print(f"Error testing data service: {e}")
    import traceback
    traceback.print_exc()
