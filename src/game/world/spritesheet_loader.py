import pygame
import json
from typing import List, Dict, Tuple, Optional

class SpritesheetLoader:
    """Carica e gestisce spritesheet per tilemap con atlas indicizzato per (riga, colonna)"""
    
    def __init__(self, spritesheet_path: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.spritesheet_path = spritesheet_path
        self.atlas: List[List[pygame.Surface]] = []
        self.spritesheet: Optional[pygame.Surface] = None
        self.rows = 0
        self.cols = 0
        
        self._load_spritesheet()
        self._create_atlas()
    
    def _load_spritesheet(self):
        """Carica il file spritesheet"""
        try:
            self.spritesheet = pygame.image.load(self.spritesheet_path).convert_alpha()
            print(f"Spritesheet caricato: {self.spritesheet_path}")
            print(f"Dimensioni: {self.spritesheet.get_size()}")
        except pygame.error as e:
            print(f"Errore nel caricamento spritesheet {self.spritesheet_path}: {e}")
            # Crea un spritesheet di fallback
            self.spritesheet = pygame.Surface((320, 320))
            self.spritesheet.fill((255, 0, 255))  # Magenta per debug
    
    def _create_atlas(self):
        """Crea l'atlas di tile indicizzato per (riga, colonna)"""
        if not self.spritesheet:
            return
        
        sheet_width, sheet_height = self.spritesheet.get_size()
        self.cols = sheet_width // self.tile_size
        self.rows = sheet_height // self.tile_size
        
        print(f"Atlas: {self.rows} righe x {self.cols} colonne")
        
        # Inizializza l'atlas
        self.atlas = []
        
        for row in range(self.rows):
            row_tiles = []
            for col in range(self.cols):
                # Estrai il tile dalla posizione (row, col)
                x = col * self.tile_size
                y = row * self.tile_size
                
                tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                tile_surface.blit(self.spritesheet, (0, 0), (x, y, self.tile_size, self.tile_size))
                
                row_tiles.append(tile_surface)
            
            self.atlas.append(row_tiles)
    
    def get_tile(self, row: int, col: int) -> Optional[pygame.Surface]:
        """Ottieni un tile specifico dall'atlas"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.atlas[row][col]
        return None
    
    def get_tile_range(self, row: int, col_start: int, col_end: int) -> List[pygame.Surface]:
        """Ottieni un range di tile da una riga"""
        tiles = []
        for col in range(col_start, min(col_end + 1, self.cols)):
            tile = self.get_tile(row, col)
            if tile:
                tiles.append(tile)
        return tiles
    
    def get_atlas_info(self) -> Dict:
        """Restituisce informazioni sull'atlas"""
        return {
            'rows': self.rows,
            'cols': self.cols,
            'tile_size': self.tile_size,
            'total_tiles': self.rows * self.cols
        }

class TilemapConfig:
    """Gestisce la configurazione del tilemap"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Carica la configurazione da file JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"Configurazione tilemap caricata: {self.config_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Errore nel caricamento configurazione {self.config_path}: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Crea una configurazione di default"""
        self.config = {
            'tile_size': 32,
            'spritesheet': 'assets/sprites/level.png',
            'tile_groups': {},
            'autotile_rows': {'ground': 9, 'walls': 10},
            'door_types': {},
            'parallax': {'enabled': False, 'layers': []}
        }
    
    def get(self, key: str, default=None):
        """Ottieni un valore dalla configurazione"""
        return self.config.get(key, default)
    
    def get_tile_group(self, group_name: str) -> Optional[Dict]:
        """Ottieni informazioni su un gruppo di tile"""
        return self.config.get('tile_groups', {}).get(group_name)
    
    def get_autotile_row(self, tile_type: str) -> Optional[int]:
        """Ottieni la riga degli autotile per un tipo specifico"""
        return self.config.get('autotile_rows', {}).get(tile_type)
    
    def get_door_type(self, door_type: str) -> Optional[Dict]:
        """Ottieni informazioni su un tipo di porta"""
        return self.config.get('door_types', {}).get(door_type)
    
    def is_parallax_enabled(self) -> bool:
        """Verifica se il parallax è abilitato"""
        return self.config.get('parallax', {}).get('enabled', False)
    
    def get_parallax_layers(self) -> List[Dict]:
        """Ottieni i layer del parallax"""
        return self.config.get('parallax', {}).get('layers', [])