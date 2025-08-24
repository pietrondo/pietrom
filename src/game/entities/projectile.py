#!/usr/bin/env python3
"""
Projectile System
Bullets, rockets and other projectiles

Developed by Team PIETRO
PIETRO's projectiles fly true and strike with divine precision!
"""

import pygame
from typing import TYPE_CHECKING, List
from ...core.config import Config
from .entity import Entity

if TYPE_CHECKING:
    # from ..world.level import Level  # Removed - now using collision_rects
    pass

class Projectile(Entity):
    """Base projectile class"""
    
    def __init__(self, x: float, y: float, width: int, height: int, facing_right: bool, asset_manager):
        super().__init__(x, y, width, height, asset_manager)
        
        # Projectile properties
        self.damage = 10
        self.speed = 400
        self.lifetime = 5.0  # Seconds before auto-destruction
        self.active = True
        self.facing_right = facing_right
        
        # Physics
        self.gravity_affected = False
        
        # Set initial velocity
        direction = 1 if facing_right else -1
        self.vel_x = self.speed * direction
        
    def update(self, dt: float, collision_rects: List[pygame.Rect]):
        """Update projectile"""
        if not self.active:
            return
            
        # Update physics
        self.update_physics(dt)
        
        # Check lifetime
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.active = False
            return
            
        # Check collision with world
        projectile_rect = pygame.Rect(int(self.x) - 2, int(self.y) - 2, 4, 4)
        for rect in collision_rects:
            if projectile_rect.colliderect(rect):
                self._on_hit_wall()
                return
            
        # Check bounds (assume 60x20 tile map)
        if (self.x < -100 or self.x > 60 * 32 + 100 or 
            self.y < -100 or self.y > 20 * 32 + 100):
            self.active = False
            
    def _on_hit_wall(self):
        """Called when projectile hits a wall"""
        self.active = False
        
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render projectile"""
        if not self.active:
            return
            
        super().render(surface, camera_offset)

class Bullet(Projectile):
    """Standard bullet projectile"""
    
    def __init__(self, x: float, y: float, facing_right: bool, asset_manager):
        super().__init__(x, y, 4, 2, facing_right, asset_manager)
        
        self.damage = Config.PISTOL_DAMAGE
        self.speed = 600
        self.set_sprite("bullet")
        
    def _on_hit_wall(self):
        """Bullet disappears on wall hit"""
        super()._on_hit_wall()
        # Could add spark effect here

class Rocket(Projectile):
    """Rocket projectile with explosion"""
    
    def __init__(self, x: float, y: float, facing_right: bool, asset_manager):
        super().__init__(x, y, 8, 4, facing_right, asset_manager)
        
        self.damage = Config.ROCKET_DAMAGE
        self.speed = 300
        self.explosion_radius = 64
        self.set_sprite("rocket")
        
        # Rocket has slight gravity
        self.gravity_affected = True
        
    def _on_hit_wall(self):
        """Rocket explodes on wall hit"""
        self._explode()
        
    def _explode(self):
        """Create explosion effect"""
        self.active = False
        
        # Play explosion sound
        self.asset_manager.play_sound("explosion")
        
        # TODO: Create explosion effect and damage nearby entities
        
    def update(self, dt: float, level: 'Level'):
        """Update rocket with trail effect"""
        super().update(dt, level)
        
        # Add some smoke trail effect here if needed
        
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render rocket with flame trail"""
        if not self.active:
            return
            
        # Render main rocket
        super().render(surface, camera_offset)
        
        # Render flame trail
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Simple flame trail
        trail_length = 16
        trail_x = screen_x - (trail_length if self.facing_right else -trail_length)
        
        flame_color = Config.YELLOW if self.animation_frame % 2 == 0 else Config.RED
        pygame.draw.circle(surface, flame_color, (trail_x, screen_y + self.height // 2), 3)

class EnemyBullet(Projectile):
    """Enemy bullet projectile"""
    
    def __init__(self, x: float, y: float, facing_right: bool, asset_manager):
        super().__init__(x, y, 3, 2, facing_right, asset_manager)
        
        self.damage = 15
        self.speed = 400
        
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render enemy bullet with different color"""
        if not self.active:
            return
            
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Draw red bullet for enemies
        pygame.draw.rect(surface, Config.RED, (screen_x, screen_y, self.width, self.height))