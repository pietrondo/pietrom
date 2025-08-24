#!/usr/bin/env python3
"""
Playing State
Main gameplay state where the action happens

Developed by Team PIETRO
PIETRO's gameplay vision comes to life!
"""

import pygame
from typing import TYPE_CHECKING, List
from ...core.config import Config
from ..game_state import GameState, GameStateType
from ..entities.player import Player
from ..entities.enemy import Enemy, MutantEnemy, RobotEnemy, MercenaryEnemy
from ..entities.enemy_standard import EnemyStandard
from ..entities.item import ItemType
from ..world.world_manager import WorldManager
from ..ui.hud import HUD

if TYPE_CHECKING:
    from ..game_engine import GameEngine

class PlayingState(GameState):
    """Main gameplay state"""
    
    def __init__(self, game_engine: 'GameEngine'):
        super().__init__(game_engine)
        self.player = None
        self.enemies: List[Enemy] = []
        self.world_manager = None
        self.hud = None
        self.paused = False
        
    def enter(self):
        """Initialize gameplay"""
        super().enter()
        
        # Create world manager
        self.world_manager = WorldManager(
            Config.SCREEN_WIDTH, 
            Config.SCREEN_HEIGHT - Config.HUD_HEIGHT,
            60, 20  # Map size: 60x20 tiles
        )
        
        # Initialize world with test room
        self.world_manager.initialize_world(generate_test_room=True)
        
        # Create player at center of map
        spawn_x = 30 * 32  # Center X (tile 30 * 32 pixels)
        spawn_y = 10 * 32  # Center Y (tile 10 * 32 pixels)
        self.player = Player(spawn_x, spawn_y, self.game_engine.get_asset_manager())
        
        # Create enemies
        self._spawn_enemies()
        
        # Spawn items
        self._spawn_items()
        
        # Create HUD
        self.hud = HUD(self.game_engine.get_asset_manager())
        
        # Start gameplay music
        # self.game_engine.get_asset_manager().play_music('gameplay_theme')
        
    def exit(self):
        """Cleanup gameplay"""
        super().exit()
        
    def update(self, dt: float):
        """Update gameplay logic"""
        if not self.active:
            return
            
        input_manager = self.game_engine.get_input_manager()
        
        # Handle pause
        if input_manager.is_pause_pressed():
            self.game_engine.change_state(GameStateType.PAUSED)
            return
            
        # Handle save/load
        if input_manager.is_save_pressed():
            self._save_game()
            
        if input_manager.is_load_pressed():
            self._load_game()
            
        # Handle world manager input
        for event in pygame.event.get():
            if self.world_manager:
                self.world_manager.handle_input(event)
        
        # Update world manager
        if self.world_manager and self.player:
            self.world_manager.update(dt, (self.player.x, self.player.y))
        
        # Update player with world collision
        if self.player and self.world_manager:
            # Pass collision rects to player
            collision_rects = self.world_manager.get_collision_rects()
            self.player.update(dt, input_manager, collision_rects)
            
            # Check hazard damage
            hazard_damage = self.world_manager.check_hazard_collision(
                pygame.Rect(self.player.x - 16, self.player.y - 16, 32, 32)
            )
            if hazard_damage > 0:
                self.player.take_damage(hazard_damage)
            
            # Check if player died
            if self.player.health <= 0:
                self.game_engine.change_state(GameStateType.GAME_OVER)
                return
                
        # Update enemies
        for enemy in self.enemies[:]:
            if self.world_manager:
                collision_rects = self.world_manager.get_collision_rects()
                enemy.update(dt, self.player, collision_rects)
            
            # Remove dead enemies
            if enemy.health <= 0:
                self.enemies.remove(enemy)
            
        # Update HUD
        if self.hud and self.player:
            self.hud.update(dt, self.player)
            
    def render(self, screen: pygame.Surface):
        """Render gameplay graphics"""
        if not self.active:
            return
            
        # Clear screen
        screen.fill(Config.BLACK)
        
        # Create game area surface (excluding HUD)
        game_surface = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT - Config.HUD_HEIGHT))
        game_surface.fill(Config.BLACK)
        
        # Render world (includes parallax, tilemap, editor UI)
        if self.world_manager:
            self.world_manager.render(game_surface)
            
        # Get camera offset for entities
        camera_offset = (0, 0)
        if self.world_manager:
            camera_offset = self.world_manager.camera.get_offset()
            
        # Render player
        if self.player:
            self.player.render(game_surface, camera_offset)
            
        # Render enemies
        for enemy in self.enemies:
            enemy.render(game_surface, camera_offset)
            
        # Render items
        if self.player:
            self.player.item_manager.render(game_surface, camera_offset)
            
        # Blit game surface to main screen
        screen.blit(game_surface, (0, Config.HUD_HEIGHT))
        
        # Render HUD
        if self.hud:
            self.hud.render(screen, self.player)
            
    def _spawn_enemies(self):
        """Spawn enemies in the level"""
        asset_manager = self.game_engine.get_asset_manager()
        
        # Spawn some test enemies around the map
        enemy_spawns = [
            (10 * 32, 8 * 32, 'standard'),    # Left side - nuovo nemico
            (50 * 32, 12 * 32, 'standard'),   # Right side - nuovo nemico
            (25 * 32, 5 * 32, 'standard'),    # Top center - nuovo nemico
            (35 * 32, 15 * 32, 'standard'),   # Bottom right - nuovo nemico
            (15 * 32, 12 * 32, 'standard'),   # Extra spawn
            (45 * 32, 8 * 32, 'standard'),    # Extra spawn
        ]
        
        for spawn_point in enemy_spawns:
            x, y, enemy_type = spawn_point
            
            if enemy_type == 'standard':
                enemy = EnemyStandard(x, y, asset_manager)
            elif enemy_type == 'mutant':
                enemy = MutantEnemy(x, y, asset_manager)
            elif enemy_type == 'robot':
                enemy = RobotEnemy(x, y, asset_manager)
            elif enemy_type == 'mercenary':
                enemy = MercenaryEnemy(x, y, asset_manager)
            else:
                enemy = EnemyStandard(x, y, asset_manager)  # Default al nuovo nemico
                
            self.enemies.append(enemy)
    
    def _spawn_items(self):
        """Spawn test items in the level"""
        if not self.player:
            return
            
        # Spawn various test items around the map
        item_spawns = [
            (20 * 32, 10 * 32, ItemType.MEDIKIT),
            (40 * 32, 8 * 32, ItemType.AMMO),
            (12 * 32, 6 * 32, ItemType.SHIELD),
            (48 * 32, 14 * 32, ItemType.DAMAGE_BOOST),
            (28 * 32, 12 * 32, ItemType.SPEED_BOOST),
            (8 * 32, 9 * 32, ItemType.JETPACK),
            (52 * 32, 7 * 32, ItemType.ARMOR),
            (16 * 32, 14 * 32, ItemType.WEAPON_MOD),
            (36 * 32, 6 * 32, ItemType.KEYCARD),
            (44 * 32, 11 * 32, ItemType.CREDITS),
            (24 * 32, 8 * 32, ItemType.CHECKPOINT),
            (32 * 32, 16 * 32, ItemType.ARTIFACT),
        ]
        
        for spawn_point in item_spawns:
            x, y, item_type = spawn_point
            self.player.item_manager.spawn_item(x, y, item_type)
            
    def _save_game(self):
        """Save current game state"""
        # TODO: Implement save functionality
        print("Game saved! (not implemented yet)")
        
    def _load_game(self):
        """Load saved game state"""
        # TODO: Implement load functionality
        print("Game loaded! (not implemented yet)")