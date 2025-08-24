import pygame
from typing import Tuple, Optional, List
from .tilemap import Tilemap, TileLayer
from .camera import Camera
from .parallax_background import ParallaxBackground, ParallaxManager
from .tilemap_editor import TilemapEditor
from .map_generator import MapGenerator

class WorldManager:
    """Manager principale per il sistema mondo del gioco"""
    
    def __init__(self, screen_width: int, screen_height: int, 
                 map_width: int = 60, map_height: int = 20):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Inizializza componenti mondo
        self.tilemap = Tilemap(map_width, map_height)
        self.camera = Camera(screen_width, screen_height)
        
        # Parallax background
        self.parallax_manager = ParallaxManager()
        self._setup_parallax_backgrounds()
        
        # Editor e generatore
        self.editor = TilemapEditor(self.tilemap)
        self.map_generator = MapGenerator(self.tilemap)
        
        # Stato del mondo
        self.world_initialized = False
        self.debug_mode = False
        
        print(f"WorldManager inizializzato: {map_width}x{map_height} tile")
    
    def _setup_parallax_backgrounds(self):
        """Configura i background parallax"""
        # Background principale
        main_bg = ParallaxBackground()
        self.parallax_manager.add_background("main", main_bg)
        self.parallax_manager.set_current_background("main")
        
        # Potresti aggiungere altri background per diversi livelli
        # space_bg = ParallaxBackground("assets/space_config.json")
        # self.parallax_manager.add_background("space", space_bg)
    
    def initialize_world(self, generate_test_room: bool = True):
        """Inizializza il mondo del gioco"""
        if self.world_initialized:
            print("Mondo già inizializzato")
            return
        
        print("Inizializzando mondo del gioco...")
        
        if generate_test_room:
            # Genera stanza di test
            self.map_generator.generate_test_room()
        
        # Posiziona camera al centro della mappa
        center_x = (self.tilemap.width * Tilemap.TILE_SIZE) // 2
        center_y = (self.tilemap.height * Tilemap.TILE_SIZE) // 2
        self.camera.set_position(center_x, center_y)
        
        self.world_initialized = True
        print("Mondo inizializzato con successo")
    
    def update(self, dt: float, player_pos: Optional[Tuple[float, float]] = None):
        """Aggiorna tutti i componenti del mondo"""
        # Aggiorna camera
        if player_pos:
            self.camera.update(dt, player_pos[0], player_pos[1])
        else:
            # Se non c'è posizione player, usa la posizione corrente della camera
            current_pos = self.camera.get_position()
            self.camera.update(dt, current_pos[0] + self.screen_width // 2, current_pos[1] + self.screen_height // 2)
        
        # Aggiorna parallax background
        camera_offset = self.camera.get_offset()
        self.parallax_manager.update(camera_offset)
    
    def handle_input(self, event: pygame.event.Event):
        """Gestisce input per editor e debug"""
        self.editor.handle_input(event)
        
        # Input aggiuntivi per world manager
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F10:
                self._toggle_debug_mode()
            elif event.key == pygame.K_F11:
                self._toggle_parallax()
            elif event.key == pygame.K_F12:
                self._regenerate_world()
    
    def render(self, surface: pygame.Surface):
        """Renderizza tutto il mondo"""
        camera_offset = self.camera.get_offset()
        
        # 1. Renderizza parallax background
        self.parallax_manager.render(surface, camera_offset)
        
        # 2. Renderizza tilemap (SOLID -> DECOR -> HAZARD)
        self.tilemap.render(surface, camera_offset)
        
        # 3. Renderizza UI editor se attivo
        self.editor.render_ui(surface, camera_offset)
        
        # 4. Debug info
        if self.debug_mode:
            self._render_debug_info(surface)
    
    def _render_debug_info(self, surface: pygame.Surface):
        """Renderizza informazioni di debug"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 16)
        
        # Informazioni camera
        camera_pos = self.camera.get_position()
        camera_offset = self.camera.get_offset()
        
        debug_lines = [
            f"Camera Pos: ({camera_pos[0]:.1f}, {camera_pos[1]:.1f})",
            f"Camera Offset: ({camera_offset[0]:.1f}, {camera_offset[1]:.1f})",
            f"Map Size: {self.tilemap.width}x{self.tilemap.height}",
            f"Collision Rects: {len(self.tilemap.get_collision_rects())}",
            f"Hazard Rects: {len(self.tilemap.get_hazard_rects())}",
            f"Parallax Layers: {self.parallax_manager.get_current_background().get_layer_count() if self.parallax_manager.get_current_background() else 0}"
        ]
        
        # Sfondo per debug info
        debug_height = len(debug_lines) * 18 + 10
        debug_surface = pygame.Surface((300, debug_height))
        debug_surface.set_alpha(180)
        debug_surface.fill((0, 0, 0))
        surface.blit(debug_surface, (10, 10))
        
        # Testo debug
        for i, line in enumerate(debug_lines):
            text = small_font.render(line, True, (255, 255, 255))
            surface.blit(text, (15, 15 + i * 18))
    
    def _toggle_debug_mode(self):
        """F10 - Toggle debug mode generale"""
        self.debug_mode = not self.debug_mode
        print(f"World debug mode: {'ON' if self.debug_mode else 'OFF'}")
    
    def _toggle_parallax(self):
        """F11 - Toggle parallax background"""
        current_bg = self.parallax_manager.get_current_background()
        if current_bg:
            current_bg.set_enabled(not current_bg.enabled)
            print(f"Parallax: {'ON' if current_bg.enabled else 'OFF'}")
    
    def _regenerate_world(self):
        """F12 - Rigenera mondo"""
        print("Rigenerando mondo...")
        self.map_generator.generate_test_room()
        print("Mondo rigenerato")
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """Ottieni rettangoli di collisione per il player"""
        return self.tilemap.get_collision_rects()
    
    def get_hazard_rects(self) -> List[Tuple[pygame.Rect, int]]:
        """Ottieni rettangoli hazard con danno"""
        return self.tilemap.get_hazard_rects()
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        """Controlla collisione con il mondo"""
        return self.tilemap.check_collision(rect)
    
    def check_hazard_collision(self, rect: pygame.Rect) -> int:
        """Controlla collisione con hazard e restituisce danno"""
        return self.tilemap.check_hazard_collision(rect)
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Converte coordinate mondo in coordinate schermo"""
        return self.camera.world_to_screen(world_pos[0], world_pos[1])
    
    def screen_to_world(self, screen_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Converte coordinate schermo in coordinate mondo"""
        return self.camera.screen_to_world(screen_pos[0], screen_pos[1])
    
    def get_tile_at_world_pos(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Ottieni coordinate tile da posizione mondo"""
        return self.tilemap.get_tile_at_world_pos(int(world_x), int(world_y))
    
    def is_position_solid(self, world_x: float, world_y: float) -> bool:
        """Controlla se una posizione mondo è solida"""
        tile_x, tile_y = self.get_tile_at_world_pos(world_x, world_y)
        tile = self.tilemap.get_tile(TileLayer.SOLID, tile_x, tile_y)
        return tile is not None and tile.solid
    
    def is_position_hazard(self, world_x: float, world_y: float) -> int:
        """Controlla se una posizione mondo è un hazard e restituisce il danno"""
        tile_x, tile_y = self.get_tile_at_world_pos(world_x, world_y)
        tile = self.tilemap.get_tile(TileLayer.HAZARD, tile_x, tile_y)
        if tile and tile.hazard:
            return tile.damage
        return 0
    
    def get_camera_bounds(self) -> Tuple[float, float, float, float]:
        """Ottieni bounds della camera (x, y, width, height)"""
        pos = self.camera.get_position()
        return (pos[0] - self.screen_width//2, 
                pos[1] - self.screen_height//2,
                self.screen_width, 
                self.screen_height)
    
    def set_camera_target(self, target_x: float, target_y: float):
        """Imposta target della camera"""
        self.camera.follow_target(target_x, target_y)
    
    def set_camera_position(self, x: float, y: float):
        """Imposta posizione camera direttamente"""
        self.camera.set_position(x, y)
    
    def save_world(self, filename: str = "world_save.json"):
        """Salva lo stato del mondo"""
        self.editor.set_map_file(filename)
        self.editor._save_map()
    
    def load_world(self, filename: str = "world_save.json"):
        """Carica lo stato del mondo"""
        self.editor.set_map_file(filename)
        self.editor._load_map()
    
    def add_parallax_layer(self, image_path: str, scroll_speed: float, 
                          repeat_x: bool = True, repeat_y: bool = False):
        """Aggiunge un layer parallax al background corrente"""
        current_bg = self.parallax_manager.get_current_background()
        if current_bg:
            current_bg.add_layer(image_path, scroll_speed, repeat_x, repeat_y)
    
    def switch_parallax_background(self, background_name: str):
        """Cambia background parallax"""
        self.parallax_manager.set_current_background(background_name)
    
    def get_world_info(self) -> dict:
        """Restituisce informazioni sullo stato del mondo"""
        camera_pos = self.camera.get_position()
        current_bg = self.parallax_manager.get_current_background()
        
        return {
            'initialized': self.world_initialized,
            'map_size': (self.tilemap.width, self.tilemap.height),
            'camera_position': camera_pos,
            'collision_count': len(self.tilemap.get_collision_rects()),
            'hazard_count': len(self.tilemap.get_hazard_rects()),
            'parallax_enabled': current_bg.enabled if current_bg else False,
            'parallax_layers': current_bg.get_layer_count() if current_bg else 0,
            'debug_mode': self.debug_mode,
            'editor_active': self.editor.editor_active
        }
    
    def cleanup(self):
        """Pulizia risorse"""
        print("Pulizia WorldManager...")
        # Qui potresti aggiungere pulizia di risorse se necessario
        
    def __del__(self):
        """Distruttore"""
        self.cleanup()