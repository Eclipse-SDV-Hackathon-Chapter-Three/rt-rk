#!/usr/bin/env python3
"""
Zenoh Subscriber Example for CARLA Data
=======================================

This script demonstrates how to receive CARLA vehicle data published
through Zenoh messaging system.
"""

import zenoh
import json
import base64
import numpy as np
import time


def decode_zenoh_payload(payload):
    """
    Helper function to decode Zenoh payload that handles both ZBytes and string payloads.
    
    Args:
        payload: Zenoh payload (could be ZBytes or string)
        
    Returns:
        str: Decoded string payload
    """
    try:
        if hasattr(payload, 'to_bytes'):
            # Handle ZBytes (newer Zenoh versions)
            return payload.to_bytes().decode('utf-8')
        elif hasattr(payload, 'decode'):
            # Handle string payload (older Zenoh versions)
            return payload.decode('utf-8')
        else:
            # Handle already decoded string
            return str(payload)
    except Exception as e:
        raise ValueError(f"Failed to decode Zenoh payload: {e}")


def main():
    """Main function to receive CARLA data via Zenoh."""
    print("🔄 Connecting to Zenoh...")
    zenoh_config = zenoh.Config()
    zenoh_config.insert_json5("mode", json.dumps("peer"))
    zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
    with zenoh.open(zenoh_config) as session:
        print("✅ Connected to Zenoh")
        
        # Subscribe to camera frames
        def camera_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                timestamp = data['timestamp']
                shape = tuple(data['shape'])
                dtype = data['dtype']
                
                print(f"📷 Camera frame received: {shape}, {dtype}, time: {timestamp}")
                
                # Decode base64 image data
                frame_bytes = base64.b64decode(data['data'])
                frame_array = np.frombuffer(frame_bytes, dtype=dtype).reshape(shape)
                
                # Here you could save or process the image
                # cv2.imshow('CARLA Camera', frame_array)
                
            except Exception as e:
                print(f"Error processing camera data: {e}")
        
        # Subscribe to obstacle distance
        def obstacle_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                distance = data['distance_meters']
                status = data['status']
                timestamp = data['timestamp']
                
                if status == 'detected':
                    print(f"⚠️  Obstacle: {distance:.1f}m at {timestamp}")
                
            except Exception as e:
                print(f"Error processing obstacle data: {e}")
        
        # Subscribe to collision status
        def collision_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                collision_detected = data['collision_detected']
                timestamp = data['timestamp']
                
                if collision_detected:
                    print(f"💥 COLLISION DETECTED at {timestamp}")
                
            except Exception as e:
                print(f"Error processing collision data: {e}")
        
        # Subscribe to vehicle speed
        def speed_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                speed_kmh = data['speed_kmh']
                timestamp = data['timestamp']
                
                print(f"🚗 Speed: {speed_kmh:.1f} km/h at {timestamp}")
                
            except Exception as e:
                print(f"Error processing speed data: {e}")
        
        # Subscribe to vehicle RPM
        def rpm_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                rpm = data['rpm']
                engine_load = data['engine_load']
                timestamp = data['timestamp']
                
                print(f"🔧 RPM: {rpm:.0f}, Load: {engine_load:.1f}% at {timestamp}")
                
            except Exception as e:
                print(f"Error processing RPM data: {e}")
        
        # Subscribe to vehicle telemetry
        def telemetry_handler(sample):
            try:
                payload_str = decode_zenoh_payload(sample.payload)
                data = json.loads(payload_str)
                speed = data['speed_kmh']
                throttle = data['throttle']
                brake = data['brake']
                steer = data['steer']
                
                print(f"📊 Telemetry - Speed: {speed:.1f}km/h, "
                      f"Throttle: {throttle:.2f}, Brake: {brake:.2f}, Steer: {steer:.2f}")
                
            except Exception as e:
                print(f"Error processing telemetry data: {e}")
        
        # Declare subscribers
        base_topic = 'carla/tesla'
        
        camera_sub = session.declare_subscriber(f"{base_topic}/camera/frame", camera_handler)
        obstacle_sub = session.declare_subscriber(f"{base_topic}/sensors/obstacle_distance", obstacle_handler)
        collision_sub = session.declare_subscriber(f"{base_topic}/sensors/collision_status", collision_handler)
        speed_sub = session.declare_subscriber(f"{base_topic}/dynamics/speed", speed_handler)
        rpm_sub = session.declare_subscriber(f"{base_topic}/dynamics/rpm", rpm_handler)
        telemetry_sub = session.declare_subscriber(f"{base_topic}/telemetry/full", telemetry_handler)
        
        print("📡 Subscribed to all CARLA topics:")
        print(f"   📷 Camera: {base_topic}/camera/frame")
        print(f"   🚧 Obstacle: {base_topic}/sensors/obstacle_distance")
        print(f"   💥 Collision: {base_topic}/sensors/collision_status")
        print(f"   🚗 Speed: {base_topic}/dynamics/speed")
        print(f"   🔧 RPM: {base_topic}/dynamics/rpm")
        print(f"   📊 Telemetry: {base_topic}/telemetry/full")
        print("\n🔄 Listening for data... (Press Ctrl+C to exit)")
        
        try:
            # Keep listening
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Subscriber shutting down...")


if __name__ == "__main__":
    main()