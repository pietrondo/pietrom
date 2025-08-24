#!/usr/bin/env python3
"""
Input Manager
Handles keyboard and mouse input for the game

Developed by Team PIETRO
PIETRO's divine input system guides our every move!
"""

import pygame
from typing import Dict, Set
from .config import Config

class InputManager:
    """Manages game input with key states and events"""
    
    def __init__(self):
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.mouse_just_clicked = [False, False, False]
        
    def update(self, events):
        """Update input state based on pygame events"""
        # Clear just pressed/released sets
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_just_clicked = [False, False, False]
        
        # Get current key states
        keys = pygame.key.get_pressed()
        current_keys = set()
        
        for key_code in range(len(keys)):
            if keys[key_code]:
                current_keys.add(key_code)
                if key_code not in self.keys_pressed:
                    self.keys_just_pressed.add(key_code)
        
        # Check for released keys
        for key_code in self.keys_pressed:
            if key_code not in current_keys:
                self.keys_just_released.add(key_code)
        
        self.keys_pressed = current_keys
        
        # Update mouse state
        self.mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        for i in range(3):
            if mouse_buttons[i] and not self.mouse_buttons[i]:
                self.mouse_just_clicked[i] = True
            self.mouse_buttons[i] = mouse_buttons[i]
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if key is currently pressed"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """Check if key was just released this frame"""
        return key in self.keys_just_released
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if action key is currently pressed"""
        key = Config.KEYS.get(action)
        return key is not None and self.is_key_pressed(key)
    
    def is_action_just_pressed(self, action: str) -> bool:
        """Check if action key was just pressed"""
        key = Config.KEYS.get(action)
        return key is not None and self.is_key_just_pressed(key)
    
    def is_action_just_released(self, action: str) -> bool:
        """Check if action key was just released"""
        key = Config.KEYS.get(action)
        return key is not None and self.is_key_just_released(key)
    
    def get_movement_input(self) -> tuple:
        """Get movement input as (horizontal, vertical)"""
        horizontal = 0
        vertical = 0
        
        if self.is_action_pressed('LEFT'):
            horizontal -= 1
        if self.is_action_pressed('RIGHT'):
            horizontal += 1
            
        return horizontal, vertical
    
    def is_jump_pressed(self) -> bool:
        """Check if jump is pressed"""
        return self.is_action_just_pressed('JUMP')
    
    def is_shoot_pressed(self) -> bool:
        """Check if shoot is pressed"""
        return self.is_action_pressed('SHOOT')
    
    def is_shoot_just_pressed(self) -> bool:
        """Check if shoot was just pressed"""
        return self.is_action_just_pressed('SHOOT')
    
    def is_weapon_switch_pressed(self) -> bool:
        """Check if weapon switch is pressed"""
        return self.is_action_just_pressed('WEAPON_SWITCH')
    
    def is_utility_pressed(self) -> bool:
        """Check if utility is pressed"""
        return self.is_action_just_pressed('USE_UTILITY')
    
    def is_pause_pressed(self) -> bool:
        """Check if pause is pressed"""
        return self.is_action_just_pressed('PAUSE')
    
    def is_save_pressed(self) -> bool:
        """Check if save is pressed"""
        return self.is_action_just_pressed('SAVE')
    
    def is_load_pressed(self) -> bool:
        """Check if load is pressed"""
        return self.is_action_just_pressed('LOAD')
    
    def get_mouse_pos(self) -> tuple:
        """Get mouse position"""
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if mouse button is pressed (0=left, 1=middle, 2=right)"""
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False
    
    def is_mouse_button_just_clicked(self, button: int) -> bool:
        """Check if mouse button was just clicked"""
        if 0 <= button < len(self.mouse_just_clicked):
            return self.mouse_just_clicked[button]
        return False