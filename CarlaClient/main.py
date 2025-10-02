#!/usr/bin/env python3
"""
CARLA Manual Driving with Live Camera Feed
==========================================

Ova skripta omogućava ručno upravljanje vozilom pomoću WASD tastera
i prikazuje live video sa prednje kamere.

Controls:
- W: Gas (napred u brzini, nazad u rikveru)
- S: Kočnica (uvek)
- A: Skretanje levo
- D: Skretanje desno
- Q: Ručna kočnica
- R: Prebaci u veću brzinu (iz rikverca u 1., zatim 1-6)
- F: Prebaci u manju brzinu (6-1, iz 1. u rikverc)
- Shift+R: Direktno prebaci u rikverc
- ESC: Izlaz

Gear System:
- 6 brzina napred (1-6) sa ograničenjima brzine
- Rikverc sa ograničenjem od 20 km/h
- W taster radi u oba smera zavisno od trenutne brzine

Requirements:
- CARLA simulator pokrenut
- pygame (pip install pygame)
- numpy
"""

import argparse
import time
import random

from src.carla_setup import CarlaSetup
from src.manual_control import ManualControl
from src.zenoh_publisher import ZenohPublisher
from src.zenoh_subscriber import ZenohSubscriber

def main():
    """Main function to run CARLA manual driving."""
    # Parse argumenti
    parser = argparse.ArgumentParser(description='CARLA Manual Driving')
    parser.add_argument('--host', default='localhost', help='CARLA server host')
    parser.add_argument('--port', default=2000, type=int, help='CARLA server port')
    args = parser.parse_args()
    
    # Initialize CARLA setup, Zenoh publisher and ADAS subscriber
    carla_setup = CarlaSetup(args.host, args.port)
    zenoh_publisher = ZenohPublisher(base_topic='carla/tesla', publish_interval=0.1)
    adas_subscriber = ZenohSubscriber(base_topic='adas')
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
        
        # Connect ADAS subscriber
        if adas_subscriber.connect():
            print("✅ ADAS subscriber povezan")
        else:
            print("⚠️  ADAS subscriber nije dostupan - nastavljamo bez njega")
        
        # Setup synchronous mode
        carla_setup.setup_synchronous_mode(fps=30)
        
        # Spawn vehicle
        vehicle = carla_setup.spawn_vehicle('vehicle.tesla.model3')
        world = carla_setup.get_world()
        
        # Create manual control instance with ADAS subscriber and carla_setup
        manual_control = ManualControl(world, vehicle, adas_subscriber, carla_setup)
        
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
        print("📡 Zenoh Publisher Topics:")
        for topic_name, topic_key in zenoh_publisher.get_topics().items():
            print(f"   {topic_name}: {topic_key}")
        print("🚗 ADAS Subscriber Topics:")
        for topic_name, topic_key in adas_subscriber.get_topics().items():
            print(f"   {topic_name}: {topic_key}")
        print("Kontrole: W-Gas, S-Brake, A/D-Steer, Q-HandBrake, ESC-Exit")
        print("Menjači: R-Veća brzina/Izlaz iz rikverca, F-Manja brzina/Ulazak u rikverc")
        print("🚶 Pešaci: Spawnuju se ispred vozila u smeru kretanja (70%) i sa strana (30%)")
        print("ADAS: Lane Assist i Emergency Brake mogu override-ovati vozača")
        print("Sačekajte da se pojavi prozor sa kamerom...")
        
        # Wait for camera to stabilize
        time.sleep(3)
        
        # Spawn initial pedestrians
        carla_setup.spawn_pedestrians_around_vehicle(5)
        print(f"🚶 Spawnovano {carla_setup.get_pedestrian_count()} pešaka oko vozila")
        
        # Create a thread to periodically update vehicle data for Zenoh
        import threading
        def update_vehicle_data():
            while True:
                try:
                    zenoh_publisher.update_vehicle_data(vehicle)
                    time.sleep(0.05)  # Update every 50ms
                except:
                    break
        
        # Create a thread for pedestrian management
        def manage_pedestrians():
            last_spawn_time = time.time()
            last_cleanup_time = time.time()
            
            while True:
                try:
                    current_time = time.time()
                    
                    # Spawn new pedestrians every 8-15 seconds
                    if current_time - last_spawn_time > random.uniform(8, 15):
                        # 70% chance for front spawning, 30% for side spawning
                        if random.random() < 0.7:
                            spawn_count = random.randint(1, 2)
                            carla_setup.spawn_pedestrians_around_vehicle(spawn_count)
                            print(f"🚶 Dodano {spawn_count} pešaka ispred vozila (ukupno: {carla_setup.get_pedestrian_count()})")
                        else:
                            left_count = random.randint(0, 1)
                            right_count = random.randint(0, 1)
                            if left_count > 0 or right_count > 0:
                                carla_setup.spawn_pedestrians_at_sides(left_count, right_count)
                                print(f"🚶 Dodano {left_count + right_count} pešaka sa strana (ukupno: {carla_setup.get_pedestrian_count()})")
                        
                        last_spawn_time = current_time
                    
                    # Cleanup distant pedestrians every 12 seconds
                    if current_time - last_cleanup_time > 12:
                        carla_setup.cleanup_distant_pedestrians()
                        last_cleanup_time = current_time
                    
                    time.sleep(1)  # Check every second
                except:
                    break
        
        vehicle_thread = threading.Thread(target=update_vehicle_data, daemon=True)
        pedestrian_thread = threading.Thread(target=manage_pedestrians, daemon=True)
        
        vehicle_thread.start()
        pedestrian_thread.start()
        
        # Start manual control
        manual_control.run()
        
    except Exception as e:
        print(f"Greška: {e}")
    finally:
        # Cleanup resources
        if 'adas_subscriber' in locals():
            adas_subscriber.disconnect()
        if 'zenoh_publisher' in locals():
            zenoh_publisher.disconnect()
        carla_setup.cleanup()


if __name__ == "__main__":
    main()