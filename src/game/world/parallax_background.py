import pygame
from typing import List, Tuple, Optional
from .spritesheet_loader import TilemapConfig

class ParallaxLayer:
    """Singolo layer di parallax background"""
    
    def __init__(self, image_path: str, scroll_speed: float, repeat_x: bool = True, repeat_y: bool = False):
        self.image_path = image_path
        self.scroll_speed = scroll_speed  # Velocità relativa (0.0 = statico, 1.0 = velocità camera)
        self.repeat_x = repeat_x
        self.repeat_y = repeat_y
        
        # Carica immagine
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.width = self.image.get_width()
            self.height = self.image.get_height()
            print(f"Caricato layer parallax: {image_path} ({self.width}x{self.height})")
        except pygame.error as e:
            print(f"Errore caricamento layer parallax {image_path}: {e}")
            # Crea immagine placeholder
            self.image = pygame.Surface((800, 600))
            self.image.fill((50, 50, 100))  # Colore blu scuro
            self.width = 800
            self.height = 600
        
        # Offset per il movimento
        self.offset_x = 0.0
        self.offset_y = 0.0
    
    def update(self, camera_offset: Tuple[float, float]):
        """Aggiorna la posizione del layer basata sul movimento della camera"""
        camera_x, camera_y = camera_offset
        
        # Calcola offset basato sulla velocità di scroll
        self.offset_x = camera_x * self.scroll_speed
        self.offset_y = camera_y * self.scroll_speed
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Renderizza il layer parallax"""
        screen_width, screen_height = surface.get_size()
        
        # Calcola posizione di rendering
        render_x = -self.offset_x
        render_y = -self.offset_y
        
        if self.repeat_x:
            # Ripeti orizzontalmente
            start_x = int(render_x % self.width) - self.width
            tiles_x = (screen_width // self.width) + 3
            
            for i in range(tiles_x):
                x_pos = start_x + (i * self.width)
                
                if self.repeat_y:
                    # Ripeti anche verticalmente
                    start_y = int(render_y % self.height) - self.height
                    tiles_y = (screen_height // self.height) + 3
                    
                    for j in range(tiles_y):
                        y_pos = start_y + (j * self.height)
                        surface.blit(self.image, (x_pos, y_pos))
                else:
                    # Solo ripetizione orizzontale
                    surface.blit(self.image, (x_pos, render_y))
        else:
            # Nessuna ripetizione
            surface.blit(self.image, (render_x, render_y))

class ParallaxBackground:
    """Sistema di background parallax multi-layer"""
    
    def __init__(self, config_path: str = "assets/tilemap_config.json"):
        self.layers: List[ParallaxLayer] = []
        self.enabled = True
        
        # Carica configurazione
        try:
            self.config = TilemapConfig(config_path)
            self._load_layers_from_config()
        except Exception as e:
            print(f"Errore caricamento config parallax: {e}")
            self._create_default_layers()
    
    def _load_layers_from_config(self):
        """Carica i layer dal file di configurazione"""
        parallax_config = self.config.get('parallax', {})
        self.enabled = parallax_config.get('enabled', True)
        
        if not self.enabled:
            print("Parallax background disabilitato da configurazione")
            return
        
        layers_config = parallax_config.get('layers', [])
        
        for layer_config in layers_config:
            image_path = layer_config.get('image', '')
            scroll_speed = layer_config.get('scroll_speed', 0.5)
            repeat_x = layer_config.get('repeat_x', True)
            repeat_y = layer_config.get('repeat_y', False)
            
            if image_path:
                layer = ParallaxLayer(image_path, scroll_speed, repeat_x, repeat_y)
                self.layers.append(layer)
        
        print(f"Caricati {len(self.layers)} layer parallax")
    
    def _create_default_layers(self):
        """Crea layer di default se la configurazione fallisce"""
        print("Creando layer parallax di default...")
        
        # Layer 1: Sfondo molto lontano (stelle/nebulosa)
        far_layer = ParallaxLayer("assets/backgrounds/far_bg.png", 0.1, True, True)
        self.layers.append(far_layer)
        
        # Layer 2: Sfondo medio (pianeti/strutture distanti)
        mid_layer = ParallaxLayer("assets/backgrounds/mid_bg.png", 0.3, True, False)
        self.layers.append(mid_layer)
        
        # Layer 3: Sfondo vicino (dettagli architettonici)
        near_layer = ParallaxLayer("assets/backgrounds/near_bg.png", 0.6, True, False)
        self.layers.append(near_layer)
    
    def add_layer(self, image_path: str, scroll_speed: float, repeat_x: bool = True, repeat_y: bool = False):
        """Aggiunge un nuovo layer parallax"""
        layer = ParallaxLayer(image_path, scroll_speed, repeat_x, repeat_y)
        self.layers.append(layer)
        print(f"Aggiunto layer parallax: {image_path} (velocità: {scroll_speed})")
    
    def remove_layer(self, index: int):
        """Rimuove un layer parallax"""
        if 0 <= index < len(self.layers):
            removed = self.layers.pop(index)
            print(f"Rimosso layer parallax: {removed.image_path}")
    
    def clear_layers(self):
        """Rimuove tutti i layer"""
        self.layers.clear()
        print("Tutti i layer parallax rimossi")
    
    def set_enabled(self, enabled: bool):
        """Abilita/disabilita il parallax background"""
        self.enabled = enabled
        print(f"Parallax background: {'abilitato' if enabled else 'disabilitato'}")
    
    def update(self, camera_offset: Tuple[float, float]):
        """Aggiorna tutti i layer parallax"""
        if not self.enabled:
            return
        
        for layer in self.layers:
            layer.update(camera_offset)
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Renderizza tutti i layer parallax in ordine"""
        if not self.enabled:
            return
        
        # Renderizza dal layer più lontano al più vicino
        for layer in self.layers:
            layer.render(surface, camera_offset)
    
    def get_layer_count(self) -> int:
        """Restituisce il numero di layer attivi"""
        return len(self.layers)
    
    def get_layer_info(self, index: int) -> Optional[dict]:
        """Restituisce informazioni su un layer specifico"""
        if 0 <= index < len(self.layers):
            layer = self.layers[index]
            return {
                'image_path': layer.image_path,
                'scroll_speed': layer.scroll_speed,
                'repeat_x': layer.repeat_x,
                'repeat_y': layer.repeat_y,
                'size': (layer.width, layer.height)
            }
        return None
    
    def set_layer_scroll_speed(self, index: int, scroll_speed: float):
        """Modifica la velocità di scroll di un layer"""
        if 0 <= index < len(self.layers):
            self.layers[index].scroll_speed = scroll_speed
            print(f"Layer {index} velocità aggiornata a: {scroll_speed}")
    
    def create_gradient_background(self, surface: pygame.Surface, 
                                 top_color: Tuple[int, int, int] = (20, 20, 40),
                                 bottom_color: Tuple[int, int, int] = (60, 40, 80)):
        """Crea un background gradiente semplice se non ci sono layer"""
        if self.layers or not self.enabled:
            return
        
        width, height = surface.get_size()
        
        # Crea gradiente verticale
        for y in range(height):
            ratio = y / height
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
            
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (width, y))
    
    def debug_render(self, surface: pygame.Surface, font: pygame.font.Font):
        """Renderizza informazioni di debug sui layer parallax"""
        if not self.enabled:
            return
        
        y_offset = 10
        for i, layer in enumerate(self.layers):
            info_text = f"Layer {i}: {layer.scroll_speed:.1f}x - {layer.image_path}"
            text_surface = font.render(info_text, True, (255, 255, 255))
            
            # Sfondo semi-trasparente
            bg_rect = text_surface.get_rect()
            bg_rect.x = 10
            bg_rect.y = y_offset
            bg_surface = pygame.Surface((bg_rect.width + 10, bg_rect.height + 4))
            bg_surface.set_alpha(128)
            bg_surface.fill((0, 0, 0))
            surface.blit(bg_surface, bg_rect)
            
            # Testo
            surface.blit(text_surface, (15, y_offset + 2))
            y_offset += 25

