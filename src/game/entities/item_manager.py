import pygame
import random
from typing import List, Dict, Any, Optional
from .item import Item, ItemType, ItemEffect
from ...core.config import Config

class PowerUp:
    """Classe per gestire power-up temporanei attivi"""
    
    def __init__(self, effect: ItemEffect, value: float, duration: float):
        self.effect = effect
        self.value = value
        self.duration = duration
        self.remaining_time = duration
        self.active = True
    
    def update(self, dt: float) -> bool:
        """Aggiorna il power-up
        
        Args:
            dt: Delta time
            
        Returns:
            True se ancora attivo
        """
        if not self.active:
            return False
            
        self.remaining_time -= dt
        if self.remaining_time <= 0:
            self.active = False
            return False
            
        return True
    
    def get_progress(self) -> float:
        """Ottiene il progresso del power-up (0.0 - 1.0)
        
        Returns:
            Progresso normalizzato
        """
        if self.duration <= 0:
            return 1.0
        return max(0.0, self.remaining_time / self.duration)

class ItemManager:
    """Gestore degli oggetti nel gioco"""
    
    def __init__(self, spritesheet: pygame.Surface):
        """Inizializza il gestore oggetti
        
        Args:
            spritesheet: Spritesheet degli oggetti
        """
        self.spritesheet = spritesheet
        self.items: List[Item] = []
        
        # Inventario permanente
        self.permanent_upgrades: Dict[ItemType, bool] = {
            ItemType.JETPACK: False,
            ItemType.ARMOR: False,
            ItemType.WEAPON_MOD: False
        }
        
        # Power-up temporanei attivi
        self.active_powerups: Dict[ItemEffect, PowerUp] = {}
        
        # Statistiche giocatore modificate
        self.player_stats = {
            'max_health_bonus': 0,
            'damage_multiplier': 1.0,
            'speed_multiplier': 1.0,
            'has_shield': False,
            'credits': 0,
            'keycards': 0,
            'artifacts_collected': 0
        }
    
    def spawn_item(self, x: float, y: float, item_type: ItemType) -> Item:
        """Spawna un nuovo oggetto
        
        Args:
            x: Posizione X
            y: Posizione Y
            item_type: Tipo di oggetto
            
        Returns:
            Oggetto creato
        """
        item = Item(x, y, item_type, self.spritesheet)
        self.items.append(item)
        return item
    
    def spawn_random_item(self, x: float, y: float, difficulty: float = 1.0) -> Item:
        """Spawna un oggetto casuale basato sulla difficoltà
        
        Args:
            x: Posizione X
            y: Posizione Y
            difficulty: Livello di difficoltà (0.0 - 2.0)
            
        Returns:
            Oggetto creato
        """
        # Probabilità basate sulla difficoltà
        if difficulty < 0.5:
            # Livello facile: più medikit e munizioni
            weights = {
                ItemType.MEDIKIT: 30,
                ItemType.AMMO: 25,
                ItemType.CREDITS: 20,
                ItemType.KEYCARD: 10,
                ItemType.SHIELD: 8,
                ItemType.SPEED_BOOST: 5,
                ItemType.JETPACK: 2
            }
        elif difficulty < 1.0:
            # Livello medio: bilanciato
            weights = {
                ItemType.MEDIKIT: 20,
                ItemType.AMMO: 20,
                ItemType.CREDITS: 15,
                ItemType.KEYCARD: 10,
                ItemType.SHIELD: 10,
                ItemType.DAMAGE_BOOST: 8,
                ItemType.SPEED_BOOST: 7,
                ItemType.JETPACK: 5,
                ItemType.ARMOR: 3,
                ItemType.ARTIFACT: 2
            }
        else:
            # Livello difficile: più power-up e upgrade
            weights = {
                ItemType.MEDIKIT: 15,
                ItemType.AMMO: 15,
                ItemType.CREDITS: 10,
                ItemType.SHIELD: 15,
                ItemType.DAMAGE_BOOST: 12,
                ItemType.SPEED_BOOST: 10,
                ItemType.JETPACK: 8,
                ItemType.ARMOR: 6,
                ItemType.WEAPON_MOD: 5,
                ItemType.ARTIFACT: 4
            }
        
        # Seleziona tipo casuale
        item_types = list(weights.keys())
        probabilities = list(weights.values())
        item_type = random.choices(item_types, weights=probabilities)[0]
        
        return self.spawn_item(x, y, item_type)
    
    def update(self, dt: float):
        """Aggiorna tutti gli oggetti e power-up
        
        Args:
            dt: Delta time
        """
        # Aggiorna oggetti
        for item in self.items:
            item.update(dt)
        
        # Rimuovi oggetti raccolti
        self.items = [item for item in self.items if not item.collected]
        
        # Aggiorna power-up temporanei
        expired_powerups = []
        for effect, powerup in self.active_powerups.items():
            if not powerup.update(dt):
                expired_powerups.append(effect)
        
        # Rimuovi power-up scaduti e ripristina statistiche
        for effect in expired_powerups:
            self._remove_powerup_effect(effect)
            del self.active_powerups[effect]
    
    def check_collision(self, player_rect: pygame.Rect) -> List[Dict[str, Any]]:
        """Controlla collisioni con il giocatore
        
        Args:
            player_rect: Rettangolo del giocatore
            
        Returns:
            Lista degli effetti degli oggetti raccolti
        """
        collected_effects = []
        
        for item in self.items:
            if not item.collected and item.get_collision_rect().colliderect(player_rect):
                effect_data = item.collect()
                if effect_data:
                    collected_effects.append(effect_data)
                    self._apply_item_effect(effect_data)
        
        return collected_effects
    
    def _apply_item_effect(self, effect_data: Dict[str, Any]):
        """Applica l'effetto di un oggetto raccolto
        
        Args:
            effect_data: Dati dell'effetto
        """
        effect = effect_data['effect']
        value = effect_data['value']
        duration = effect_data['duration']
        item_type = effect_data['type']
        
        if effect == ItemEffect.HEAL:
            # Gestito dal player direttamente
            pass
        elif effect == ItemEffect.ADD_AMMO:
            # Gestito dal player direttamente
            pass
        elif effect == ItemEffect.UNLOCK_DOOR:
            self.player_stats['keycards'] += value
        elif effect == ItemEffect.ADD_CREDITS:
            self.player_stats['credits'] += value
        elif effect == ItemEffect.COLLECT_ARTIFACT:
            self.player_stats['artifacts_collected'] += value
        elif effect == ItemEffect.SAVE_CHECKPOINT:
            # Gestito dal game state
            pass
        elif effect in [ItemEffect.TEMPORARY_SHIELD, ItemEffect.TEMPORARY_DAMAGE, ItemEffect.TEMPORARY_SPEED]:
            # Power-up temporaneo
            powerup = PowerUp(effect, value, duration)
            self.active_powerups[effect] = powerup
            self._apply_powerup_effect(effect, value)
        elif effect in [ItemEffect.PERMANENT_JETPACK, ItemEffect.PERMANENT_ARMOR, ItemEffect.PERMANENT_WEAPON]:
            # Upgrade permanente
            self.permanent_upgrades[item_type] = True
            if effect == ItemEffect.PERMANENT_ARMOR:
                self.player_stats['max_health_bonus'] += value
    
    def _apply_powerup_effect(self, effect: ItemEffect, value: float):
        """Applica effetto power-up temporaneo
        
        Args:
            effect: Tipo di effetto
            value: Valore dell'effetto
        """
        if effect == ItemEffect.TEMPORARY_SHIELD:
            self.player_stats['has_shield'] = True
        elif effect == ItemEffect.TEMPORARY_DAMAGE:
            self.player_stats['damage_multiplier'] = value
        elif effect == ItemEffect.TEMPORARY_SPEED:
            self.player_stats['speed_multiplier'] = value
    
    def _remove_powerup_effect(self, effect: ItemEffect):
        """Rimuove effetto power-up scaduto
        
        Args:
            effect: Tipo di effetto
        """
        if effect == ItemEffect.TEMPORARY_SHIELD:
            self.player_stats['has_shield'] = False
        elif effect == ItemEffect.TEMPORARY_DAMAGE:
            self.player_stats['damage_multiplier'] = 1.0
        elif effect == ItemEffect.TEMPORARY_SPEED:
            self.player_stats['speed_multiplier'] = 1.0
    
    def render(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """Renderizza tutti gli oggetti
        
        Args:
            screen: Superficie di rendering
            camera_x: Offset camera X
            camera_y: Offset camera Y
        """
        for item in self.items:
            item.render(screen, camera_x, camera_y)
    
    def get_active_powerups(self) -> Dict[ItemEffect, PowerUp]:
        """Ottiene i power-up attivi
        
        Returns:
            Dizionario dei power-up attivi
        """
        return self.active_powerups.copy()
    
    def has_active_power_up(self, item_type: ItemType) -> bool:
        """Controlla se un power-up è attivo
        
        Args:
            item_type: Tipo di item da controllare
            
        Returns:
            True se il power-up è attivo
        """
        # Converti ItemType in ItemEffect
        effect_mapping = {
            ItemType.DAMAGE_BOOST: ItemEffect.TEMPORARY_DAMAGE,
            ItemType.SPEED_BOOST: ItemEffect.TEMPORARY_SPEED,
            ItemType.SHIELD: ItemEffect.TEMPORARY_SHIELD
        }
        
        effect = effect_mapping.get(item_type)
        return effect is not None and effect in self.active_powerups
    
    def get_permanent_upgrades(self) -> Dict[ItemType, bool]:
        """Ottiene gli upgrade permanenti
        
        Returns:
            Dizionario degli upgrade permanenti
        """
        return self.permanent_upgrades.copy()
    
    def get_player_stats(self) -> Dict[str, Any]:
        """Ottiene le statistiche modificate del giocatore
        
        Returns:
            Dizionario delle statistiche
        """
        return self.player_stats.copy()
    
    def has_keycard(self) -> bool:
        """Verifica se il giocatore ha almeno una keycard
        
        Returns:
            True se ha keycards
        """
        return self.player_stats['keycards'] > 0
    
    def use_keycard(self) -> bool:
        """Usa una keycard
        
        Returns:
            True se è stata usata con successo
        """
        if self.player_stats['keycards'] > 0:
            self.player_stats['keycards'] -= 1
            return True
        return False
    
    def clear_all_items(self):
        """Rimuove tutti gli oggetti (per cambio livello)"""
        self.items.clear()
    
    def get_items_count(self) -> int:
        """Ottiene il numero di oggetti attivi
        
        Returns:
            Numero di oggetti
        """
        return len([item for item in self.items if not item.collected])
    
    def spawn_checkpoint(self, x: float, y: float) -> Item:
        """Spawna un checkpoint
        
        Args:
            x: Posizione X
            y: Posizione Y
            
        Returns:
            Checkpoint creato
        """
        return self.spawn_item(x, y, ItemType.CHECKPOINT)
    
    def get_save_data(self) -> Dict[str, Any]:
        """Ottiene i dati per il salvataggio
        
        Returns:
            Dati di salvataggio
        """
        return {
            'permanent_upgrades': self.permanent_upgrades,
            'player_stats': self.player_stats,
            'items': [
                {
                    'x': item.x,
                    'y': item.y,
                    'type': item.item_type.value,
                    'collected': item.collected
                }
                for item in self.items
            ]
        }
    
    def load_save_data(self, data: Dict[str, Any]):
        """Carica i dati dal salvataggio
        
        Args:
            data: Dati di salvataggio
        """
        if 'permanent_upgrades' in data:
            for upgrade_name, value in data['permanent_upgrades'].items():
                if hasattr(ItemType, upgrade_name.upper()):
                    item_type = ItemType(upgrade_name)
                    self.permanent_upgrades[item_type] = value
        
        if 'player_stats' in data:
            self.player_stats.update(data['player_stats'])
        
        if 'items' in data:
            self.items.clear()
            for item_data in data['items']:
                if not item_data.get('collected', False):
                    item_type = ItemType(item_data['type'])
                    item = self.spawn_item(item_data['x'], item_data['y'], item_type)