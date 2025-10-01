"""
Zenoh Subscriber Module for CARLA ADAS
=====================================

This module contains the ZenohSubscriber class that handles receiving
ADAS commands via Zenoh topics and provides simple override functionality.
"""

import time
import threading
import json
import logging

try:
    import zenoh
    ZENOH_AVAILABLE = True
except ImportError:
    ZENOH_AVAILABLE = False


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


class ZenohSubscriber:
    """
    Simple Zenoh subscriber for ADAS commands that can override driver input.
    """
    
    def __init__(self, base_topic='adas'):
        """
        Initialize Zenoh subscriber.
        
        Args:
            base_topic: Base topic name for ADAS commands
        """
        self.base_topic = base_topic
        self.session = None
        self.logger = self._setup_logging()
        
        # ADAS override states
        self.lane_assist_active = False
        self.lane_assist_angle = 0.0
        self.lane_assist_last_update = 0.0
        
        self.emergency_brake_active = False
        self.emergency_brake_force = 0.0
        self.emergency_brake_last_update = 0.0
        
        # Timeout settings (seconds)
        self.lane_assist_timeout = 2.0
        self.emergency_brake_timeout = 1.0
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Topic names
        self.topics = {
            'lane_assist': f"{base_topic}/la/angle",
            'emergency_brake': f"{base_topic}/es/brake"
        }
        
        # Subscribers
        self.subscribers = {}
        
    def _setup_logging(self):
        """Setup logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def connect(self):
        """
        Connect to Zenoh and setup subscribers.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not ZENOH_AVAILABLE:
            self.logger.warning("Zenoh nije dostupan - ADAS subscriber onemogućen")
            return False
            
        try:
            self.session = zenoh.open(zenoh.Config())
            self.logger.info("ADAS Subscriber: Zenoh session otvoren")
            
            # Setup lane assist subscriber
            self.subscribers['lane_assist'] = self.session.declare_subscriber(
                self.topics['lane_assist'], 
                self._lane_assist_handler
            )
            
            # Setup emergency brake subscriber
            self.subscribers['emergency_brake'] = self.session.declare_subscriber(
                self.topics['emergency_brake'], 
                self._emergency_brake_handler
            )
            
            self.logger.info(f"ADAS Subscriber: Pretplaćen na topike:")
            self.logger.info(f"  Lane Assist: {self.topics['lane_assist']}")
            self.logger.info(f"  Emergency Brake: {self.topics['emergency_brake']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"ADAS Subscriber: Greška pri povezivanju: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Zenoh session."""
        if self.session:
            self.session.close()
            self.logger.info("ADAS Subscriber: Zenoh session zatvoren")
    
    def _lane_assist_handler(self, sample):
        """
        Handle lane assist commands.
        
        Args:
            sample: Zenoh sample containing lane assist data
        """
        try:
            payload_str = decode_zenoh_payload(sample.payload)
            data = json.loads(payload_str)
            
            with self.lock:
                self.lane_assist_angle = float(data.get('angle', 0.0))
                self.lane_assist_last_update = time.time()
                self.lane_assist_active = True
                
            self.logger.info(f"🛣️  Lane Assist: ugao={self.lane_assist_angle:.3f}")
            
        except Exception as e:
            self.logger.error(f"ADAS Subscriber: Greška u lane assist podacima: {e}")
    
    def _emergency_brake_handler(self, sample):
        """
        Handle emergency brake commands.
        
        Args:
            sample: Zenoh sample containing emergency brake data
        """
        try:
            payload_str = decode_zenoh_payload(sample.payload)
            data = json.loads(payload_str)
            
            with self.lock:
                self.emergency_brake_force = float(data.get('brake_force', 0.0))
                self.emergency_brake_last_update = time.time()
                self.emergency_brake_active = self.emergency_brake_force > 0.0
                
            if self.emergency_brake_active:
                self.logger.warning(f"🚨 Emergency Brake: sila={self.emergency_brake_force:.3f}")
            
        except Exception as e:
            self.logger.error(f"ADAS Subscriber: Greška u emergency brake podacima: {e}")
    
    def _check_timeouts(self):
        """Check if ADAS commands have timed out."""
        current_time = time.time()
        
        with self.lock:
            # Check lane assist timeout
            if self.lane_assist_active:
                if current_time - self.lane_assist_last_update > self.lane_assist_timeout:
                    self.lane_assist_active = False
                    self.lane_assist_angle = 0.0
                    self.logger.info("🛣️  Lane Assist: Timeout - deaktivirano")
            
            # Check emergency brake timeout
            if self.emergency_brake_active:
                if current_time - self.emergency_brake_last_update > self.emergency_brake_timeout:
                    self.emergency_brake_active = False
                    self.emergency_brake_force = 0.0
                    self.logger.info("🚨 Emergency Brake: Timeout - deaktivirano")
    
    def get_lane_assist_override(self):
        """
        Get lane assist override value if active.
        
        Returns:
            tuple: (is_active, angle) - angle to use for steering override
        """
        self._check_timeouts()
        
        with self.lock:
            return self.lane_assist_active, self.lane_assist_angle
    
    def get_emergency_brake_override(self):
        """
        Get emergency brake override value if active.
        
        Returns:
            tuple: (is_active, brake_force) - brake force to use for brake override
        """
        self._check_timeouts()
        
        with self.lock:
            return self.emergency_brake_active, self.emergency_brake_force
    
    def is_any_system_active(self):
        """
        Check if any ADAS system is currently active.
        
        Returns:
            bool: True if any ADAS system is active
        """
        self._check_timeouts()
        
        with self.lock:
            return self.lane_assist_active or self.emergency_brake_active
    
    def get_status(self):
        """
        Get current ADAS status.
        
        Returns:
            dict: Current ADAS status information
        """
        self._check_timeouts()
        
        with self.lock:
            return {
                'lane_assist': {
                    'active': self.lane_assist_active,
                    'angle': self.lane_assist_angle,
                    'last_update': self.lane_assist_last_update
                },
                'emergency_brake': {
                    'active': self.emergency_brake_active,
                    'force': self.emergency_brake_force,
                    'last_update': self.emergency_brake_last_update
                }
            }
    
    def get_topics(self):
        """Get dictionary of all ADAS topic names."""
        return self.topics.copy()