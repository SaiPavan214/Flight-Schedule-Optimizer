#!/usr/bin/env python3
"""
Test script for Schedule Optimization Service
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.app.services.schedule_optimization_service import schedule_optimization_service
    print("✅ Schedule optimization service imported successfully")
    
    # Test optimal times
    print("\n🔍 Testing optimal times for BOM airport...")
    optimal_times = schedule_optimization_service.find_optimal_takeoff_landing_times("BOM")
    print(f"Optimal times: {optimal_times}")
    
    # Test busy time slots
    print("\n🔍 Testing busy time slots for BOM airport...")
    busy_slots = schedule_optimization_service.identify_busy_time_slots("BOM")
    print(f"Busy time slots: {busy_slots}")
    
    # Test cascading delays
    print("\n🔍 Testing cascading delays analysis...")
    cascading = schedule_optimization_service.analyze_cascading_delays()
    print(f"Cascading delays: {cascading}")
    
    # Test runway capacity
    print("\n🔍 Testing runway capacity analysis...")
    capacity = schedule_optimization_service.get_runway_capacity_analysis("BOM")
    print(f"Runway capacity: {capacity}")
    
    print("\n✅ All tests completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
