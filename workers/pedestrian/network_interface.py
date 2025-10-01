"""
Network interface module for pedestrian worker.
Handles communication with other system components.
"""
import zenoh
import json
import base64
import numpy as np
import time
from typing import Optional


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
            
            print(f"📷 Camera frame received: {shape}, {dtype}, time: {timestamp}")
            
            # Decode base64 image data
            frame_bytes = base64.b64decode(data['data'])
            frame_array = np.frombuffer(frame_bytes, dtype=dtype).reshape(shape)
            
            # Store the latest frame
            self.latest_frame = frame_array
            self.frame_shape = shape
            self.frame_dtype = dtype
            self.last_update_time = time.time()
            
        except Exception as e:
            print(f"Error processing camera data: {e}")
    
    def connect(self):
        """Connect to Zenoh and setup subscriber."""
        if self.connected:
            return
            
        try:
            print("🔄 Connecting to Zenoh...")
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
            
            self.session = zenoh.open(zenoh_config)
            print("✅ Connected to Zenoh")
            
            # Subscribe to camera frames
            base_topic = 'carla/tesla'
            camera_topic = f"{base_topic}/camera/frame"
            self.subscriber = self.session.declare_subscriber(camera_topic, self.camera_handler)
            
            print(f"📡 Subscribed to: {camera_topic}")
            self.connected = True
            
        except Exception as e:
            print(f"Error connecting to Zenoh: {e}")
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
            print("🔌 Disconnected from Zenoh")


# Global camera subscriber instance
_camera_subscriber = ZenohCameraSubscriber()


def receive_frame():
    """
    Function for receiving video frames over network.
    Returns the latest camera frame as numpy array.
    
    Returns:
        np.ndarray: Latest camera frame or None if no recent frame available
    """
    return _camera_subscriber.get_latest_frame()


def send_warning_data(warning_message):
    """
    Function for sending pedestrian warning data over network.
    Sends pedestrian detection warnings to dashboard via Zenoh.
    
    Args:
        warning_message (str): Warning message for pedestrian detection ("LEFT", "RIGHT", or "" to clear)
    """
    try:
        # Get or create Zenoh session from camera subscriber
        if not _camera_subscriber.connected:
            _camera_subscriber.connect()
        
        session = _camera_subscriber.session
        if not session:
            print("❌ No Zenoh session available for pedestrian warnings")
            return
        
        # Define the pedestrian warning topic (same as test script)
        pedestrian_topic = "carla/tesla/warnings/pedestrian"
        
        # Send pedestrian warning
        if warning_message:
            print(f"🚨 Sending pedestrian warning: {warning_message}")
            session.put(pedestrian_topic, warning_message)
        else:
            # Clear warning if empty message
            print(f"✅ Clearing pedestrian warning")
            
    except Exception as e:
        print(f"❌ Error sending pedestrian warning data: {e}")
