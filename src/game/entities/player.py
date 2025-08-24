#!/usr/bin/env python3
"""
Player Class
Main player character with weapons, movement, and abilities

Developed by Team PIETRO
PIETRO's chosen warrior, armed and ready for battle!
"""

import pygame
from typing import List, Optional, TYPE_CHECKING
from ...core.config import Config
from ...core.input_manager import InputManager
from .entity import Entity
from .projectile import Bullet, Rocket
from .weapon import Weapon, WeaponType
from .animation import PlayerAnimator, AnimationState

if TYPE_CHECKING:
    # from ..world.level import Level  # Removed - now using collision_rects
    pass

class Player(Entity):
    """Player character class"""
    
    def __init__(self, x: float, y: float, asset_manager):
        super().__init__(x, y, Config.PLAYER_SIZE[0], Config.PLAYER_SIZE[1], asset_manager)
        
        # Player stats
        self.max_health = Config.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.speed = Config.PLAYER_SPEED
        self.jump_speed = Config.PLAYER_JUMP_SPEED
        
        # Movement state
        self.is_jumping = False
        self.is_moving = False
        self.can_jump = True
        self.jump_buffer = 0.0
        self.coyote_time = 0.0
        
        # Weapons system
        self.weapons: List[Weapon] = []
        self.current_weapon_index = 0
        self.projectiles: List = []
        self.shoot_cooldown = 0.0
        
        # Initialize weapons
        self._init_weapons()
        
        # Utilities
        self.has_jetpack = False
        self.jetpack_fuel = 100.0
        self.max_jetpack_fuel = 100.0
        self.jetpack_active = False
        
        self.has_flashlight = True
        self.flashlight_on = False
        
        self.has_scanner = False
        self.scanner_active = False
        
        # Collectibles
        self.score = 0
        self.keys_collected = 0
        
        # Animation system
        self.animator = PlayerAnimator("assets/sprites/player.png")
        self.current_animation_state = AnimationState.IDLE
        
        # Action states for animations
        self.is_shooting = False
        self.is_changing_weapon = False
        self.is_using_utility = False
        self.action_timer = 0.0
        
    def _init_weapons(self):
        """Initialize player weapons"""
        # Start with pistol
        pistol = Weapon(WeaponType.PISTOL, self.asset_manager)
        pistol.ammo = 50  # Start with some ammo
        self.weapons.append(pistol)
        
        # Add other weapons (initially without ammo)
        shotgun = Weapon(WeaponType.SHOTGUN, self.asset_manager)
        rocket_launcher = Weapon(WeaponType.ROCKET_LAUNCHER, self.asset_manager)
        
        self.weapons.extend([shotgun, rocket_launcher])
        
    def get_current_weapon(self) -> Optional[Weapon]:
        """Get currently selected weapon"""
        if 0 <= self.current_weapon_index < len(self.weapons):
            return self.weapons[self.current_weapon_index]
        return None
        
    def switch_weapon(self):
        """Switch to next weapon"""
        if len(self.weapons) > 1:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)
            # Attiva animazione cambio arma
            self.is_changing_weapon = True
            self.action_timer = 0.4  # Durata animazione cambio arma
            
    def add_ammo(self, weapon_type: WeaponType, amount: int):
        """Add ammo for specific weapon type"""
        for weapon in self.weapons:
            if weapon.weapon_type == weapon_type:
                weapon.add_ammo(amount)
                break
                
    def update(self, dt: float, input_manager: InputManager, collision_rects: List[pygame.Rect]):
        """Update player logic"""
        if not self.alive:
            return
            
        # Handle input
        self._handle_input(dt, input_manager)
        
        # Update physics
        self.update_physics(dt)
        
        # Handle collisions with world
        self._handle_world_collision(collision_rects)
        
        # Update weapons and projectiles
        self._update_weapons(dt)
        self._update_projectiles(dt, collision_rects)
        
        # Update utilities
        self._update_utilities(dt)
        
        # Update animation state
        self._update_animation_state()
        
        # Update timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
            
        if self.jump_buffer > 0:
            self.jump_buffer -= dt
            
        if self.coyote_time > 0:
            self.coyote_time -= dt
            
    def _handle_input(self, dt: float, input_manager: InputManager):
        """Handle player input"""
        # Movement
        horizontal, _ = input_manager.get_movement_input()
        
        if horizontal != 0:
            self.vel_x = horizontal * self.speed
            self.facing_right = horizontal > 0
            self.is_moving = True
        else:
            self.is_moving = False
            
        # Jumping
        if input_manager.is_jump_pressed():
            self.jump_buffer = 0.1  # Jump buffer time
            
        if self.jump_buffer > 0 and (self.on_ground or self.coyote_time > 0):
            self.vel_y = self.jump_speed
            self.is_jumping = True
            self.on_ground = False
            self.jump_buffer = 0
            self.coyote_time = 0
            
        # Shooting
        if input_manager.is_shoot_pressed() and self.shoot_cooldown <= 0:
            self._shoot()
            
        # Weapon switching
        if input_manager.is_weapon_switch_pressed():
            self.switch_weapon()
            
        # Utilities
        if input_manager.is_utility_pressed():
            self._use_utility()
            
        # Jetpack
        if self.has_jetpack and input_manager.is_key_pressed(pygame.K_SPACE) and not self.on_ground:
            if self.jetpack_fuel > 0:
                self.jetpack_active = True
                self.vel_y = min(self.vel_y, -2)  # Counteract gravity
                self.jetpack_fuel -= 50 * dt
            else:
                self.jetpack_active = False
        else:
            self.jetpack_active = False
            
    def _shoot(self):
        """Shoot current weapon"""
        weapon = self.get_current_weapon()
        if not weapon or not weapon.can_shoot():
            return
            
        # Attiva animazione di sparo
        self.is_shooting = True
        self.action_timer = 0.3  # Durata animazione sparo
            
        # Calculate projectile spawn position
        spawn_x = self.x + (self.width if self.facing_right else 0)
        spawn_y = self.y + self.height // 2
        
        # Create projectile based on weapon type
        if weapon.weapon_type == WeaponType.PISTOL:
            projectile = Bullet(spawn_x, spawn_y, self.facing_right, self.asset_manager)
            projectile.damage = Config.PISTOL_DAMAGE
            
        elif weapon.weapon_type == WeaponType.SHOTGUN:
            # Create multiple bullets for shotgun
            for i in range(3):
                angle_offset = (i - 1) * 0.2  # Spread bullets
                projectile = Bullet(spawn_x, spawn_y, self.facing_right, self.asset_manager)
                projectile.damage = Config.SHOTGUN_DAMAGE // 3
                projectile.vel_y += angle_offset * 100
                self.projectiles.append(projectile)
            weapon.shoot()
            self.shoot_cooldown = weapon.fire_rate
            return
            
        elif weapon.weapon_type == WeaponType.ROCKET_LAUNCHER:
            projectile = Rocket(spawn_x, spawn_y, self.facing_right, self.asset_manager)
            projectile.damage = Config.ROCKET_DAMAGE
            
        else:
            return
            
        self.projectiles.append(projectile)
        weapon.shoot()
        self.shoot_cooldown = weapon.fire_rate
        
    def _use_utility(self):
        """Use current utility item"""
        if self.has_flashlight:
            self.flashlight_on = not self.flashlight_on
            # Attiva animazione uso utility
            self.is_using_utility = True
            self.action_timer = 0.5  # Durata animazione utility
        elif self.has_scanner:
            self.scanner_active = not self.scanner_active
            # Attiva animazione uso utility
            self.is_using_utility = True
            self.action_timer = 0.5  # Durata animazione utility
            
    def _handle_world_collision(self, collision_rects: List[pygame.Rect]):
        """Handle collision with world geometry"""
        if not collision_rects:
            return
            
        # Simple collision detection with world tiles
        player_rect = self.get_rect()
        
        # Check if on ground
        ground_check_rect = pygame.Rect(player_rect.x, player_rect.bottom, player_rect.width, 2)
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # Check collision with all solid rects
        for rect in collision_rects:
            if ground_check_rect.colliderect(rect):
                self.on_ground = True
                break
        
        # Coyote time - allow jumping briefly after leaving ground
        if was_on_ground and not self.on_ground:
            self.coyote_time = 0.1
            
        # Reset vertical velocity if on ground
        if self.on_ground and self.vel_y > 0:
            self.vel_y = 0
            self.is_jumping = False
            
        # Recharge jetpack when on ground
        if self.on_ground and self.jetpack_fuel < self.max_jetpack_fuel:
            self.jetpack_fuel = min(self.max_jetpack_fuel, self.jetpack_fuel + 30 * 0.016)  # Assuming 60 FPS
            
    def _update_weapons(self, dt: float):
        """Update weapon states"""
        for weapon in self.weapons:
            weapon.update(dt)
            
    def _update_projectiles(self, dt: float, collision_rects: List[pygame.Rect]):
        """Update player projectiles"""
        for projectile in self.projectiles[:]:
            projectile.update(dt, collision_rects)
            
            # Remove projectiles that are no longer active
            if not projectile.active:
                self.projectiles.remove(projectile)
                
    def _update_utilities(self, dt: float):
        """Update utility states"""
        # Update jetpack fuel regeneration
        if not self.jetpack_active and self.jetpack_fuel < self.max_jetpack_fuel:
            self.jetpack_fuel = min(self.max_jetpack_fuel, self.jetpack_fuel + 20 * dt)
            
    def _update_animation_state(self):
        """Update animation state based on player state"""
        # Aggiorna timer delle azioni
        if self.action_timer > 0:
            self.action_timer -= 0.016  # Circa 60 FPS
        
        # Determina lo stato di animazione basato sulle azioni e movimento
        new_state = AnimationState.IDLE
        
        # Priorità alle azioni temporanee
        if self.is_shooting and self.action_timer > 0:
            new_state = AnimationState.SHOOTING
        elif self.is_changing_weapon and self.action_timer > 0:
            new_state = AnimationState.WEAPON_CHANGE
        elif self.is_using_utility and self.action_timer > 0:
            new_state = AnimationState.UTILITY_USE
        # Stati di movimento
        elif not self.on_ground:
            new_state = AnimationState.JUMPING
        elif self.is_moving:
            new_state = AnimationState.RUNNING
        else:
            new_state = AnimationState.IDLE
        
        # Aggiorna lo stato dell'animatore
        if new_state != self.current_animation_state:
            self.animator.set_state(new_state)
            self.current_animation_state = new_state
        
        # Aggiorna la direzione
        self.animator.set_facing_direction(self.facing_right)
        
        # Aggiorna l'animatore
        self.animator.update(0.016)  # Circa 60 FPS
        
        # Reset delle azioni quando l'animazione è finita
        if self.animator.is_animation_finished():
            if self.is_shooting:
                self.is_shooting = False
            elif self.is_changing_weapon:
                self.is_changing_weapon = False
            elif self.is_using_utility:
                self.is_using_utility = False
            
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render player and effects"""
        # Render player sprite usando il nuovo sistema di animazioni
        current_sprite = self.animator.get_current_sprite()
        if current_sprite:
            screen_x = int(self.x - camera_offset[0])
            screen_y = int(self.y - camera_offset[1])
            surface.blit(current_sprite, (screen_x, screen_y))
        
        # Render projectiles
        for projectile in self.projectiles:
            projectile.render(surface, camera_offset)
            
        # Render jetpack effect
        if self.jetpack_active:
            self._render_jetpack_effect(surface, camera_offset)
            
        # Render flashlight effect
        if self.flashlight_on:
            self._render_flashlight_effect(surface, camera_offset)
            
    def _render_jetpack_effect(self, surface: pygame.Surface, camera_offset: tuple):
        """Render jetpack flame effect"""
        screen_x = int(self.x - camera_offset[0] + self.width // 2)
        screen_y = int(self.y - camera_offset[1] + self.height)
        
        # Simple flame effect
        flame_color = Config.YELLOW if self.animation_frame % 2 == 0 else Config.RED
        pygame.draw.circle(surface, flame_color, (screen_x, screen_y), 8)
        
    def _render_flashlight_effect(self, surface: pygame.Surface, camera_offset: tuple):
        """Render flashlight beam effect"""
        screen_x = int(self.x - camera_offset[0] + self.width // 2)
        screen_y = int(self.y - camera_offset[1] + self.height // 2)
        
        # Simple flashlight beam
        beam_length = 200
        beam_end_x = screen_x + (beam_length if self.facing_right else -beam_length)
        
        # Draw beam as a triangle
        points = [
            (screen_x, screen_y - 10),
            (screen_x, screen_y + 10),
            (beam_end_x, screen_y)
        ]
        
        # Create semi-transparent surface for beam
        beam_surface = pygame.Surface((abs(beam_end_x - screen_x), 20))
        beam_surface.set_alpha(64)
        beam_surface.fill(Config.YELLOW)
        
        beam_rect = beam_surface.get_rect()
        beam_rect.center = ((screen_x + beam_end_x) // 2, screen_y)
        surface.blit(beam_surface, beam_rect)
        
    def collect_item(self, item_type: str, value: int = 1):
        """Collect an item"""
        if item_type == "health":
            self.heal(value)
        elif item_type == "ammo_pistol":
            self.add_ammo(WeaponType.PISTOL, value)
        elif item_type == "ammo_shotgun":
            self.add_ammo(WeaponType.SHOTGUN, value)
        elif item_type == "ammo_rocket":
            self.add_ammo(WeaponType.ROCKET_LAUNCHER, value)
        elif item_type == "key":
            self.keys_collected += value
        elif item_type == "jetpack":
            self.has_jetpack = True
        elif item_type == "scanner":
            self.has_scanner = True
        elif item_type == "score":
            self.score += value