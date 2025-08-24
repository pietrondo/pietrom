#!/usr/bin/env python3
"""
Procedural Level Generator
Generates random levels with platforms, secrets, and challenges

Developed by Team PIETRO
PIETRO's generator creates infinite worlds for endless adventures!
"""

import random
import math
from typing import List, Tuple, Dict, Any
from ...core.config import Config
from .level import Level, Tile

class LevelGenerator:
    """Procedural level generator"""
    
    def __init__(self, asset_manager):
        self.asset_manager = asset_manager
        
        # Generation parameters
        self.min_width = 40
        self.max_width = 80
        self.min_height = 25
        self.max_height = 35
        
        # Structure parameters
        self.platform_density = 0.3
        self.enemy_density = 0.15
        self.collectible_density = 0.2
        self.secret_chance = 0.1
        
    def generate_level(self, difficulty: int = 1, seed: int = None) -> Level:
        """Generate a new level"""
        if seed is not None:
            random.seed(seed)
            
        # Determine level size based on difficulty
        width = self.min_width + (difficulty * 5)
        height = self.min_height + (difficulty * 2)
        width = min(width, self.max_width)
        height = min(height, self.max_height)
        
        # Create level
        level = Level(width, height, self.asset_manager)
        level.tiles.clear()  # Clear default tiles
        
        # Generate level structure
        self._generate_terrain(level, difficulty)
        self._generate_platforms(level, difficulty)
        self._generate_structures(level, difficulty)
        self._generate_secrets(level, difficulty)
        self._place_spawns(level, difficulty)
        self._place_collectibles(level, difficulty)
        self._place_enemies(level, difficulty)
        
        return level
        
    def _generate_terrain(self, level: Level, difficulty: int):
        """Generate basic terrain (ground, walls, ceiling)"""
        # Create ground with variation
        ground_height = level.height - 4
        ground_variation = 2
        
        for x in range(level.width):
            # Vary ground height
            variation = int(math.sin(x * 0.3) * ground_variation)
            current_ground = ground_height + variation
            
            # Fill ground
            for y in range(current_ground, level.height):
                if y == current_ground:
                    level.set_tile(x, y, 'ground')
                else:
                    level.set_tile(x, y, 'ground')
                    
        # Create walls
        for y in range(level.height):
            level.set_tile(0, y, 'wall')
            level.set_tile(level.width - 1, y, 'wall')
            
        # Create ceiling in some areas
        if difficulty >= 2:
            ceiling_sections = random.randint(1, 3)
            for _ in range(ceiling_sections):
                start_x = random.randint(5, level.width - 15)
                length = random.randint(5, 10)
                
                for x in range(start_x, min(start_x + length, level.width - 1)):
                    level.set_tile(x, 0, 'wall')
                    level.set_tile(x, 1, 'wall')
                    
    def _generate_platforms(self, level: Level, difficulty: int):
        """Generate platforms throughout the level"""
        ground_y = level.height - 4
        platform_count = int(level.width * self.platform_density)
        
        for _ in range(platform_count):
            # Random platform position
            platform_x = random.randint(3, level.width - 8)
            platform_y = random.randint(5, ground_y - 3)
            platform_length = random.randint(2, 6)
            
            # Check if area is clear
            clear = True
            for i in range(platform_length):
                if level.get_tile(platform_x + i, platform_y):
                    clear = False
                    break
                    
            if clear:
                # Create platform
                for i in range(platform_length):
                    if platform_x + i < level.width - 1:
                        level.set_tile(platform_x + i, platform_y, 'platform')
                        
                # Add support pillars occasionally
                if random.random() < 0.3:
                    support_x = platform_x + platform_length // 2
                    for y in range(platform_y + 1, ground_y):
                        if not level.get_tile(support_x, y):
                            level.set_tile(support_x, y, 'wall')
                        else:
                            break
                            
    def _generate_structures(self, level: Level, difficulty: int):
        """Generate special structures (stairs, towers, etc.)"""
        structure_count = random.randint(1, 3)
        
        for _ in range(structure_count):
            structure_type = random.choice(['stairs', 'tower', 'bridge', 'maze'])
            
            if structure_type == 'stairs':
                self._create_stairs(level)
            elif structure_type == 'tower':
                self._create_tower(level)
            elif structure_type == 'bridge':
                self._create_bridge(level)
            elif structure_type == 'maze' and difficulty >= 3:
                self._create_maze_section(level)
                
    def _create_stairs(self, level: Level):
        """Create stair structure"""
        start_x = random.randint(5, level.width - 15)
        start_y = level.height - 5
        stair_height = random.randint(4, 8)
        going_up = random.choice([True, False])
        
        for i in range(stair_height):
            step_y = start_y - i if going_up else start_y + i
            if 0 < step_y < level.height - 1:
                # Create step
                for j in range(i + 1):
                    step_x = start_x + (i if going_up else -i)
                    if 0 < step_x < level.width - 1:
                        level.set_tile(step_x, step_y - j, 'platform')
                        
    def _create_tower(self, level: Level):
        """Create tower structure"""
        tower_x = random.randint(8, level.width - 8)
        tower_height = random.randint(6, 12)
        tower_width = random.randint(3, 5)
        
        ground_y = level.height - 4
        tower_base = ground_y - tower_height
        
        if tower_base > 2:
            # Create tower walls
            for y in range(tower_base, ground_y):
                level.set_tile(tower_x, y, 'wall')
                level.set_tile(tower_x + tower_width - 1, y, 'wall')
                
            # Create tower floors
            floor_count = tower_height // 4
            for i in range(1, floor_count):
                floor_y = tower_base + (i * 4)
                for x in range(tower_x, tower_x + tower_width):
                    level.set_tile(x, floor_y, 'platform')
                    
            # Create tower top
            for x in range(tower_x, tower_x + tower_width):
                level.set_tile(x, tower_base, 'wall')
                
    def _create_bridge(self, level: Level):
        """Create bridge between platforms"""
        bridge_y = random.randint(8, level.height - 8)
        bridge_start = random.randint(5, level.width // 2)
        bridge_end = random.randint(level.width // 2, level.width - 5)
        
        # Create bridge
        for x in range(bridge_start, bridge_end):
            level.set_tile(x, bridge_y, 'platform')
            
        # Add support pillars
        pillar_spacing = 6
        for x in range(bridge_start, bridge_end, pillar_spacing):
            for y in range(bridge_y + 1, level.height - 1):
                if level.get_tile(x, y):
                    break
                level.set_tile(x, y, 'wall')
                
    def _create_maze_section(self, level: Level):
        """Create small maze section"""
        maze_x = random.randint(10, level.width - 20)
        maze_y = random.randint(5, level.height - 15)
        maze_width = 10
        maze_height = 8
        
        # Create maze walls
        for x in range(maze_x, maze_x + maze_width):
            for y in range(maze_y, maze_y + maze_height):
                if (x - maze_x) % 2 == 0 or (y - maze_y) % 2 == 0:
                    if random.random() < 0.7:  # 70% chance for wall
                        level.set_tile(x, y, 'wall')
                        
        # Ensure entrance and exit
        level.set_tile(maze_x, maze_y + maze_height // 2, None)
        level.set_tile(maze_x + maze_width - 1, maze_y + maze_height // 2, None)
        
    def _generate_secrets(self, level: Level, difficulty: int):
        """Generate secret areas and passages"""
        secret_count = random.randint(1, 2) if difficulty >= 2 else 0
        
        for _ in range(secret_count):
            secret_type = random.choice(['hidden_room', 'secret_passage', 'treasure_room'])
            
            if secret_type == 'hidden_room':
                self._create_hidden_room(level)
            elif secret_type == 'secret_passage':
                self._create_secret_passage(level)
            elif secret_type == 'treasure_room':
                self._create_treasure_room(level)
                
    def _create_hidden_room(self, level: Level):
        """Create hidden room behind wall"""
        room_x = random.randint(5, level.width - 10)
        room_y = random.randint(5, level.height - 10)
        room_width = random.randint(4, 6)
        room_height = random.randint(3, 5)
        
        # Clear room area
        for x in range(room_x, room_x + room_width):
            for y in range(room_y, room_y + room_height):
                level.tiles.pop((x, y), None)
                
        # Create room walls
        for x in range(room_x, room_x + room_width):
            level.set_tile(x, room_y, 'wall')
            level.set_tile(x, room_y + room_height - 1, 'wall')
            
        for y in range(room_y, room_y + room_height):
            level.set_tile(room_x, y, 'wall')
            level.set_tile(room_x + room_width - 1, y, 'wall')
            
        # Create secret entrance
        entrance_side = random.choice(['left', 'right', 'top', 'bottom'])
        if entrance_side == 'left':
            level.tiles.pop((room_x, room_y + room_height // 2), None)
        elif entrance_side == 'right':
            level.tiles.pop((room_x + room_width - 1, room_y + room_height // 2), None)
            
        # Add secret marker
        level.secrets.append({
            'type': 'hidden_room',
            'x': room_x * Config.TILE_SIZE,
            'y': room_y * Config.TILE_SIZE,
            'width': room_width * Config.TILE_SIZE,
            'height': room_height * Config.TILE_SIZE
        })
        
    def _create_secret_passage(self, level: Level):
        """Create secret passage through walls"""
        passage_y = random.randint(5, level.height - 5)
        passage_start = random.randint(5, level.width // 2)
        passage_end = random.randint(level.width // 2, level.width - 5)
        
        # Create hidden passage
        for x in range(passage_start, passage_end):
            level.tiles.pop((x, passage_y), None)
            level.tiles.pop((x, passage_y + 1), None)
            
    def _create_treasure_room(self, level: Level):
        """Create treasure room with valuable items"""
        room_x = random.randint(8, level.width - 12)
        room_y = random.randint(8, level.height - 8)
        room_size = 4
        
        # Create room
        for x in range(room_x, room_x + room_size):
            for y in range(room_y, room_y + room_size):
                if x == room_x or x == room_x + room_size - 1 or y == room_y or y == room_y + room_size - 1:
                    level.set_tile(x, y, 'wall')
                else:
                    level.tiles.pop((x, y), None)
                    
        # Create entrance
        level.tiles.pop((room_x + room_size // 2, room_y + room_size - 1), None)
        
        # Add treasure
        treasure_x = (room_x + room_size // 2) * Config.TILE_SIZE
        treasure_y = (room_y + room_size // 2) * Config.TILE_SIZE
        
        level.collectibles.append({
            'type': 'powerup',
            'subtype': 'mega_health',
            'x': treasure_x,
            'y': treasure_y,
            'value': 100,
            'collected': False
        })
        
    def _place_spawns(self, level: Level, difficulty: int):
        """Place player and enemy spawn points"""
        # Clear existing spawns
        level.spawn_points.clear()
        level.enemy_spawns.clear()
        
        # Find suitable spawn locations
        spawn_candidates = []
        
        for x in range(2, level.width - 2):
            for y in range(2, level.height - 2):
                # Check if position is clear and has ground below
                if (not level.get_tile(x, y) and 
                    not level.get_tile(x, y - 1) and 
                    level.is_solid_at(x, y + 1)):
                    spawn_candidates.append((x, y))
                    
        # Place player spawn (prefer left side)
        player_spawns = [pos for pos in spawn_candidates if pos[0] < level.width // 3]
        if player_spawns:
            level.spawn_points.append(random.choice(player_spawns))
        elif spawn_candidates:
            level.spawn_points.append(spawn_candidates[0])
            
    def _place_collectibles(self, level: Level, difficulty: int):
        """Place collectible items"""
        level.collectibles.clear()
        
        collectible_count = int(level.width * level.height * self.collectible_density)
        
        # Find suitable positions
        positions = []
        for x in range(1, level.width - 1):
            for y in range(1, level.height - 1):
                if (not level.get_tile(x, y) and 
                    level.is_solid_at(x, y + 1)):
                    positions.append((x, y))
                    
        # Place collectibles
        random.shuffle(positions)
        
        for i, pos in enumerate(positions[:collectible_count]):
            item_type = self._choose_collectible_type(difficulty)
            
            collectible = {
                'type': item_type['type'],
                'x': pos[0] * Config.TILE_SIZE,
                'y': pos[1] * Config.TILE_SIZE,
                'collected': False
            }
            
            # Add type-specific properties
            collectible.update(item_type)
            level.collectibles.append(collectible)
            
    def _choose_collectible_type(self, difficulty: int) -> Dict[str, Any]:
        """Choose collectible type based on difficulty"""
        types = [
            {'type': 'health_pack', 'value': 25},
            {'type': 'ammo', 'subtype': 'pistol', 'value': 20},
            {'type': 'ammo', 'subtype': 'shotgun', 'value': 10},
        ]
        
        if difficulty >= 2:
            types.extend([
                {'type': 'ammo', 'subtype': 'rocket', 'value': 5},
                {'type': 'powerup', 'subtype': 'speed_boost', 'duration': 10.0},
            ])
            
        if difficulty >= 3:
            types.extend([
                {'type': 'powerup', 'subtype': 'damage_boost', 'duration': 15.0},
                {'type': 'powerup', 'subtype': 'invincibility', 'duration': 5.0},
            ])
            
        return random.choice(types)
        
    def _place_enemies(self, level: Level, difficulty: int):
        """Place enemy spawn points"""
        enemy_count = int(level.width * level.height * self.enemy_density * difficulty)
        
        # Find suitable positions (away from player spawn)
        player_spawn = level.spawn_points[0] if level.spawn_points else (5, 5)
        
        positions = []
        for x in range(1, level.width - 1):
            for y in range(1, level.height - 1):
                if (not level.get_tile(x, y) and 
                    level.is_solid_at(x, y + 1) and
                    abs(x - player_spawn[0]) > 5):  # Keep distance from player
                    positions.append((x, y))
                    
        # Place enemies
        random.shuffle(positions)
        
        for i, pos in enumerate(positions[:enemy_count]):
            enemy_type = self._choose_enemy_type(difficulty)
            level.enemy_spawns.append((pos[0], pos[1], enemy_type))
            
    def _choose_enemy_type(self, difficulty: int) -> str:
        """Choose enemy type based on difficulty"""
        if difficulty == 1:
            return random.choice(['standard', 'standard', 'mutant'])
        elif difficulty == 2:
            return random.choice(['standard', 'standard', 'mutant', 'robot'])
        else:
            return random.choice(['standard', 'mutant', 'robot', 'mercenary'])