class ParallaxManager:
    """Manager per gestire multiple istanze di parallax background"""
    
    def __init__(self):
        self.backgrounds: dict[str, ParallaxBackground] = {}
        self.current_background: Optional[str] = None
    
    def add_background(self, name: str, background: ParallaxBackground):
        """Aggiunge un background parallax"""
        self.backgrounds[name] = background
        if self.current_background is None:
            self.current_background = name
        print(f"Background parallax '{name}' aggiunto")
    
    def set_current_background(self, name: str):
        """Imposta il background corrente"""
        if name in self.backgrounds:
            self.current_background = name
            print(f"Background parallax corrente: '{name}'")
        else:
            print(f"Background parallax '{name}' non trovato")
    
    def get_current_background(self) -> Optional[ParallaxBackground]:
        """Restituisce il background corrente"""
        if self.current_background and self.current_background in self.backgrounds:
            return self.backgrounds[self.current_background]
        return None
    
    def update(self, camera_offset: Tuple[float, float]):
        """Aggiorna il background corrente"""
        current = self.get_current_background()
        if current:
            current.update(camera_offset)
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float]):
        """Renderizza il background corrente"""
        current = self.get_current_background()
        if current:
            current.render(surface, camera_offset)
        else:
            # Fallback: sfondo gradiente
            self._render_fallback_background(surface)
    
    def _render_fallback_background(self, surface: pygame.Surface):
        """Renderizza un background di fallback"""
        surface.fill((30, 30, 60))  # Blu scuro