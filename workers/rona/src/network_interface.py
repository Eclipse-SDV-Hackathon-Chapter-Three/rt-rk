"""
Network interface module for RONA (Recorder Of Network Accidents) worker.
Handles communication with other system components for accident recording.
"""

import zenoh
import json
import base64
import numpy as np
import time
from typing import Optional, Dict, Any


class ZenohCameraSubscriber:
    """Zenoh subscriber for camera frame data."""
    
    def __init__(self):
        self.session = None
        self.subscriber = None
        self.latest_frame = None
        self.frame_shape = None
        self.frame_dtype = None
        self.last_update_time = 0
        self.connected = False
        
    def decode_zenoh_payload(self, payload):
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
    
    def camera_handler(self, sample):
        """Handler for camera frame messages."""
        try:
            payload_str = self.decode_zenoh_payload(sample.payload)
            data = json.loads(payload_str)
            timestamp = data['timestamp']
            shape = tuple(data['shape'])
            dtype = data['dtype']
            
            print(f"📷 RONA: Camera frame received: {shape}, {dtype}, time: {timestamp}")
            
            # Decode base64 image data
            frame_bytes = base64.b64decode(data['data'])
            frame_array = np.frombuffer(frame_bytes, dtype=dtype).reshape(shape)
            
            # Store the latest frame
            self.latest_frame = frame_array
            self.frame_shape = shape
            self.frame_dtype = dtype
            self.last_update_time = time.time()
            
        except Exception as e:
            print(f"❌ RONA: Error processing camera data: {e}")
    
    def connect(self):
        """Connect to Zenoh and setup subscriber."""
        if self.connected:
            return
            
        try:
            print("🔄 RONA: Connecting to Zenoh...")
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
            
            self.session = zenoh.open(zenoh_config)
            print("✅ RONA: Connected to Zenoh")
            
            # Subscribe to camera frames
            base_topic = 'carla/tesla'
            camera_topic = f"{base_topic}/camera/frame"
            self.subscriber = self.session.declare_subscriber(camera_topic, self.camera_handler)
            
            print(f"📡 RONA: Subscribed to: {camera_topic}")
            self.connected = True
            
        except Exception as e:
            print(f"❌ RONA: Error connecting to Zenoh: {e}")
            self.connected = False
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest camera frame if available and recent."""
        if not self.connected:
            self.connect()
            
        # Check if data is recent (within last 2 seconds)
        current_time = time.time()
        if current_time - self.last_update_time > 2.0:
            return None
            
        return self.latest_frame
    
    def disconnect(self):
        """Disconnect from Zenoh."""
        if self.session:
            self.session.close()
            self.session = None
            self.subscriber = None
            self.connected = False
            print("🔌 RONA: Disconnected from Zenoh")


class ZenohObstacleSubscriber:
    """Zenoh subscriber for obstacle/collision sensor data."""
    
    def __init__(self):
        self.session = None
        self.subscriber = None
        self.obstacle_distance = None
        self.collision_detected = False
        self.last_update_time = 0
        self.connected = False
        
    def decode_zenoh_payload(self, payload):
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
    
    def obstacle_handler(self, sample):
        """Handler for obstacle distance messages."""
        try:
            payload_str = self.decode_zenoh_payload(sample.payload)
            data = json.loads(payload_str)
            distance = data['distance_meters']
            status = data['status']
            timestamp = data['timestamp']
            
            if status == 'detected':
                self.obstacle_distance = distance
                self.last_update_time = time.time()
                
                # Determine if this is close enough to be considered a collision
                # For accident recording, we consider anything < 1 meter as potential collision
                if distance < 1.0:
                    self.collision_detected = True
                    print(f"🚨 RONA: Collision detected! Obstacle at {distance:.1f}m at {timestamp}")
                else:
                    self.collision_detected = False
                    print(f"⚠️  RONA: Obstacle detected: {distance:.1f}m at {timestamp}")
            else:
                self.obstacle_distance = None
                self.collision_detected = False
                self.last_update_time = time.time()
                
        except Exception as e:
            print(f"❌ RONA: Error processing obstacle data: {e}")
    
    def connect(self):
        """Connect to Zenoh and setup subscriber."""
        if self.connected:
            return
            
        try:
            print("🔄 RONA: Connecting to Zenoh for obstacle data...")
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
            
            self.session = zenoh.open(zenoh_config)
            print("✅ RONA: Connected to Zenoh for obstacle data")
            
            # Subscribe to obstacle distance
            base_topic = 'carla/tesla'
            obstacle_topic = f"{base_topic}/sensors/obstacle_distance"
            self.subscriber = self.session.declare_subscriber(obstacle_topic, self.obstacle_handler)
            
            print(f"📡 RONA: Subscribed to: {obstacle_topic}")
            self.connected = True
            
        except Exception as e:
            print(f"❌ RONA: Error connecting to Zenoh for obstacle data: {e}")
            self.connected = False
    
    def get_sensor_data(self) -> Optional[Dict[str, Any]]:
        """Get current obstacle sensor data if available and recent."""
        if not self.connected:
            self.connect()
            
        # Check if data is recent (within last 2 seconds)
        current_time = time.time()
        if current_time - self.last_update_time > 2.0:
            return None
            
        return {
            'obstacle_distance': self.obstacle_distance,
            'collision_detected': self.collision_detected,
            'timestamp': self.last_update_time
        }
    
    def disconnect(self):
        """Disconnect from Zenoh."""
        if self.session:
            self.session.close()
            self.session = None
            self.subscriber = None
            self.connected = False
            print("🔌 RONA: Disconnected from Zenoh obstacle subscriber")


# Global subscriber instances
_camera_subscriber = ZenohCameraSubscriber()
_obstacle_subscriber = ZenohObstacleSubscriber()


def receive_frame_from_network() -> Optional[np.ndarray]:
    """
    Function for receiving video frames over network for accident recording.
    Returns the latest camera frame as numpy array.
    
    Returns:
        np.ndarray: Latest camera frame or None if no recent frame available
    """
    return _camera_subscriber.get_latest_frame()


def receive_obstacle_sensor_data() -> Optional[Dict[str, Any]]:
    """
    Function for receiving obstacle sensor data for collision detection.
    Returns sensor data including collision status.
    
    Returns:
        dict: Sensor data containing obstacle_distance, collision_detected, and timestamp
              or None if no recent data available
    """
    return _obstacle_subscriber.get_sensor_data()


def cleanup_network_connections():
    """
    Cleanup all network connections.
    Should be called during shutdown.
    """
    print("🧹 RONA: Cleaning up network connections...")
    _camera_subscriber.disconnect()
    _obstacle_subscriber.disconnect()
    print("✅ RONA: Network cleanup completed")
