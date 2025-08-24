import pygame
import math
from enum import Enum
from typing import Optional, Dict, Any
from ..core.config import Config

class ItemType(Enum):
    """Tipi di oggetti disponibili"""
    # Oggetti collezionabili
    MEDIKIT = "medikit"
    AMMO = "ammo"
    KEYCARD = "keycard"
    CREDITS = "credits"
    
    # Power-up temporanei
    SHIELD = "shield"
    DAMAGE_BOOST = "damage_boost"
    SPEED_BOOST = "speed_boost"
    
    # Upgrade permanenti
    JETPACK = "jetpack"
    ARMOR = "armor"
    WEAPON_MOD = "weapon_mod"
    
    # Oggetti speciali
    CHECKPOINT = "checkpoint"
    ARTIFACT = "artifact"

class ItemEffect(Enum):
    """Effetti degli oggetti"""
    HEAL = "heal"
    ADD_AMMO = "add_ammo"
    UNLOCK_DOOR = "unlock_door"
    ADD_CREDITS = "add_credits"
    TEMPORARY_SHIELD = "temporary_shield"
    TEMPORARY_DAMAGE = "temporary_damage"
    TEMPORARY_SPEED = "temporary_speed"
    PERMANENT_JETPACK = "permanent_jetpack"
    PERMANENT_ARMOR = "permanent_armor"
    PERMANENT_WEAPON = "permanent_weapon"
    SAVE_CHECKPOINT = "save_checkpoint"
    COLLECT_ARTIFACT = "collect_artifact"

