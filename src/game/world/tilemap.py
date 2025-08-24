import pygame
import json
import csv
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from .spritesheet_loader import SpritesheetLoader, TilemapConfig
from .autotiling import AutotilingSystem, AutotileType, AutotilePalette

class TileLayer(Enum):
    """Layer del tilemap"""
    SOLID = "solid"      # Layer per collisioni
    DECOR = "decor"      # Layer decorativo
    HAZARD = "hazard"    # Layer per trappole e pericoli

class TileType:
    """Tipi di tile con le loro proprietà"""
    EMPTY = 0
    GROUND_BASE = 1
    GROUND_WORN = 2
    WALL_BASIC = 3
    WALL_REINFORCED = 4
    STAIRS = 5
    PIPES = 6
    DOOR_STANDARD = 7
    DOOR_REINFORCED = 8
    DOOR_ELECTRONIC = 9
    TERMINAL = 10
    DECAL = 11
    LASER_TRAP = 12
    SPIKE_TRAP = 13
    NEON_SIGN = 14

class Tile:
    """Rappresenta un singolo tile"""
    
    def __init__(self, tile_id: int = 0, sprite_row: int = 0, sprite_col: int = 0, 
                 solid: bool = False, hazard: bool = False):
        self.tile_id = tile_id
        self.sprite_row = sprite_row
        self.sprite_col = sprite_col
        self.solid = solid
        self.hazard = hazard
        self.damage = 0  # Danno per tile hazard
        self.properties = {}  # Proprietà aggiuntive

