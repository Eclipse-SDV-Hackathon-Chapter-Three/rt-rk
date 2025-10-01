#!/usr/bin/env python3
"""
Test script for Vehicle Dashboard ADAS systems
Demonstrates how to send data to the dashboard
"""

import requests
import json
import time
import random

BASE_URL = "http://localhost:5000"

def test_lane_assist():
    """Test lane assist warnings"""
    print("Testing Lane Assist...")
    
    # Send left warning
    response = requests.post(f"{BASE_URL}/api/lane-assist", 
                           json={"direction": "LEFT"})
    print(f"Left warning: {response.json()}")
    time.sleep(3)
    
    # Send right warning  
    response = requests.post(f"{BASE_URL}/api/lane-assist", 
                           json={"direction": "RIGHT"})
    print(f"Right warning: {response.json()}")
    time.sleep(3)
    
    # Clear warning
    response = requests.post(f"{BASE_URL}/api/lane-assist", 
                           json={"direction": None})
    print(f"Clear warning: {response.json()}")

def test_emergency_stop():
    """Test emergency stop system"""
    print("Testing Emergency Stop...")
    
    # Test different distances
    distances = [50, 25, 15, 8, 3]
    
    for distance in distances:
        response = requests.post(f"{BASE_URL}/api/emergency-stop", 
                               json={"type": "OBSTACLE", "distance": distance})
        print(f"Obstacle at {distance}m: {response.json()}")
        time.sleep(2)
    
    # Clear warning
    response = requests.post(f"{BASE_URL}/api/emergency-stop", 
                           json={"type": None, "distance": 0})
    print(f"Clear emergency: {response.json()}")

def test_pedestrian_detection():
    """Test pedestrian detection"""
    print("Testing Pedestrian Detection...")
    
    # Send left pedestrian
    response = requests.post(f"{BASE_URL}/api/pedestrian-detect", 
                           json={"direction": "LEFT"})
    print(f"Left pedestrian: {response.json()}")
    time.sleep(3)
    
    # Send right pedestrian
    response = requests.post(f"{BASE_URL}/api/pedestrian-detect", 
                           json={"direction": "RIGHT"})
    print(f"Right pedestrian: {response.json()}")
    time.sleep(3)
    
    # Clear warning
    response = requests.post(f"{BASE_URL}/api/pedestrian-detect", 
                           json={"direction": None})
    print(f"Clear pedestrian: {response.json()}")

def simulate_driving():
    """Simulate realistic driving scenario"""
    print("Simulating driving scenario...")
    
    for i in range(30):  # 30 second simulation
        # Random speed and RPM
        speed = random.randint(30, 120)
        rpm = random.randint(1500, 5000)
        
        # Update speed and RPM
        requests.post(f"{BASE_URL}/api/speed", json={"speed": speed})
        requests.post(f"{BASE_URL}/api/rpm", json={"rpm": rpm})
        
        # Random ADAS events
        if random.random() < 0.1:  # 10% chance
            direction = random.choice(["LEFT", "RIGHT"])
            requests.post(f"{BASE_URL}/api/lane-assist", json={"direction": direction})
            print(f"Lane warning: {direction}")
        
        if random.random() < 0.05:  # 5% chance
            distance = random.uniform(5, 30)
            requests.post(f"{BASE_URL}/api/emergency-stop", 
                         json={"type": "OBSTACLE", "distance": distance})
            print(f"Obstacle detected at {distance:.1f}m")
        
        if random.random() < 0.03:  # 3% chance
            direction = random.choice(["LEFT", "RIGHT"])
            requests.post(f"{BASE_URL}/api/pedestrian-detect", 
                         json={"direction": direction})
            print(f"Pedestrian detected: {direction}")
        
        time.sleep(1)
    
    # Clear all warnings at the end
    requests.post(f"{BASE_URL}/api/clear-warnings")
    print("Simulation complete, all warnings cleared")

def main():
    print("Vehicle Dashboard Test Script")
    print("=============================")
    print("Make sure the dashboard server is running on http://localhost:5000")
    print()
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/api/vehicle-data")
        print("✓ Connected to dashboard")
        print()
        
        while True:
            print("Choose test:")
            print("1. Lane Assist")
            print("2. Emergency Stop")
            print("3. Pedestrian Detection")
            print("4. Simulate Driving")
            print("5. Clear All Warnings")
            print("0. Exit")
            
            choice = input("Enter choice (0-5): ").strip()
            
            if choice == "1":
                test_lane_assist()
            elif choice == "2":
                test_emergency_stop()
            elif choice == "3":
                test_pedestrian_detection()
            elif choice == "4":
                simulate_driving()
            elif choice == "5":
                requests.post(f"{BASE_URL}/api/clear-warnings")
                print("All warnings cleared")
            elif choice == "0":
                break
            else:
                print("Invalid choice")
            
            print()
    
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to dashboard server")
        print("Make sure the server is running with: ./start.sh")
    except KeyboardInterrupt:
        print("\nTest script interrupted")

if __name__ == "__main__":
    main()