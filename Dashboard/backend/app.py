from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import threading
import time
from datetime import datetime
import zenoh

app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend/static')
CORS(app)

# Zenoh session (global variable)
zenoh_session = None

def decode_zenoh_payload(payload):
    """
    Helper function to decode Zenoh payload that handles both ZBytes and string payloads.
    
    Args:
        payload: Zenoh payload (could be ZBytes or string)
        
    Returns:
        str: Decoded string payload
    """
    try:
        if hasattr(payload, 'to_bytes'):
            # Handle ZBytes (newer Zenoh versions)
            return payload.to_bytes().decode('utf-8')
        elif hasattr(payload, 'decode'):
            # Handle string payload (older Zenoh versions)
            return payload.decode('utf-8')
        else:
            # Handle already decoded string
            return str(payload)
    except Exception as e:
        raise ValueError(f"Failed to decode Zenoh payload: {e}")

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

# Zenoh subscriber handlers
def speed_handler(sample):
    """Handle speed data from Zenoh topic"""
    try:
        payload_str = decode_zenoh_payload(sample.payload)
        data = json.loads(payload_str)
        speed_kmh = data['speed_kmh']
        timestamp = data['timestamp']
        
        # Update global vehicle data
        vehicle_data['speed'] = speed_kmh
        vehicle_data['timestamp'] = timestamp
        
        print(f"🚗 Speed: {speed_kmh:.1f} km/h at {timestamp}")
        
    except Exception as e:
        print(f"Error processing speed data: {e}")

def rpm_handler(sample):
    """Handle RPM data from Zenoh topic"""
    try:
        payload_str = decode_zenoh_payload(sample.payload)
        data = json.loads(payload_str)
        rpm = data['rpm']
        engine_load = data.get('engine_load', 0)  # Optional field
        timestamp = data['timestamp']
        
        # Update global vehicle data
        vehicle_data['rpm'] = rpm
        vehicle_data['timestamp'] = timestamp
        
        print(f"🔧 RPM: {rpm:.0f}, Load: {engine_load:.1f}% at {timestamp}")
        
    except Exception as e:
        print(f"Error processing RPM data: {e}")

