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
    
    def __init__(self, world, vehicle):
        """
        Initialize the manual control system.
        
        Args:
            world: CARLA world instance
            vehicle: CARLA vehicle instance to control
        """
        self.world = world
        self.vehicle = vehicle
        self.control = carla.VehicleControl()
        
        # Pygame setup
        pygame.init()
        self.display = pygame.display.set_mode((640, 360))
        pygame.display.set_caption('CARLA Manual Driving - WASD Controls')
        self.clock = pygame.time.Clock()
        
        # Font za prikaz informacija
        self.font = pygame.font.Font(None, 36)
        
        self.running = True
        self.current_image = None

    def set_current_image(self, image):
        """
        Set the current image from camera callback.
        
        Args:
            image: Processed numpy array image from camera
        """
        self.current_image = image

    def process_input(self):
        """Procesira input sa tastature."""
        keys = pygame.key.get_pressed()
        
        # Reset control
        self.control.throttle = 0.0
        self.control.brake = 0.0
        self.control.steer = 0.0
        self.control.hand_brake = False
        
        # Throttle (W)
        if keys[pygame.K_w]:
            self.control.throttle = 0.8
        
        # Brake/Reverse (S)
        if keys[pygame.K_s]:
            self.control.brake = 0.8
        
        # Steer left (A)
        if keys[pygame.K_a]:
            self.control.steer = -0.5
        
        # Steer right (D)
        if keys[pygame.K_d]:
            self.control.steer = 0.5
        
        # Hand brake (Q)
        if keys[pygame.K_q]:
            self.control.hand_brake = True
        
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
            
            # Dodaj informacije o kontroli
            self.render_info()
        
        pygame.display.flip()

    def render_info(self):
        """Prikazuje informacije o trenutnim kontrolama."""
        # Velocity
        velocity = self.vehicle.get_velocity()
        speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5
        
        # Control info
        info_lines = [
            f"Speed: {speed:.1f} km/h",
            f"Throttle: {self.control.throttle:.2f}",
            f"Brake: {self.control.brake:.2f}",
            f"Steer: {self.control.steer:.2f}",
            "Controls: W-Gas, S-Brake, A/D-Steer, Q-HandBrake, ESC-Exit"
        ]
        
        y_offset = 10
        for line in info_lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.display.blit(text_surface, (10, y_offset))
            y_offset += 30

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