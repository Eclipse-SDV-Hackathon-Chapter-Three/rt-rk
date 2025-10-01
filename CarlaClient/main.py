#!/usr/bin/env python3
"""
CARLA Manual Driving with Live Camera Feed
==========================================

Ova skripta omogućava ručno upravljanje vozilom pomoću WASD tastera
i prikazuje live video sa prednje kamere.

Controls:
- W: Gas (ubrzavanje)
- S: Kočnica/nazad
- A: Skretanje levo
- D: Skretanje desno
- Q: Ručna kočnica
- ESC: Izlaz

Requirements:
- CARLA simulator pokrenut
- pygame (pip install pygame)
- numpy
"""

import argparse
import time

from src.carla_setup import CarlaSetup
from src.manual_control import ManualControl
from src.zenoh_publisher import ZenohPublisher

def main():
    """Main function to run CARLA manual driving."""
    # Parse argumenti
    parser = argparse.ArgumentParser(description='CARLA Manual Driving')
    parser.add_argument('--host', default='localhost', help='CARLA server host')
    parser.add_argument('--port', default=2000, type=int, help='CARLA server port')
    args = parser.parse_args()
    
    # Initialize CARLA setup and Zenoh publisher
    carla_setup = CarlaSetup(args.host, args.port)
    zenoh_publisher = ZenohPublisher(base_topic='carla/tesla', publish_interval=0.1)
    manual_control = None
    
    try:
        # Connect to CARLA server
        if not carla_setup.connect_to_server():
            print("Greška: Nije moguće povezivanje sa CARLA serverom!")
            return
        
        # Connect to Zenoh
        if zenoh_publisher.connect():
            print("✅ Zenoh publisher povezan")
        else:
            print("⚠️  Zenoh publisher nije dostupan - nastavljamo bez njega")
        
        # Setup synchronous mode
        carla_setup.setup_synchronous_mode(fps=30)
        
        # Spawn vehicle
        vehicle = carla_setup.spawn_vehicle('vehicle.tesla.model3')
        world = carla_setup.get_world()
        
        # Create manual control instance
        manual_control = ManualControl(world, vehicle)
        
        # Setup camera with callback to manual control AND Zenoh
        def camera_callback(image_array):
            manual_control.set_current_image(image_array)
            zenoh_publisher.update_camera_frame(image_array)
        
        # Setup obstacle sensor callback with Zenoh publishing
        def obstacle_callback(obstacle_data):
            distance = obstacle_data['distance']
            actor_type = obstacle_data['actor_type']
            print(f"⚠️  PREPREKA DETEKTOVANA! Udaljenost: {distance:.1f}m, Tip: {actor_type}")
            zenoh_publisher.update_obstacle_distance(obstacle_data)
        
        # Setup collision sensor callback with Zenoh publishing
        def collision_callback(collision_data):
            actor_type = collision_data['actor_type']
            impulse = collision_data['impulse']
            impulse_magnitude = (impulse['x']**2 + impulse['y']**2 + impulse['z']**2)**0.5
            print(f"💥 KOLIZIJA! Sa: {actor_type}, Jačina udara: {impulse_magnitude:.2f}")
            zenoh_publisher.update_collision_status(collision_data)
        
        carla_setup.setup_camera(camera_callback, resolution=(640, 360), fps=30)
        carla_setup.setup_obstacle_sensor(obstacle_callback, detection_range=40.0)
        carla_setup.setup_collision_sensor(collision_callback)
        
        # Start Zenoh publishing
        zenoh_publisher.start_publishing()
        
        print("Rezolucija: 640x360")
        print("Senzori: Obstacle (40m), Collision Detection")
        print("📡 Zenoh Topics:")
        for topic_name, topic_key in zenoh_publisher.get_topics().items():
            print(f"   {topic_name}: {topic_key}")
        print("Kontrole: W-Gas, S-Brake, A/D-Steer, Q-HandBrake, ESC-Exit")
        print("Sačekajte da se pojavi prozor sa kamerom...")
        
        # Wait for camera to stabilize
        time.sleep(3)
        
        # Create a thread to periodically update vehicle data for Zenoh
        import threading
        def update_vehicle_data():
            while True:
                try:
                    zenoh_publisher.update_vehicle_data(vehicle)
                    time.sleep(0.05)  # Update every 50ms
                except:
                    break
        
        vehicle_thread = threading.Thread(target=update_vehicle_data, daemon=True)
        vehicle_thread.start()
        
        # Start manual control
        manual_control.run()
        
    except Exception as e:
        print(f"Greška: {e}")
    finally:
        # Cleanup resources
        if 'zenoh_publisher' in locals():
            zenoh_publisher.disconnect()
        carla_setup.cleanup()


if __name__ == "__main__":
    main()