import pygame
from typing import List, Dict, Tuple, Optional
from enum import IntEnum

class AutotileType(IntEnum):
    """Tipi di autotile supportati"""
    GROUND = 0
    WALLS = 1

class AutotilingSystem:
    """Sistema di autotiling con bitmask a 47 tile"""
    
    # Mappa dei bitmask ai tile index (47 tile autotiling)
    BITMASK_TO_TILE = {
        # Tile singoli e isolati
        0: 46,      # Tile isolato
        
        # Linee orizzontali
        2: 0,       # Linea orizzontale sinistra
        8: 1,       # Linea orizzontale centro
        10: 2,      # Linea orizzontale destra
        
        # Linee verticali
        16: 3,      # Linea verticale sopra
        64: 4,      # Linea verticale centro
        80: 5,      # Linea verticale sotto
        
        # Angoli esterni
        18: 6,      # Angolo esterno top-left
        24: 7,      # Angolo esterno top-right
        72: 8,      # Angolo esterno bottom-left
        96: 9,      # Angolo esterno bottom-right
        
        # Angoli interni
        22: 10,     # Angolo interno top-left
        31: 11,     # Angolo interno top-right
        104: 12,    # Angolo interno bottom-left
        248: 13,    # Angolo interno bottom-right
        
        # T-junction
        26: 14,     # T verso l'alto
        88: 15,     # T verso il basso
        30: 16,     # T verso sinistra
        120: 17,    # T verso destra
        
        # Croci
        122: 18,    # Croce completa
        
        # Bordi
        66: 19,     # Bordo verticale
        82: 20,     # Bordo verticale con connessioni
        
        # Riempimenti
        90: 21,     # Riempimento base
        106: 22,    # Riempimento con dettagli
        
        # Tile speciali per variazioni
        127: 23,    # Tile pieno circondato
        255: 24,    # Tile completamente circondato
        
        # Variazioni aggiuntive per completare i 47 tile
        1: 25, 4: 26, 32: 27, 128: 28,
        3: 29, 6: 30, 12: 31, 17: 32,
        33: 33, 34: 34, 36: 35, 48: 36,
        65: 37, 68: 38, 129: 39, 130: 40,
        132: 41, 136: 42, 144: 43, 160: 44,
        192: 45
    }
    
    def __init__(self):
        pass
    
    def calculate_bitmask(self, grid: List[List[bool]], x: int, y: int) -> int:
        """Calcola il bitmask per un tile alla posizione (x, y)"""
        if not grid or y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return 0
        
        # Se il tile corrente è vuoto, non calcolare il bitmask
        if not grid[y][x]:
            return 0
        
        bitmask = 0
        
        # Controlla i tile adiacenti (8 direzioni)
        # Ordine: NW, N, NE, W, E, SW, S, SE
        directions = [
            (-1, -1), (0, -1), (1, -1),  # Top row
            (-1, 0),           (1, 0),   # Middle row (escluso centro)
            (-1, 1),  (0, 1),  (1, 1)   # Bottom row
        ]
        
        bit_values = [1, 2, 4, 8, 16, 32, 64, 128]
        
        for i, (dx, dy) in enumerate(directions):
            nx, ny = x + dx, y + dy
            
            # Controlla se la posizione è valida e contiene un tile
            if (0 <= ny < len(grid) and 0 <= nx < len(grid[ny]) and grid[ny][nx]):
                bitmask |= bit_values[i]
        
        return bitmask
    
    def get_autotile_index(self, grid: List[List[bool]], x: int, y: int) -> int:
        """Ottieni l'indice del tile autotile per la posizione data"""
        bitmask = self.calculate_bitmask(grid, x, y)
        return self.BITMASK_TO_TILE.get(bitmask, 0)  # Default al primo tile se non trovato
    
    def generate_autotile_grid(self, solid_grid: List[List[bool]], tile_type: AutotileType) -> List[List[int]]:
        """Genera una griglia di indici autotile da una griglia booleana"""
        if not solid_grid:
            return []
        
        height = len(solid_grid)
        width = len(solid_grid[0]) if height > 0 else 0
        
        autotile_grid = []
        
        for y in range(height):
            row = []
            for x in range(width):
                if solid_grid[y][x]:
                    tile_index = self.get_autotile_index(solid_grid, x, y)
                    row.append(tile_index)
                else:
                    row.append(-1)  # -1 indica nessun tile
            autotile_grid.append(row)
        
        return autotile_grid
    
    def create_test_pattern(self, width: int, height: int) -> List[List[bool]]:
        """Crea un pattern di test per verificare l'autotiling"""
        grid = [[False for _ in range(width)] for _ in range(height)]
        
        # Crea un rettangolo con alcuni buchi per testare tutti i casi
        for y in range(2, height - 2):
            for x in range(2, width - 2):
                grid[y][x] = True
        
        # Aggiungi alcuni pattern specifici
        if width > 10 and height > 10:
            # Rimuovi alcuni tile per creare angoli interni
            grid[4][4] = False
            grid[4][width-5] = False
            grid[height-5][4] = False
            grid[height-5][width-5] = False
            
            # Aggiungi alcune protuberanze per T-junction
            if height > 15:
                for x in range(width//2 - 2, width//2 + 3):
                    grid[height//2][x] = True
                for y in range(height//2 - 2, height//2 + 3):
                    grid[y][width//2] = True
        
        return grid
    
    def debug_print_bitmasks(self, grid: List[List[bool]], max_width: int = 20, max_height: int = 10):
        """Stampa i bitmask per debug (limitato per leggibilità)"""
        height = min(len(grid), max_height)
        width = min(len(grid[0]) if grid else 0, max_width)
        
        print("\nBitmask Grid (primi {}x{} tile):".format(width, height))
        for y in range(height):
            row_str = ""
            for x in range(width):
                if grid[y][x]:
                    bitmask = self.calculate_bitmask(grid, x, y)
                    tile_idx = self.BITMASK_TO_TILE.get(bitmask, 0)
                    row_str += f"{tile_idx:2d} "
                else:
                    row_str += "   "
            print(row_str)
        print()

class AutotilePalette:
    """Gestisce le palette di ID per diversi set di autotile"""
    
    def __init__(self):
        self.palettes = {
            AutotileType.GROUND: {
                'base_row': 9,  # Riga 9 per autotile pavimenti
                'name': 'ground_autotile'
            },
            AutotileType.WALLS: {
                'base_row': 10,  # Riga 10 per autotile muri
                'name': 'wall_autotile'
            }
        }
    
    def get_tile_coords(self, tile_type: AutotileType, autotile_index: int) -> Tuple[int, int]:
        """Converte un indice autotile in coordinate (row, col) del spritesheet"""
        if tile_type not in self.palettes:
            return (0, 0)
        
        base_row = self.palettes[tile_type]['base_row']
        
        # Assumendo che ogni riga abbia 47 tile (o meno)
        # Se l'indice supera la larghezza della riga, va alla riga successiva
        tiles_per_row = 16  # Assumendo 16 tile per riga nel spritesheet
        
        row_offset = autotile_index // tiles_per_row
        col = autotile_index % tiles_per_row
        row = base_row + row_offset
        
        return (row, col)
    
    def get_palette_info(self, tile_type: AutotileType) -> Dict:
        """Ottieni informazioni sulla palette"""
        return self.palettes.get(tile_type, {})