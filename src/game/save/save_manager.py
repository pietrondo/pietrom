#!/usr/bin/env python3
"""
Save Manager
Handles game save and load functionality

Developed by Team PIETRO
PIETRO's save system ensures no progress is ever lost!
"""

import json
import os
import pickle
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from ...core.config import Config

class SaveManager:
    """Manages game save and load operations"""
    
    def __init__(self):
        self.save_directory = Config.SAVE_PATH
        self.save_slots = 3  # Number of save slots
        self.current_save_data = None
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
    def save_game(self, slot: int, game_state: Dict[str, Any]) -> bool:
        """Save game to specified slot"""
        try:
            # Prepare save data
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'slot': slot,
                'game_state': game_state
            }
            
            # Save to JSON file
            save_file = os.path.join(self.save_directory, f"save_slot_{slot}.json")
            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            # Also save as binary backup
            backup_file = os.path.join(self.save_directory, f"save_slot_{slot}.bak")
            with open(backup_file, 'wb') as f:
                pickle.dump(save_data, f)
                
            self.current_save_data = save_data
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
            
    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """Load game from specified slot"""
        try:
            save_file = os.path.join(self.save_directory, f"save_slot_{slot}.json")
            
            if not os.path.exists(save_file):
                # Try backup file
                backup_file = os.path.join(self.save_directory, f"save_slot_{slot}.bak")
                if os.path.exists(backup_file):
                    with open(backup_file, 'rb') as f:
                        save_data = pickle.load(f)
                        self.current_save_data = save_data
                        return save_data['game_state']
                return None
                
            with open(save_file, 'r') as f:
                save_data = json.load(f)
                
            self.current_save_data = save_data
            return save_data['game_state']
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
            
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """Get save slot information without loading full data"""
        try:
            save_file = os.path.join(self.save_directory, f"save_slot_{slot}.json")
            
            if not os.path.exists(save_file):
                return None
                
            with open(save_file, 'r') as f:
                save_data = json.load(f)
                
            # Return basic info
            return {
                'slot': slot,
                'timestamp': save_data.get('timestamp'),
                'version': save_data.get('version'),
                'level': save_data['game_state'].get('current_level', 1),
                'player_health': save_data['game_state'].get('player', {}).get('health', 100),
                'score': save_data['game_state'].get('player', {}).get('score', 0),
                'playtime': save_data['game_state'].get('playtime', 0)
            }
            
        except Exception as e:
            print(f"Error getting save info: {e}")
            return None
            
    def delete_save(self, slot: int) -> bool:
        """Delete save from specified slot"""
        try:
            save_file = os.path.join(self.save_directory, f"save_slot_{slot}.json")
            backup_file = os.path.join(self.save_directory, f"save_slot_{slot}.bak")
            
            if os.path.exists(save_file):
                os.remove(save_file)
                
            if os.path.exists(backup_file):
                os.remove(backup_file)
                
            return True
            
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
            
    def get_all_saves(self) -> List[Dict[str, Any]]:
        """Get information about all save slots"""
        saves = []
        
        for slot in range(1, self.save_slots + 1):
            save_info = self.get_save_info(slot)
            if save_info:
                saves.append(save_info)
            else:
                saves.append({'slot': slot, 'empty': True})
                
        return saves
        
    def create_game_state(self, player, level, enemies, collectibles, 
                         current_level: int, playtime: float) -> Dict[str, Any]:
        """Create game state dictionary for saving"""
        game_state = {
            'current_level': current_level,
            'playtime': playtime,
            'timestamp': time.time(),
            
            # Player data
            'player': {
                'x': player.x,
                'y': player.y,
                'health': player.health,
                'max_health': player.max_health,
                'score': getattr(player, 'score', 0),
                'keys': getattr(player, 'keys', 0),
                
                # Weapons
                'current_weapon_index': player.current_weapon_index,
                'weapons': [],
                
                # Utilities
                'jetpack_fuel': getattr(player, 'jetpack_fuel', 100),
                'max_jetpack_fuel': getattr(player, 'max_jetpack_fuel', 100),
                'flashlight_active': getattr(player, 'flashlight_active', False),
                'scanner_active': getattr(player, 'scanner_active', False),
                
                # Power-ups
                'active_powerups': getattr(player, 'active_powerups', {}),
                
                # Reserve ammo
                'reserve_ammo': getattr(player, 'reserve_ammo', {})
            },
            
            # Level data
            'level': {
                'width': level.width,
                'height': level.height,
                'tiles': {},
                'collectibles': [],
                'secrets': level.secrets
            },
            
            # Enemies data
            'enemies': [],
            
            # Game settings
            'settings': {
                'difficulty': 1,
                'master_volume': 1.0,
                'sfx_volume': 1.0,
                'music_volume': 1.0
            }
        }
        
        # Save weapon data
        for weapon in player.weapons:
            weapon_data = {
                'type': weapon.weapon_type.name,
                'current_ammo': weapon.current_ammo,
                'max_ammo': weapon.max_ammo
            }
            game_state['player']['weapons'].append(weapon_data)
            
        # Save level tiles (only non-default ones)
        for (x, y), tile in level.tiles.items():
            game_state['level']['tiles'][f"{x},{y}"] = {
                'type': tile.tile_type,
                'x': x,
                'y': y
            }
            
        # Save collectibles (only uncollected ones)
        for collectible in collectibles:
            if not collectible.get('collected', False):
                game_state['level']['collectibles'].append(collectible)
                
        # Save enemies
        for enemy in enemies:
            if enemy.alive:
                enemy_data = {
                    'type': enemy.__class__.__name__,
                    'x': enemy.x,
                    'y': enemy.y,
                    'health': enemy.health,
                    'max_health': enemy.max_health,
                    'state': enemy.state
                }
                game_state['enemies'].append(enemy_data)
                
        return game_state
        
    def apply_game_state(self, game_state: Dict[str, Any], player, level, 
                        asset_manager) -> tuple:
        """Apply loaded game state to game objects"""
        try:
            # Apply player state
            player_data = game_state['player']
            player.x = player_data['x']
            player.y = player_data['y']
            player.health = player_data['health']
            player.max_health = player_data['max_health']
            
            if hasattr(player, 'score'):
                player.score = player_data.get('score', 0)
            if hasattr(player, 'keys'):
                player.keys = player_data.get('keys', 0)
                
            # Apply utilities
            if hasattr(player, 'jetpack_fuel'):
                player.jetpack_fuel = player_data.get('jetpack_fuel', 100)
                player.max_jetpack_fuel = player_data.get('max_jetpack_fuel', 100)
                
            if hasattr(player, 'flashlight_active'):
                player.flashlight_active = player_data.get('flashlight_active', False)
                
            if hasattr(player, 'scanner_active'):
                player.scanner_active = player_data.get('scanner_active', False)
                
            # Apply power-ups
            if hasattr(player, 'active_powerups'):
                player.active_powerups = player_data.get('active_powerups', {})
                
            # Apply reserve ammo
            if hasattr(player, 'reserve_ammo'):
                player.reserve_ammo = player_data.get('reserve_ammo', {})
                
            # Apply weapons
            player.current_weapon_index = player_data.get('current_weapon_index', 0)
            
            # Restore weapon ammo
            weapons_data = player_data.get('weapons', [])
            for i, weapon_data in enumerate(weapons_data):
                if i < len(player.weapons):
                    player.weapons[i].current_ammo = weapon_data['current_ammo']
                    
            # Apply level state
            level_data = game_state['level']
            
            # Clear and rebuild tiles
            level.tiles.clear()
            tiles_data = level_data.get('tiles', {})
            
            for pos_str, tile_data in tiles_data.items():
                x, y = map(int, pos_str.split(','))
                level.set_tile(x, y, tile_data['type'])
                
            # Restore collectibles
            level.collectibles = level_data.get('collectibles', [])
            
            # Restore secrets
            level.secrets = level_data.get('secrets', [])
            
            # Create enemies from save data
            from ..entities.enemy import MutantEnemy, RobotEnemy, MercenaryEnemy
            from ..entities.enemy_standard import EnemyStandard
            
            enemies = []
            enemies_data = game_state.get('enemies', [])
            
            for enemy_data in enemies_data:
                enemy_type = enemy_data['type']
                x, y = enemy_data['x'], enemy_data['y']
                
                if enemy_type == 'EnemyStandard':
                    enemy = EnemyStandard(x, y, asset_manager)
                elif enemy_type == 'MutantEnemy':
                    enemy = MutantEnemy(x, y, asset_manager)
                elif enemy_type == 'RobotEnemy':
                    enemy = RobotEnemy(x, y, asset_manager)
                elif enemy_type == 'MercenaryEnemy':
                    enemy = MercenaryEnemy(x, y, asset_manager)
                else:
                    continue
                    
                enemy.health = enemy_data['health']
                enemy.max_health = enemy_data['max_health']
                enemy.state = enemy_data.get('state', 'patrol')
                
                enemies.append(enemy)
                
            return {
                'current_level': game_state['current_level'],
                'playtime': game_state['playtime'],
                'enemies': enemies,
                'settings': game_state.get('settings', {})
            }
            
        except Exception as e:
            print(f"Error applying game state: {e}")
            return None
            
    def quick_save(self, game_state: Dict[str, Any]) -> bool:
        """Quick save to slot 0 (auto-save)"""
        return self.save_game(0, game_state)
        
    def quick_load(self) -> Optional[Dict[str, Any]]:
        """Quick load from slot 0 (auto-save)"""
        return self.load_game(0)
        
    def auto_save(self, game_state: Dict[str, Any]):
        """Automatic save (called periodically)"""
        # Save to auto-save slot
        self.save_game(0, game_state)
        
    def export_save(self, slot: int, export_path: str) -> bool:
        """Export save to external file"""
        try:
            save_data = self.load_game(slot)
            if not save_data:
                return False
                
            with open(export_path, 'w') as f:
                json.dump(save_data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error exporting save: {e}")
            return False
            
    def import_save(self, slot: int, import_path: str) -> bool:
        """Import save from external file"""
        try:
            with open(import_path, 'r') as f:
                save_data = json.load(f)
                
            return self.save_game(slot, save_data)
            
        except Exception as e:
            print(f"Error importing save: {e}")
            return False
            
    def get_save_statistics(self) -> Dict[str, Any]:
        """Get statistics about save files"""
        stats = {
            'total_saves': 0,
            'total_size': 0,
            'oldest_save': None,
            'newest_save': None
        }
        
        try:
            for slot in range(self.save_slots + 1):  # Include auto-save
                save_file = os.path.join(self.save_directory, f"save_slot_{slot}.json")
                
                if os.path.exists(save_file):
                    stats['total_saves'] += 1
                    
                    # Get file size
                    file_size = os.path.getsize(save_file)
                    stats['total_size'] += file_size
                    
                    # Get modification time
                    mod_time = os.path.getmtime(save_file)
                    
                    if stats['oldest_save'] is None or mod_time < stats['oldest_save']:
                        stats['oldest_save'] = mod_time
                        
                    if stats['newest_save'] is None or mod_time > stats['newest_save']:
                        stats['newest_save'] = mod_time
                        
        except Exception as e:
            print(f"Error getting save statistics: {e}")
            
        return stats