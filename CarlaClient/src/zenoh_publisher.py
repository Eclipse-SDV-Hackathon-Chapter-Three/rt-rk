"""
Zenoh Publisher Module for CARLA
===============================

This module contains the ZenohPublisher class that publishes CARLA vehicle
and sensor data through Zenoh messaging system to separate topics.
"""

import zenoh
import json
import base64
import time
import threading
import logging
from datetime import datetime
import numpy as np


class ZenohPublisher:
    """
    Publishes CARLA vehicle and sensor data through Zenoh messaging system.
    Each data type is published to a separate topic.
    """
    
    def __init__(self, base_topic='carla/vehicle', publish_interval=0.1):
        """
        Initialize Zenoh publisher with base topic and publishing interval.
        
        Args:
            base_topic: Base topic name for all publications
            publish_interval: Publishing interval in seconds (default 100ms)
        """
        self.base_topic = base_topic
        self.publish_interval = publish_interval
        self.session = None
        self.publishers = {}
        self.running = False
        self.publish_thread = None
        self.logger = self._setup_logging()
        
        # Data storage
        self.current_frame = None
        self.obstacle_distance = None
        self.collision_detected = False
        self.collision_data = None
        self.vehicle_speed = 0.0
        self.vehicle_rpm = 0.0
        self.vehicle_data = None
        
        # Topic names
        self.topics = {
            'camera_frame': f"{base_topic}/camera/frame",
            'obstacle_distance': f"{base_topic}/sensors/obstacle_distance",
            'collision_status': f"{base_topic}/sensors/collision_status", 
            'collision_data': f"{base_topic}/sensors/collision_data",
            'vehicle_speed': f"{base_topic}/dynamics/speed",
            'vehicle_rpm': f"{base_topic}/dynamics/rpm",
            'vehicle_telemetry': f"{base_topic}/telemetry/full"
        }
    
    def _setup_logging(self):
        """Setup logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def connect(self):
        """
        Connect to Zenoh session and declare publishers.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            zenoh_config = zenoh.Config()
            zenoh_config.insert_json5("mode", json.dumps("peer"))
            zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
            self.session = zenoh.open(zenoh_config)
            self.logger.info("Zenoh session opened successfully")
            
            # Declare publishers for each topic
            for topic_name, topic_key in self.topics.items():
                publisher = self.session.declare_publisher(topic_key)
                self.publishers[topic_name] = publisher
                self.logger.info(f"Publisher declared for topic: {topic_key}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Zenoh: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Zenoh session."""
        self.stop_publishing()
        
        if self.session:
            self.session.close()
            self.logger.info("Zenoh session closed")
    
    def update_camera_frame(self, frame_array):
        """
        Update camera frame data.
        
        Args:
            frame_array: Numpy array containing camera image
        """
        self.current_frame = frame_array
    
    def update_obstacle_distance(self, obstacle_data):
        """
        Update obstacle sensor data.
        
        Args:
            obstacle_data: Dictionary containing obstacle detection data
        """
        self.obstacle_distance = obstacle_data.get('distance', None)
    
    def update_collision_status(self, collision_data):
        """
        Update collision sensor data.
        
        Args:
            collision_data: Dictionary containing collision data
        """
        self.collision_detected = True
        self.collision_data = collision_data
    
    def update_vehicle_data(self, vehicle):
        """
        Update vehicle dynamics data (speed, RPM).
        
        Args:
            vehicle: CARLA vehicle instance
        """
        if vehicle:
            # Calculate speed
            velocity = vehicle.get_velocity()
            self.vehicle_speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5
            
            # Get engine RPM (estimated from speed and throttle)
            control = vehicle.get_control()
            # Rough RPM estimation: idle (800) + speed factor + throttle factor
            self.vehicle_rpm = 800 + (self.vehicle_speed * 50) + (control.throttle * 2000)
            
            # Store full vehicle data for telemetry
            self.vehicle_data = {
                'speed_kmh': self.vehicle_speed,
                'rpm': self.vehicle_rpm,
                'throttle': control.throttle,
                'brake': control.brake,
                'steer': control.steer,
                'hand_brake': control.hand_brake,
                'reverse': control.reverse,
                'manual_gear_shift': control.manual_gear_shift,
                'gear': control.gear
            }
    
    def publish_camera_frame(self):
        """Publish camera frame to Zenoh topic."""
        if self.current_frame is not None:
            try:
                # Convert numpy array to base64 encoded string
                frame_bytes = self.current_frame.tobytes()
                frame_b64 = base64.b64encode(frame_bytes).decode('utf-8')
                
                frame_data = {
                    'timestamp': time.time(),
                    'shape': self.current_frame.shape,
                    'dtype': str(self.current_frame.dtype),
                    'data': frame_b64
                }
                
                payload = json.dumps(frame_data)
                self.publishers['camera_frame'].put(payload.encode('utf-8'))
                
            except Exception as e:
                self.logger.error(f"Error publishing camera frame: {e}")
    
    def publish_obstacle_distance(self):
        """Publish obstacle distance to Zenoh topic."""
        if self.obstacle_distance is not None:
            try:
                distance_data = {
                    'timestamp': time.time(),
                    'distance_meters': self.obstacle_distance,
                    'status': 'detected' if self.obstacle_distance < 40.0 else 'clear'
                }
                
                payload = json.dumps(distance_data)
                self.publishers['obstacle_distance'].put(payload.encode('utf-8'))
                
            except Exception as e:
                self.logger.error(f"Error publishing obstacle distance: {e}")
    
    def publish_collision_status(self):
        """Publish collision detection status to Zenoh topic."""
        try:
            collision_status = {
                'timestamp': time.time(),
                'collision_detected': self.collision_detected,
                'status': 'collision' if self.collision_detected else 'safe'
            }
            
            payload = json.dumps(collision_status)
            self.publishers['collision_status'].put(payload.encode('utf-8'))
            
            # Reset collision flag after publishing
            if self.collision_detected:
                self.collision_detected = False
                
        except Exception as e:
            self.logger.error(f"Error publishing collision status: {e}")
    
    def publish_collision_data(self):
        """Publish detailed collision data to Zenoh topic."""
        if self.collision_data is not None:
            try:
                payload = json.dumps(self.collision_data)
                self.publishers['collision_data'].put(payload.encode('utf-8'))
                
                # Clear collision data after publishing
                self.collision_data = None
                
            except Exception as e:
                self.logger.error(f"Error publishing collision data: {e}")
    
    def publish_vehicle_speed(self):
        """Publish vehicle speed to Zenoh topic."""
        try:
            speed_data = {
                'timestamp': time.time(),
                'speed_kmh': self.vehicle_speed,
                'speed_ms': self.vehicle_speed / 3.6
            }
            
            payload = json.dumps(speed_data)
            self.publishers['vehicle_speed'].put(payload.encode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Error publishing vehicle speed: {e}")
    
    def publish_vehicle_rpm(self):
        """Publish vehicle RPM to Zenoh topic."""
        try:
            rpm_data = {
                'timestamp': time.time(),
                'rpm': self.vehicle_rpm,
                'engine_load': min(100, (self.vehicle_rpm - 800) / 20)  # Estimated load %
            }
            
            payload = json.dumps(rpm_data)
            self.publishers['vehicle_rpm'].put(payload.encode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Error publishing vehicle RPM: {e}")
    
    def publish_vehicle_telemetry(self):
        """Publish complete vehicle telemetry to Zenoh topic."""
        if self.vehicle_data is not None:
            try:
                telemetry_data = {
                    'timestamp': time.time(),
                    **self.vehicle_data
                }
                
                payload = json.dumps(telemetry_data)
                self.publishers['vehicle_telemetry'].put(payload.encode('utf-8'))
                
            except Exception as e:
                self.logger.error(f"Error publishing vehicle telemetry: {e}")
    
    def _publish_all_data(self):
        """Internal method to publish all data types."""
        self.publish_camera_frame()
        self.publish_obstacle_distance()
        self.publish_collision_status()
        self.publish_collision_data()
        self.publish_vehicle_speed()
        self.publish_vehicle_rpm()
        self.publish_vehicle_telemetry()
    
    def _publishing_loop(self):
        """Internal publishing loop that runs in separate thread."""
        self.logger.info(f"Started publishing loop with {self.publish_interval}s interval")
        
        while self.running:
            try:
                self._publish_all_data()
                time.sleep(self.publish_interval)
                
            except Exception as e:
                self.logger.error(f"Error in publishing loop: {e}")
                time.sleep(self.publish_interval)
    
    def start_publishing(self):
        """Start periodic publishing in background thread."""
        if not self.session:
            raise RuntimeError("Zenoh session not connected. Call connect() first.")
        
        if self.running:
            self.logger.warning("Publishing already started")
            return
        
        self.running = True
        self.publish_thread = threading.Thread(target=self._publishing_loop, daemon=True)
        self.publish_thread.start()
        self.logger.info("Zenoh publishing started")
    
    def stop_publishing(self):
        """Stop periodic publishing."""
        if self.running:
            self.running = False
            if self.publish_thread:
                self.publish_thread.join(timeout=2.0)
            self.logger.info("Zenoh publishing stopped")
    
    def get_topics(self):
        """Get dictionary of all topic names."""
        return self.topics.copy()