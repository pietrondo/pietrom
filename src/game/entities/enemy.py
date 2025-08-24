#!/usr/bin/env python3
"""
Enemy System
Various enemy types with AI behaviors

Developed by Team PIETRO
PIETRO's adversaries provide worthy challenges for his chosen warrior!
"""

import pygame
import random
import math
from typing import Optional, TYPE_CHECKING, List
from ...core.config import Config
from .entity import Entity
from .projectile import EnemyBullet

if TYPE_CHECKING:
    # from ..world.level import Level  # Removed - now using collision_rects
    from .player import Player

class Enemy(Entity):
    """Base enemy class with AI"""
    
    def __init__(self, x: float, y: float, width: int, height: int, asset_manager):
        super().__init__(x, y, width, height, asset_manager)
        
        # AI properties
        self.detection_range = 200
        self.attack_range = 150
        self.patrol_distance = 100
        self.patrol_start_x = x
        self.patrol_direction = 1
        
        # AI state
        self.state = "patrol"  # patrol, chase, attack, idle
        self.target: Optional['Player'] = None
        self.last_seen_target_x = 0
        self.state_timer = 0.0
        
        # Combat
        self.attack_cooldown = 0.0
        self.attack_damage = 20
        self.projectiles = []
        
        # Movement
        self.move_speed = 2.0
        self.jump_speed = -10
        
    def update(self, dt: float, player: 'Player', collision_rects: List[pygame.Rect]):
        """Update enemy AI and behavior"""
        if not self.alive:
            return
            
        # Update timers
        self.state_timer += dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Update AI
        self._update_ai(dt, player, collision_rects)
        
        # Update physics
        self.update_physics(dt)
        
        # Handle world collision
        self._handle_world_collision(collision_rects)
        
        # Update projectiles
        self._update_projectiles(dt, collision_rects)
        
    def _update_ai(self, dt: float, player: 'Player', collision_rects: List[pygame.Rect]):
        """Update AI state machine"""
        if not player or not player.alive:
            self.state = "patrol"
            self.target = None
            return
            
        distance_to_player = self.distance_to(player)
        can_see_player = self._can_see_target(player, collision_rects)
        
        # State transitions
        if self.state == "patrol":
            if can_see_player and distance_to_player <= self.detection_range:
                self.state = "chase"
                self.target = player
                self.state_timer = 0
                
        elif self.state == "chase":
            if not can_see_player and self.state_timer > 3.0:  # Lost sight for 3 seconds
                self.state = "patrol"
                self.target = None
            elif distance_to_player <= self.attack_range:
                self.state = "attack"
                self.state_timer = 0
                
        elif self.state == "attack":
            if distance_to_player > self.attack_range * 1.5:
                self.state = "chase"
                self.state_timer = 0
                
        # Execute state behavior
        if self.state == "patrol":
            self._patrol_behavior(dt)
        elif self.state == "chase":
            self._chase_behavior(dt, player)
        elif self.state == "attack":
            self._attack_behavior(dt, player)
            
    def _patrol_behavior(self, dt: float):
        """Patrol back and forth"""
        # Move in patrol direction
        self.vel_x = self.move_speed * self.patrol_direction
        self.facing_right = self.patrol_direction > 0
        
        # Check if reached patrol boundary
        if (self.patrol_direction > 0 and self.x > self.patrol_start_x + self.patrol_distance) or \
           (self.patrol_direction < 0 and self.x < self.patrol_start_x - self.patrol_distance):
            self.patrol_direction *= -1
            
    def _chase_behavior(self, dt: float, player: 'Player'):
        """Chase the player"""
        if not player:
            return
            
        # Move towards player
        if player.x > self.x:
            self.vel_x = self.move_speed * 1.5  # Move faster when chasing
            self.facing_right = True
        else:
            self.vel_x = -self.move_speed * 1.5
            self.facing_right = False
            
        # Remember last seen position
        self.last_seen_target_x = player.x
        
        # Jump if player is above and close
        if (abs(player.x - self.x) < 50 and player.y < self.y - 32 and 
            self.on_ground and random.random() < 0.02):  # 2% chance per frame
            self.vel_y = self.jump_speed
            
    def _attack_behavior(self, dt: float, player: 'Player'):
        """Attack the player"""
        if not player:
            return
            
        # Face the player
        self.facing_right = player.x > self.x
        
        # Stop moving when attacking
        self.vel_x *= 0.5
        
        # Attack if cooldown is ready
        if self.attack_cooldown <= 0:
            self._perform_attack(player)
            self.attack_cooldown = 1.0  # 1 second cooldown
            
    def _perform_attack(self, player: 'Player'):
        """Perform attack (override in subclasses)"""
        # Default: shoot projectile
        self._shoot_at_target(player)
        
    def _shoot_at_target(self, target: 'Player'):
        """Shoot projectile at target"""
        # Calculate projectile spawn position
        spawn_x = self.x + (self.width if self.facing_right else 0)
        spawn_y = self.y + self.height // 2
        
        # Create bullet
        bullet = EnemyBullet(spawn_x, spawn_y, self.facing_right, self.asset_manager)
        bullet.damage = self.attack_damage
        
        # Aim at target (simple leading)
        dx = target.x - spawn_x
        dy = target.y - spawn_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            bullet.vel_x = (dx / distance) * bullet.speed
            bullet.vel_y = (dy / distance) * bullet.speed
            
        self.projectiles.append(bullet)
        
    def _can_see_target(self, target: 'Player', collision_rects: List[pygame.Rect]) -> bool:
        """Check if enemy can see the target (simple line of sight)"""
        if not target:
            return False
            
        # Simple distance check for now
        distance = self.distance_to(target)
        return distance <= self.detection_range
        
    def _handle_world_collision(self, collision_rects: List[pygame.Rect]):
        """Handle collision with world geometry"""
        enemy_rect = self.get_rect()
        ground_check_rect = pygame.Rect(enemy_rect.x, enemy_rect.bottom, enemy_rect.width, 2)
        
        # Check if on ground
        self.on_ground = False
        for rect in collision_rects:
            if ground_check_rect.colliderect(rect):
                self.on_ground = True
                break
        
        # Reset vertical velocity if on ground
        if self.on_ground and self.vel_y > 0:
            self.vel_y = 0
            
    def _update_projectiles(self, dt: float, collision_rects: List[pygame.Rect]):
        """Update enemy projectiles"""
        for projectile in self.projectiles[:]:
            projectile.update(dt, collision_rects)
            
            # Remove inactive projectiles
            if not projectile.active:
                self.projectiles.remove(projectile)
                
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render enemy and projectiles"""
        if not self.alive:
            return
            
        # Render enemy sprite
        super().render(surface, camera_offset)
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(surface, camera_offset)
            
        # Render health bar
        self._render_health_bar(surface, camera_offset)
        
    def _render_health_bar(self, surface: pygame.Surface, camera_offset: tuple):
        """Render enemy health bar"""
        if self.health >= self.max_health:
            return  # Don't show full health bar
            
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1] - 10)
        
        bar_width = self.width
        bar_height = 4
        
        # Background
        pygame.draw.rect(surface, Config.RED, (screen_x, screen_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(surface, Config.GREEN, (screen_x, screen_y, health_width, bar_height))

class MutantEnemy(Enemy):
    """Mutant enemy - fast and aggressive"""
    
    def __init__(self, x: float, y: float, asset_manager):
        super().__init__(x, y, 32, 32, asset_manager)
        
        self.max_health = Config.MUTANT_HEALTH
        self.health = self.max_health
        self.move_speed = 3.0
        self.attack_damage = 15
        self.detection_range = 250
        self.set_sprite("mutant")
        
    def _perform_attack(self, player: 'Player'):
        """Mutant performs melee attack"""
        # Check if close enough for melee
        if self.distance_to(player) < 40:
            player.take_damage(self.attack_damage)
            # Add screen shake or hit effect here
        else:
            # Shoot if not in melee range
            self._shoot_at_target(player)

class RobotEnemy(Enemy):
    """Robot enemy - tough and shoots accurately"""
    
    def __init__(self, x: float, y: float, asset_manager):
        super().__init__(x, y, 32, 48, asset_manager)
        
        self.max_health = Config.ROBOT_HEALTH
        self.health = self.max_health
        self.move_speed = 1.5
        self.attack_damage = 25
        self.attack_range = 200
        self.set_sprite("robot")
        
    def _perform_attack(self, player: 'Player'):
        """Robot shoots with high accuracy"""
        self._shoot_at_target(player)
        
        # Robots can shoot multiple bullets
        if random.random() < 0.3:  # 30% chance for burst fire
            # Schedule second shot
            pass  # Could implement burst fire here

class MercenaryEnemy(Enemy):
    """Mercenary enemy - balanced and tactical"""
    
    def __init__(self, x: float, y: float, asset_manager):
        super().__init__(x, y, 32, 64, asset_manager)
        
        self.max_health = Config.MERCENARY_HEALTH
        self.health = self.max_health
        self.move_speed = 2.5
        self.attack_damage = 30
        self.detection_range = 300
        self.set_sprite("mercenary")
        
        # Mercenaries can take cover
        self.taking_cover = False
        self.cover_timer = 0.0
        
    def _attack_behavior(self, dt: float, player: 'Player'):
        """Mercenary uses cover and tactical movement"""
        super()._attack_behavior(dt, player)
        
        # Occasionally take cover
        if not self.taking_cover and random.random() < 0.01:  # 1% chance per frame
            self.taking_cover = True
            self.cover_timer = 2.0
            
        if self.taking_cover:
            self.cover_timer -= dt
            if self.cover_timer <= 0:
                self.taking_cover = False
                
    def _perform_attack(self, player: 'Player'):
        """Mercenary attacks tactically"""
        if not self.taking_cover:
            self._shoot_at_target(player)