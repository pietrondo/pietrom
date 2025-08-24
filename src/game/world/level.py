#!/usr/bin/env python3
"""
Level System
Game level management and collision detection

Developed by Team PIETRO
PIETRO's levels challenge warriors with intricate designs!
"""

import pygame
import random
from typing import List, Tuple, Optional, Dict, Any
from ...core.config import Config

class Tile:
    """Individual tile in the level"""
    
    def __init__(self, x: int, y: int, tile_type: str):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.solid = tile_type in ['wall', 'platform', 'ground']
        self.destructible = tile_type in ['crate', 'barrel']
        self.interactive = tile_type in ['door', 'switch', 'terminal']
        
    def get_rect(self) -> pygame.Rect:
        """Get tile collision rectangle"""
        return pygame.Rect(self.x * Config.TILE_SIZE, self.y * Config.TILE_SIZE, 
                          Config.TILE_SIZE, Config.TILE_SIZE)

class Level:
    """Game level with tiles, entities, and collision detection"""
    
    def __init__(self, width: int, height: int, asset_manager):
        self.width = width
        self.height = height
        self.asset_manager = asset_manager
        
        # Level data
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.spawn_points: List[Tuple[int, int]] = []
        self.enemy_spawns: List[Tuple[int, int, str]] = []  # x, y, enemy_type
        self.collectibles: List[Dict[str, Any]] = []
        self.secrets: List[Dict[str, Any]] = []
        
        # Level properties
        self.background_color = Config.BLACK
        self.ambient_light = 0.8
        self.gravity = Config.GRAVITY
        
        # Generate basic level structure
        self._generate_basic_structure()
        
    def _generate_basic_structure(self):
        """Generate basic level structure"""
        # Create ground
        ground_y = self.height - 3
        for x in range(self.width):
            self.set_tile(x, ground_y, 'ground')
            self.set_tile(x, ground_y + 1, 'ground')
            self.set_tile(x, ground_y + 2, 'ground')
            
        # Create walls
        for y in range(self.height):
            self.set_tile(0, y, 'wall')
            self.set_tile(self.width - 1, y, 'wall')
            
        # Add some platforms
        self._add_platforms()
        
        # Add spawn points
        self.spawn_points.append((2, ground_y - 1))
        
        # Add enemy spawns
        self._add_enemy_spawns()
        
        # Add collectibles
        self._add_collectibles()
        
    def _add_platforms(self):
        """Add platforms to the level"""
        ground_y = self.height - 3
        
        # Add some random platforms
        for _ in range(random.randint(3, 6)):
            platform_x = random.randint(5, self.width - 10)
            platform_y = random.randint(ground_y - 15, ground_y - 5)
            platform_length = random.randint(3, 8)
            
            for i in range(platform_length):
                if platform_x + i < self.width - 1:
                    self.set_tile(platform_x + i, platform_y, 'platform')
                    
        # Add some stairs
        stair_x = random.randint(10, self.width - 15)
        for i in range(5):
            for j in range(i + 1):
                if stair_x + i < self.width - 1 and ground_y - j - 1 > 0:
                    self.set_tile(stair_x + i, ground_y - j - 1, 'platform')
                    
    def _add_enemy_spawns(self):
        """Add enemy spawn points"""
        ground_y = self.height - 3
        
        # Add standard enemy spawns (nuovo nemico principale)
        for _ in range(random.randint(3, 5)):
            spawn_x = random.randint(5, self.width - 5)
            self.enemy_spawns.append((spawn_x, ground_y - 1, 'standard'))
            
        # Add standard enemies on platforms
        for _ in range(random.randint(1, 3)):
            spawn_x = random.randint(5, self.width - 5)
            spawn_y = random.randint(ground_y - 10, ground_y - 5)
            self.enemy_spawns.append((spawn_x, spawn_y, 'standard'))
            
        # Add occasional mutant spawns
        for _ in range(random.randint(0, 1)):
            spawn_x = random.randint(10, self.width - 10)
            self.enemy_spawns.append((spawn_x, ground_y - 1, 'mutant'))
            
    def _add_collectibles(self):
        """Add collectible items to the level"""
        ground_y = self.height - 3
        
        # Add health packs
        for _ in range(random.randint(2, 4)):
            item_x = random.randint(3, self.width - 3)
            item_y = ground_y - 1
            self.collectibles.append({
                'type': 'health_pack',
                'x': item_x * Config.TILE_SIZE,
                'y': item_y * Config.TILE_SIZE,
                'value': 25,
                'collected': False
            })
            
        # Add ammo boxes
        for _ in range(random.randint(3, 5)):
            item_x = random.randint(3, self.width - 3)
            item_y = ground_y - 1
            ammo_type = random.choice(['pistol', 'shotgun', 'rocket'])
            self.collectibles.append({
                'type': 'ammo',
                'subtype': ammo_type,
                'x': item_x * Config.TILE_SIZE,
                'y': item_y * Config.TILE_SIZE,
                'value': 20,
                'collected': False
            })
            
        # Add power-ups
        for _ in range(random.randint(1, 2)):
            item_x = random.randint(5, self.width - 5)
            item_y = ground_y - 1
            powerup_type = random.choice(['speed_boost', 'damage_boost', 'invincibility'])
            self.collectibles.append({
                'type': 'powerup',
                'subtype': powerup_type,
                'x': item_x * Config.TILE_SIZE,
                'y': item_y * Config.TILE_SIZE,
                'duration': 10.0,
                'collected': False
            })
            
    def set_tile(self, x: int, y: int, tile_type: str):
        """Set tile at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[(x, y)] = Tile(x, y, tile_type)
            
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position"""
        return self.tiles.get((x, y))
        
    def get_tile_at_pixel(self, pixel_x: float, pixel_y: float) -> Optional[Tile]:
        """Get tile at pixel coordinates"""
        tile_x = int(pixel_x // Config.TILE_SIZE)
        tile_y = int(pixel_y // Config.TILE_SIZE)
        return self.get_tile(tile_x, tile_y)
        
    def is_solid_at(self, x: int, y: int) -> bool:
        """Check if tile at position is solid"""
        tile = self.get_tile(x, y)
        return tile is not None and tile.solid
        
    def is_solid_at_pixel(self, pixel_x: float, pixel_y: float) -> bool:
        """Check if position in pixels is solid"""
        tile_x = int(pixel_x // Config.TILE_SIZE)
        tile_y = int(pixel_y // Config.TILE_SIZE)
        return self.is_solid_at(tile_x, tile_y)
        
    def is_solid_at_rect(self, rect: pygame.Rect) -> bool:
        """Check if any part of rectangle intersects solid tiles"""
        start_x = int(rect.left // Config.TILE_SIZE)
        end_x = int(rect.right // Config.TILE_SIZE)
        start_y = int(rect.top // Config.TILE_SIZE)
        end_y = int(rect.bottom // Config.TILE_SIZE)
        
        for x in range(start_x, end_x + 1):
            for y in range(start_y, end_y + 1):
                if self.is_solid_at(x, y):
                    return True
                    
        return False
        
    def get_collision_rects(self, area_rect: pygame.Rect) -> List[pygame.Rect]:
        """Get all solid tile rectangles in the given area"""
        collision_rects = []
        
        start_x = max(0, int(area_rect.left // Config.TILE_SIZE))
        end_x = min(self.width, int(area_rect.right // Config.TILE_SIZE) + 1)
        start_y = max(0, int(area_rect.top // Config.TILE_SIZE))
        end_y = min(self.height, int(area_rect.bottom // Config.TILE_SIZE) + 1)
        
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.get_tile(x, y)
                if tile and tile.solid:
                    collision_rects.append(tile.get_rect())
                    
        return collision_rects
        
    def check_collectible_collision(self, rect: pygame.Rect) -> List[Dict[str, Any]]:
        """Check collision with collectible items"""
        collected_items = []
        
        for item in self.collectibles:
            if item['collected']:
                continue
                
            item_rect = pygame.Rect(item['x'], item['y'], Config.TILE_SIZE, Config.TILE_SIZE)
            if rect.colliderect(item_rect):
                item['collected'] = True
                collected_items.append(item)
                
        return collected_items
        
    def damage_tile(self, x: int, y: int, damage: int) -> bool:
        """Damage a tile (for destructible tiles)"""
        tile = self.get_tile(x, y)
        if tile and tile.destructible:
            # Remove destructible tile
            del self.tiles[(x, y)]
            return True
        return False
        
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render the level"""
        # Calculate visible tile range
        start_x = max(0, int(camera_offset[0] // Config.TILE_SIZE) - 1)
        end_x = min(self.width, int((camera_offset[0] + Config.SCREEN_WIDTH) // Config.TILE_SIZE) + 2)
        start_y = max(0, int(camera_offset[1] // Config.TILE_SIZE) - 1)
        end_y = min(self.height, int((camera_offset[1] + Config.SCREEN_HEIGHT) // Config.TILE_SIZE) + 2)
        
        # Render background
        surface.fill(self.background_color)
        
        # Render grid (debug)
        if Config.DEBUG_DRAW_GRID:
            self._render_grid(surface, camera_offset, start_x, end_x, start_y, end_y)
            
        # Render tiles
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                tile = self.get_tile(x, y)
                if tile:
                    self._render_tile(surface, tile, camera_offset)
                    
        # Render collectibles
        self._render_collectibles(surface, camera_offset)
        
    def _render_grid(self, surface: pygame.Surface, camera_offset: Tuple[int, int], 
                    start_x: int, end_x: int, start_y: int, end_y: int):
        """Render debug grid"""
        grid_color = (40, 40, 40)
        
        # Vertical lines
        for x in range(start_x, end_x + 1):
            screen_x = x * Config.TILE_SIZE - camera_offset[0]
            pygame.draw.line(surface, grid_color, 
                           (screen_x, 0), (screen_x, Config.SCREEN_HEIGHT))
                           
        # Horizontal lines
        for y in range(start_y, end_y + 1):
            screen_y = y * Config.TILE_SIZE - camera_offset[1]
            pygame.draw.line(surface, grid_color, 
                           (0, screen_y), (Config.SCREEN_WIDTH, screen_y))
                           
    def _render_tile(self, surface: pygame.Surface, tile: Tile, camera_offset: Tuple[int, int]):
        """Render individual tile"""
        screen_x = tile.x * Config.TILE_SIZE - camera_offset[0]
        screen_y = tile.y * Config.TILE_SIZE - camera_offset[1]
        
        # Skip if off-screen
        if (screen_x < -Config.TILE_SIZE or screen_x > Config.SCREEN_WIDTH or
            screen_y < -Config.TILE_SIZE or screen_y > Config.SCREEN_HEIGHT):
            return
            
        tile_rect = pygame.Rect(screen_x, screen_y, Config.TILE_SIZE, Config.TILE_SIZE)
        
        # Render based on tile type
        if tile.tile_type == 'ground':
            pygame.draw.rect(surface, Config.BROWN, tile_rect)
            pygame.draw.rect(surface, Config.DARK_BROWN, tile_rect, 2)
        elif tile.tile_type == 'wall':
            pygame.draw.rect(surface, Config.GRAY, tile_rect)
            pygame.draw.rect(surface, Config.DARK_GRAY, tile_rect, 2)
        elif tile.tile_type == 'platform':
            pygame.draw.rect(surface, Config.BLUE, tile_rect)
            pygame.draw.rect(surface, Config.DARK_BLUE, tile_rect, 2)
        elif tile.tile_type == 'crate':
            pygame.draw.rect(surface, Config.BROWN, tile_rect)
            pygame.draw.rect(surface, Config.BLACK, tile_rect, 2)
            # Draw X pattern
            pygame.draw.line(surface, Config.BLACK, 
                           (screen_x, screen_y), 
                           (screen_x + Config.TILE_SIZE, screen_y + Config.TILE_SIZE), 2)
            pygame.draw.line(surface, Config.BLACK, 
                           (screen_x + Config.TILE_SIZE, screen_y), 
                           (screen_x, screen_y + Config.TILE_SIZE), 2)
                           
    def _render_collectibles(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Render collectible items"""
        for item in self.collectibles:
            if item['collected']:
                continue
                
            screen_x = item['x'] - camera_offset[0]
            screen_y = item['y'] - camera_offset[1]
            
            # Skip if off-screen
            if (screen_x < -Config.TILE_SIZE or screen_x > Config.SCREEN_WIDTH or
                screen_y < -Config.TILE_SIZE or screen_y > Config.SCREEN_HEIGHT):
                continue
                
            item_rect = pygame.Rect(screen_x, screen_y, Config.TILE_SIZE, Config.TILE_SIZE)
            
            # Render based on item type
            if item['type'] == 'health_pack':
                pygame.draw.rect(surface, Config.RED, item_rect)
                pygame.draw.rect(surface, Config.WHITE, item_rect, 2)
                # Draw cross
                center_x = screen_x + Config.TILE_SIZE // 2
                center_y = screen_y + Config.TILE_SIZE // 2
                pygame.draw.line(surface, Config.WHITE, 
                               (center_x - 8, center_y), (center_x + 8, center_y), 3)
                pygame.draw.line(surface, Config.WHITE, 
                               (center_x, center_y - 8), (center_x, center_y + 8), 3)
                               
            elif item['type'] == 'ammo':
                pygame.draw.rect(surface, Config.YELLOW, item_rect)
                pygame.draw.rect(surface, Config.BLACK, item_rect, 2)
                
            elif item['type'] == 'powerup':
                pygame.draw.rect(surface, Config.MAGENTA, item_rect)
                pygame.draw.rect(surface, Config.WHITE, item_rect, 2)
                
    def get_spawn_point(self) -> Tuple[int, int]:
        """Get player spawn point"""
        if self.spawn_points:
            spawn = random.choice(self.spawn_points)
            return (spawn[0] * Config.TILE_SIZE, spawn[1] * Config.TILE_SIZE)
        return (Config.TILE_SIZE * 2, Config.TILE_SIZE * (self.height - 5))
        
    def get_enemy_spawns(self) -> List[Tuple[int, int, str]]:
        """Get enemy spawn points"""
        spawns = []
        for spawn in self.enemy_spawns:
            spawns.append((spawn[0] * Config.TILE_SIZE, spawn[1] * Config.TILE_SIZE, spawn[2]))
        return spawns