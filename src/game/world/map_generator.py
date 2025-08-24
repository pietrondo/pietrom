import random
from typing import List, Tuple
from .tilemap import Tilemap, TileLayer, TileType
from .autotiling import AutotileType

class MapGenerator:
    """Generatore di mappe per creare stanze e livelli"""
    
    def __init__(self, tilemap: Tilemap):
        self.tilemap = tilemap
    
    def generate_test_room(self, width: int = 60, height: int = 20) -> None:
        """Genera una stanza di test con pavimenti, muri, decorazioni e hazard"""
        print(f"Generando stanza di test {width}x{height}...")
        
        # 1. Crea pattern booleano per pavimenti (interno della stanza)
        floor_pattern = self._create_floor_pattern(width, height)
        
        # 2. Crea pattern booleano per muri (perimetro)
        wall_pattern = self._create_wall_pattern(width, height)
        
        # 3. Applica autotiling per pavimenti
        self.tilemap.apply_autotiling(TileLayer.SOLID, AutotileType.GROUND, floor_pattern)
        
        # 4. Applica autotiling per muri (sovrascrive dove necessario)
        self._apply_walls_over_floor(wall_pattern, width, height)
        
        # 5. Aggiungi decorazioni
        self._add_decorations(width, height)
        
        # 6. Aggiungi hazard
        self._add_hazards(width, height)
        
        # 7. Aggiungi porte
        self._add_doors(width, height)
        
        print("Stanza di test generata con successo!")
    
    def _create_floor_pattern(self, width: int, height: int) -> List[List[bool]]:
        """Crea pattern booleano per i pavimenti (area interna)"""
        pattern = [[False for _ in range(width)] for _ in range(height)]
        
        # Riempi l'area interna (lasciando spazio per i muri)
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                pattern[y][x] = True
        
        return pattern
    
    def _create_wall_pattern(self, width: int, height: int) -> List[List[bool]]:
        """Crea pattern booleano per i muri (perimetro)"""
        pattern = [[False for _ in range(width)] for _ in range(height)]
        
        # Muri perimetrali
        for x in range(width):
            pattern[0][x] = True          # Muro superiore
            pattern[height-1][x] = True   # Muro inferiore
        
        for y in range(height):
            pattern[y][0] = True          # Muro sinistro
            pattern[y][width-1] = True    # Muro destro
        
        # Aggiungi alcuni muri interni per varietà
        # Pilastro centrale
        center_x, center_y = width // 2, height // 2
        if center_x > 2 and center_y > 2:
            pattern[center_y][center_x] = True
            pattern[center_y][center_x + 1] = True
            pattern[center_y + 1][center_x] = True
            pattern[center_y + 1][center_x + 1] = True
        
        # Alcuni muri sparsi
        for _ in range(3):
            x = random.randint(5, width - 6)
            y = random.randint(3, height - 4)
            pattern[y][x] = True
            pattern[y][x + 1] = True
        
        return pattern
    
    def _apply_walls_over_floor(self, wall_pattern: List[List[bool]], width: int, height: int):
        """Applica i muri sopra i pavimenti dove necessario"""
        # Applica autotiling per muri
        self.tilemap.apply_autotiling(TileLayer.SOLID, AutotileType.WALLS, wall_pattern)
        
        # Sovrascrive manualmente i tile dove ci sono muri
        for y in range(height):
            for x in range(width):
                if wall_pattern[y][x]:
                    # Usa tile muro base per ora (l'autotiling ha già impostato le coordinate corrette)
                    current_tile = self.tilemap.get_tile(TileLayer.SOLID, x, y)
                    if current_tile:
                        current_tile.tile_id = TileType.WALL_BASIC
                        current_tile.solid = True
    
    def _add_decorations(self, width: int, height: int):
        """Aggiunge decorazioni alla stanza"""
        decorations_added = 0
        
        # Terminali lungo le pareti
        terminal_positions = [
            (5, 1),   # Parete superiore
            (width - 6, 1),
            (1, height // 2),  # Pareti laterali
            (width - 2, height // 2),
            (width // 2, height - 2)  # Parete inferiore
        ]
        
        for x, y in terminal_positions:
            if self._is_valid_decor_position(x, y):
                # Terminal (riga 6, colonna 0 del config)
                self.tilemap.set_tile_by_id(TileLayer.DECOR, x, y, TileType.TERMINAL, 5, 0)
                decorations_added += 1
        
        # Insegne neon sparse
        neon_count = 6
        attempts = 0
        while decorations_added < 8 and attempts < 20:
            x = random.randint(3, width - 4)
            y = random.randint(2, height - 3)
            
            if self._is_valid_decor_position(x, y):
                # Insegna neon (riga 7, colonne varie)
                neon_col = random.randint(0, 3)
                self.tilemap.set_tile_by_id(TileLayer.DECOR, x, y, TileType.NEON_SIGN, 6, neon_col)
                decorations_added += 1
            
            attempts += 1
        
        print(f"Aggiunte {decorations_added} decorazioni")
    
    def _add_hazards(self, width: int, height: int):
        """Aggiunge hazard alla stanza (4 laser + 6 spuntoni)"""
        hazards_added = 0
        
        # 4 laser trap
        laser_positions = [
            (10, height // 2),
            (width - 11, height // 2),
            (width // 2, 5),
            (width // 2, height - 6)
        ]
        
        for x, y in laser_positions:
            if self._is_valid_hazard_position(x, y):
                # Laser trap (riga 8, colonna 0)
                self.tilemap.set_tile_by_id(TileLayer.HAZARD, x, y, TileType.LASER_TRAP, 7, 0)
                hazards_added += 1
        
        # 6 spike trap sparsi
        spike_count = 0
        attempts = 0
        while spike_count < 6 and attempts < 30:
            x = random.randint(4, width - 5)
            y = random.randint(4, height - 5)
            
            if self._is_valid_hazard_position(x, y):
                # Spike trap (riga 8, colonna 1)
                self.tilemap.set_tile_by_id(TileLayer.HAZARD, x, y, TileType.SPIKE_TRAP, 7, 1)
                spike_count += 1
                hazards_added += 1
            
            attempts += 1
        
        print(f"Aggiunti {hazards_added} hazard ({len(laser_positions)} laser, {spike_count} spuntoni)")
    
    def _add_doors(self, width: int, height: int):
        """Aggiunge porte alla stanza"""
        doors_added = 0
        
        # Porta principale (centro parete inferiore)
        door_x = width // 2
        door_y = height - 1
        self.tilemap.place_door(door_x, door_y, "standard")
        doors_added += 1
        
        # Porta secondaria (parete laterale)
        if width > 20:
            door_x = width - 1
            door_y = height // 2
            self.tilemap.place_door(door_x, door_y, "electronic")
            doors_added += 1
        
        print(f"Aggiunte {doors_added} porte")
    
    def _is_valid_decor_position(self, x: int, y: int) -> bool:
        """Controlla se una posizione è valida per decorazioni"""
        # Non deve esserci un tile solido
        solid_tile = self.tilemap.get_tile(TileLayer.SOLID, x, y)
        if solid_tile and solid_tile.solid:
            return False
        
        # Non deve esserci già una decorazione
        decor_tile = self.tilemap.get_tile(TileLayer.DECOR, x, y)
        if decor_tile and decor_tile.tile_id != TileType.EMPTY:
            return False
        
        # Deve essere vicino a un muro per i terminali
        adjacent_positions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        has_adjacent_wall = False
        
        for adj_x, adj_y in adjacent_positions:
            adj_tile = self.tilemap.get_tile(TileLayer.SOLID, adj_x, adj_y)
            if adj_tile and adj_tile.solid and adj_tile.tile_id in [TileType.WALL_BASIC, TileType.WALL_REINFORCED]:
                has_adjacent_wall = True
                break
        
        return has_adjacent_wall
    
    def _is_valid_hazard_position(self, x: int, y: int) -> bool:
        """Controlla se una posizione è valida per hazard"""
        # Non deve esserci un tile solido
        solid_tile = self.tilemap.get_tile(TileLayer.SOLID, x, y)
        if solid_tile and solid_tile.solid:
            return False
        
        # Non deve esserci già un hazard
        hazard_tile = self.tilemap.get_tile(TileLayer.HAZARD, x, y)
        if hazard_tile and hazard_tile.hazard:
            return False
        
        # Non deve essere troppo vicino ad altri hazard
        for check_y in range(max(0, y-2), min(self.tilemap.height, y+3)):
            for check_x in range(max(0, x-2), min(self.tilemap.width, x+3)):
                if check_x == x and check_y == y:
                    continue
                check_tile = self.tilemap.get_tile(TileLayer.HAZARD, check_x, check_y)
                if check_tile and check_tile.hazard:
                    return False
        
        return True
    
    def generate_corridor(self, start_x: int, start_y: int, end_x: int, end_y: int, width: int = 3):
        """Genera un corridoio tra due punti"""
        # Implementazione semplice per corridoi orizzontali/verticali
        if start_x == end_x:  # Corridoio verticale
            min_y, max_y = min(start_y, end_y), max(start_y, end_y)
            for y in range(min_y, max_y + 1):
                for offset in range(-(width//2), width//2 + 1):
                    x = start_x + offset
                    if 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height:
                        if offset == -(width//2) or offset == width//2:
                            # Muri laterali
                            self.tilemap.set_tile_by_id(TileLayer.SOLID, x, y, TileType.WALL_BASIC, 3, 0)
                        else:
                            # Pavimento
                            self.tilemap.set_tile_by_id(TileLayer.SOLID, x, y, TileType.GROUND_BASE, 0, 0)
        
        elif start_y == end_y:  # Corridoio orizzontale
            min_x, max_x = min(start_x, end_x), max(start_x, end_x)
            for x in range(min_x, max_x + 1):
                for offset in range(-(width//2), width//2 + 1):
                    y = start_y + offset
                    if 0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height:
                        if offset == -(width//2) or offset == width//2:
                            # Muri laterali
                            self.tilemap.set_tile_by_id(TileLayer.SOLID, x, y, TileType.WALL_BASIC, 3, 0)
                        else:
                            # Pavimento
                            self.tilemap.set_tile_by_id(TileLayer.SOLID, x, y, TileType.GROUND_BASE, 0, 0)
    
    def clear_area(self, x: int, y: int, width: int, height: int):
        """Pulisce un'area del tilemap"""
        for clear_y in range(y, min(y + height, self.tilemap.height)):
            for clear_x in range(x, min(x + width, self.tilemap.width)):
                for layer in [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]:
                    self.tilemap.set_tile(layer, clear_x, clear_y, 
                                        self.tilemap.Tile(TileType.EMPTY, 0, 0))
        
        print(f"Area pulita: ({x},{y}) {width}x{height}")
    
    def add_room(self, x: int, y: int, width: int, height: int, room_type: str = "basic"):
        """Aggiunge una stanza di tipo specifico"""
        if room_type == "basic":
            self._add_basic_room(x, y, width, height)
        elif room_type == "treasure":
            self._add_treasure_room(x, y, width, height)
        elif room_type == "danger":
            self._add_danger_room(x, y, width, height)
    
    def _add_basic_room(self, x: int, y: int, width: int, height: int):
        """Aggiunge una stanza base"""
        # Pavimento
        for room_y in range(y + 1, y + height - 1):
            for room_x in range(x + 1, x + width - 1):
                self.tilemap.set_tile_by_id(TileLayer.SOLID, room_x, room_y, TileType.GROUND_BASE, 0, 0)
        
        # Muri perimetrali
        for room_x in range(x, x + width):
            self.tilemap.set_tile_by_id(TileLayer.SOLID, room_x, y, TileType.WALL_BASIC, 3, 0)
            self.tilemap.set_tile_by_id(TileLayer.SOLID, room_x, y + height - 1, TileType.WALL_BASIC, 3, 0)
        
        for room_y in range(y, y + height):
            self.tilemap.set_tile_by_id(TileLayer.SOLID, x, room_y, TileType.WALL_BASIC, 3, 0)
            self.tilemap.set_tile_by_id(TileLayer.SOLID, x + width - 1, room_y, TileType.WALL_BASIC, 3, 0)
    
    def _add_treasure_room(self, x: int, y: int, width: int, height: int):
        """Aggiunge una stanza del tesoro"""
        self._add_basic_room(x, y, width, height)
        
        # Aggiungi terminali e decorazioni speciali
        center_x, center_y = x + width // 2, y + height // 2
        self.tilemap.set_tile_by_id(TileLayer.DECOR, center_x, center_y, TileType.TERMINAL, 5, 1)
    
    def _add_danger_room(self, x: int, y: int, width: int, height: int):
        """Aggiunge una stanza pericolosa"""
        self._add_basic_room(x, y, width, height)
        
        # Aggiungi più hazard
        hazard_count = (width * height) // 20
        for _ in range(hazard_count):
            hx = random.randint(x + 2, x + width - 3)
            hy = random.randint(y + 2, y + height - 3)
            if self._is_valid_hazard_position(hx, hy):
                hazard_type = random.choice([TileType.LASER_TRAP, TileType.SPIKE_TRAP])
                sprite_col = 0 if hazard_type == TileType.LASER_TRAP else 1
                self.tilemap.set_tile_by_id(TileLayer.HAZARD, hx, hy, hazard_type, 7, sprite_col)