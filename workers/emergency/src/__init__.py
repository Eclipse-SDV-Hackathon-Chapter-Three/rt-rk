"""
Emergency Stopping (ES) System Source Package

This package contains the core modules for the Emergency Stopping system:
- obstacle_detection: Main ObstacleDetectionSystem class
- network_interface: Network communication functions
"""

__version__ = "1.0.0"
__author__ = "ADAS Team"

from .obstacle_detection import ObstacleDetectionSystem
from .network_interface import receive_obstacle_distance, send_brake_command, send_warning_data

__all__ = [
    'ObstacleDetectionSystem',
    'receive_obstacle_distance', 
    'send_brake_command',
    'send_warning_data'
]