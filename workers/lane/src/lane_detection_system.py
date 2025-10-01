import cv2
import numpy as np
from .imagePreProcesing import ImagePreProcessing
from .LaneDetector import LaneDetector
from .network_interface import send_warning_data, send_angle_cmd, receive_frame


class LaneDetectionSystem:
    def __init__(self, width=640, height=360, debugging=False):
        self.width = width
        self.height = height
        self.debugging = debugging
        
        # Initialize image preprocessing and lane detector
        self.image_processor = ImagePreProcessing(width, height, None, False)
        self.lane_detector = LaneDetector(width, height, None, False)
        
        # Warning parameters
        self.warning_distance = 160  # pixels from center line to trigger warning
        self.center_x = width // 2
        
    def calculate_vehicle_position_warnings(self, left_x, right_x, left_visible, right_visible):
        """Calculate if vehicle is too close to lane lines using last detected positions.
        ALWAYS uses last detected positions regardless of line visibility."""
        warnings = []
        
        # ALWAYS use last known line positions for calculations
        # regardless of current visibility
        if left_x is not None and right_x is not None:
            lane_center = (left_x + right_x) // 2
            vehicle_offset = self.center_x - lane_center
            lane_width = right_x - left_x
            
        # ALWAYS use left line position regardless of visibility
        if left_x is not None:
            distance_to_left = self.center_x - left_x
            # Generate warning based on position regardless of visibility
            if distance_to_left < self.warning_distance:
                warning_msg = "LEFT"
                warnings.append(warning_msg)
        
        # ALWAYS use right line position regardless of visibility
        if right_x is not None:
            distance_to_right = right_x - self.center_x
            # Generate warning based on position regardless of visibility
            if distance_to_right < self.warning_distance:
                warning_msg = "RIGHT"
                warnings.append(warning_msg)

        if warnings:
            # If there are warnings, determine the appropriate steering angle
            if "LEFT" in warnings:
                angle = -5.0  # Turn left
            elif "RIGHT" in warnings:
                angle = 5.0  # Turn right
            else:
                angle = 0.0  # No turn
            send_angle_cmd(angle)

        return warnings
    
    def process_network_frame(self):
        """Process frames received from network and send warning data."""
       
        frame = receive_frame()
        if frame is None:
            return
        
        # Step 1: Image preprocessing
        edges = self.image_processor.process_frame(frame)
        
        # Step 2: Lane detection (without display frame)
        _, left_x, right_x, left_visible, right_visible = \
            self.lane_detector.process_frame(edges, frame)
        
        # Step 3: Calculate warnings
        warnings = self.calculate_vehicle_position_warnings(
            left_x, right_x, left_visible, right_visible)
        
        # Step 4: Send warning data if any warnings exist
        if warnings:
            send_warning_data(warnings)