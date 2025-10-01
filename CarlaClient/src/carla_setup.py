"""
CARLA Setup Module
==================

This module contains the CarlaSetup class that handles the initialization
and management of CARLA world, vehicle, camera, and sensors.
"""

import carla
import numpy as np
import time
import logging
import random


class CarlaSetup:
    """
    Handles CARLA world, vehicle, camera and sensor setup and management.
    """
    
    def __init__(self, host='localhost', port=2000):
        """
        Initialize CARLA setup with connection parameters.
        
        Args:
            host: CARLA server host address
            port: CARLA server port
        """
        self.host = host
        self.port = port
        self.client = None
        self.world = None
        self.vehicle = None
        self.camera = None
        self.obstacle_sensor = None
        self.collision_sensor = None
        self.logger = self._setup_logging()
        self.camera_callback = None
        self.obstacle_callback = None
        self.collision_callback = None
        
    def _setup_logging(self):
        """Setup logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def connect_to_server(self):
        """
        Connect to CARLA server and get world instance.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Povezivanje sa CARLA serverom na {self.host}:{self.port}")
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(10.0)
            
            # Provera verzije
            version = self.client.get_server_version()
            self.logger.info(f"CARLA server verzija: {version}")
            print("Uspešno povezano sa CARLA simulatorom!")
            
            # Dobijanje sveta
            self.world = self.client.get_world()
            self.logger.info("Dobijen CARLA svet")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Greška pri povezivanju: {e}")
            return False
    
    def setup_synchronous_mode(self, fps=30):
        """
        Setup synchronous mode for stable simulation.
        
        Args:
            fps: Target frames per second
        """
        if not self.world:
            raise RuntimeError("World nije inicijalizovan")
            
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0 / fps  # Convert FPS to delta time
        self.world.apply_settings(settings)
        self.logger.info(f"Postavljen sinhronizovan mod sa {fps} FPS")
    
    def spawn_vehicle(self, vehicle_type='vehicle.tesla.model3'):
        """
        Spawn a vehicle at a random spawn point.
        
        Args:
            vehicle_type: Type of vehicle blueprint to use
            
        Returns:
            carla.Vehicle: Spawned vehicle instance
        """
        if not self.world:
            raise RuntimeError("World nije inicijalizovan")
            
        # Dobijanje blueprint biblioteke
        blueprint_library = self.world.get_blueprint_library()
        
        # Odabir vozila
        vehicle_bp = blueprint_library.filter(vehicle_type)[0]
        self.logger.info(f"Odabran blueprint za vozilo: {vehicle_type}")
        
        # Pronalaženje spawn tačaka
        spawn_points = self.world.get_map().get_spawn_points()
        if not spawn_points:
            raise RuntimeError("Nema dostupnih spawn tačaka!")
        
        # Odabir nasumične spawn tačke
        spawn_point = random.choice(spawn_points)
        self.logger.info(f"Odabrana spawn tačka: {spawn_point.location}")
        
        # Spawn vozila
        self.vehicle = self.world.spawn_actor(vehicle_bp, spawn_point)
        self.logger.info(f"Vozilo spawn-ovano sa ID: {self.vehicle.id}")
        
        # Sačekaj da se vozilo stabilizuje
        time.sleep(2)
        
        return self.vehicle
    
    def setup_camera(self, callback_function, resolution=(640, 360), fov=90, fps=30):
        """
        Setup and attach RGB camera to the vehicle.
        
        Args:
            callback_function: Function to call when new image is received
            resolution: Camera resolution as (width, height) tuple
            fov: Field of view in degrees
            fps: Camera frame rate
            
        Returns:
            carla.Sensor: Camera sensor instance
        """
        if not self.world or not self.vehicle:
            raise RuntimeError("World ili vehicle nisu inicijalizovani")
            
        # Kreiranje kamere
        blueprint_library = self.world.get_blueprint_library()
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(resolution[0]))
        camera_bp.set_attribute('image_size_y', str(resolution[1]))
        camera_bp.set_attribute('fov', str(fov))
        camera_bp.set_attribute('sensor_tick', str(1.0 / fps))
        
        # Pozicija kamere (prednji deo vozila)
        camera_transform = carla.Transform(
            carla.Location(x=2.0, z=1.0),  # 2m napred, 1m visoko
            carla.Rotation(pitch=0)        # Bez naginjanja
        )
        
        # Spawn kamere i attach na vozilo
        self.camera = self.world.spawn_actor(camera_bp, camera_transform, attach_to=self.vehicle)
        self.logger.info(f"Kamera kreirana sa ID: {self.camera.id}")
        
        # Registracija callback funkcije
        self.camera_callback = callback_function
        self.camera.listen(self._camera_callback_wrapper)
        
        return self.camera
    
    def _camera_callback_wrapper(self, image):
        """
        Internal wrapper for camera callback that processes CARLA image.
        
        Args:
            image: CARLA image data
        """
        # Konvertuje CARLA sliku u numpy array
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]  # Uklanja alpha kanal
        array = array[:, :, ::-1]  # BGR to RGB za OpenCV
        
        # Poziv korisničke callback funkcije
        if self.camera_callback:
            self.camera_callback(array)
    
    def setup_obstacle_sensor(self, callback_function, detection_range=40.0):
        """
        Setup and attach obstacle detection sensor to the vehicle.
        
        Args:
            callback_function: Function to call when obstacle is detected
            detection_range: Maximum detection range in meters (default 40m)
            
        Returns:
            carla.Sensor: Obstacle sensor instance
        """
        if not self.world or not self.vehicle:
            raise RuntimeError("World ili vehicle nisu inicijalizovani")
            
        # Kreiranje obstacle detection senzora
        blueprint_library = self.world.get_blueprint_library()
        obstacle_bp = blueprint_library.find('sensor.other.obstacle')
        obstacle_bp.set_attribute('distance', str(detection_range))
        obstacle_bp.set_attribute('hit_radius', '0.5')
        obstacle_bp.set_attribute('only_dynamics', 'false')
        
        # Pozicija senzora (prednji deo vozila)
        obstacle_transform = carla.Transform(
            carla.Location(x=2.5, z=0.5),  # 2.5m napred, 0.5m visoko
            carla.Rotation(pitch=0)        # Gleda pravo napred
        )
        
        # Spawn senzora i attach na vozilo
        self.obstacle_sensor = self.world.spawn_actor(obstacle_bp, obstacle_transform, attach_to=self.vehicle)
        self.logger.info(f"Obstacle senzor kreiran sa ID: {self.obstacle_sensor.id}, domet: {detection_range}m")
        
        # Registracija callback funkcije
        self.obstacle_callback = callback_function
        self.obstacle_sensor.listen(self._obstacle_callback_wrapper)
        
        return self.obstacle_sensor
    
    def _obstacle_callback_wrapper(self, event):
        """
        Internal wrapper for obstacle sensor callback.
        
        Args:
            event: CARLA obstacle detection event
        """
        if self.obstacle_callback:
            obstacle_data = {
                'frame': event.frame,
                'timestamp': event.timestamp,
                'distance': event.distance,
                'actor': event.other_actor,
                'actor_id': event.other_actor.id if event.other_actor else None,
                'actor_type': event.other_actor.type_id if event.other_actor else 'unknown'
            }
            self.obstacle_callback(obstacle_data)
    
    def setup_collision_sensor(self, callback_function):
        """
        Setup and attach collision detection sensor to the vehicle.
        
        Args:
            callback_function: Function to call when collision is detected
            
        Returns:
            carla.Sensor: Collision sensor instance
        """
        if not self.world or not self.vehicle:
            raise RuntimeError("World ili vehicle nisu inicijalizovani")
            
        # Kreiranje collision detection senzora
        blueprint_library = self.world.get_blueprint_library()
        collision_bp = blueprint_library.find('sensor.other.collision')
        
        # Pozicija senzora (centar vozila)
        collision_transform = carla.Transform(
            carla.Location(x=0.0, z=0.0),  # Centar vozila
            carla.Rotation(pitch=0)
        )
        
        # Spawn senzora i attach na vozilo
        self.collision_sensor = self.world.spawn_actor(collision_bp, collision_transform, attach_to=self.vehicle)
        self.logger.info(f"Collision senzor kreiran sa ID: {self.collision_sensor.id}")
        
        # Registracija callback funkcije
        self.collision_callback = callback_function
        self.collision_sensor.listen(self._collision_callback_wrapper)
        
        return self.collision_sensor
    
    def _collision_callback_wrapper(self, event):
        """
        Internal wrapper for collision sensor callback.
        
        Args:
            event: CARLA collision event
        """
        if self.collision_callback:
            collision_data = {
                'frame': event.frame,
                'timestamp': event.timestamp,
                'actor': event.other_actor,
                'actor_id': event.other_actor.id if event.other_actor else None,
                'actor_type': event.other_actor.type_id if event.other_actor else 'unknown',
                'impulse': {
                    'x': event.normal_impulse.x,
                    'y': event.normal_impulse.y,
                    'z': event.normal_impulse.z
                }
            }
            self.collision_callback(collision_data)
    
    def cleanup(self):
        """Clean up all CARLA resources."""
        self.logger.info("Čišćenje resursa...")
        
        if self.collision_sensor:
            self.collision_sensor.stop()
            self.collision_sensor.destroy()
            self.logger.info("Collision senzor uništen")
        
        if self.obstacle_sensor:
            self.obstacle_sensor.stop()
            self.obstacle_sensor.destroy()
            self.logger.info("Obstacle senzor uništen")
        
        if self.camera:
            self.camera.stop()
            self.camera.destroy()
            self.logger.info("Kamera uništena")
        
        if self.vehicle:
            self.vehicle.destroy()
            self.logger.info("Vozilo uništeno")
        
        # Resetuj sinhronizovan mod
        if self.world:
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            self.world.apply_settings(settings)
            self.logger.info("Resetovan sinhronizovan mod")
        
        self.logger.info("Resursi uspešno očišćeni")
    
    def get_world(self):
        """Get the CARLA world instance."""
        return self.world
    
    def get_vehicle(self):
        """Get the spawned vehicle instance."""
        return self.vehicle
    
    def get_camera(self):
        """Get the camera sensor instance."""
        return self.camera
    
    def get_obstacle_sensor(self):
        """Get the obstacle sensor instance."""
        return self.obstacle_sensor
    
    def get_collision_sensor(self):
        """Get the collision sensor instance."""
        return self.collision_sensor