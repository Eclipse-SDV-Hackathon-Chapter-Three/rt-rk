# Emergency Stop (ES) System

## Overview

The Emergency Stop (ES) system is a critical safety component of the ADAS (Advanced Driver Assistance Systems) suite. It provides real-time obstacle detection and automatic emergency braking capabilities to prevent collisions.

## System Architecture

```
ES/
├── main.py                    # Main entry point
├── src/                       # Source code package
│   ├── __init__.py           # Package initialization
│   ├── obstacle_detection.py # Core obstacle detection logic
│   └── network_interface.py  # Network communication module
└── README.md                 # This documentation
```

## Features

- **Real-time Obstacle Detection**: Continuously monitors for obstacles ahead
- **Adaptive Braking**: Calculates brake intensity based on obstacle distance
- **Warning System**: Provides early warnings when obstacles are detected
- **Network Communication**: Sends brake commands and warning data over network
- **Configurable Safety Distances**: Customizable critical, warning, and safe distances

## Core Components

### ObstacleDetectionSystem Class

The main class responsible for processing obstacle detection and coordinating the emergency stop response.

#### Key Parameters:
- **Critical Distance**: 5.0m - Emergency braking threshold
- **Warning Distance**: 15.0m - Warning activation threshold  
- **Safe Distance**: 25.0m - Maximum monitoring range
- **Emergency Brake**: 0.8 - Maximum brake intensity for emergencies
- **Warning Brake**: 0.3 - Brake intensity for warning conditions

#### Methods:
- `calculate_brake_intensity(distance)`: Calculates appropriate brake force
- `process_obstacle_detection()`: Main processing loop

### Network Interface

Handles communication with external systems:
- `receive_obstacle_distance()`: Receives distance data from sensors
- `send_brake_command(brake_value)`: Sends brake commands (0.0-1.0)
- `send_warning_data(warnings, distance)`: Transmits warning information

## Usage

### Basic Usage

```python
from src.obstacle_detection import ObstacleDetectionSystem

# Initialize the system
es_system = ObstacleDetectionSystem(debugging=True)

# Start obstacle detection
es_system.process_obstacle_detection()
```

### Running the System

```bash
cd ES/
python main.py
```

## Brake Intensity Logic

The system uses a graduated braking approach:

1. **Distance > 25m**: No braking (brake = 0.0)
2. **15m < Distance ≤ 25m**: Warning braking (brake = 0.3)
3. **5m < Distance ≤ 15m**: Progressive braking (0.3 - 0.8)
4. **Distance ≤ 5m**: Emergency braking (brake = 0.8)

## Safety Features

- **Failsafe Operation**: Applies emergency braking on system errors
- **Graceful Shutdown**: Releases brakes on clean exit (Ctrl+C)
- **Continuous Monitoring**: 10Hz update rate (100ms intervals)
- **Error Recovery**: Automatic restart after transient errors

## Integration

The ES system is designed to integrate with:
- Sensor systems (LiDAR, cameras, radar)
- Vehicle control systems
- Other ADAS components (LA - Lane Assist, RONA - Accident Recorder)

## Configuration

The system can be configured by modifying the parameters in the `ObstacleDetectionSystem` class:

```python
# Distance thresholds (meters)
self.critical_distance = 5.0
self.warning_distance = 15.0
self.safe_distance = 25.0

# Brake intensities (0.0 - 1.0)
self.warning_brake = 0.3
self.emergency_brake = 0.8
```

## Dependencies

- **Python 3.x**
- **time** (standard library)
- Network interface implementation (sensor-specific)

## Error Handling

The system includes comprehensive error handling:
- Network communication failures
- Sensor data errors
- System interrupts
- Automatic recovery mechanisms

## Development Notes

- Debug mode available for development and testing
- Modular design allows easy component replacement
- Network interface can be adapted for different communication protocols
- Thread-safe operation for integration with larger systems

## License

Part of the ADAS system suite. Internal use only.

## Version History

- **v1.0.0**: Initial implementation with basic obstacle detection and emergency braking