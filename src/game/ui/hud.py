#!/usr/bin/env python3
"""
HUD System
Retro DOS-style heads-up display

Developed by Team PIETRO
PIETRO's HUD provides essential battlefield information!
"""

import pygame
import math
from typing import TYPE_CHECKING
from ...core.config import Config

if TYPE_CHECKING:
    from ..entities.player import Player

class HUD:
    """Heads-up display for game information"""
    
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
        # Fonts
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        
        # Animation timers
        self.health_flash_timer = 0.0
        self.ammo_flash_timer = 0.0
        self.damage_indicator_timer = 0.0
        self.last_health = 100
        
        # Colors
        self.health_color = Config.GREEN
        self.ammo_color = Config.YELLOW
        self.text_color = Config.WHITE
        
    def update(self, dt: float, player: 'Player'):
        """Update HUD animations and states"""
        # Update flash timers
        if self.health_flash_timer > 0:
            self.health_flash_timer -= dt
            
        if self.ammo_flash_timer > 0:
            self.ammo_flash_timer -= dt
            
        if self.damage_indicator_timer > 0:
            self.damage_indicator_timer -= dt
            
        # Check for health change
        if player.health < self.last_health:
            self.health_flash_timer = 0.5  # Flash for 0.5 seconds
            self.damage_indicator_timer = 1.0
            
        self.last_health = player.health
        
        # Check for low ammo
        current_weapon = player.get_current_weapon()
        if current_weapon and current_weapon.ammo <= 5:
            if self.ammo_flash_timer <= 0:
                self.ammo_flash_timer = 0.3
                
    def render(self, surface: pygame.Surface, player: 'Player'):
        """Render the HUD"""
        # Render background panel
        self._render_background(surface)
        
        # Render health
        self._render_health(surface, player)
        
        # Render ammo
        self._render_ammo(surface, player)
        
        # Render weapon info
        self._render_weapon_info(surface, player)
        
        # Render utility items
        self._render_utilities(surface, player)
        
        # Render collectibles
        self._render_collectibles(surface, player)
        
        # Render permanent upgrades
        self._render_permanent_upgrades(surface, player)
        
        # Render damage indicator
        self._render_damage_indicator(surface)
        
        # Render crosshair
        self._render_crosshair(surface)
        
    def _render_background(self, surface: pygame.Surface):
        """Render HUD background panel"""
        # Top panel
        panel_rect = pygame.Rect(0, 0, Config.SCREEN_WIDTH, 60)
        pygame.draw.rect(surface, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(surface, Config.CYAN, panel_rect, 2)
        
        # Bottom mini panel for utilities
        mini_panel = pygame.Rect(10, Config.SCREEN_HEIGHT - 80, 300, 70)
        pygame.draw.rect(surface, (0, 0, 0, 120), mini_panel)
        pygame.draw.rect(surface, Config.CYAN, mini_panel, 1)
        
    def _render_health(self, surface: pygame.Surface, player: 'Player'):
        """Render health bar and info"""
        x, y = 20, 15
        
        # Health label
        health_text = self.font_medium.render("HEALTH", True, self.text_color)
        surface.blit(health_text, (x, y))
        
        # Health bar background
        bar_x, bar_y = x + 80, y + 2
        bar_width, bar_height = 150, 14
        
        pygame.draw.rect(surface, Config.DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, Config.WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Health bar fill
        health_ratio = max(0, player.health / player.max_health)
        fill_width = int(bar_width * health_ratio)
        
        # Flash red when taking damage
        health_color = self.health_color
        if self.health_flash_timer > 0 and int(self.health_flash_timer * 10) % 2:
            health_color = Config.RED
            
        if fill_width > 0:
            pygame.draw.rect(surface, health_color, (bar_x, bar_y, fill_width, bar_height))
            
        # Health text
        health_value = f"{int(player.health)}/{int(player.max_health)}"
        health_num_text = self.font_small.render(health_value, True, self.text_color)
        surface.blit(health_num_text, (bar_x + bar_width + 10, bar_y + 1))
        
        # Critical health warning
        if player.health <= 25:
            warning_text = self.font_small.render("CRITICAL!", True, Config.RED)
            surface.blit(warning_text, (bar_x + bar_width + 80, bar_y + 1))
            
    def _render_ammo(self, surface: pygame.Surface, player: 'Player'):
        """Render ammo information"""
        x, y = 20, 35
        
        current_weapon = player.get_current_weapon()
        if not current_weapon:
            return
            
        # Ammo label
        ammo_text = self.font_medium.render("AMMO", True, self.text_color)
        surface.blit(ammo_text, (x, y))
        
        # Ammo count
        ammo_x = x + 80
        ammo_color = self.ammo_color
        
        # Flash when low on ammo
        if self.ammo_flash_timer > 0 and int(self.ammo_flash_timer * 10) % 2:
            ammo_color = Config.RED
            
        ammo_count = f"{current_weapon.ammo}/{current_weapon.max_ammo}"
        ammo_count_text = self.font_medium.render(ammo_count, True, ammo_color)
        surface.blit(ammo_count_text, (ammo_x, y))
        
        # Reserve ammo
        if hasattr(player, 'reserve_ammo'):
            reserve_text = f"[{player.reserve_ammo.get(current_weapon.weapon_type.name, 0)}]"
            reserve_ammo_text = self.font_small.render(reserve_text, True, Config.GRAY)
            surface.blit(reserve_ammo_text, (ammo_x + 80, y + 2))
            
    def _render_weapon_info(self, surface: pygame.Surface, player: 'Player'):
        """Render current weapon information"""
        x, y = 400, 15
        
        current_weapon = player.get_current_weapon()
        if not current_weapon:
            return
            
        # Weapon name
        weapon_name = current_weapon.weapon_type.name.upper()
        weapon_text = self.font_medium.render(weapon_name, True, self.text_color)
        surface.blit(weapon_text, (x, y))
        
        # Weapon icon/sprite (placeholder)
        icon_rect = pygame.Rect(x, y + 20, 32, 16)
        pygame.draw.rect(surface, Config.GRAY, icon_rect)
        pygame.draw.rect(surface, Config.WHITE, icon_rect, 1)
        
        # Fire rate indicator
        if current_weapon.cooldown_timer > 0:
            cooldown_ratio = current_weapon.cooldown_timer / current_weapon.fire_rate
            cooldown_width = int(32 * cooldown_ratio)
            pygame.draw.rect(surface, Config.YELLOW, (x, y + 37, cooldown_width, 3))
            
    def _render_utilities(self, surface: pygame.Surface, player: 'Player'):
        """Render utility items status"""
        x, y = 20, Config.SCREEN_HEIGHT - 70
        
        # Jetpack fuel
        if hasattr(player, 'jetpack_fuel'):
            jetpack_text = self.font_small.render("JETPACK", True, self.text_color)
            surface.blit(jetpack_text, (x, y))
            
            fuel_bar_x, fuel_bar_y = x + 60, y + 2
            fuel_bar_width, fuel_bar_height = 80, 8
            
            pygame.draw.rect(surface, Config.DARK_BLUE, (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height))
            pygame.draw.rect(surface, Config.WHITE, (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 1)
            
            fuel_ratio = player.jetpack_fuel / player.max_jetpack_fuel
            fuel_fill = int(fuel_bar_width * fuel_ratio)
            
            if fuel_fill > 0:
                pygame.draw.rect(surface, Config.BLUE, (fuel_bar_x, fuel_bar_y, fuel_fill, fuel_bar_height))
                
        # Flashlight status
        if hasattr(player, 'flashlight_active') and player.flashlight_active:
            flashlight_text = self.font_small.render("FLASHLIGHT: ON", True, Config.YELLOW)
            surface.blit(flashlight_text, (x, y + 15))
            
        # Scanner status
        if hasattr(player, 'scanner_active') and player.scanner_active:
            scanner_text = self.font_small.render("SCANNER: ACTIVE", True, Config.GREEN)
            surface.blit(scanner_text, (x, y + 30))
            
    def _render_collectibles(self, surface: pygame.Surface, player: 'Player'):
        """Render collected items count"""
        x, y = Config.SCREEN_WIDTH - 200, 15
        
        # Score/points
        if hasattr(player, 'score'):
            score_text = self.font_medium.render(f"SCORE: {player.score:06d}", True, self.text_color)
            surface.blit(score_text, (x, y))
            
        # Keys collected
        if hasattr(player, 'keys'):
            keys_text = self.font_small.render(f"KEYS: {player.keys}", True, Config.YELLOW)
            surface.blit(keys_text, (x, y + 20))
            
        # Power-ups (show active ones)
        if hasattr(player, 'active_powerups'):
            powerup_y = y + 35
            for powerup, timer in player.active_powerups.items():
                if timer > 0:
                    powerup_text = self.font_small.render(f"{powerup.upper()}: {timer:.1f}s", True, Config.MAGENTA)
                    surface.blit(powerup_text, (x, powerup_y))
                    powerup_y += 12
                    
    def _render_damage_indicator(self, surface: pygame.Surface):
        """Render damage indicator (red screen flash)"""
        if self.damage_indicator_timer > 0:
            alpha = int(100 * (self.damage_indicator_timer / 1.0))
            damage_surface = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
            damage_surface.set_alpha(alpha)
            damage_surface.fill(Config.RED)
            surface.blit(damage_surface, (0, 0))
            
    def _render_crosshair(self, surface: pygame.Surface):
        """Render crosshair in center of screen"""
        center_x = Config.SCREEN_WIDTH // 2
        center_y = Config.SCREEN_HEIGHT // 2
        
        # Simple crosshair
        crosshair_size = 8
        crosshair_color = Config.WHITE
        
        # Horizontal line
        pygame.draw.line(surface, crosshair_color, 
                        (center_x - crosshair_size, center_y), 
                        (center_x + crosshair_size, center_y), 2)
        
        # Vertical line
        pygame.draw.line(surface, crosshair_color, 
                        (center_x, center_y - crosshair_size), 
                        (center_x, center_y + crosshair_size), 2)
        
        # Center dot
        pygame.draw.circle(surface, crosshair_color, (center_x, center_y), 1)
        
    def render_minimap(self, surface: pygame.Surface, player: 'Player', level):
        """Render minimap (optional feature)"""
        if not hasattr(self, 'show_minimap') or not self.show_minimap:
            return
            
        minimap_size = 120
        minimap_x = Config.SCREEN_WIDTH - minimap_size - 10
        minimap_y = Config.SCREEN_HEIGHT - minimap_size - 10
        
        # Minimap background
        minimap_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)
        pygame.draw.rect(surface, (0, 0, 0, 150), minimap_rect)
        pygame.draw.rect(surface, Config.CYAN, minimap_rect, 2)
        
        # Player position (center of minimap)
        player_x = minimap_x + minimap_size // 2
        player_y = minimap_y + minimap_size // 2
        pygame.draw.circle(surface, Config.GREEN, (player_x, player_y), 3)
    
    def _render_permanent_upgrades(self, surface: pygame.Surface, player: 'Player'):
        """Render permanent upgrades acquired by player"""
        if not hasattr(player, 'item_manager'):
            return
            
        x, y = Config.SCREEN_WIDTH - 150, Config.SCREEN_HEIGHT - 120
        
        # Background panel for upgrades
        panel_width, panel_height = 140, 100
        panel_rect = pygame.Rect(x - 10, y - 10, panel_width, panel_height)
        pygame.draw.rect(surface, (0, 0, 0, 120), panel_rect)
        pygame.draw.rect(surface, Config.CYAN, panel_rect, 1)
        
        # Title
        title_text = self.font_small.render("UPGRADES", True, Config.CYAN)
        surface.blit(title_text, (x, y))
        
        # List permanent upgrades
        upgrade_y = y + 15
        upgrades = player.item_manager.permanent_upgrades
        
        if not upgrades:
            no_upgrades_text = self.font_small.render("None", True, Config.GRAY)
            surface.blit(no_upgrades_text, (x, upgrade_y))
        else:
            for upgrade in upgrades:
                upgrade_name = upgrade.name.replace('_', ' ').title()
                upgrade_text = self.font_small.render(f"• {upgrade_name}", True, Config.GREEN)
                surface.blit(upgrade_text, (x, upgrade_y))
                upgrade_y += 12
        
        # Show active power-ups with timers
        if player.item_manager.active_power_ups:
            powerup_y = upgrade_y + 10
            powerup_title = self.font_small.render("ACTIVE:", True, Config.YELLOW)
            surface.blit(powerup_title, (x, powerup_y))
            powerup_y += 12
            
            for powerup in player.item_manager.active_power_ups:
                time_left = powerup.remaining_time
                powerup_name = powerup.power_up_type.name.replace('_', ' ').title()
                powerup_text = self.font_small.render(f"• {powerup_name}: {time_left:.1f}s", True, Config.MAGENTA)
                surface.blit(powerup_text, (x, powerup_y))
                powerup_y += 12
        
        # Show credits and keycards
        info_y = y + 75
        if hasattr(player, 'credits'):
            credits_text = self.font_small.render(f"Credits: {player.credits}", True, Config.YELLOW)
            surface.blit(credits_text, (x, info_y))
        
        if hasattr(player, 'keycards'):
            keycards_text = self.font_small.render(f"Keycards: {player.keycards}", True, Config.CYAN)
            surface.blit(keycards_text, (x, info_y + 12))
        
        # Player direction indicator
        direction_x = player_x + (10 if player.facing_right else -10)
        pygame.draw.line(surface, Config.GREEN, (player_x, player_y), (direction_x, player_y), 2)