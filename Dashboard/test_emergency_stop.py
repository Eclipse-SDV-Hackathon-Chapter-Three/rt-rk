#!/usr/bin/env python3
"""
Test script for emergency stop warning integration
This script publishes distance values (in meters) to the Zenoh topic
to test the dashboard emergency stop integration.
"""

import zenoh
import json
import time
import random
from datetime import datetime

def test_emergency_stop_warnings():
    """Test publishing emergency stop warning data to Zenoh topic"""
    try:
        print("🔄 Connecting to Zenoh...")
        
        # Configure Zenoh connection (same as dashboard)
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        # Define the emergency stop warning topic
        emergency_topic = "carla/tesla/warnings/emergency_stop"
        
        print(f"📡 Publishing to topic: {emergency_topic}")
        print("🚨 Simulating emergency stop warnings...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            # Generate random scenario
            scenario = random.choice(["obstacle", "clear", "wait"])
            
            if scenario == "obstacle":
                # Generate random distance between 5-50 meters
                distance = round(random.uniform(5.0, 50.0), 1)
                print(f"🚨 Publishing emergency stop: Obstacle at {distance}m")
                session.put(emergency_topic, str(distance))
                
                # Keep warning for 3-5 seconds
                time.sleep(random.uniform(3, 5))
                
            elif scenario == "clear":
                # Clear warning
                print(f"✅ Clearing emergency stop warning")
                session.put(emergency_topic, "")
                
                # Wait before next potential warning
                time.sleep(random.uniform(3, 8))
                
            else:  # wait
                print("😌 No emergency situation")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping emergency stop warning test...")
    except Exception as e:
        print(f"❌ Error in emergency stop warning test: {e}")
    finally:
        if 'session' in locals():
            session.close()

def test_specific_distances():
    """Test with specific distance values"""
    try:
        print("🔄 Connecting to Zenoh for specific distance test...")
        
        # Configure Zenoh connection
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        emergency_topic = "carla/tesla/warnings/emergency_stop"
        
        # Test specific distances
        test_distances = [25.5, 15.0, 8.2, 3.1, 45.8]
        
        print(f"📡 Testing specific distances on topic: {emergency_topic}")
        
        for distance in test_distances:
            print(f"🚨 Testing distance: {distance}m")
            session.put(emergency_topic, str(distance))
            time.sleep(3)
            
            print(f"✅ Clearing warning")
            session.put(emergency_topic, "")
            time.sleep(2)
            
        print("✅ Specific distance test completed")
        
    except Exception as e:
        print(f"❌ Error in specific distance test: {e}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    print("=================================")
    print("  Emergency Stop Warning Test")
    print("=================================")
    print("This script publishes emergency stop warnings to Zenoh")
    print("Make sure the dashboard is running to see the warnings")
    print("")
    
    print("Choose test mode:")
    print("1. Random simulation (default)")
    print("2. Specific distances test")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "2":
            test_specific_distances()
        else:
            test_emergency_stop_warnings()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")