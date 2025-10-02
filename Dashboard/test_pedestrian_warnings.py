#!/usr/bin/env python3
"""
Test script for pedestrian warning integration
This script publishes LEFT/RIGHT pedestrian warnings to the Zenoh topic
to test the dashboard integration.
"""

import zenoh
import json
import time
import random
from datetime import datetime

def test_pedestrian_warnings():
    """Test publishing pedestrian warning data to Zenoh topic"""
    try:
        print("🔄 Connecting to Zenoh...")
        
        # Configure Zenoh connection (same as dashboard)
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        # Define the pedestrian warning topic
        pedestrian_topic = "carla/tesla/warnings/pedestrian"
        
        print(f"📡 Publishing to topic: {pedestrian_topic}")
        print("🚶 Simulating pedestrian detections...")
        print("Press Ctrl+C to stop\n")
        
        warning_states = ["LEFT", "RIGHT", "", ""]  # Empty string to clear warnings
        
        while True:
            # Generate random warning or clear
            if random.random() < 0.3:  # 30% chance of warning
                warning = random.choice(["LEFT", "RIGHT"])
                print(f"🚨 Publishing pedestrian warning: {warning}")
                session.put(pedestrian_topic, warning)
                
                # Keep warning for 3 seconds
                time.sleep(3)
                
                # Clear warning
                print(f"✅ Clearing pedestrian warning")
                session.put(pedestrian_topic, "")
                
                # Wait before next potential warning
                time.sleep(random.uniform(5, 10))
            else:
                print("😌 No pedestrian detected")
                time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping pedestrian warning test...")
    except Exception as e:
        print(f"❌ Error in pedestrian warning test: {e}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    print("=================================")
    print("  Pedestrian Warning Test")
    print("=================================")
    print("This script publishes pedestrian warnings to Zenoh")
    print("Make sure the dashboard is running to see the warnings")
    print("")
    
    test_pedestrian_warnings()