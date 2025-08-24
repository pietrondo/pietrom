import pygame
from typing import Tuple
from ...core.config import Config

class Camera:
    """Camera system for following player and managing viewport"""
    
    def __init__(self, width: int, height: int):
        self.x = 0.0
        self.y = 0.0
        self.width = width
        self.height = height
        self.target_x = 0.0
        self.target_y = 0.0
        self.smoothing = 0.1  # Camera smoothing factor
        
    def update(self, dt: float, target_x: float, target_y: float, level_width: int = None, level_height: int = None):
        """Update camera position to follow target"""
        # Calculate target position (center target on screen)
        self.target_x = target_x - self.width // 2
        self.target_y = target_y - self.height // 2
        
        # Apply smoothing
        self.x += (self.target_x - self.x) * self.smoothing
        self.y += (self.target_y - self.y) * self.smoothing
        
        # Clamp camera to level bounds if provided
        if level_width:
            self.x = max(0, min(self.x, level_width - self.width))
        if level_height:
            self.y = max(0, min(self.y, level_height - self.height))
            
    def get_offset(self) -> Tuple[int, int]:
        """Get camera offset for rendering"""
        return (int(self.x), int(self.y))
        
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        screen_x = int(world_x - self.x)
        screen_y = int(world_y - self.y)
        return (screen_x, screen_y)
        
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)
        
    def is_visible(self, x: float, y: float, width: float, height: float) -> bool:
        """Check if a rectangle is visible in camera view"""
        return not (x + width < self.x or 
                   x > self.x + self.width or
                   y + height < self.y or 
                   y > self.y + self.height)
    
    def set_position(self, x: float, y: float):
        """Set camera position directly"""
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
    
    def get_position(self) -> Tuple[float, float]:
        """Get current camera position"""
        return (self.x, self.y)
    
    def follow_target(self, target_x: float, target_y: float):
        """Set target for camera to follow"""
        self.target_x = target_x - self.width // 2
        self.target_y = target_y - self.height // 2