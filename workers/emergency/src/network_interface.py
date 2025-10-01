"""
Network interface module for the Emergency Stopping (ES) system.
Contains functions for receiving obstacle data and sending commands.
"""

def receive_obstacle_distance():
    """Returns distance to obstacle in meters or None if no obstacle detected."""
    pass

def send_brake_command(brake_value):
    """Sends brake command over network. brake_value: 0.0-1.0"""
    pass

def send_warning_data(warnings, distance):
    """Sends warning data over network."""
    pass