"""
Network interface module for the Emergency Stopping (ES) system.
Contains functions for receiving obstacle data and sending commands.
"""

import zenoh
import json
import time
from typing import Optional


class ZenohObstacleSubscriber:
    """Zenoh subscriber for obstacle distance data."""
    
    def __init__(self):
        self.session = None
        self.subscriber = None
        self.obstacle_distance = None
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
                print(f"⚠️  Obstacle: {distance:.1f}m at {timestamp}")
            else:
                self.obstacle_distance = None
                self.last_update_time = time.time()
                
        except Exception as e:
            print(f"Error processing obstacle data: {e}")
    
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
            
            # Subscribe to obstacle distance
            base_topic = 'carla/tesla'
            obstacle_topic = f"{base_topic}/sensors/obstacle_distance"
            self.subscriber = self.session.declare_subscriber(obstacle_topic, self.obstacle_handler)
            
            print(f"📡 Subscribed to: {obstacle_topic}")
            self.connected = True
            
        except Exception as e:
            print(f"Error connecting to Zenoh: {e}")
            self.connected = False
    
    def get_obstacle_distance(self) -> Optional[float]:
        """Get current obstacle distance if available and recent."""
        if not self.connected:
            self.connect()
            
        # Check if data is recent (within last 2 seconds)
        current_time = time.time()
        if current_time - self.last_update_time > 2.0:
            return None
            
        return self.obstacle_distance
    
    def disconnect(self):
        """Disconnect from Zenoh."""
        if self.session:
            self.session.close()
            self.session = None
            self.subscriber = None
            self.connected = False
            print("🔌 Disconnected from Zenoh")


# Global subscriber instance
_obstacle_subscriber = ZenohObstacleSubscriber()


def receive_obstacle_distance():
    """Returns distance to obstacle in meters or None if no obstacle detected."""
    return _obstacle_subscriber.get_obstacle_distance()


def send_brake_command(brake_value):
    """Sends brake command over network. brake_value: 0.0-1.0"""
    # TODO: Implement brake command sending via Zenoh
    pass


def send_warning_data(warnings, distance):
    """Sends warning data over network."""
    try:
        # Get or create Zenoh session
        if not _obstacle_subscriber.connected:
            _obstacle_subscriber.connect()
        
        session = _obstacle_subscriber.session
        if not session:
            print("❌ No Zenoh session available")
            return
        
        # Define the emergency stop warning topic (same as dashboard expects)
        emergency_topic = "carla/tesla/warnings/emergency_stop"
        
        # Send distance to dashboard - if distance is None or no obstacle, send empty string to clear
        if distance is not None and distance > 0:
            print(f"🚨 Sending emergency stop warning: Obstacle at {distance}m")
            session.put(emergency_topic, str(distance))
        else:
            print(f"✅ Clearing emergency stop warning")
            session.put(emergency_topic, "")
            
    except Exception as e:
        print(f"❌ Error sending warning data: {e}")