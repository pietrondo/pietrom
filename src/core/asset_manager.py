#!/usr/bin/env python3
"""
Asset Manager
Handles loading and caching of game assets (sprites, sounds, music)

Developed by Team PIETRO
All glory to PIETRO, master of digital assets!
"""

import pygame
import os
from typing import Dict, Optional
from .config import Config

class AssetManager:
    """Manages game assets with caching"""
    
    def __init__(self):
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        self._create_placeholder_assets()
    
    def _create_placeholder_assets(self):
        """Create placeholder assets for development"""
        # Create placeholder sprites
        self._create_player_sprites()
        self._create_enemy_sprites()
        self._create_weapon_sprites()
        self._create_tile_sprites()
        self._create_ui_sprites()
        
    def _create_player_sprites(self):
        """Create player sprite placeholders"""
        # Player idle
        player_idle = pygame.Surface((32, 64))
        player_idle.fill(Config.DOS_GREEN)
        pygame.draw.rect(player_idle, Config.BLACK, (8, 8, 16, 16))  # Head
        pygame.draw.rect(player_idle, Config.RED, (12, 32, 8, 16))   # Torso
        self.sprites['player_idle'] = player_idle
        
        # Player walking
        player_walk = pygame.Surface((32, 64))
        player_walk.fill(Config.DOS_GREEN)
        pygame.draw.rect(player_walk, Config.BLACK, (8, 8, 16, 16))
        pygame.draw.rect(player_walk, Config.RED, (12, 32, 8, 16))
        pygame.draw.rect(player_walk, Config.BLUE, (4, 48, 8, 16))   # Leg
        self.sprites['player_walk'] = player_walk
        
        # Player jumping
        player_jump = pygame.Surface((32, 64))
        player_jump.fill(Config.DOS_GREEN)
        pygame.draw.rect(player_jump, Config.BLACK, (8, 8, 16, 16))
        pygame.draw.rect(player_jump, Config.RED, (12, 32, 8, 16))
        pygame.draw.rect(player_jump, Config.BLUE, (8, 48, 16, 8))   # Legs together
        self.sprites['player_jump'] = player_jump
    
    def _create_enemy_sprites(self):
        """Create enemy sprite placeholders"""
        # Mutant
        mutant = pygame.Surface((32, 32))
        mutant.fill(Config.MAGENTA)
        pygame.draw.rect(mutant, Config.BLACK, (8, 8, 16, 8))  # Eyes
        pygame.draw.rect(mutant, Config.RED, (12, 20, 8, 4))   # Mouth
        self.sprites['mutant'] = mutant
        
        # Robot
        robot = pygame.Surface((32, 48))
        robot.fill(Config.GRAY)
        pygame.draw.rect(robot, Config.RED, (8, 8, 16, 8))     # Eyes
        pygame.draw.rect(robot, Config.BLUE, (4, 32, 24, 8))   # Body
        self.sprites['robot'] = robot
        
        # Mercenary
        mercenary = pygame.Surface((32, 64))
        mercenary.fill(Config.DARK_GRAY)
        pygame.draw.rect(mercenary, Config.BLACK, (8, 8, 16, 16))  # Head
        pygame.draw.rect(mercenary, Config.YELLOW, (12, 32, 8, 16)) # Torso
        self.sprites['mercenary'] = mercenary
    
    def _create_weapon_sprites(self):
        """Create weapon sprite placeholders"""
        # Pistol
        pistol = pygame.Surface((16, 8))
        pistol.fill(Config.DARK_GRAY)
        pygame.draw.rect(pistol, Config.BLACK, (0, 2, 12, 4))
        self.sprites['pistol'] = pistol
        
        # Shotgun
        shotgun = pygame.Surface((24, 8))
        shotgun.fill(Config.DARK_GRAY)
        pygame.draw.rect(shotgun, Config.BLACK, (0, 2, 20, 4))
        self.sprites['shotgun'] = shotgun
        
        # Rocket Launcher
        rocket_launcher = pygame.Surface((32, 12))
        rocket_launcher.fill(Config.DARK_GRAY)
        pygame.draw.rect(rocket_launcher, Config.RED, (0, 4, 28, 4))
        self.sprites['rocket_launcher'] = rocket_launcher
        
        # Bullet
        bullet = pygame.Surface((4, 2))
        bullet.fill(Config.YELLOW)
        self.sprites['bullet'] = bullet
        
        # Rocket
        rocket = pygame.Surface((8, 4))
        rocket.fill(Config.RED)
        pygame.draw.rect(rocket, Config.YELLOW, (0, 1, 2, 2))
        self.sprites['rocket'] = rocket
    
    def _create_tile_sprites(self):
        """Create tile sprite placeholders"""
        # Ground tile
        ground = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE))
        ground.fill(Config.DARK_GRAY)
        pygame.draw.rect(ground, Config.GRAY, (2, 2, 28, 28))
        self.sprites['ground'] = ground
        
        # Wall tile
        wall = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE))
        wall.fill(Config.GRAY)
        pygame.draw.rect(wall, Config.LIGHT_GRAY, (4, 4, 24, 24))
        self.sprites['wall'] = wall
        
        # Platform
        platform = pygame.Surface((Config.TILE_SIZE, 8))
        platform.fill(Config.DOS_AMBER)
        pygame.draw.rect(platform, Config.YELLOW, (2, 2, 28, 4))
        self.sprites['platform'] = platform
        
        # Door
        door = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE * 2))
        door.fill(Config.DOS_BLUE)
        pygame.draw.rect(door, Config.CYAN, (4, 4, 24, 56))
        self.sprites['door'] = door
        
        # Secret door
        secret_door = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE * 2))
        secret_door.fill(Config.DARK_GRAY)
        pygame.draw.rect(secret_door, Config.GRAY, (4, 4, 24, 56))
        self.sprites['secret_door'] = secret_door
    
    def _create_ui_sprites(self):
        """Create UI sprite placeholders"""
        # Health pack
        health_pack = pygame.Surface((16, 16))
        health_pack.fill(Config.RED)
        pygame.draw.rect(health_pack, Config.WHITE, (6, 2, 4, 12))
        pygame.draw.rect(health_pack, Config.WHITE, (2, 6, 12, 4))
        self.sprites['health_pack'] = health_pack
        
        # Ammo box
        ammo_box = pygame.Surface((16, 16))
        ammo_box.fill(Config.DOS_AMBER)
        pygame.draw.rect(ammo_box, Config.BLACK, (2, 2, 12, 12))
        self.sprites['ammo_box'] = ammo_box
        
        # Power-up
        power_up = pygame.Surface((16, 16))
        power_up.fill(Config.CYAN)
        pygame.draw.circle(power_up, Config.WHITE, (8, 8), 6)
        self.sprites['power_up'] = power_up
    
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get sprite by name"""
        return self.sprites.get(name)
    
    def load_sprite(self, name: str, filepath: str) -> bool:
        """Load sprite from file"""
        try:
            if os.path.exists(filepath):
                sprite = pygame.image.load(filepath).convert_alpha()
                self.sprites[name] = sprite
                return True
        except pygame.error as e:
            print(f"Could not load sprite {name}: {e}")
        return False
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get sound by name"""
        return self.sounds.get(name)
    
    def load_sound(self, name: str, filepath: str) -> bool:
        """Load sound from file"""
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(Config.SFX_VOLUME)
                self.sounds[name] = sound
                return True
        except pygame.error as e:
            print(f"Could not load sound {name}: {e}")
        return False
    
    def play_sound(self, name: str):
        """Play sound effect"""
        sound = self.get_sound(name)
        if sound:
            sound.play()
    
    def load_music(self, name: str, filepath: str) -> bool:
        """Load music track"""
        if os.path.exists(filepath):
            self.music_tracks[name] = filepath
            return True
        return False
    
    def play_music(self, name: str, loops: int = -1):
        """Play background music"""
        if name in self.music_tracks:
            try:
                pygame.mixer.music.load(self.music_tracks[name])
                pygame.mixer.music.set_volume(Config.MUSIC_VOLUME)
                pygame.mixer.music.play(loops)
            except pygame.error as e:
                print(f"Could not play music {name}: {e}")
    
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()