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
└── frontend/
    ├── index.html          # Main dashboard HTML
    └── static/
        ├── css/
        │   └── style.css   # Dashboard styling
        └── js/
            └── dashboard.js # Dashboard functionality
```

## Installation & Setup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Flask Server
```bash
cd backend
python app.py
```

### 3. Access Dashboard
Open your browser and navigate to: `http://localhost:5000`

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

The dashboard includes built-in test controls in the bottom-right corner:
- Speed/RPM sliders
- Lane warning buttons
- Emergency stop distance input
- Pedestrian detection buttons

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