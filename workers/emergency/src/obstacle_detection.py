"""
Obstacle Detection System module for the Emergency Stopping (ES) system.
Contains the main ObstacleDetectionSystem class for processing obstacle data.
"""

import time
from .network_interface import receive_obstacle_distance, send_brake_command, send_warning_data


class ObstacleDetectionSystem:
    
    def __init__(self, debugging=False):
        self.debugging = debugging
        
        self.critical_distance = 5.0
        self.warning_distance = 15.0
        self.safe_distance = 25.0
        
        self.max_brake = 1.0
        self.warning_brake = 0.3
        self.emergency_brake = 0.8
        
        self.last_brake_value = 0.0
        self.obstacle_detected = False
        
    def calculate_brake_intensity(self, distance):
        """Calculates brake intensity based on distance to obstacle."""
        if distance is None:
            return 0.0
            
        if distance <= self.critical_distance:
            return self.emergency_brake
            
        elif distance <= self.warning_distance:
            brake_intensity = self.warning_brake + \
                             (self.emergency_brake - self.warning_brake) * \
                             (1.0 - (distance - self.critical_distance) / 
                              (self.warning_distance - self.critical_distance))
            
            return brake_intensity
            
        elif distance <= self.safe_distance:
            return self.warning_brake
            
        else:
            return 0.0
    
    def process_obstacle_detection(self):
        """Main loop for obstacle detection processing."""
        
        try:
            obstacle_distance = receive_obstacle_distance()
            brake_intensity = self.calculate_brake_intensity(obstacle_distance)
            if obstacle_distance < self.warning_distance:
                self.warning = True
            else:
                self.warning = False
            
            if brake_intensity != self.last_brake_value:
                send_brake_command(brake_intensity)
                self.last_brake_value = brake_intensity
            if self.warning:
                send_warning_data("OBSTACLE", obstacle_distance)
            
            self.obstacle_detected = (obstacle_distance is not None)
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            send_brake_command(0.0)
            return
        except Exception as e:
            send_brake_command(0.0)
            time.sleep(1.0)