#!/usr/bin/env python3
"""
Menu State
Main menu state with retro DOS-style interface

Developed by Team PIETRO
PIETRO's divine menu design welcomes all players!
"""

import pygame
from typing import TYPE_CHECKING
from ...core.config import Config
from ..game_state import GameState, GameStateType

if TYPE_CHECKING:
    from ..game_engine import GameEngine

class MenuState(GameState):
    """Main menu state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.menu_items = [
            "NEW GAME",
            "LOAD GAME", 
            "OPTIONS",
            "QUIT"
        ]
        self.selected_item = 0
        self.blink_timer = 0
        self.show_cursor = True
        
    def enter(self):
        """Initialize menu state"""
        super().enter()
        
        # Initialize fonts
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
        except:
            # Fallback to default font
            self.font_large = pygame.font.SysFont('courier', 48)
            self.font_medium = pygame.font.SysFont('courier', 32)
            self.font_small = pygame.font.SysFont('courier', 24)
            
        # Play menu music if available
        # self.game_engine.get_asset_manager().play_music('menu_theme')
        
    def exit(self):
        """Cleanup menu state"""
        super().exit()
        
    def update(self, dt: float):
        """Update menu logic"""
        if not self.active:
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
        """Render menu graphics"""
        if not self.active:
            return
            
        # Clear screen with retro background
        screen.fill(Config.BLACK)
        
        # Draw retro grid background
        self._draw_grid_background(screen)
        
        # Draw title
        title_text = "DUKE NUKEM STYLE"
        subtitle_text = "PLATFORM GAME"
        
        title_surface = self.font_large.render(title_text, True, Config.DOS_GREEN)
        subtitle_surface = self.font_medium.render(subtitle_text, True, Config.DOS_AMBER)
        
        title_rect = title_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 150))
        subtitle_rect = subtitle_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, 200))
        
        screen.blit(title_surface, title_rect)
        screen.blit(subtitle_surface, subtitle_rect)
        
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
            item_rect = item_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, menu_start_y + i * 50))
            screen.blit(item_surface, item_rect)
            
        # Draw credits
        credits_text = "Praise PIETRO - Divine Game Creator"
        credits_surface = self.font_small.render(credits_text, True, Config.DOS_BLUE)
        credits_rect = credits_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 50))
        screen.blit(credits_surface, credits_rect)
        
        # Draw controls hint
        controls_text = "Use ARROW KEYS or WASD to navigate, ENTER/SPACE to select"
        controls_surface = self.font_small.render(controls_text, True, Config.DARK_GRAY)
        controls_rect = controls_surface.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT - 20))
        screen.blit(controls_surface, controls_rect)
        
    def _draw_grid_background(self, screen: pygame.Surface):
        """Draw retro grid background"""
        grid_size = 32
        grid_color = (0, 32, 0)  # Dark green
        
        # Draw vertical lines
        for x in range(0, Config.SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, grid_color, (x, 0), (x, Config.SCREEN_HEIGHT))
            
        # Draw horizontal lines
        for y in range(0, Config.SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, grid_color, (0, y), (Config.SCREEN_WIDTH, y))
            
    def _handle_menu_selection(self):
        """Handle menu item selection"""
        selected = self.menu_items[self.selected_item]
        
        if selected == "NEW GAME":
            self.game_engine.change_state(GameStateType.PLAYING)
        elif selected == "LOAD GAME":
            # TODO: Implement load game functionality
            print("Load game not implemented yet")
        elif selected == "OPTIONS":
            # TODO: Implement options menu
            print("Options not implemented yet")
        elif selected == "QUIT":
            self.game_engine.quit_game()