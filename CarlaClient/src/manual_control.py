"""
Manual Control Module for CARLA
===============================

This module contains the ManualControl class that handles vehicle control
using keyboard input and displays the live camera feed.
"""

import carla
import pygame
import numpy as np


class ManualControl:
    """
    Handles manual vehicle control using WASD keys and displays live camera feed.
    """
    
    def __init__(self, world, vehicle, adas_subscriber=None, carla_setup=None):
        """
        Initialize the manual control system.
        
        Args:
            world: CARLA world instance
            vehicle: CARLA vehicle instance to control
            adas_subscriber: Optional ADAS subscriber for command overrides
            carla_setup: Optional CarlaSetup instance for pedestrian info
        """
        self.world = world
        self.vehicle = vehicle
        self.control = carla.VehicleControl()
        self.adas_subscriber = adas_subscriber
        self.carla_setup = carla_setup
        
        # Gear system
        self.current_gear = 1  # Start in first gear (0=reverse, 1-6=forward gears)
        self.is_reverse_mode = False  # Track if we're in reverse mode
        self.gear_speeds = {
            0: 20,   # Reverse - max 20 km/h
            1: 30,   # 1st gear - max 30 km/h
            2: 50,   # 2nd gear - max 50 km/h
            3: 80,   # 3rd gear - max 80 km/h
            4: 120,  # 4th gear - max 120 km/h
            5: 160,  # 5th gear - max 160 km/h
            6: 200   # 6th gear - max 200 km/h
        }
        self.max_gear = 6
        self.reverse_gear = 0
        
        # Pygame setup
        pygame.init()
        self.display = pygame.display.set_mode((640, 360))
        pygame.display.set_caption('CARLA Manual Driving - WASD Controls')
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.current_image = None

    def set_current_image(self, image):
        """
        Set the current image from camera callback.
        
        Args:
            image: Processed numpy array image from camera
        """
        self.current_image = image

    def shift_gear_up(self):
        """Shift to higher gear."""
        if self.is_reverse_mode:
            # From reverse, go to 1st gear
            self.current_gear = 1
            self.is_reverse_mode = False
            print("🔧 Prebačeno na 1. brzinu")
        elif self.current_gear < self.max_gear:
            self.current_gear += 1
            self.is_reverse_mode = False
            print(f"🔧 Prebačeno na {self.current_gear}. brzinu")

    def shift_gear_down(self):
        """Shift to lower gear."""
        if self.current_gear > 1:
            self.current_gear -= 1
            self.is_reverse_mode = False
            print(f"🔧 Prebačeno na {self.current_gear}. brzinu")
        elif self.current_gear == 1:
            # From 1st gear, go to reverse
            self.shift_to_reverse()

    def shift_to_reverse(self):
        """Shift to reverse gear."""
        self.current_gear = self.reverse_gear
        self.is_reverse_mode = True
        print("🔧 Prebačeno u rikverc")

    def get_gear_name(self):
        """Get display name for current gear."""
        if self.is_reverse_mode:
            return "R"
        else:
            return str(self.current_gear)

    def get_max_speed_for_gear(self):
        """Get maximum speed for current gear."""
        if self.is_reverse_mode:
            return self.gear_speeds[self.reverse_gear]
        return self.gear_speeds.get(self.current_gear, 50)

    def process_input(self):
        """Procesira input sa tastature."""
        keys = pygame.key.get_pressed()
        
        # Reset control
        self.control.throttle = 0.0
        self.control.brake = 0.0
        self.control.steer = 0.0
        self.control.hand_brake = False
        
        # Get current vehicle speed
        velocity = self.vehicle.get_velocity()
        current_speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5
        max_speed = self.get_max_speed_for_gear()
        
        # Throttle (W) - gas (forward or reverse depending on current gear)
        if keys[pygame.K_w]:
            if current_speed < max_speed:
                self.control.throttle = 0.8
                # Set reverse mode based on current gear
                if self.is_reverse_mode:
                    self.control.reverse = True
                else:
                    self.control.reverse = False
            else:
                self.control.throttle = 0.2  # Reduced throttle when at speed limit
                if self.is_reverse_mode:
                    self.control.reverse = True
        
        # Brake (S) - always brake, never change gear
        if keys[pygame.K_s]:
            self.control.brake = 0.8
            self.control.reverse = False  # Stop any movement when braking
        
        # Steer left (A)
        if keys[pygame.K_a]:
            self.control.steer = -0.5
        
        # Steer right (D)
        if keys[pygame.K_d]:
            self.control.steer = 0.5
        
        # Hand brake (Q)
        if keys[pygame.K_q]:
            self.control.hand_brake = True
        
        # Apply ADAS overrides if subscriber is available
        if self.adas_subscriber:
            # Check lane assist override
            la_active, la_angle = self.adas_subscriber.get_lane_assist_override()
            if la_active:
                self.control.steer = la_angle  # Override driver steering
            
            # Check emergency brake override
            eb_active, eb_force = self.adas_subscriber.get_emergency_brake_override()
            if eb_active:
                self.control.brake = eb_force  # Override driver brake
                self.control.throttle = 0.0    # Cut throttle when emergency braking
        
        # Primeni kontrol na vozilo
        self.vehicle.apply_control(self.control)

    def render_frame(self):
        """Renderuje trenutni frame sa kamere."""
        if self.current_image is not None:
            # Konvertuj OpenCV format u pygame
            image_surface = pygame.surfarray.make_surface(self.current_image.swapaxes(0, 1))
            
            # Skaliraj na display veličinu
            image_surface = pygame.transform.scale(image_surface, (640, 360))
            self.display.blit(image_surface, (0, 0))
        
        pygame.display.flip()

    def run(self):
        """Glavna petlja za ručno upravljanje."""
        try:
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        # Gear shifting controls
                        elif event.key == pygame.K_r:
                            # Check if Shift is pressed for reverse
                            keys = pygame.key.get_pressed()
                            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                                self.shift_to_reverse()
                            else:
                                self.shift_gear_up()
                        elif event.key == pygame.K_f:
                            self.shift_gear_down()
                
                # Process input and update vehicle
                self.process_input()
                
                # Tick world u sinhronizovanom modu
                self.world.tick()
                
                # Render frame
                self.render_frame()
                
                # Control frame rate
                self.clock.tick(30)  # 30 FPS za bolje performanse
                
        except KeyboardInterrupt:
            print("Manual control interrupted")
        finally:
            pygame.quit()