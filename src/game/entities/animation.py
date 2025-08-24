import pygame
from enum import Enum
from typing import Dict, List, Tuple

class AnimationState(Enum):
    """Stati di animazione del protagonista"""
    IDLE = "idle"
    RUNNING = "running"
    JUMPING = "jumping"
    SHOOTING = "shooting"
    WEAPON_CHANGE = "weapon_change"
    UTILITY_USE = "utility_use"

class Animation:
    """Classe per gestire una singola animazione"""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, loop: bool = True):
        self.frames = frames
        self.frame_duration = frame_duration  # Durata di ogni frame in secondi
        self.loop = loop
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.finished = False
    
    def update(self, dt: float) -> None:
        """Aggiorna l'animazione"""
        if self.finished and not self.loop:
            return
            
        self.time_accumulator += dt
        
        if self.time_accumulator >= self.frame_duration:
            self.time_accumulator = 0.0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
    
    def get_current_frame(self) -> pygame.Surface:
        """Restituisce il frame corrente"""
        return self.frames[self.current_frame]
    
    def reset(self) -> None:
        """Resetta l'animazione"""
        self.current_frame = 0
        self.time_accumulator = 0.0
        self.finished = False

class PlayerAnimator:
    """Gestore delle animazioni del protagonista"""
    
    def __init__(self, sprite_sheet_path: str):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.animations: Dict[AnimationState, Animation] = {}
        self.current_state = AnimationState.IDLE
        self.previous_state = AnimationState.IDLE
        self.facing_right = True
        
        # Calcola dimensioni sprite basate sull'immagine effettiva
        sheet_width, sheet_height = self.sprite_sheet.get_size()
        print(f"Player spritesheet size: {sheet_width}x{sheet_height}")
        
        # Assumendo 6 sprite in orizzontale per il player
        original_width = sheet_width // 6
        original_height = sheet_height
        
        # Scala a dimensioni ragionevoli per il gameplay (target: 32x64)
        self.target_width = 32
        self.target_height = 64
        self.sprite_width = original_width
        self.sprite_height = original_height
        
        print(f"Player sprite original: {original_width}x{original_height}")
        print(f"Player sprite target: {self.target_width}x{self.target_height}")
        
        self._load_animations()
    
    def _load_animations(self) -> None:
        """Carica tutte le animazioni dal sprite sheet"""
        # Estrae i singoli sprite dal sheet (6 pose in orizzontale)
        sprites = []
        for i in range(6):
            x = i * self.sprite_width
            sprite_rect = pygame.Rect(x, 0, self.sprite_width, self.sprite_height)
            sprite = self.sprite_sheet.subsurface(sprite_rect)
            sprites.append(sprite)
        
        # Crea le animazioni per ogni stato
        # Idle → prima posa (frame 0)
        self.animations[AnimationState.IDLE] = Animation(
            frames=[sprites[0]], 
            frame_duration=1.0,  # Statico
            loop=True
        )
        
        # Corsa → seconda posa (frame 1) - animazione ciclica
        self.animations[AnimationState.RUNNING] = Animation(
            frames=[sprites[1], sprites[0]],  # Alterna tra corsa e idle per movimento
            frame_duration=0.2,
            loop=True
        )
        
        # Salto → terza posa (frame 2) adattata al movimento verticale
        self.animations[AnimationState.JUMPING] = Animation(
            frames=[sprites[2]], 
            frame_duration=0.1,
            loop=False
        )
        
        # Sparo → terza posa (frame 2)
        self.animations[AnimationState.SHOOTING] = Animation(
            frames=[sprites[2], sprites[0]],  # Sparo poi ritorna idle
            frame_duration=0.1,
            loop=False
        )
        
        # Cambio arma → quinta posa (frame 4)
        self.animations[AnimationState.WEAPON_CHANGE] = Animation(
            frames=[sprites[4], sprites[0]],  # Cambio arma poi ritorna idle
            frame_duration=0.15,
            loop=False
        )
        
        # Uso utility → sesta posa (frame 5)
        self.animations[AnimationState.UTILITY_USE] = Animation(
            frames=[sprites[5], sprites[0]],  # Uso utility poi ritorna idle
            frame_duration=0.2,
            loop=False
        )
    
    def set_state(self, new_state: AnimationState) -> None:
        """Cambia lo stato dell'animazione"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.animations[new_state].reset()
    
    def set_facing_direction(self, facing_right: bool) -> None:
        """Imposta la direzione del personaggio"""
        self.facing_right = facing_right
    
    def update(self, dt: float) -> None:
        """Aggiorna l'animazione corrente"""
        current_animation = self.animations[self.current_state]
        current_animation.update(dt)
        
        # Se l'animazione non è ciclica ed è finita, torna a idle
        if current_animation.finished and not current_animation.loop:
            if self.current_state != AnimationState.IDLE:
                self.set_state(AnimationState.IDLE)
    
    def get_current_sprite(self) -> pygame.Surface:
        """Restituisce lo sprite corrente con la direzione corretta e scalato"""
        sprite = self.animations[self.current_state].get_current_frame()
        
        # Scala lo sprite alle dimensioni target
        if sprite.get_size() != (self.target_width, self.target_height):
            sprite = pygame.transform.scale(sprite, (self.target_width, self.target_height))
        
        # Specchia lo sprite se il personaggio guarda a sinistra
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        return sprite
    
    def is_animation_finished(self) -> bool:
        """Controlla se l'animazione corrente è finita"""
        return self.animations[self.current_state].finished
    
    def get_sprite_rect(self, x: float, y: float) -> pygame.Rect:
        """Restituisce il rettangolo dello sprite per il rendering"""
        return pygame.Rect(x - self.sprite_width // 2, y - self.sprite_height // 2, 
                          self.sprite_width, self.sprite_height)