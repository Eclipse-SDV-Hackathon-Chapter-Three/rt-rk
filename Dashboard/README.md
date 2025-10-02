# Vehicle Dashboard Project

A real-time vehicle control panel dashboard that simulates a car's instrument cluster with ADAS (Advanced Driver Assistance Systems) integration.

## Features

### Gauges
- **Speedometer**: Digital + Analog display (0-200 km/h)
- **Tachometer**: Digital + Analog display (0-8000 RPM)
- Realistic needle animations with color coding

### ADAS Systems
1. **Lane Assist Module**
   - Visual lane representation
   - Left/Right warning indicators
   - Red line highlighting when approaching lanes

2. **Emergency Stop System**
   - Obstacle distance visualization (5-bar indicator)
   - Distance-based color coding (green/yellow/red)
   - Obstacle detection warnings

3. **Pedestrian Detection**
   - Left/Right pedestrian indicators
   - Warning lights activation
   - Visual pedestrian icons

## Project Structure

```
Dashboard/
├── backend/
│   ├── app.py              # Flask server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main dashboard HTML
│   └── static/
│       ├── css/
│       │   └── style.css   # Dashboard styling
│       └── js/
│           └── dashboard.js # Dashboard functionality
├── test-app/               # Separate test application
│   ├── app.py              # Test interface server
│   ├── requirements.txt    # Test app dependencies
│   ├── start_test.sh       # Test app startup script
│   └── templates/
│       └── test_interface.html # Test interface
├── README.md               # Documentation
├── start.sh               # Main dashboard startup
└── test_dashboard.py      # Command line test script
```

## Installation & Setup

### Method 1: Quick Start (Recommended)
```bash
# Start main dashboard
./start.sh

# In another terminal, start test interface
cd test-app
./start_test.sh
```

### Method 2: Manual Setup

#### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Run the Flask Server
```bash
cd backend
python app.py
```

#### 3. Access Dashboard
Main Dashboard: `http://localhost:5000`

#### 4. Run Test Interface (Optional)
```bash
cd test-app
pip install -r requirements.txt
python app.py
```
Test Interface: `http://localhost:5001`

## API Endpoints

### Data Reception
- `GET /api/vehicle-data` - Get current vehicle data
- `POST /api/speed` - Update speed
- `POST /api/rpm` - Update RPM

### ADAS Data Input
- `POST /api/lane-assist` - Lane detection warnings
  ```json
  {"direction": "LEFT|RIGHT"}
  ```

- `POST /api/emergency-stop` - Emergency stop warnings
  ```json
  {"type": "OBSTACLE", "distance": 15.5}
  ```

- `POST /api/pedestrian-detect` - Pedestrian detection
  ```json
  {"direction": "LEFT|RIGHT"}
  ```

### Control
- `POST /api/clear-warnings` - Clear all active warnings

## Data Integration

### Network Data Reception (Placeholder Functions)

The following placeholder functions are ready for network integration:

```python
# In app.py
def receive_lane_detection_data():
    # Returns 'LEFT', 'RIGHT', or None
    pass

def receive_emergency_stop_data():
    # Calls send_warning_data("OBSTACLE", distance)
    pass

def receive_pedestrian_data():
    # Returns 'LEFT', 'RIGHT', or None
    pass
```

### Example Data Formats

**Lane Detection**: String "LEFT" or "RIGHT"
**Emergency Stop**: `send_warning_data("OBSTACLE", obstacle_distance)`
**Pedestrian Detection**: String "LEFT" or "RIGHT" (no string = no warning)

## Testing

### Web Test Interface (Recommended)
1. Start the main dashboard: `./start.sh`
2. Start the test interface: `cd test-app && ./start_test.sh`
3. Open `http://localhost:5001` for the test interface
4. Use the web controls to send test data to the dashboard

### Command Line Testing
```bash
python test_dashboard.py
```

### Test Interface Features
- **Speed/RPM Sliders**: Real-time gauge control
- **ADAS Warning Buttons**: Test all warning systems
- **Driving Simulation**: 60-second automated test scenario
- **Connection Status**: Real-time dashboard connectivity
- **Professional UI**: Easy-to-use web interface

## Features

- **Real-time Updates**: 100ms polling for responsive dashboard
- **Responsive Design**: Adapts to different screen sizes
- **Visual Feedback**: Color-coded warnings and animations
- **Professional Look**: Vehicle-grade dashboard appearance
- **Modular Code**: Easy to extend and customize

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Development

To modify the dashboard:
1. **Styling**: Edit `frontend/static/css/style.css`
2. **Functionality**: Edit `frontend/static/js/dashboard.js`
3. **Layout**: Edit `frontend/index.html`
4. **Backend**: Edit `backend/app.py`

The dashboard automatically refreshes data from the server, so you only need to restart the Flask server when changing backend code.