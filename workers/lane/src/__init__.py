# Lane Assistant Source Package
"""
This package contains the core components of the Lane Assistant system:
- LaneDetectionSystem: Main system coordinator
- LaneDetector: Lane line detection algorithms
- ImagePreProcessing: Image preprocessing utilities
- network_interface: Network communication functions
"""

__version__ = "1.0.0"
__author__ = "ADAS Team"

from .lane_detection_system import LaneDetectionSystem
from .LaneDetector import LaneDetector
from .imagePreProcesing import ImagePreProcessing
from .network_interface import send_warning_data, send_angle_cmd, receive_frame

__all__ = [
    "LaneDetectionSystem",
    "LaneDetector", 
    "ImagePreProcessing",
    "send_warning_data",
    "send_angle_cmd", 
    "receive_frame"
]