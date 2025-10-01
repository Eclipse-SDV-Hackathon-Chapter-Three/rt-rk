#!/usr/bin/env python3
"""
Test script for lane warning integration
This script publishes LEFT/RIGHT lane warnings to the Zenoh topic
to test the dashboard lane assist integration.
"""

import zenoh
import json
import time
import random
from datetime import datetime

def test_lane_warnings():
    """Test publishing lane warning data to Zenoh topic"""
    try:
        print("🔄 Connecting to Zenoh...")
        
        # Configure Zenoh connection (same as dashboard)
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        # Define the lane warning topic
        lane_topic = "carla/tesla/warnings/lane"
        
        print(f"📡 Publishing to topic: {lane_topic}")
        print("🛣️  Simulating lane departure warnings...")
        print("Press Ctrl+C to stop\n")
        
        while True:
            # Generate random scenario
            scenario = random.choice(["left_drift", "right_drift", "clear", "wait"])
            
            if scenario == "left_drift":
                print(f"⬅️  Publishing lane warning: LEFT (vehicle approaching left line)")
                session.put(lane_topic, "LEFT")
                
                # Keep warning for 2-4 seconds
                time.sleep(random.uniform(2, 4))
                
                # Clear warning
                print(f"✅ Clearing lane warning")
                session.put(lane_topic, "")
                
                # Wait before next potential warning
                time.sleep(random.uniform(3, 8))
                
            elif scenario == "right_drift":
                print(f"➡️  Publishing lane warning: RIGHT (vehicle approaching right line)")
                session.put(lane_topic, "RIGHT")
                
                # Keep warning for 2-4 seconds
                time.sleep(random.uniform(2, 4))
                
                # Clear warning
                print(f"✅ Clearing lane warning")
                session.put(lane_topic, "")
                
                # Wait before next potential warning
                time.sleep(random.uniform(3, 8))
                
            elif scenario == "clear":
                # Explicitly clear any warnings
                print(f"✅ Ensuring no lane warnings")
                session.put(lane_topic, "")
                time.sleep(random.uniform(2, 5))
                
            else:  # wait
                print("🛣️  Vehicle in center of lane")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping lane warning test...")
    except Exception as e:
        print(f"❌ Error in lane warning test: {e}")
    finally:
        if 'session' in locals():
            session.close()

def test_specific_scenarios():
    """Test with specific lane warning scenarios"""
    try:
        print("🔄 Connecting to Zenoh for specific scenario test...")
        
        # Configure Zenoh connection
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        lane_topic = "carla/tesla/warnings/lane"
        
        print(f"📡 Testing specific scenarios on topic: {lane_topic}")
        
        scenarios = [
            ("LEFT", "Vehicle drifting towards left lane"),
            ("RIGHT", "Vehicle drifting towards right lane"),
            ("LEFT", "Another left lane warning"),
            ("RIGHT", "Another right lane warning")
        ]
        
        for direction, description in scenarios:
            print(f"🛣️  Testing: {description}")
            session.put(lane_topic, direction)
            time.sleep(3)
            
            print(f"✅ Clearing lane warning")
            session.put(lane_topic, "")
            time.sleep(2)
            
        print("✅ Specific scenario test completed")
        
    except Exception as e:
        print(f"❌ Error in specific scenario test: {e}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    print("=================================")
    print("     Lane Warning Test")
    print("=================================")
    print("This script publishes lane warnings to Zenoh")
    print("Make sure the dashboard is running to see the warnings")
    print("")
    
    print("Choose test mode:")
    print("1. Random simulation (default)")
    print("2. Specific scenarios test")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        if choice == "2":
            test_specific_scenarios()
        else:
            test_lane_warnings()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")