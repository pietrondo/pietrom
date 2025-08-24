import pygame
import os
from typing import Tuple, Optional
from .tilemap import Tilemap, TileLayer, TileType
from .map_generator import MapGenerator

class TilemapEditor:
    """Editor/debugger per tilemap con controlli F1, F2, F3"""
    
    def __init__(self, tilemap: Tilemap):
        self.tilemap = tilemap
        self.map_generator = MapGenerator(tilemap)
        
        # Stato editor
        self.editor_active = False
        self.current_layer = TileLayer.SOLID
        self.current_tile_id = TileType.GROUND_BASE
        self.brush_size = 1
        
        # Mouse state
        self.mouse_tile_x = 0
        self.mouse_tile_y = 0
        self.is_painting = False
        self.is_erasing = False
        
        # UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # File paths
        self.maps_directory = "assets/maps"
        self.current_map_file = "test_map.json"
        
        # Crea directory se non esiste
        os.makedirs(self.maps_directory, exist_ok=True)
        
        print("Tilemap Editor inizializzato")
        print("Controlli:")
        print("  F1 - Toggle griglia e info tile")
        print("  F2 - Salva mappa")
        print("  F3 - Carica mappa")
        print("  F4 - Toggle editor mode")
        print("  F5 - Genera stanza test")
        print("  Tab - Cambia layer")
        print("  1-9 - Seleziona tipo tile")
        print("  Mouse - Disegna/Cancella")
        print("  Shift+Mouse - Cancella")
    
    def handle_input(self, event: pygame.event.Event):
        """Gestisce input per l'editor"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self._toggle_debug_display()
            elif event.key == pygame.K_F2:
                self._save_map()
            elif event.key == pygame.K_F3:
                self._load_map()
            elif event.key == pygame.K_F4:
                self._toggle_editor_mode()
            elif event.key == pygame.K_F5:
                self._generate_test_room()
            elif event.key == pygame.K_TAB:
                self._cycle_layer()
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                self._select_tile_type(event.key - pygame.K_1 + 1)
            elif event.key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
                self._clear_map()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.editor_active:
                if event.button == 1:  # Left click
                    self.is_painting = True
                    self._paint_tile()
                elif event.button == 3:  # Right click
                    self.is_erasing = True
                    self._erase_tile()
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_painting = False
            elif event.button == 3:
                self.is_erasing = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.editor_active:
                self._update_mouse_position(event.pos)
                if self.is_painting:
                    self._paint_tile()
                elif self.is_erasing:
                    self._erase_tile()
    
    def _toggle_debug_display(self):
        """F1 - Toggle griglia e visualizzazione info tile"""
        if not self.tilemap.debug_mode:
            self.tilemap.toggle_debug_mode()
            self.tilemap.toggle_grid()
            self.tilemap.toggle_tile_indices()
        else:
            self.tilemap.toggle_debug_mode()
            self.tilemap.show_grid = False
            self.tilemap.show_tile_indices = False
        
        print(f"Debug display: {'ON' if self.tilemap.debug_mode else 'OFF'}")
    
    def _save_map(self):
        """F2 - Salva la mappa corrente"""
        filepath = os.path.join(self.maps_directory, self.current_map_file)
        self.tilemap.save_to_json(filepath)
        
        # Salva anche i singoli layer in CSV per debug
        base_name = os.path.splitext(self.current_map_file)[0]
        for layer in [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]:
            csv_file = f"{base_name}_{layer.value}.csv"
            csv_path = os.path.join(self.maps_directory, csv_file)
            self.tilemap.save_to_csv(csv_path, layer)
        
        print(f"Mappa salvata: {filepath}")
    
    def _load_map(self):
        """F3 - Carica la mappa"""
        filepath = os.path.join(self.maps_directory, self.current_map_file)
        if os.path.exists(filepath):
            self.tilemap.load_from_json(filepath)
            print(f"Mappa caricata: {filepath}")
        else:
            print(f"File mappa non trovato: {filepath}")
    
    def _toggle_editor_mode(self):
        """F4 - Attiva/disattiva modalità editor"""
        self.editor_active = not self.editor_active
        print(f"Editor mode: {'ON' if self.editor_active else 'OFF'}")
    
    def _generate_test_room(self):
        """F5 - Genera stanza di test"""
        self.map_generator.generate_test_room()
        print("Stanza di test generata")
    
    def _cycle_layer(self):
        """Tab - Cambia layer corrente"""
        layers = [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]
        current_index = layers.index(self.current_layer)
        self.current_layer = layers[(current_index + 1) % len(layers)]
        print(f"Layer corrente: {self.current_layer.value}")
    
    def _select_tile_type(self, tile_number: int):
        """1-9 - Seleziona tipo di tile"""
        tile_types = [
            TileType.EMPTY,
            TileType.GROUND_BASE,
            TileType.GROUND_WORN,
            TileType.WALL_BASIC,
            TileType.WALL_REINFORCED,
            TileType.DOOR_STANDARD,
            TileType.TERMINAL,
            TileType.LASER_TRAP,
            TileType.SPIKE_TRAP
        ]
        
        if 0 <= tile_number < len(tile_types):
            self.current_tile_id = tile_types[tile_number]
            print(f"Tile selezionato: {self.current_tile_id} ({tile_number})")
    
    def _update_mouse_position(self, mouse_pos: Tuple[int, int]):
        """Aggiorna posizione mouse in coordinate tile"""
        mouse_x, mouse_y = mouse_pos
        # Nota: dovremmo considerare l'offset della camera qui
        self.mouse_tile_x = mouse_x // self.tilemap.TILE_SIZE
        self.mouse_tile_y = mouse_y // self.tilemap.TILE_SIZE
    
    def _paint_tile(self):
        """Disegna tile nella posizione corrente"""
        if not self.editor_active:
            return
        
        x, y = self.mouse_tile_x, self.mouse_tile_y
        
        # Verifica bounds
        if not (0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height):
            return
        
        # Determina coordinate sprite basate sul tipo di tile
        sprite_row, sprite_col = self._get_sprite_coords_for_tile(self.current_tile_id)
        
        # Applica brush
        for dy in range(-self.brush_size//2, self.brush_size//2 + 1):
            for dx in range(-self.brush_size//2, self.brush_size//2 + 1):
                paint_x, paint_y = x + dx, y + dy
                if 0 <= paint_x < self.tilemap.width and 0 <= paint_y < self.tilemap.height:
                    self.tilemap.set_tile_by_id(self.current_layer, paint_x, paint_y, 
                                               self.current_tile_id, sprite_row, sprite_col)
    
    def _erase_tile(self):
        """Cancella tile nella posizione corrente"""
        if not self.editor_active:
            return
        
        x, y = self.mouse_tile_x, self.mouse_tile_y
        
        # Verifica bounds
        if not (0 <= x < self.tilemap.width and 0 <= y < self.tilemap.height):
            return
        
        # Applica brush per cancellazione
        for dy in range(-self.brush_size//2, self.brush_size//2 + 1):
            for dx in range(-self.brush_size//2, self.brush_size//2 + 1):
                erase_x, erase_y = x + dx, y + dy
                if 0 <= erase_x < self.tilemap.width and 0 <= erase_y < self.tilemap.height:
                    self.tilemap.set_tile_by_id(self.current_layer, erase_x, erase_y, 
                                               TileType.EMPTY, 0, 0)
    
    def _get_sprite_coords_for_tile(self, tile_id: int) -> Tuple[int, int]:
        """Restituisce coordinate sprite per un tipo di tile"""
        # Mappatura tile ID -> coordinate sprite (row, col)
        sprite_map = {
            TileType.EMPTY: (0, 0),
            TileType.GROUND_BASE: (0, 0),      # Riga 1
            TileType.GROUND_WORN: (1, 0),      # Riga 2
            TileType.WALL_BASIC: (2, 0),       # Riga 3
            TileType.WALL_REINFORCED: (3, 0),  # Riga 4
            TileType.STAIRS: (4, 0),           # Riga 5
            TileType.PIPES: (4, 1),
            TileType.DOOR_STANDARD: (5, 0),    # Riga 6
            TileType.DOOR_REINFORCED: (5, 1),
            TileType.DOOR_ELECTRONIC: (5, 2),
            TileType.TERMINAL: (5, 3),
            TileType.DECAL: (6, 0),            # Riga 7
            TileType.LASER_TRAP: (7, 0),       # Riga 8
            TileType.SPIKE_TRAP: (7, 1),
            TileType.NEON_SIGN: (6, 1)
        }
        
        return sprite_map.get(tile_id, (0, 0))
    
    def _clear_map(self):
        """Pulisce tutta la mappa"""
        for layer in [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]:
            for y in range(self.tilemap.height):
                for x in range(self.tilemap.width):
                    self.tilemap.set_tile_by_id(layer, x, y, TileType.EMPTY, 0, 0)
        print("Mappa pulita")
    
    def render_ui(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Renderizza UI dell'editor"""
        if not self.editor_active and not self.tilemap.debug_mode:
            return
        
        screen_width, screen_height = surface.get_size()
        
        # Panel informazioni editor
        if self.editor_active:
            self._render_editor_panel(surface)
        
        # Informazioni tile sotto il mouse
        if self.tilemap.debug_mode:
            self._render_mouse_info(surface, camera_offset)
        
        # Cursore editor
        if self.editor_active:
            self._render_editor_cursor(surface, camera_offset)
    
    def _render_editor_panel(self, surface: pygame.Surface):
        """Renderizza panel con informazioni editor"""
        panel_width = 250
        panel_height = 150
        panel_x = surface.get_width() - panel_width - 10
        panel_y = 10
        
        # Sfondo panel
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((40, 40, 40))
        surface.blit(panel_surface, (panel_x, panel_y))
        
        # Testo informazioni
        y_offset = panel_y + 10
        
        # Titolo
        title_text = self.font.render("TILEMAP EDITOR", True, (255, 255, 0))
        surface.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Layer corrente
        layer_text = self.small_font.render(f"Layer: {self.current_layer.value}", True, (255, 255, 255))
        surface.blit(layer_text, (panel_x + 10, y_offset))
        y_offset += 18
        
        # Tile corrente
        tile_text = self.small_font.render(f"Tile: {self.current_tile_id}", True, (255, 255, 255))
        surface.blit(tile_text, (panel_x + 10, y_offset))
        y_offset += 18
        
        # Posizione mouse
        mouse_text = self.small_font.render(f"Mouse: ({self.mouse_tile_x}, {self.mouse_tile_y})", True, (255, 255, 255))
        surface.blit(mouse_text, (panel_x + 10, y_offset))
        y_offset += 18
        
        # Brush size
        brush_text = self.small_font.render(f"Brush: {self.brush_size}x{self.brush_size}", True, (255, 255, 255))
        surface.blit(brush_text, (panel_x + 10, y_offset))
    
    def _render_mouse_info(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Renderizza informazioni tile sotto il mouse"""
        offset_x, offset_y = camera_offset
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calcola posizione tile considerando camera offset
        world_x = mouse_x + offset_x
        world_y = mouse_y + offset_y
        tile_x = world_x // self.tilemap.TILE_SIZE
        tile_y = world_y // self.tilemap.TILE_SIZE
        
        # Verifica bounds
        if not (0 <= tile_x < self.tilemap.width and 0 <= tile_y < self.tilemap.height):
            return
        
        # Ottieni informazioni tile
        info_lines = []
        info_lines.append(f"Tile: ({tile_x}, {tile_y})")
        
        for layer in [TileLayer.SOLID, TileLayer.DECOR, TileLayer.HAZARD]:
            tile = self.tilemap.get_tile(layer, tile_x, tile_y)
            if tile and tile.tile_id != TileType.EMPTY:
                info_lines.append(f"{layer.value}: {tile.tile_id}")
                if tile.solid:
                    info_lines.append("  [SOLID]")
                if tile.hazard:
                    info_lines.append(f"  [HAZARD: {tile.damage}]")
        
        # Renderizza info box
        if info_lines:
            box_width = 200
            box_height = len(info_lines) * 16 + 10
            box_x = mouse_x + 15
            box_y = mouse_y - box_height - 10
            
            # Assicurati che il box sia visibile
            if box_x + box_width > surface.get_width():
                box_x = mouse_x - box_width - 15
            if box_y < 0:
                box_y = mouse_y + 15
            
            # Sfondo
            info_surface = pygame.Surface((box_width, box_height))
            info_surface.set_alpha(220)
            info_surface.fill((0, 0, 0))
            surface.blit(info_surface, (box_x, box_y))
            
            # Testo
            for i, line in enumerate(info_lines):
                text = self.small_font.render(line, True, (255, 255, 255))
                surface.blit(text, (box_x + 5, box_y + 5 + i * 16))
    
    def _render_editor_cursor(self, surface: pygame.Surface, camera_offset: Tuple[int, int]):
        """Renderizza cursore editor"""
        offset_x, offset_y = camera_offset
        
        # Calcola posizione screen del tile sotto il mouse
        screen_x = self.mouse_tile_x * self.tilemap.TILE_SIZE - offset_x
        screen_y = self.mouse_tile_y * self.tilemap.TILE_SIZE - offset_y
        
        # Colore cursore basato su modalità
        if self.is_painting:
            color = (0, 255, 0)  # Verde per disegno
        elif self.is_erasing:
            color = (255, 0, 0)  # Rosso per cancellazione
        else:
            color = (255, 255, 0)  # Giallo normale
        
        # Disegna cursore
        cursor_size = self.brush_size * self.tilemap.TILE_SIZE
        cursor_offset = (cursor_size - self.tilemap.TILE_SIZE) // 2
        
        cursor_rect = pygame.Rect(
            screen_x - cursor_offset,
            screen_y - cursor_offset,
            cursor_size,
            cursor_size
        )
        
        pygame.draw.rect(surface, color, cursor_rect, 2)
    
    def set_map_file(self, filename: str):
        """Imposta il file mappa corrente"""
        self.current_map_file = filename
        print(f"File mappa corrente: {filename}")
    
    def set_brush_size(self, size: int):
        """Imposta dimensione brush"""
        self.brush_size = max(1, min(5, size))
        print(f"Brush size: {self.brush_size}")