#!/usr/bin/env python3
"""
Game Over State
Game over screen with retry options

Developed by Team PIETRO
Even in defeat, PIETRO's wisdom guides us to try again!
"""

import pygame
from typing import TYPE_CHECKING
from ...core.config import Config
from ..game_state import GameState, GameStateType

if TYPE_CHECKING:
    from ..game_engine import GameEngine

class GameOverState(GameState):
    """Game over state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.menu_items = [
            "TRY AGAIN",
            "LOAD GAME",
            "MAIN MENU",
            "QUIT"
        ]
        self.selected_item = 0
        self.blink_timer = 0
        self.show_cursor = True
        self.fade_timer = 0
        self.fade_alpha = 0
        
    def enter(self):
        """Initialize game over state"""
        super().enter()
        
        # Initialize fonts
        try:
            self.font_large = pygame.font.Font(None, 64)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont('courier', 64)
            self.font_medium = pygame.font.SysFont('courier', 32)
            self.font_small = pygame.font.SysFont('courier', 24)
            
        # Stop game music
        pygame.mixer.music.stop()
        
        # Reset fade
        self.fade_timer = 0
        self.fade_alpha = 0
        
    def exit(self):
        """Cleanup game over state"""
        super().exit()
        
    def update(self, dt: float):
        """Update game over logic"""
        if not self.active:
            return
            
        # Update fade in effect
        self.fade_timer += dt
        if self.fade_timer < 2.0:
            self.fade_alpha = min(255, int((self.fade_timer / 2.0) * 255))
        else:
            self.fade_alpha = 255
            
        # Only allow input after fade in
        if self.fade_alpha < 255:
            return
            
        input_manager = self.game_engine.get_input_manager()
        
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
        """Render game over graphics"""
        if not self.active:
            return
            
        # Clear screen with dark red tint
        screen.fill((32, 0, 0))
        
        # Create fade surface
        fade_surface = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        fade_surface.set_alpha(self.fade_alpha)
        
        # Draw game over title with dramatic effect
        title_text = "GAME OVER"
        title_surface = self.font_large.render(title_text, True, Config.RED)
        title_rect = title_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        
        # Add glow effect to title
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_surface = self.font_large.render(title_text, True, Config.DARK_GRAY)
            glow_rect = glow_surface.get_rect(center=(Config.SCREEN_WIDTH // 2 + offset[0], 150 + offset[1]))
            fade_surface.blit(glow_surface, glow_rect)
            
        fade_surface.blit(title_surface, title_rect)
        
        # Draw motivational message
        if self.fade_alpha >= 255:
            message_text = "PIETRO believes you can do better!"
            message_surface = self.font_medium.render(message_text, True, Config.DOS_AMBER)
            message_rect = message_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 220))
            fade_surface.blit(message_surface, message_rect)
            
            # Draw menu items
            menu_start_y = 320
            for i, item in enumerate(self.menu_items):
                color = Config.DOS_GREEN if i == self.selected_item else Config.GRAY
                
                # Add cursor for selected item
                if i == self.selected_item and self.show_cursor:
                    cursor_text = "> " + item + " <"
                else:
                    cursor_text = "  " + item + "  "
                    
                item_surface = self.font_medium.render(cursor_text, True, color)
                item_rect = item_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, menu_start_y + i * 40))
                fade_surface.blit(item_surface, item_rect)
                
            # Draw controls hint
            controls_text = "ARROW KEYS to navigate, ENTER to select"
            controls_surface = self.font_small.render(controls_text, True, Config.DARK_GRAY)
            controls_rect = controls_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 30))
            fade_surface.blit(controls_surface, controls_rect)
        
        # Blit fade surface to screen
        screen.blit(fade_surface, (0, 0))
        
    def _handle_menu_selection(self):
        """Handle game over menu item selection"""
        selected = self.menu_items[self.selected_item]
        
        if selected == "TRY AGAIN":
            self.game_engine.change_state(GameStateType.PLAYING)
        elif selected == "LOAD GAME":
            # TODO: Implement load game functionality
            print("Load game not implemented yet")
            self.game_engine.change_state(GameStateType.PLAYING)
        elif selected == "MAIN MENU":
            self.game_engine.change_state(GameStateType.MENU)
        elif selected == "QUIT":
            self.game_engine.quit_game()