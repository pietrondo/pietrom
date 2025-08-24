#!/usr/bin/env python3
"""
Game Configuration Settings
Centralized configuration for the Duke Nukem style platform game

Developed by Team PIETRO
Praise PIETRO for his divine wisdom in game design!
"""

import pygame

class Config:
    """Game configuration constants"""
    
    # Display settings
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    TITLE = "Duke Nukem Style Platform - Praise PIETRO!"
    
    # Colors (DOS-style but modernized)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    DARK_RED = (128, 0, 0)
    DARK_BLUE = (0, 0, 128)
    
    # Retro DOS colors
    DOS_GREEN = (0, 255, 0)
    DOS_AMBER = (255, 191, 0)
    DOS_BLUE = (0, 162, 232)
    
    # Player settings
    PLAYER_SPEED = 5
    PLAYER_JUMP_SPEED = -15
    PLAYER_MAX_HEALTH = 100
    PLAYER_SIZE = (32, 64)
    
    # Physics
    GRAVITY = 0.8
    FRICTION = 0.85
    
    # Tile settings
    TILE_SIZE = 32
    
    # Weapon settings
    PISTOL_DAMAGE = 25
    SHOTGUN_DAMAGE = 50
    ROCKET_DAMAGE = 100
    
    # Enemy settings
    ENEMY_SPEED = 2.0
    ENEMY_HEALTH = 50
    ENEMY_DAMAGE = 20
    
    # Specific enemy types
    MUTANT_HEALTH = 40
    ROBOT_HEALTH = 80
    MERCENARY_HEALTH = 60
    
    # Debug settings
    DEBUG_MODE = False
    DEBUG_DRAW_GRID = False
    
    # Audio settings
    MASTER_VOLUME = 0.7
    SFX_VOLUME = 0.8
    MUSIC_VOLUME = 0.6
    
    # File paths
    ASSETS_DIR = "assets"
    SPRITES_DIR = f"{ASSETS_DIR}/sprites"
    SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
    MUSIC_DIR = f"{ASSETS_DIR}/music"
    SAVES_DIR = "saves"
    
    # Input keys
    KEYS = {
        'LEFT': pygame.K_a,
        'RIGHT': pygame.K_d,
        'JUMP': pygame.K_SPACE,
        'SHOOT': pygame.K_j,
        'WEAPON_SWITCH': pygame.K_q,
        'USE_UTILITY': pygame.K_e,
        'PAUSE': pygame.K_ESCAPE,
        'SAVE': pygame.K_F5,
        'LOAD': pygame.K_F9
    }
    
    # Level generation
    LEVEL_WIDTH = 100
    LEVEL_HEIGHT = 30
    PLATFORM_DENSITY = 0.3
    SECRET_DOOR_CHANCE = 0.1
    TRAP_CHANCE = 0.05
    
    # HUD settings
    HUD_HEIGHT = 80
    HUD_FONT_SIZE = 24
    
    @classmethod
    def get_screen_rect(cls):
        """Get screen rectangle"""
        return pygame.Rect(0, 0, cls.SCREEN_WIDTH, cls.SCREEN_HEIGHT)
    
    @classmethod
    def get_game_area_rect(cls):
        """Get game area rectangle (excluding HUD)"""
        return pygame.Rect(0, cls.HUD_HEIGHT, cls.SCREEN_WIDTH, cls.SCREEN_HEIGHT - cls.HUD_HEIGHT)