#!/usr/bin/env python3
"""
Game Engine
Main game engine that coordinates all game systems

Developed by Team PIETRO
PIETRO's divine architecture powers this magnificent engine!
"""

import pygame
import sys
from typing import Optional
from ..core.config import Config
from ..core.asset_manager import AssetManager
from ..core.input_manager import InputManager
from .game_state import GameState, GameStateType
from .states.menu_state import MenuState
from .states.playing_state import PlayingState
from .states.pause_state import PauseState
from .states.game_over_state import GameOverState

class GameEngine:
    """Main game engine class"""
    
    def __init__(self):
        """Initialize the game engine"""
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Create display
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        
        # Game systems
        self.clock = pygame.time.Clock()
        self.asset_manager = AssetManager()
        self.input_manager = InputManager()
        
        # Game state management
        self.current_state: Optional[GameState] = None
        self.states = {
            GameStateType.MENU: MenuState(self),
            GameStateType.PLAYING: PlayingState(self),
            GameStateType.PAUSED: PauseState(self),
            GameStateType.GAME_OVER: GameOverState(self)
        }
        
        # Start with menu state
        self.change_state(GameStateType.MENU)
        
        # Game control
        self.running = True
        self.dt = 0
        
    def run(self):
        """Main game loop"""
        while self.running:
            # Calculate delta time
            self.dt = self.clock.tick(Config.FPS) / 1000.0
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Update input
            self.input_manager.update(events)
            
            # Update current state
            if self.current_state:
                self.current_state.update(self.dt)
                
            # Render
            self.screen.fill(Config.BLACK)
            if self.current_state:
                self.current_state.render(self.screen)
                
            # Update display
            pygame.display.flip()
            
        # Cleanup
        self.cleanup()
        
    def change_state(self, state_type: GameStateType):
        """Change to a different game state"""
        if state_type in self.states:
            # Exit current state
            if self.current_state:
                self.current_state.exit()
                
            # Enter new state
            self.current_state = self.states[state_type]
            self.current_state.enter()
            
    def quit_game(self):
        """Quit the game"""
        self.running = False
        
    def cleanup(self):
        """Cleanup resources"""
        if self.current_state:
            self.current_state.exit()
            
        pygame.mixer.quit()
        pygame.quit()
        
    def get_asset_manager(self) -> AssetManager:
        """Get asset manager"""
        return self.asset_manager
        
    def get_input_manager(self) -> InputManager:
        """Get input manager"""
        return self.input_manager