from flask import Flask, render_template, request, jsonify
import requests
import json
import threading
import time
import random

app = Flask(__name__)

# Dashboard API URL
DASHBOARD_URL = "http://localhost:5000"

@app.route('/')
def test_interface():
    """Serve the test interface"""
    return render_template('test_interface.html')

@app.route('/api/send-speed', methods=['POST'])
def send_speed():
    """Send speed data to dashboard"""
    data = request.get_json()
    speed = data.get('speed', 0)
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/speed", 
                               json={"speed": speed}, 
                               timeout=2)
        return jsonify({"status": "success", "speed": speed})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-rpm', methods=['POST'])
def send_rpm():
    """Send RPM data to dashboard"""
    data = request.get_json()
    rpm = data.get('rpm', 0)
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/rpm", 
                               json={"rpm": rpm}, 
                               timeout=2)
        return jsonify({"status": "success", "rpm": rpm})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-lane-warning', methods=['POST'])
def send_lane_warning():
    """Send lane assist warning to dashboard"""
    data = request.get_json()
    direction = data.get('direction')
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/lane-assist", 
                               json={"direction": direction}, 
                               timeout=2)
        return jsonify({"status": "success", "direction": direction})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-emergency', methods=['POST'])
def send_emergency():
    """Send emergency stop warning to dashboard"""
    data = request.get_json()
    distance = data.get('distance', 0)
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/emergency-stop", 
                               json={"type": "OBSTACLE", "distance": distance}, 
                               timeout=2)
        return jsonify({"status": "success", "distance": distance})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-pedestrian', methods=['POST'])
def send_pedestrian():
    """Send pedestrian detection to dashboard"""
    data = request.get_json()
    direction = data.get('direction')
    
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/pedestrian-detect", 
                               json={"direction": direction}, 
                               timeout=2)
        return jsonify({"status": "success", "direction": direction})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/clear-warnings', methods=['POST'])
def clear_warnings():
    """Clear all warnings on dashboard"""
    try:
        response = requests.post(f"{DASHBOARD_URL}/api/clear-warnings", 
                               json={}, 
                               timeout=2)
        return jsonify({"status": "success"})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start-simulation', methods=['POST'])
def start_simulation():
    """Start driving simulation"""
    def simulate_driving():
        for i in range(60):  # 60 second simulation
            try:
                # Random speed and RPM
                speed = random.randint(30, 120)
                rpm = random.randint(1500, 5000)
                
                # Update speed and RPM
                requests.post(f"{DASHBOARD_URL}/api/speed", 
                            json={"speed": speed}, timeout=1)
                requests.post(f"{DASHBOARD_URL}/api/rpm", 
                            json={"rpm": rpm}, timeout=1)
                
                # Random ADAS events
                if random.random() < 0.1:  # 10% chance
                    direction = random.choice(["LEFT", "RIGHT"])
                    requests.post(f"{DASHBOARD_URL}/api/lane-assist", 
                                json={"direction": direction}, timeout=1)
                    time.sleep(2)  # Show warning for 2 seconds
                    requests.post(f"{DASHBOARD_URL}/api/lane-assist", 
                                json={"direction": None}, timeout=1)
                
                if random.random() < 0.05:  # 5% chance
                    distance = random.uniform(5, 30)
                    requests.post(f"{DASHBOARD_URL}/api/emergency-stop", 
                                json={"type": "OBSTACLE", "distance": distance}, timeout=1)
                    time.sleep(3)  # Show warning for 3 seconds
                    requests.post(f"{DASHBOARD_URL}/api/emergency-stop", 
                                json={"type": None, "distance": 0}, timeout=1)
                
                if random.random() < 0.03:  # 3% chance
                    direction = random.choice(["LEFT", "RIGHT"])
                    requests.post(f"{DASHBOARD_URL}/api/pedestrian-detect", 
                                json={"direction": direction}, timeout=1)
                    time.sleep(2)  # Show warning for 2 seconds
                    requests.post(f"{DASHBOARD_URL}/api/pedestrian-detect", 
                                json={"direction": None}, timeout=1)
                
                time.sleep(1)
            except:
                break
        
        # Clear all warnings at the end
        try:
            requests.post(f"{DASHBOARD_URL}/api/clear-warnings", timeout=1)
        except:
            pass
    
    # Start simulation in background thread
    thread = threading.Thread(target=simulate_driving, daemon=True)
    thread.start()
    
    return jsonify({"status": "success", "message": "Simulation started"})

@app.route('/api/check-dashboard', methods=['GET'])
def check_dashboard():
    """Check if dashboard is accessible"""
    try:
        response = requests.get(f"{DASHBOARD_URL}/api/vehicle-data", timeout=2)
        return jsonify({"status": "connected", "dashboard_url": DASHBOARD_URL})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "disconnected", "error": str(e)}), 500

if __name__ == '__main__':
    print("=================================")
    print("  Vehicle Dashboard Test App")
    print("=================================")
    print(f"Dashboard URL: {DASHBOARD_URL}")
    print("Test Interface: http://localhost:5001")
    print("Make sure the main dashboard is running on port 5000")
    print("Press Ctrl+C to stop")
    print("")
    
    app.run(debug=True, host='0.0.0.0', port=5001)