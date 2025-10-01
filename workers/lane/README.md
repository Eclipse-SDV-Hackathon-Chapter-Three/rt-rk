# Lane Assistant (LA) - Lane Detection System

## Project Overview

The Lane Assistant is an advanced driver assistance system (ADAS) component that provides real-time lane detection and warning capabilities. The system processes video frames to detect lane lines and alerts drivers when the vehicle is approaching or crossing lane boundaries.

## Features

- **Real-time lane detection** using computer vision algorithms
- **Lane departure warnings** when vehicle approaches lane boundaries  
- **Network communication** for receiving video frames and sending commands
- **Configurable parameters** for different road conditions and camera setups
- **Modular design** with separate preprocessing and detection components

## Project Structure

```
LA/
├── main.py                    # Main entry point
├── src/                       # Source code package
│   ├── __init__.py           # Package initialization
│   ├── lane_detection_system.py  # Main system coordinator
│   ├── LaneDetector.py       # Lane detection algorithms
│   ├── imagePreProcesing.py  # Image preprocessing utilities
│   └── network_interface.py  # Network communication functions
├── test_videos/              # Test video files
│   ├── test1.avi
│   └── test2.avi
└── README.md                 # This documentation

```

## System Components

### 1. LaneDetectionSystem
Main system coordinator that orchestrates the entire lane detection pipeline:
- Initializes image preprocessing and lane detection components
- Processes frames received from network
- Calculates vehicle position and generates warnings
- Coordinates communication with other systems

### 2. LaneDetector 
Core lane detection algorithms:
- Applies region of interest (ROI) masking
- Performs edge detection and line extraction
- Tracks lane lines across frames
- Calculates lane geometry and vehicle position

### 3. ImagePreProcessing
Image preprocessing utilities:
- Handles camera calibration and distortion correction
- Applies perspective transformation for bird's eye view
- Implements noise reduction and enhancement filters
- Manages region of interest definition

### 4. NetworkInterface
Network communication functions:
- Receives video frames from external sources
- Sends warning data to dashboard/HMI systems
- Transmits steering angle commands
- Handles communication protocols

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenCV (cv2)
- NumPy
- Network connectivity for frame reception

### Setup
1. Clone or download the project
2. Install required dependencies:
   ```bash
   pip install opencv-python numpy
   ```
3. Navigate to the LA directory
4. Run the main application:
   ```bash
   python main.py
   ```

## Configuration

The system can be configured with the following parameters:

- **Resolution**: Default 640x360 pixels (configurable in main.py)
- **Debugging**: Enable/disable debug output and visualizations
- **Warning Distance**: Threshold for lane departure warnings (default: 160 pixels)
- **Camera FOV**: Field of view in degrees (default: 79.3°)

## Usage

### Basic Usage
```python
from src.lane_detection_system import LaneDetectionSystem

# Initialize the system
system = LaneDetectionSystem(width=640, height=360, debugging=False)

# Start processing network frames
system.process_network_frames()
```

### Advanced Configuration
```python
# Initialize with custom parameters
system = LaneDetectionSystem(
    width=1280, 
    height=720, 
    debugging=True
)

# Process individual frames
processed_frame = system.process_frame(input_frame)
```

## Testing

Test videos are provided in the `test_videos/` directory:
- `test1.avi`: Basic lane detection scenario
- `test2.avi`: Complex road conditions

To test with video files, modify the network interface to read from local files instead of network sources.

## API Reference

### LaneDetectionSystem
- `__init__(width, height, debugging)`: Initialize the system
- `process_network_frames()`: Main processing loop for network frames
- `process_frame(frame)`: Process a single frame
- `calculate_vehicle_position_warnings()`: Generate lane departure warnings

### LaneDetector  
- `detect_lanes(frame)`: Main lane detection function
- `apply_roi(frame)`: Apply region of interest masking
- `extract_lines(frame)`: Extract lane lines from processed frame

### ImagePreProcessing
- `preprocess(frame)`: Apply preprocessing pipeline
- `perspective_transform(frame)`: Convert to bird's eye view
- `enhance_lanes(frame)`: Enhance lane visibility

## Development

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Include docstrings for all classes and functions
- Maintain modular design principles

### Contributing
1. Create feature branches for new developments
2. Test thoroughly with provided test videos
3. Update documentation for new features
4. Follow the existing code structure

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the `src` package is properly initialized with `__init__.py`
2. **Camera Calibration**: Adjust camera FOV and perspective parameters for your specific camera
3. **Performance**: Reduce resolution or disable debugging for better performance
4. **Network Issues**: Check network connectivity and frame reception functions

### Debug Mode
Enable debugging to see:
- Processed frame visualizations
- Lane detection overlay
- Warning trigger points
- Performance metrics

## Technical Specifications

- **Input**: Video frames (RGB/BGR format)
- **Output**: Lane detection results and warning signals
- **Processing**: Real-time capable (depends on hardware)
- **Accuracy**: Optimized for highway and urban road conditions
- **Latency**: Low-latency processing for real-time applications

## License

This project is part of the AlgorithmsADAS system. Please refer to the main project license.

## Support

For technical support and questions:
- Check the troubleshooting section
- Review the API reference
- Test with provided video samples
- Ensure all dependencies are properly installed

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Developed by**: ADAS Development Team