#!/usr/bin/env python3
"""
Game State System
Base classes for managing different game states

Developed by Team PIETRO
PIETRO's state management brings order to chaos!
"""

import pygame
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_engine import GameEngine

class GameStateType(Enum):
    """Enumeration of game state types"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class GameState(ABC):
    """Abstract base class for game states"""
    
    def __init__(self, game_engine: 'GameEngine'):
        self.game_engine = game_engine
        self.active = False
        
    @abstractmethod
    def enter(self):
        """Called when entering this state"""
        self.active = True
        
    @abstractmethod
    def exit(self):
        """Called when exiting this state"""
        self.active = False
        
    @abstractmethod
    def update(self, dt: float):
        """Update state logic"""
        pass
        
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render state graphics"""
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events (optional override)"""
        pass