def pedestrian_warning_handler(sample):
    """Handle pedestrian warning data from Zenoh topic"""
    try:
        payload_str = decode_zenoh_payload(sample.payload)
        # The payload should contain "LEFT" or "RIGHT" or be empty/null for no warning
        warning_direction = payload_str.strip().strip('"')  # Remove quotes if present
        
        if warning_direction in ['LEFT', 'RIGHT']:
            vehicle_data['pedestrian_warning'] = warning_direction
            print(f"🚶 Pedestrian detected: {warning_direction} side")
        else:
            vehicle_data['pedestrian_warning'] = None
            if warning_direction:  # Only log if there was some content
                print(f"🚶 Pedestrian warning cleared")
        
        vehicle_data['timestamp'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Error processing pedestrian warning data: {e}")

def emergency_stop_handler(sample):
    """Handle emergency stop warning data from Zenoh topic"""
    try:
        payload_str = decode_zenoh_payload(sample.payload)
        
        # Parse distance (expecting just a number as string or empty for no warning)
        distance_str = payload_str.strip()
        
        if distance_str and distance_str != "":
            try:
                distance = float(distance_str)
                vehicle_data['emergency_stop'] = {
                    'active': True,
                    'distance': distance
                }
                print(f"🚨 Emergency stop: Obstacle at {distance:.1f}m")
            except ValueError:
                print(f"Invalid distance value: {distance_str}")
        else:
            # Clear emergency stop warning
            vehicle_data['emergency_stop'] = {
                'active': False,
                'distance': 0
            }
            print(f"✅ Emergency stop warning cleared")
        
        vehicle_data['timestamp'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Error processing emergency stop data: {e}")

def lane_warning_handler(sample):
    """Handle lane warning data from Zenoh topic"""
    try:
        payload_str = decode_zenoh_payload(sample.payload)
        # The payload should contain "LEFT" or "RIGHT" or be empty/null for no warning
        warning_direction = payload_str.strip().strip('"')  # Remove quotes if present
        
        if warning_direction in ['LEFT', 'RIGHT']:
            vehicle_data['lane_warning'] = warning_direction
            print(f"🛣️  Lane warning: Vehicle approaching {warning_direction} line")
        else:
            vehicle_data['lane_warning'] = None
            if warning_direction:  # Only log if there was some content
                print(f"🛣️  Lane warning cleared")
        
        vehicle_data['timestamp'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Error processing lane warning data: {e}")

@app.route('/')
def dashboard():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/api/vehicle-data', methods=['GET'])
def get_vehicle_data():
    """Get current vehicle data for dashboard display"""
    return jsonify(vehicle_data)

# Speed and RPM are now updated via Zenoh subscribers
# @app.route('/api/speed', methods=['POST'])
# def update_speed():
#     """Update vehicle speed"""
#     data = request.get_json()
#     if 'speed' in data:
#         vehicle_data['speed'] = data['speed']
#         vehicle_data['timestamp'] = datetime.now().isoformat()
#     return jsonify({'status': 'success'})

# @app.route('/api/rpm', methods=['POST'])
# def update_rpm():
#     """Update vehicle RPM"""
#     data = request.get_json()
#     if 'rpm' in data:
#         vehicle_data['rpm'] = data['rpm']
#         vehicle_data['timestamp'] = datetime.now().isoformat()
#     return jsonify({'status': 'success'})

# Lane assist is now handled via Zenoh subscriber
# @app.route('/api/lane-assist', methods=['POST'])
# def lane_assist_warning():
#     """
#     Receive lane assist warning data
#     Expected data: {'direction': 'LEFT' or 'RIGHT'}
#     """
#     data = request.get_json()
#     direction = data.get('direction')
#     
#     if direction in ['LEFT', 'RIGHT']:
#         vehicle_data['lane_warning'] = direction
#         print(f"Lane assist warning: Vehicle approaching {direction} line")
#     else:
#         vehicle_data['lane_warning'] = None
#     
#     vehicle_data['timestamp'] = datetime.now().isoformat()
#     return jsonify({'status': 'success', 'warning': vehicle_data['lane_warning']})

# Emergency stop is now handled via Zenoh subscriber
# @app.route('/api/emergency-stop', methods=['POST'])
# def emergency_stop_warning():
#     """
#     Receive emergency stop warning data
#     Expected data: {'type': 'OBSTACLE', 'distance': float}
#     """
#     data = request.get_json()
#     warning_type = data.get('type')
#     distance = data.get('distance', 0)
#     
#     if warning_type == 'OBSTACLE':
#         vehicle_data['emergency_stop'] = {
#             'active': True,
#             'distance': distance
#         }
#         print(f"Emergency stop warning: Obstacle detected at {distance}m")
#     else:
#         vehicle_data['emergency_stop'] = {
#             'active': False,
#             'distance': 0
#         }
#     
#     vehicle_data['timestamp'] = datetime.now().isoformat()
#     return jsonify({'status': 'success', 'emergency_stop': vehicle_data['emergency_stop']})

# Pedestrian detection is now handled via Zenoh subscriber
# @app.route('/api/pedestrian-detect', methods=['POST'])
# def pedestrian_detection():
#     """
#     Receive pedestrian detection warning data
#     Expected data: {'direction': 'LEFT' or 'RIGHT'}
#     """
#     data = request.get_json()
#     direction = data.get('direction')
#     
#     if direction in ['LEFT', 'RIGHT']:
#         vehicle_data['pedestrian_warning'] = direction
#         print(f"Pedestrian detected: {direction} side")
#     else:
#         vehicle_data['pedestrian_warning'] = None
#     
#     vehicle_data['timestamp'] = datetime.now().isoformat()
#     return jsonify({'status': 'success', 'pedestrian_warning': vehicle_data['pedestrian_warning']})

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

def initialize_zenoh():
    """Initialize Zenoh session and subscribers"""
    global zenoh_session
    
    try:
        print("🔄 Connecting to Zenoh...")
        
        # Configure Zenoh connection
        zenoh_config = zenoh.Config()
        zenoh_config.insert_json5("mode", json.dumps("peer"))
        zenoh_config.insert_json5("connect/endpoints", json.dumps(["tcp/192.168.33.243:7447"]))
        
        # Open Zenoh session with configuration
        zenoh_session = zenoh.open(zenoh_config)
        print("✅ Connected to Zenoh")
        
        # Define the base topic
        base_topic = 'carla/tesla'
        
        # Subscribe to speed, RPM, pedestrian warning, emergency stop, and lane warning topics
        speed_topic = f"{base_topic}/dynamics/speed"
        rpm_topic = f"{base_topic}/dynamics/rpm"
        pedestrian_topic = f"{base_topic}/warnings/pedestrian"
        emergency_topic = f"{base_topic}/warnings/emergency_stop"
        lane_topic = f"{base_topic}/warnings/lane"
        
        print(f"📡 Subscribing to topics:")
        print(f"   🚗 Speed: {speed_topic}")
        speed_sub = zenoh_session.declare_subscriber(speed_topic, speed_handler)
        
        print(f"   🔧 RPM: {rpm_topic}")
        rpm_sub = zenoh_session.declare_subscriber(rpm_topic, rpm_handler)
        
        print(f"   🚶 Pedestrian: {pedestrian_topic}")
        pedestrian_sub = zenoh_session.declare_subscriber(pedestrian_topic, pedestrian_warning_handler)
        
        print(f"   🚨 Emergency Stop: {emergency_topic}")
        emergency_sub = zenoh_session.declare_subscriber(emergency_topic, emergency_stop_handler)
        
        print(f"   🛣️  Lane Warning: {lane_topic}")
        lane_sub = zenoh_session.declare_subscriber(lane_topic, lane_warning_handler)
        
        print("✅ Zenoh subscribers initialized successfully!")
        print("🔄 Listening for CARLA data...")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Zenoh: {e}")
        print("Dashboard will continue without Zenoh integration")
        return False

if __name__ == '__main__':
    print("Starting Vehicle Dashboard Server...")
    print("Dashboard available at: http://localhost:5000")
    print("\nZenoh Integration:")
    print("- Speed topic: carla/tesla/dynamics/speed")
    print("- RPM topic: carla/tesla/dynamics/rpm")
    print("- Pedestrian warnings: carla/tesla/warnings/pedestrian")
    print("- Emergency stop: carla/tesla/warnings/emergency_stop")
    print("- Lane warnings: carla/tesla/warnings/lane")
    print("\nAPI Endpoints:")
    print("- GET /api/vehicle-data - Get current vehicle data")
    print("- POST /api/clear-warnings - Clear all warnings")
    print("\nNote: Speed, RPM, Pedestrian warnings, Emergency stop, and Lane warnings are now updated automatically via Zenoh subscribers")
    
    # Initialize Zenoh in a separate thread to avoid blocking Flask startup
    def init_zenoh_thread():
        time.sleep(1)  # Give Flask a moment to start
        initialize_zenoh()
    
    zenoh_thread = threading.Thread(target=init_zenoh_thread, daemon=True)
    zenoh_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)