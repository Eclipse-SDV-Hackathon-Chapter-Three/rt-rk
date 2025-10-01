from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime

app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend/static')
CORS(app)

# Global variables to store current vehicle data
vehicle_data = {
    'speed': 0,
    'rpm': 0,
    'lane_warning': None,  # 'LEFT' or 'RIGHT' or None
    'emergency_stop': {
        'active': False,
        'distance': 0
    },
    'pedestrian_warning': None,  # 'LEFT' or 'RIGHT' or None
    'timestamp': datetime.now().isoformat()
}

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/vehicle-data', methods=['GET'])
def get_vehicle_data():
    """Get current vehicle data for dashboard display"""
    return jsonify(vehicle_data)

@app.route('/api/speed', methods=['POST'])
def update_speed():
    """Update vehicle speed"""
    data = request.get_json()
    if 'speed' in data:
        vehicle_data['speed'] = data['speed']
        vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success'})

@app.route('/api/rpm', methods=['POST'])
def update_rpm():
    """Update vehicle RPM"""
    data = request.get_json()
    if 'rpm' in data:
        vehicle_data['rpm'] = data['rpm']
        vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success'})

@app.route('/api/lane-assist', methods=['POST'])
def lane_assist_warning():
    """
    Receive lane assist warning data
    Expected data: {'direction': 'LEFT' or 'RIGHT'}
    """
    data = request.get_json()
    direction = data.get('direction')
    
    if direction in ['LEFT', 'RIGHT']:
        vehicle_data['lane_warning'] = direction
        print(f"Lane assist warning: Vehicle approaching {direction} line")
    else:
        vehicle_data['lane_warning'] = None
    
    vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success', 'warning': vehicle_data['lane_warning']})

@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop_warning():
    """
    Receive emergency stop warning data
    Expected data: {'type': 'OBSTACLE', 'distance': float}
    """
    data = request.get_json()
    warning_type = data.get('type')
    distance = data.get('distance', 0)
    
    if warning_type == 'OBSTACLE':
        vehicle_data['emergency_stop'] = {
            'active': True,
            'distance': distance
        }
        print(f"Emergency stop warning: Obstacle detected at {distance}m")
    else:
        vehicle_data['emergency_stop'] = {
            'active': False,
            'distance': 0
        }
    
    vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success', 'emergency_stop': vehicle_data['emergency_stop']})

@app.route('/api/pedestrian-detect', methods=['POST'])
def pedestrian_detection():
    """
    Receive pedestrian detection warning data
    Expected data: {'direction': 'LEFT' or 'RIGHT'}
    """
    data = request.get_json()
    direction = data.get('direction')
    
    if direction in ['LEFT', 'RIGHT']:
        vehicle_data['pedestrian_warning'] = direction
        print(f"Pedestrian detected: {direction} side")
    else:
        vehicle_data['pedestrian_warning'] = None
    
    vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success', 'pedestrian_warning': vehicle_data['pedestrian_warning']})

@app.route('/api/clear-warnings', methods=['POST'])
def clear_warnings():
    """Clear all active warnings"""
    vehicle_data['lane_warning'] = None
    vehicle_data['emergency_stop'] = {'active': False, 'distance': 0}
    vehicle_data['pedestrian_warning'] = None
    vehicle_data['timestamp'] = datetime.now().isoformat()
    return jsonify({'status': 'success'})

# Placeholder functions for network data reception
def receive_lane_detection_data():
    """
    Placeholder function for receiving lane detection data from network
    Should return 'LEFT', 'RIGHT', or None
    """
    # TODO: Implement actual network data reception
    pass

def receive_emergency_stop_data():
    """
    Placeholder function for receiving emergency stop data from network
    Should call send_warning_data("OBSTACLE", obstacle_distance)
    """
    # TODO: Implement actual network data reception
    pass

def receive_pedestrian_data():
    """
    Placeholder function for receiving pedestrian detection data from network
    Should return 'LEFT', 'RIGHT', or None
    """
    # TODO: Implement actual network data reception
    pass

def send_warning_data(warning_type, distance):
    """
    Placeholder function for processing warning data
    """
    if warning_type == "OBSTACLE":
        vehicle_data['emergency_stop'] = {
            'active': True,
            'distance': distance
        }
        vehicle_data['timestamp'] = datetime.now().isoformat()

if __name__ == '__main__':
    print("Starting Vehicle Dashboard Server...")
    print("Dashboard available at: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("- GET /api/vehicle-data - Get current vehicle data")
    print("- POST /api/lane-assist - Send lane warning (JSON: {'direction': 'LEFT'|'RIGHT'})")
    print("- POST /api/emergency-stop - Send emergency stop (JSON: {'type': 'OBSTACLE', 'distance': float})")
    print("- POST /api/pedestrian-detect - Send pedestrian warning (JSON: {'direction': 'LEFT'|'RIGHT'})")
    print("- POST /api/clear-warnings - Clear all warnings")
    
    app.run(debug=True, host='0.0.0.0', port=5000)