class Item:
    """Classe base per tutti gli oggetti collezionabili"""
    
    # Configurazione spritesheet (32x32 per frame)
    SPRITE_SIZE = 32
    ANIMATION_SPEED = 0.1  # Secondi per frame
    
    # Configurazione oggetti per tipo
    ITEM_CONFIG = {
        ItemType.MEDIKIT: {
            'sprite_row': 0, 'sprite_col': 0, 'frames': 1,
            'effect': ItemEffect.HEAL, 'value': 25, 'duration': 0,
            'animated': False
        },
        ItemType.AMMO: {
            'sprite_row': 0, 'sprite_col': 1, 'frames': 1,
            'effect': ItemEffect.ADD_AMMO, 'value': 30, 'duration': 0,
            'animated': False
        },
        ItemType.KEYCARD: {
            'sprite_row': 0, 'sprite_col': 2, 'frames': 2,
            'effect': ItemEffect.UNLOCK_DOOR, 'value': 1, 'duration': 0,
            'animated': True
        },
        ItemType.CREDITS: {
            'sprite_row': 0, 'sprite_col': 4, 'frames': 3,
            'effect': ItemEffect.ADD_CREDITS, 'value': 100, 'duration': 0,
            'animated': True
        },
        ItemType.SHIELD: {
            'sprite_row': 1, 'sprite_col': 0, 'frames': 4,
            'effect': ItemEffect.TEMPORARY_SHIELD, 'value': 1, 'duration': 10.0,
            'animated': True
        },
        ItemType.DAMAGE_BOOST: {
            'sprite_row': 1, 'sprite_col': 4, 'frames': 3,
            'effect': ItemEffect.TEMPORARY_DAMAGE, 'value': 2.0, 'duration': 15.0,
            'animated': True
        },
        ItemType.SPEED_BOOST: {
            'sprite_row': 2, 'sprite_col': 0, 'frames': 3,
            'effect': ItemEffect.TEMPORARY_SPEED, 'value': 1.5, 'duration': 12.0,
            'animated': True
        },
        ItemType.JETPACK: {
            'sprite_row': 2, 'sprite_col': 3, 'frames': 2,
            'effect': ItemEffect.PERMANENT_JETPACK, 'value': 1, 'duration': 0,
            'animated': True
        },
        ItemType.ARMOR: {
            'sprite_row': 2, 'sprite_col': 5, 'frames': 1,
            'effect': ItemEffect.PERMANENT_ARMOR, 'value': 50, 'duration': 0,
            'animated': False
        },
        ItemType.WEAPON_MOD: {
            'sprite_row': 3, 'sprite_col': 0, 'frames': 2,
            'effect': ItemEffect.PERMANENT_WEAPON, 'value': 1, 'duration': 0,
            'animated': True
        },
        ItemType.CHECKPOINT: {
            'sprite_row': 3, 'sprite_col': 2, 'frames': 4,
            'effect': ItemEffect.SAVE_CHECKPOINT, 'value': 1, 'duration': 0,
            'animated': True
        },
        ItemType.ARTIFACT: {
            'sprite_row': 3, 'sprite_col': 6, 'frames': 2,
            'effect': ItemEffect.COLLECT_ARTIFACT, 'value': 1, 'duration': 0,
            'animated': True
        }
    }
    
    def __init__(self, x: float, y: float, item_type: ItemType, spritesheet: pygame.Surface):
        """Inizializza un oggetto
        
        Args:
            x: Posizione X
            y: Posizione Y
            item_type: Tipo di oggetto
            spritesheet: Spritesheet degli oggetti
        """
        self.x = x
        self.y = y
        self.item_type = item_type
        self.spritesheet = spritesheet
        
        # Carica configurazione oggetto
        self.config = self.ITEM_CONFIG[item_type]
        self.effect = self.config['effect']
        self.value = self.config['value']
        self.duration = self.config['duration']
        self.animated = self.config['animated']
        
        # Proprietà animazione
        self.current_frame = 0
        self.animation_timer = 0.0
        self.frames = self.config['frames']
        
        # Carica sprite
        self._load_sprites()
        
        # Collision box (più piccola del sprite per migliore gameplay)
        self.collision_rect = pygame.Rect(
            x + 4, y + 4, 
            self.SPRITE_SIZE - 8, self.SPRITE_SIZE - 8
        )
        
        # Effetto floating
        self.float_offset = 0.0
        self.float_speed = 2.0
        
        # Stato
        self.collected = False
        
    def _load_sprites(self):
        """Carica gli sprite dall'oggetto spritesheet"""
        self.sprites = []
        row = self.config['sprite_row']
        col = self.config['sprite_col']
        
        for i in range(self.frames):
            sprite_x = (col + i) * self.SPRITE_SIZE
            sprite_y = row * self.SPRITE_SIZE
            
            sprite = self.spritesheet.subsurface(
                sprite_x, sprite_y, self.SPRITE_SIZE, self.SPRITE_SIZE
            ).convert_alpha()
            
            self.sprites.append(sprite)
    
    def update(self, dt: float):
        """Aggiorna l'oggetto
        
        Args:
            dt: Delta time in secondi
        """
        if self.collected:
            return
            
        # Aggiorna animazione se animato
        if self.animated and self.frames > 1:
            self.animation_timer += dt
            if self.animation_timer >= self.ANIMATION_SPEED:
                self.animation_timer = 0.0
                self.current_frame = (self.current_frame + 1) % self.frames
        
        # Effetto floating
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003 * self.float_speed) * 3
        
        # Aggiorna collision rect
        self.collision_rect.x = self.x + 4
        self.collision_rect.y = self.y + 4 + self.float_offset
    
    def get_current_sprite(self) -> pygame.Surface:
        """Ottiene lo sprite corrente
        
        Returns:
            Sprite corrente
        """
        return self.sprites[self.current_frame]
    
    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Renderizza l'oggetto
        
        Args:
            screen: Superficie di rendering
            camera_x: Offset camera X
            camera_y: Offset camera Y
        """
        if self.collected:
            return
            
        # Calcola posizione sullo schermo
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y + self.float_offset
        
        # Renderizza solo se visibile
        if (-self.SPRITE_SIZE <= screen_x <= Config.SCREEN_WIDTH and 
            -self.SPRITE_SIZE <= screen_y <= Config.SCREEN_HEIGHT):
            
            sprite = self.get_current_sprite()
            screen.blit(sprite, (screen_x, screen_y))
            
            # Debug: mostra collision box
            if Config.DEBUG_MODE:
                debug_rect = pygame.Rect(
                    screen_x + 4, screen_y + 4,
                    self.SPRITE_SIZE - 8, self.SPRITE_SIZE - 8
                )
                pygame.draw.rect(screen, (0, 255, 0), debug_rect, 1)
    
    def collect(self) -> Dict[str, Any]:
        """Raccoglie l'oggetto
        
        Returns:
            Dizionario con informazioni sull'effetto
        """
        if self.collected:
            return {}
            
        self.collected = True
        
        return {
            'type': self.item_type,
            'effect': self.effect,
            'value': self.value,
            'duration': self.duration
        }
    
    def is_temporary_powerup(self) -> bool:
        """Verifica se è un power-up temporaneo
        
        Returns:
            True se è temporaneo
        """
        return self.duration > 0
    
    def is_permanent_upgrade(self) -> bool:
        """Verifica se è un upgrade permanente
        
        Returns:
            True se è permanente
        """
        return self.item_type in [ItemType.JETPACK, ItemType.ARMOR, ItemType.WEAPON_MOD]
    
    def get_collision_rect(self) -> pygame.Rect:
        """Ottiene il rettangolo di collisione
        
        Returns:
            Rettangolo di collisione
        """
        return self.collision_rect