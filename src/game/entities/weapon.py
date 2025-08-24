#!/usr/bin/env python3
"""
Weapon System
Weapon classes and types for the player

Developed by Team PIETRO
PIETRO's divine arsenal brings justice to the battlefield!
"""

import pygame
from enum import Enum
from typing import Optional
from ...core.config import Config
from ...core.asset_manager import AssetManager

class WeaponType(Enum):
    """Weapon types enumeration"""
    PISTOL = "pistol"
    SHOTGUN = "shotgun"
    ROCKET_LAUNCHER = "rocket_launcher"

class Weapon:
    """Weapon class with ammo and firing mechanics"""
    
    def __init__(self, weapon_type: WeaponType, asset_manager: AssetManager):
        self.weapon_type = weapon_type
        self.asset_manager = asset_manager
        
        # Weapon stats based on type
        self._init_weapon_stats()
        
        # Current state
        self.ammo = 0
        self.cooldown_timer = 0.0
        
    def _init_weapon_stats(self):
        """Initialize weapon stats based on type"""
        if self.weapon_type == WeaponType.PISTOL:
            self.name = "Pistol"
            self.damage = Config.PISTOL_DAMAGE
            self.fire_rate = 0.3  # Seconds between shots
            self.max_ammo = 200
            self.sprite_name = "pistol"
            
        elif self.weapon_type == WeaponType.SHOTGUN:
            self.name = "Shotgun"
            self.damage = Config.SHOTGUN_DAMAGE
            self.fire_rate = 0.8
            self.max_ammo = 50
            self.sprite_name = "shotgun"
            
        elif self.weapon_type == WeaponType.ROCKET_LAUNCHER:
            self.name = "Rocket Launcher"
            self.damage = Config.ROCKET_DAMAGE
            self.fire_rate = 1.5
            self.max_ammo = 20
            self.sprite_name = "rocket_launcher"
            
    def update(self, dt: float):
        """Update weapon state"""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
    def can_shoot(self) -> bool:
        """Check if weapon can shoot"""
        return self.ammo > 0 and self.cooldown_timer <= 0
        
    def shoot(self) -> bool:
        """Attempt to shoot weapon"""
        if not self.can_shoot():
            return False
            
        self.ammo -= 1
        self.cooldown_timer = self.fire_rate
        
        # Play weapon sound
        sound_name = f"{self.weapon_type.value}_shoot"
        self.asset_manager.play_sound(sound_name)
        
        return True
        
    def add_ammo(self, amount: int):
        """Add ammo to weapon"""
        self.ammo = min(self.max_ammo, self.ammo + amount)
        
    def get_sprite(self) -> Optional[pygame.Surface]:
        """Get weapon sprite"""
        return self.asset_manager.get_sprite(self.sprite_name)
        
    def get_ammo_percentage(self) -> float:
        """Get ammo as percentage of max"""
        return self.ammo / self.max_ammo if self.max_ammo > 0 else 0.0