class Tilemap:
    """Sistema di tilemap completo con layer multipli"""
    
    TILE_SIZE = 32
    
    def __init__(self, width: int, height: int, config_path: str = "assets/tilemap_config.json"):
        self.width = width
        self.height = height
        
        # Carica configurazione
        self.config = TilemapConfig(config_path)
        
        # Carica spritesheet
        spritesheet_path = self.config.get('spritesheet', 'assets/sprites/level.png')
        self.spritesheet = SpritesheetLoader(spritesheet_path, self.TILE_SIZE)
        
        # Sistema di autotiling
        self.autotiling = AutotilingSystem()
        self.autotile_palette = AutotilePalette()
        
        # Layer del tilemap
        self.layers = {
            TileLayer.SOLID: [[Tile() for _ in range(width)] for _ in range(height)],
            TileLayer.DECOR: [[Tile() for _ in range(width)] for _ in range(height)],
            TileLayer.HAZARD: [[Tile() for _ in range(width)] for _ in range(height)]
        }
        
        # Cache per collisioni
        self.collision_rects = []
        self.hazard_rects = []
        self._collision_cache_dirty = True
        
        # Debug mode
        self.debug_mode = False
        self.show_grid = False
        self.show_tile_indices = False
        
        print(f"Tilemap creato: {width}x{height} tile")
    
    def set_tile(self, layer: TileLayer, x: int, y: int, tile: Tile):
        """Imposta un tile in un layer specifico"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.layers[layer][y][x] = tile
            if layer == TileLayer.SOLID:
                self._collision_cache_dirty = True
    
    def get_tile(self, layer: TileLayer, x: int, y: int) -> Optional[Tile]:
        """Ottieni un tile da un layer specifico"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.layers[layer][y][x]
        return None
    
    def set_tile_by_id(self, layer: TileLayer, x: int, y: int, tile_id: int, 
                       sprite_row: int = 0, sprite_col: int = 0):
        """Imposta un tile usando ID e coordinate sprite"""
        tile = Tile(tile_id, sprite_row, sprite_col)
        
        # Imposta proprietà basate sul tipo
        if tile_id in [TileType.GROUND_BASE, TileType.GROUND_WORN, 
                       TileType.WALL_BASIC, TileType.WALL_REINFORCED]:
            tile.solid = True
        elif tile_id in [TileType.LASER_TRAP, TileType.SPIKE_TRAP]:
            tile.hazard = True
            tile.damage = 10 if tile_id == TileType.SPIKE_TRAP else 15
        
        self.set_tile(layer, x, y, tile)
    
    def apply_autotiling(self, layer: TileLayer, tile_type: AutotileType, 
                        solid_pattern: List[List[bool]]):
        """Applica autotiling a un'area del tilemap"""
        autotile_grid = self.autotiling.generate_autotile_grid(solid_pattern, tile_type)
        
        for y in range(len(autotile_grid)):
            for x in range(len(autotile_grid[y])):
                if autotile_grid[y][x] != -1:
                    # Converti indice autotile in coordinate sprite
                    sprite_row, sprite_col = self.autotile_palette.get_tile_coords(
                        tile_type, autotile_grid[y][x]
                    )
                    
                    # Determina il tile_id basato sul tipo
                    tile_id = TileType.GROUND_BASE if tile_type == AutotileType.GROUND else TileType.WALL_BASIC
                    
                    self.set_tile_by_id(layer, x, y, tile_id, sprite_row, sprite_col)
    
    def place_door(self, x: int, y: int, door_type: str = "standard"):
        """Piazza una porta del tipo specificato"""
        door_config = self.config.get_door_type(door_type)
        if not door_config:
            print(f"Tipo di porta sconosciuto: {door_type}")
            return
        
        sprite_row = door_config['row']
        sprite_col = door_config['col']
        
        # Mappa i tipi di porta agli ID
        door_id_map = {
            'standard': TileType.DOOR_STANDARD,
            'reinforced': TileType.DOOR_REINFORCED,
            'electronic': TileType.DOOR_ELECTRONIC
        }
        
        tile_id = door_id_map.get(door_type, TileType.DOOR_STANDARD)
        self.set_tile_by_id(TileLayer.SOLID, x, y, tile_id, sprite_row, sprite_col)
    
    def _update_collision_cache(self):
        """Aggiorna la cache delle collisioni"""
        if not self._collision_cache_dirty:
            return
        
        self.collision_rects.clear()
        self.hazard_rects.clear()
        
        # Genera rettangoli di collisione per tile SOLID
        for y in range(self.height):
            for x in range(self.width):
                solid_tile = self.layers[TileLayer.SOLID][y][x]
                if solid_tile.solid:
                    rect = pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE, 
                                     self.TILE_SIZE, self.TILE_SIZE)
                    self.collision_rects.append(rect)
                
                # Genera rettangoli per hazard
                hazard_tile = self.layers[TileLayer.HAZARD][y][x]
                if hazard_tile.hazard:
                    rect = pygame.Rect(x * self.TILE_SIZE, y * self.TILE_SIZE, 
                                     self.TILE_SIZE, self.TILE_SIZE)
                    self.hazard_rects.append((rect, hazard_tile.damage))
        
        self._collision_cache_dirty = False
        print(f"Cache collisioni aggiornata: {len(self.collision_rects)} tile solidi, {len(self.hazard_rects)} hazard")
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """Ottieni tutti i rettangoli di collisione"""
        self._update_collision_cache()
        return self.collision_rects
    
    def get_hazard_rects(self) -> List[Tuple[pygame.Rect, int]]:
        """Ottieni tutti i rettangoli hazard con il loro danno"""
        self._update_collision_cache()
        return self.hazard_rects
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        """Controlla collisione con tile solidi"""
        collision_rects = self.get_collision_rects()
        return any(rect.colliderect(tile_rect) for tile_rect in collision_rects)
    
    def check_hazard_collision(self, rect: pygame.Rect) -> int:
        """Controlla collisione con hazard e restituisce il danno totale"""
        hazard_rects = self.get_hazard_rects()
        total_damage = 0
        for hazard_rect, damage in hazard_rects:
            if rect.colliderect(hazard_rect):
                total_damage += damage
        return total_damage
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Renderizza il tilemap con culling della camera"""
        offset_x, offset_y = camera_offset
        
        # Calcola i tile visibili
        screen_width, screen_height = surface.get_size()
        start_x = max(0, offset_x // self.TILE_SIZE)
        start_y = max(0, offset_y // self.TILE_SIZE)
        end_x = min(self.width, (offset_x + screen_width) // self.TILE_SIZE + 2)
        end_y = min(self.height, (offset_y + screen_height) // self.TILE_SIZE + 2)
        
        # Rendering ordinato: SOLID -> DECOR -> HAZARD
        layer_order = [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]
        
        for layer in layer_order:
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    tile = self.layers[layer][y][x]
                    if tile.tile_id != TileType.EMPTY:
                        # Ottieni sprite dal spritesheet
                        sprite = self.spritesheet.get_tile(tile.sprite_row, tile.sprite_col)
                        if sprite:
                            screen_x = x * self.TILE_SIZE - offset_x
                            screen_y = y * self.TILE_SIZE - offset_y
                            surface.blit(sprite, (screen_x, screen_y))
        
        # Debug rendering
        if self.debug_mode:
            self._render_debug(surface, camera_offset, start_x, start_y, end_x, end_y)
    
    def _render_debug(self, surface: pygame.Surface, camera_offset: Tuple[int, int],
                     start_x: int, start_y: int, end_x: int, end_y: int):
        """Renderizza informazioni di debug"""
        offset_x, offset_y = camera_offset
        
        # Griglia
        if self.show_grid:
            grid_color = (100, 100, 100, 128)
            for x in range(start_x, end_x + 1):
                screen_x = x * self.TILE_SIZE - offset_x
                pygame.draw.line(surface, grid_color, 
                               (screen_x, 0), (screen_x, surface.get_height()))
            
            for y in range(start_y, end_y + 1):
                screen_y = y * self.TILE_SIZE - offset_y
                pygame.draw.line(surface, grid_color, 
                               (0, screen_y), (surface.get_width(), screen_y))
        
        # Indici tile
        if self.show_tile_indices:
            font = pygame.font.Font(None, 16)
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    screen_x = x * self.TILE_SIZE - offset_x
                    screen_y = y * self.TILE_SIZE - offset_y
                    
                    # Mostra ID del tile SOLID
                    solid_tile = self.layers[TileLayer.SOLID][y][x]
                    if solid_tile.tile_id != TileType.EMPTY:
                        text = font.render(str(solid_tile.tile_id), True, (255, 255, 0))
                        surface.blit(text, (screen_x + 2, screen_y + 2))
    
    def save_to_json(self, filename: str):
        """Salva il tilemap in formato JSON"""
        data = {
            'width': self.width,
            'height': self.height,
            'layers': {}
        }
        
        for layer_name, layer_data in self.layers.items():
            layer_tiles = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    tile = layer_data[y][x]
                    tile_data = {
                        'id': tile.tile_id,
                        'sprite_row': tile.sprite_row,
                        'sprite_col': tile.sprite_col,
                        'solid': tile.solid,
                        'hazard': tile.hazard,
                        'damage': tile.damage
                    }
                    row.append(tile_data)
                layer_tiles.append(row)
            data['layers'][layer_name.value] = layer_tiles
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Tilemap salvato in: {filename}")
    
    def load_from_json(self, filename: str):
        """Carica il tilemap da formato JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.width = data['width']
            self.height = data['height']
            
            # Ricrea i layer
            self.layers = {
                TileLayer.SOLID: [[Tile() for _ in range(self.width)] for _ in range(self.height)],
                TileLayer.DECOR: [[Tile() for _ in range(self.width)] for _ in range(self.height)],
                TileLayer.HAZARD: [[Tile() for _ in range(self.width)] for _ in range(self.height)]
            }
            
            # Carica i tile
            for layer_name, layer_tiles in data['layers'].items():
                layer = TileLayer(layer_name)
                for y in range(self.height):
                    for x in range(self.width):
                        tile_data = layer_tiles[y][x]
                        tile = Tile(
                            tile_data['id'],
                            tile_data['sprite_row'],
                            tile_data['sprite_col'],
                            tile_data.get('solid', False),
                            tile_data.get('hazard', False)
                        )
                        tile.damage = tile_data.get('damage', 0)
                        self.layers[layer][y][x] = tile
            
            self._collision_cache_dirty = True
            print(f"Tilemap caricato da: {filename}")
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Errore nel caricamento tilemap {filename}: {e}")
    
    def save_to_csv(self, filename: str, layer: TileLayer):
        """Salva un layer in formato CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    tile = self.layers[layer][y][x]
                    row.append(tile.tile_id)
                writer.writerow(row)
        print(f"Layer {layer.value} salvato in CSV: {filename}")
    
    def toggle_debug_mode(self):
        """Attiva/disattiva modalità debug"""
        self.debug_mode = not self.debug_mode
        print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
    
    def toggle_grid(self):
        """Attiva/disattiva visualizzazione griglia"""
        self.show_grid = not self.show_grid
        print(f"Grid overlay: {'ON' if self.show_grid else 'OFF'}")
    
    def toggle_tile_indices(self):
        """Attiva/disattiva visualizzazione indici tile"""
        self.show_tile_indices = not self.show_tile_indices
        print(f"Tile indices: {'ON' if self.show_tile_indices else 'OFF'}")
    
    def get_tile_at_world_pos(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Converte coordinate mondo in coordinate tile"""
        tile_x = world_x // self.TILE_SIZE
        tile_y = world_y // self.TILE_SIZE
        return (tile_x, tile_y)
    
    def get_world_pos_from_tile(self, tile_x: int, tile_y: int) -> Tuple[int, int]:
        """Converte coordinate tile in coordinate mondo"""
        world_x = tile_x * self.TILE_SIZE
        world_y = tile_y * self.TILE_SIZE
        return (world_x, world_y)