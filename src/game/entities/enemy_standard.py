#!/usr/bin/env python3
"""
EnemyStandard - Nemico standard con animazioni complete
Utilizza spritesheet nemico1.png con animazioni pixel art 32x32

Developed by Team PIETRO
Un degno avversario per il campione scelto da PIETRO!
"""

import pygame
import math
from typing import Optional, TYPE_CHECKING, List
from ...core.config import Config
from .enemy import Enemy
from .animation import Animation

if TYPE_CHECKING:
    from .player import Player

class EnemyStandard(Enemy):
    """Nemico standard con sistema di animazioni completo"""
    
    def __init__(self, x: float, y: float, asset_manager):
        # Dimensioni 32x32 per il tile, collision box 28x28 centrato
        super().__init__(x, y, 32, 32, asset_manager)
        
        # Collision box più precisa (28x28 centrata)
        self.collision_width = 28
        self.collision_height = 28
        self.collision_offset_x = 2  # (32-28)/2
        self.collision_offset_y = 2  # (32-28)/2
        
        # Carica spritesheet nemico
        self.spritesheet = None
        self._load_spritesheet()
        
        # Sistema animazioni
        self.animations = {}
        self.current_animation = "idle"
        self.animation_timer = 0.0
        self.current_frame = 0
        self._setup_animations()
        
        # Stati animazione
        self.animation_state = "idle"  # idle, walk, attack, hit, death
        self.hit_timer = 0.0
        self.death_animation_complete = False
        
        # Proprietà AI specifiche
        self.detection_range = 160  # 5 tile
        self.attack_range = 96      # 3 tile
        self.patrol_distance = 128  # 4 tile
        self.move_speed = 1.5
        
        # Salute
        self.max_health = 60
        self.health = self.max_health
        
    def _load_spritesheet(self):
        """Carica il spritesheet del nemico"""
        try:
            import os
            sprite_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'sprites', 'nemico1.png')
            self.spritesheet = pygame.image.load(sprite_path).convert_alpha()
            print(f"Spritesheet nemico caricato: {self.spritesheet.get_size()}")
        except Exception as e:
            print(f"Errore caricamento spritesheet nemico: {e}")
            # Crea un placeholder rosso
            self.spritesheet = pygame.Surface((320, 32), pygame.SRCALPHA)
            self.spritesheet.fill((255, 0, 0, 128))
            
    def _setup_animations(self):
        """Configura tutte le animazioni del nemico"""
        if not self.spritesheet:
            return
            
        # Layout spritesheet: ogni animazione su una riga
        # Riga 0: idle (2 frame)
        # Riga 1: walk (4 frame) 
        # Riga 2: attack (3 frame)
        # Riga 3: hit (2 frame)
        # Riga 4: death (4 frame)
        
        self.animations = {
            "idle": {
                "frames": self._extract_frames(0, 2),
                "frame_duration": 0.8,  # Lento per idle
                "loop": True
            },
            "walk": {
                "frames": self._extract_frames(1, 4),
                "frame_duration": 0.2,  # Veloce per camminata
                "loop": True
            },
            "attack": {
                "frames": self._extract_frames(2, 3),
                "frame_duration": 0.15,  # Rapido per attacco
                "loop": False
            },
            "hit": {
                "frames": self._extract_frames(3, 2),
                "frame_duration": 0.1,   # Molto rapido per hit
                "loop": False
            },
            "death": {
                "frames": self._extract_frames(4, 4),
                "frame_duration": 0.25,  # Medio per morte
                "loop": False
            }
        }
        
    def _extract_frames(self, row: int, frame_count: int) -> List[pygame.Surface]:
        """Estrae i frame da una riga del spritesheet"""
        frames = []
        for i in range(frame_count):
            frame = pygame.Surface((32, 32), pygame.SRCALPHA)
            source_rect = pygame.Rect(i * 32, row * 32, 32, 32)
            frame.blit(self.spritesheet, (0, 0), source_rect)
            frames.append(frame)
        return frames
        
    def get_collision_rect(self) -> pygame.Rect:
        """Restituisce il rettangolo di collisione preciso (28x28)"""
        return pygame.Rect(
            int(self.x + self.collision_offset_x),
            int(self.y + self.collision_offset_y),
            self.collision_width,
            self.collision_height
        )
        
    def update(self, dt: float, player: 'Player', collision_rects: List[pygame.Rect]):
        """Aggiorna nemico con gestione animazioni"""
        if not self.alive and not self.death_animation_complete:
            self._update_death_animation(dt)
            return
        elif not self.alive:
            return
            
        # Aggiorna timer hit
        if self.hit_timer > 0:
            self.hit_timer -= dt
            
        # Aggiorna AI e fisica
        super().update(dt, player, collision_rects)
        
        # Determina stato animazione basato su AI state
        self._update_animation_state()
        
        # Aggiorna animazioni
        self._update_animations(dt)
        
    def _update_animation_state(self):
        """Determina quale animazione riprodurre basata sullo stato AI"""
        if self.hit_timer > 0:
            self.animation_state = "hit"
        elif not self.alive:
            self.animation_state = "death"
        elif self.state == "attack" and self.attack_cooldown <= 0:
            self.animation_state = "attack"
        elif abs(self.vel_x) > 0.1:  # Si sta muovendo
            self.animation_state = "walk"
        else:
            self.animation_state = "idle"
            
    def _update_animations(self, dt: float):
        """Aggiorna il sistema di animazioni"""
        if self.animation_state not in self.animations:
            return
            
        # Cambia animazione se necessario
        if self.current_animation != self.animation_state:
            self.current_animation = self.animation_state
            self.current_frame = 0
            self.animation_timer = 0.0
            
        # Aggiorna timer animazione
        anim = self.animations[self.current_animation]
        self.animation_timer += dt
        
        # Cambia frame se necessario
        if self.animation_timer >= anim["frame_duration"]:
            self.animation_timer = 0.0
            
            if anim["loop"]:
                self.current_frame = (self.current_frame + 1) % len(anim["frames"])
            else:
                if self.current_frame < len(anim["frames"]) - 1:
                    self.current_frame += 1
                elif self.current_animation == "death":
                    self.death_animation_complete = True
                elif self.current_animation == "attack":
                    # Torna a idle dopo attacco
                    self.current_animation = "idle"
                    self.current_frame = 0
                elif self.current_animation == "hit":
                    # Torna a idle dopo hit
                    self.current_animation = "idle"
                    self.current_frame = 0
                    
    def _update_death_animation(self, dt: float):
        """Aggiorna solo l'animazione di morte"""
        self.animation_state = "death"
        self._update_animations(dt)
        
    def take_damage(self, damage: int):
        """Riceve danno e attiva animazione hit"""
        if not self.alive:
            return
            
        self.health -= damage
        self.hit_timer = 0.2  # Durata animazione hit
        
        if self.health <= 0:
            self.alive = False
            self.health = 0
            print(f"EnemyStandard eliminato!")
            
    def render(self, surface: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Renderizza il nemico con animazioni"""
        if not self.alive and self.death_animation_complete:
            return
            
        # Calcola posizione schermo
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        # Ottieni frame corrente
        if (self.current_animation in self.animations and 
            self.current_frame < len(self.animations[self.current_animation]["frames"])):
            
            frame = self.animations[self.current_animation]["frames"][self.current_frame]
            
            # Flip orizzontale se necessario
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
                
            surface.blit(frame, (screen_x, screen_y))
            
        # Debug: mostra collision box
        if Config.DEBUG_MODE:
            collision_rect = self.get_collision_rect()
            debug_rect = pygame.Rect(
                collision_rect.x - camera_offset[0],
                collision_rect.y - camera_offset[1],
                collision_rect.width,
                collision_rect.height
            )
            pygame.draw.rect(surface, (255, 0, 0), debug_rect, 1)
            
        # Barra salute
        if self.alive and self.health < self.max_health:
            self._render_health_bar(surface, screen_x, screen_y - 10)
            
    def _render_health_bar(self, surface: pygame.Surface, x: int, y: int):
        """Renderizza barra della salute"""
        bar_width = 30
        bar_height = 4
        
        # Sfondo barra
        bg_rect = pygame.Rect(x + 1, y, bar_width, bar_height)
        pygame.draw.rect(surface, Config.DARK_RED, bg_rect)
        
        # Barra salute
        health_ratio = self.health / self.max_health
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            health_rect = pygame.Rect(x + 1, y, health_width, bar_height)
            pygame.draw.rect(surface, Config.RED, health_rect)
            
    def _attack_behavior(self, dt: float, player: 'Player'):
        """Comportamento di attacco con animazione"""
        if not player:
            return
            
        # Face the player
        self.facing_right = player.x > self.x
        
        # Stop moving when attacking
        self.vel_x = 0
        
        # Attack if cooldown is ready
        if self.attack_cooldown <= 0:
            self._perform_attack(player)
            self.attack_cooldown = 1.5  # Cooldown attacco
            
    def _perform_attack(self, player: 'Player'):
        """Esegue l'attacco (placeholder per proiettili futuri)"""
        print(f"EnemyStandard attacca il player!")
        # TODO: Implementare sistema proiettili