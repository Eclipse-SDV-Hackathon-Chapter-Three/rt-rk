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
        print(f"RONA: Camera frame message received")
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


class ZenohCollisionSubscriber:
    """Zenoh subscriber for collision sensor data."""
    
    def __init__(self):
        self.session = None
        self.subscriber = None
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
    
    def collision_handler(self, sample):
        """Handler for collision status messages."""
        try:
            payload_str = self.decode_zenoh_payload(sample.payload)
            data = json.loads(payload_str)
            collision_detected = data['collision_detected']
            timestamp = data['timestamp']
            
            self.collision_detected = collision_detected
            self.last_update_time = time.time()
            
            if collision_detected:
                print(f"🚨 RONA: COLLISION DETECTED at {timestamp}")
            else:
                print(f"✅ RONA: No collision at {timestamp}")
                
        except Exception as e:
            print(f"❌ RONA: Error processing collision data: {e}")
    
    def connect(self):
        """Connect to Zenoh and setup subscriber."""
        if self.connected:
            return
            
        try:
            print("🔄 RONA: Connecting to Zenoh for collision data...")
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
            
            self.session = zenoh.open(zenoh_config)
            print("✅ RONA: Connected to Zenoh for collision data")
            
            # Subscribe to collision status
            base_topic = 'carla/tesla'
            collision_topic = f"{base_topic}/sensors/collision_status"
            self.subscriber = self.session.declare_subscriber(collision_topic, self.collision_handler)
            
            print(f"📡 RONA: Subscribed to: {collision_topic}")
            self.connected = True
            
        except Exception as e:
            print(f"❌ RONA: Error connecting to Zenoh for collision data: {e}")
            self.connected = False
    
    def get_collision_data(self) -> Optional[Dict[str, Any]]:
        """Get current collision sensor data if available and recent."""
        if not self.connected:
            self.connect()
            
        # Check if data is recent (within last 2 seconds)
        current_time = time.time()
        if current_time - self.last_update_time > 2.0:
            return None
            
        return {
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
            print("🔌 RONA: Disconnected from Zenoh collision subscriber")


# Global subscriber instances
_camera_subscriber = ZenohCameraSubscriber()
_collision_subscriber = ZenohCollisionSubscriber()


def receive_frame_from_network() -> Optional[np.ndarray]:
    """
    Function for receiving video frames over network for accident recording.
    Returns the latest camera frame as numpy array.
    
    Returns:
        np.ndarray: Latest camera frame or None if no recent frame available
    """
    return _camera_subscriber.get_latest_frame()


def receive_collision_sensor_data() -> Optional[Dict[str, Any]]:
    """
    Function for receiving collision sensor data for accident detection.
    Returns sensor data including collision status.
    
    Returns:
        dict: Sensor data containing collision_detected and timestamp
              or None if no recent data available
    """
    return _collision_subscriber.get_collision_data()


def cleanup_network_connections():
    """
    Cleanup all network connections.
    Should be called during shutdown.
    """
    print("🧹 RONA: Cleaning up network connections...")
    _camera_subscriber.disconnect()
    _collision_subscriber.disconnect()
    print("✅ RONA: Network cleanup completed")
