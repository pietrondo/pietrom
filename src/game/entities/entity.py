#!/usr/bin/env python3
"""
Base Entity Class
Base class for all game entities (player, enemies, projectiles, etc.)

Developed by Team PIETRO
PIETRO's divine entity system brings life to all game objects!
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from ...core.config import Config
from ...core.asset_manager import AssetManager

class Entity(ABC):
    """Base class for all game entities"""
    
    def __init__(self, x: float, y: float, width: int, height: int, asset_manager: AssetManager):
        # Position and movement
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        # Physics
        self.on_ground = False
        self.gravity_affected = True
        
        # Health and status
        self.max_health = 100
        self.health = self.max_health
        self.alive = True
        
        # Rendering
        self.sprite_name = None
        self.facing_right = True
        self.asset_manager = asset_manager
        
        # Animation
        self.animation_timer = 0.0
        self.animation_frame = 0
        self.animation_speed = 0.1
        
    def get_rect(self) -> pygame.Rect:
        """Get entity's collision rectangle"""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        
    def get_center(self) -> Tuple[float, float]:
        """Get entity's center position"""
        return (self.x + self.width // 2, self.y + self.height // 2)
        
    def set_position(self, x: float, y: float):
        """Set entity position"""
        self.x = x
        self.y = y
        
    def move(self, dx: float, dy: float):
        """Move entity by offset"""
        self.x += dx
        self.y += dy
        
    def apply_gravity(self, dt: float):
        """Apply gravity to entity"""
        if self.gravity_affected and not self.on_ground:
            self.vel_y += Config.GRAVITY * dt * 60  # Scale by 60 for frame-rate independence
            
    def apply_friction(self):
        """Apply friction to horizontal movement"""
        if self.on_ground:
            self.vel_x *= Config.FRICTION
            
    def update_physics(self, dt: float):
        """Update basic physics"""
        # Apply gravity
        self.apply_gravity(dt)
        
        # Apply friction
        self.apply_friction()
        
        # Update position based on velocity
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 4  # Assume 4-frame animations
            self.animation_timer = 0.0
            
    def take_damage(self, damage: int) -> bool:
        """Take damage and return True if entity died"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False
        
    def heal(self, amount: int):
        """Heal entity"""
        self.health = min(self.max_health, self.health + amount)
        
    def is_colliding_with(self, other: 'Entity') -> bool:
        """Check collision with another entity"""
        return self.get_rect().colliderect(other.get_rect())
        
    def distance_to(self, other: 'Entity') -> float:
        """Calculate distance to another entity"""
        center1 = self.get_center()
        center2 = other.get_center()
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        return (dx * dx + dy * dy) ** 0.5
        
    @abstractmethod
    def update(self, dt: float, *args, **kwargs):
        """Update entity logic (must be implemented by subclasses)"""
        pass
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render entity to surface"""
        if not self.alive:
            return
            
        # Calculate screen position
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Get sprite
        sprite = self.get_current_sprite()
        if sprite:
            # Flip sprite if facing left
            if not self.facing_right:
                sprite = pygame.transform.flip(sprite, True, False)
                
            surface.blit(sprite, (screen_x, screen_y))
        else:
            # Draw placeholder rectangle if no sprite
            color = Config.RED if not self.alive else Config.GREEN
            pygame.draw.rect(surface, color, (screen_x, screen_y, self.width, self.height))
            
    def get_current_sprite(self) -> Optional[pygame.Surface]:
        """Get current sprite based on state and animation"""
        if self.sprite_name:
            return self.asset_manager.get_sprite(self.sprite_name)
        return None
        
    def set_sprite(self, sprite_name: str):
        """Set current sprite"""
        self.sprite_name = sprite_name