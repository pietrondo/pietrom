#!/usr/bin/env python3
"""
Pause State
Pause menu state during gameplay

Developed by Team PIETRO
Even PIETRO needs a moment to contemplate his divine creations!
"""

import pygame
from typing import TYPE_CHECKING
from ...core.config import Config
from ..game_state import GameState, GameStateType

if TYPE_CHECKING:
    from ..game_engine import GameEngine

class PauseState(GameState):
    """Pause menu state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font_large = None
        self.font_medium = None
        self.menu_items = [
            "RESUME",
            "SAVE GAME",
            "LOAD GAME",
            "MAIN MENU",
            "QUIT"
        ]
        self.selected_item = 0
        self.blink_timer = 0
        self.show_cursor = True
        
    def enter(self):
        """Initialize pause state"""
        super().enter()
        
        # Initialize fonts
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
        except:
            self.font_large = pygame.font.SysFont('courier', 48)
            self.font_medium = pygame.font.SysFont('courier', 32)
            
        # Pause game music
        pygame.mixer.music.pause()
        
    def exit(self):
        """Cleanup pause state"""
        super().exit()
        
        # Resume game music
        pygame.mixer.music.unpause()
        
    def update(self, dt: float):
        """Update pause menu logic"""
        if not self.active:
            return
            
        input_manager = self.game_engine.get_input_manager()
        
        # Handle resume with pause key
        if input_manager.is_pause_pressed():
            self.game_engine.change_state(GameStateType.PLAYING)
            return
            
        # Handle menu navigation
        if input_manager.is_key_just_pressed(pygame.K_UP) or input_manager.is_key_just_pressed(pygame.K_w):
            self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            
        if input_manager.is_key_just_pressed(pygame.K_DOWN) or input_manager.is_key_just_pressed(pygame.K_s):
            self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            
        # Handle menu selection
        if input_manager.is_key_just_pressed(pygame.K_RETURN) or input_manager.is_key_just_pressed(pygame.K_SPACE):
            self._handle_menu_selection()
            
        # Update cursor blink
        self.blink_timer += dt
        if self.blink_timer >= 0.5:
            self.show_cursor = not self.show_cursor
            self.blink_timer = 0
            
    def render(self, screen: pygame.Surface):
        """Render pause menu graphics"""
        if not self.active:
            return
            
        # Create semi-transparent overlay
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Config.BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw pause title
        title_text = "GAME PAUSED"
        title_surface = self.font_large.render(title_text, True, Config.DOS_GREEN)
        title_rect = title_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 200))
        screen.blit(title_surface, title_rect)
        
        # Draw menu items
        menu_start_y = 300
        for i, item in enumerate(self.menu_items):
            color = Config.DOS_GREEN if i == self.selected_item else Config.GRAY
            
            # Add cursor for selected item
            if i == self.selected_item and self.show_cursor:
                cursor_text = "> " + item + " <"
            else:
                cursor_text = "  " + item + "  "
                
            item_surface = self.font_medium.render(cursor_text, True, color)
            item_rect = item_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, menu_start_y + i * 40))
            screen.blit(item_surface, item_rect)
            
        # Draw controls hint
        controls_text = "ESC to resume, ARROW KEYS to navigate, ENTER to select"
        controls_surface = pygame.font.Font(None, 20).render(controls_text, True, Config.DARK_GRAY)
        controls_rect = controls_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 30))
        screen.blit(controls_surface, controls_rect)
        
    def _handle_menu_selection(self):
        """Handle pause menu item selection"""
        selected = self.menu_items[self.selected_item]
        
        if selected == "RESUME":
            self.game_engine.change_state(GameStateType.PLAYING)
        elif selected == "SAVE GAME":
            # TODO: Implement save game functionality
            print("Save game not implemented yet")
        elif selected == "LOAD GAME":
            # TODO: Implement load game functionality
            print("Load game not implemented yet")
        elif selected == "MAIN MENU":
            self.game_engine.change_state(GameStateType.MENU)
        elif selected == "QUIT":
            self.game_engine.quit_game()