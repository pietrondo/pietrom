#!/usr/bin/env python3
"""
Audio Manager
Manages sound effects and music for retro gaming experience

Developed by Team PIETRO
PIETRO's audio system delivers epic soundscapes!
"""

import pygame
import random
import math
from typing import Dict, List, Optional, Tuple
from ...core.config import Config

class AudioManager:
    """Manages all game audio including SFX and music"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Audio storage
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        
        # Audio state
        self.master_volume = Config.MASTER_VOLUME
        self.sfx_volume = Config.SFX_VOLUME
        self.music_volume = Config.MUSIC_VOLUME
        self.current_music = None
        self.music_paused = False
        
        # Sound channels for better management
        self.weapon_channel = pygame.mixer.Channel(0)
        self.player_channel = pygame.mixer.Channel(1)
        self.enemy_channel = pygame.mixer.Channel(2)
        self.ambient_channel = pygame.mixer.Channel(3)
        
        # Generate placeholder sounds
        self._generate_placeholder_sounds()
        
    def _generate_placeholder_sounds(self):
        """Generate placeholder chiptune-style sounds"""
        sample_rate = 22050
        
        # Weapon sounds
        self.sounds['pistol_fire'] = self._generate_gunshot(sample_rate, 0.1, 800, 200)
        self.sounds['shotgun_fire'] = self._generate_gunshot(sample_rate, 0.2, 400, 100)
        self.sounds['rocket_fire'] = self._generate_explosion(sample_rate, 0.3, 200, 50)
        self.sounds['reload'] = self._generate_mechanical(sample_rate, 0.5, 600)
        
        # Player sounds
        self.sounds['jump'] = self._generate_jump(sample_rate, 0.2, 400)
        self.sounds['land'] = self._generate_thud(sample_rate, 0.1, 200)
        self.sounds['footstep'] = self._generate_footstep(sample_rate, 0.05, 300)
        self.sounds['hurt'] = self._generate_hurt(sample_rate, 0.3, 600)
        self.sounds['death'] = self._generate_death(sample_rate, 1.0, 400)
        
        # Enemy sounds
        self.sounds['enemy_hurt'] = self._generate_enemy_hurt(sample_rate, 0.2, 500)
        self.sounds['enemy_death'] = self._generate_enemy_death(sample_rate, 0.5, 300)
        self.sounds['enemy_attack'] = self._generate_enemy_attack(sample_rate, 0.3, 700)
        
        # Collectible sounds
        self.sounds['pickup_health'] = self._generate_pickup(sample_rate, 0.2, 800, 1200)
        self.sounds['pickup_ammo'] = self._generate_pickup(sample_rate, 0.2, 600, 900)
        self.sounds['pickup_powerup'] = self._generate_powerup(sample_rate, 0.4, 1000)
        
        # UI sounds
        self.sounds['menu_select'] = self._generate_beep(sample_rate, 0.1, 800)
        self.sounds['menu_confirm'] = self._generate_beep(sample_rate, 0.2, 1000)
        self.sounds['menu_back'] = self._generate_beep(sample_rate, 0.1, 600)
        
        # Ambient sounds
        self.sounds['explosion'] = self._generate_explosion(sample_rate, 0.5, 150, 30)
        self.sounds['door_open'] = self._generate_mechanical(sample_rate, 0.3, 400)
        self.sounds['switch'] = self._generate_beep(sample_rate, 0.1, 1200)
        
    def _generate_wave(self, sample_rate: int, duration: float, frequency: float, 
                      wave_type: str = 'square') -> List[float]:
        """Generate basic waveform"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            
            if wave_type == 'square':
                value = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif wave_type == 'sawtooth':
                value = 2.0 * (t * frequency - math.floor(t * frequency + 0.5))
            elif wave_type == 'triangle':
                value = 2.0 * abs(2.0 * (t * frequency - math.floor(t * frequency + 0.5))) - 1.0
            else:  # sine
                value = math.sin(2 * math.pi * frequency * t)
                
            # Apply envelope
            envelope = self._apply_envelope(i, samples, 'adsr')
            wave.append(value * envelope)
            
        return wave
        
    def _apply_envelope(self, sample: int, total_samples: int, envelope_type: str = 'linear') -> float:
        """Apply envelope to sound"""
        progress = sample / total_samples
        
        if envelope_type == 'linear':
            return 1.0 - progress
        elif envelope_type == 'adsr':
            if progress < 0.1:  # Attack
                return progress / 0.1
            elif progress < 0.3:  # Decay
                return 1.0 - (progress - 0.1) * 0.3 / 0.2
            elif progress < 0.7:  # Sustain
                return 0.7
            else:  # Release
                return 0.7 * (1.0 - (progress - 0.7) / 0.3)
        else:
            return 1.0
            
    def _generate_gunshot(self, sample_rate: int, duration: float, 
                         start_freq: float, end_freq: float) -> pygame.mixer.Sound:
        """Generate gunshot sound effect"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Frequency sweep
            freq = start_freq + (end_freq - start_freq) * progress
            
            # Mix noise and tone
            noise = random.uniform(-1, 1) * 0.7
            tone = math.sin(2 * math.pi * freq * t) * 0.3
            
            # Apply sharp envelope
            envelope = math.exp(-progress * 8)
            value = (noise + tone) * envelope
            
            wave.append(int(value * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_explosion(self, sample_rate: int, duration: float, 
                           start_freq: float, end_freq: float) -> pygame.mixer.Sound:
        """Generate explosion sound effect"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Heavy noise with low frequency rumble
            noise = random.uniform(-1, 1) * 0.8
            rumble = math.sin(2 * math.pi * (start_freq + end_freq * progress) * t) * 0.4
            
            # Apply explosion envelope
            envelope = math.exp(-progress * 3) * (1 + math.sin(progress * 20) * 0.2)
            value = (noise + rumble) * envelope
            
            wave.append(int(value * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_jump(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate jump sound effect"""
        wave = self._generate_wave(sample_rate, duration, frequency, 'square')
        
        # Add frequency sweep up
        samples = len(wave)
        for i in range(samples):
            progress = i / samples
            freq_mult = 1.0 + progress * 0.5
            t = float(i) / sample_rate
            wave[i] = math.sin(2 * math.pi * frequency * freq_mult * t) * (1.0 - progress)
            
        wave_int = [int(sample * 32767) for sample in wave]
        return pygame.sndarray.make_sound(pygame.array.array('h', wave_int))
        
    def _generate_hurt(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate hurt sound effect"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Distorted descending tone
            freq = frequency * (1.0 - progress * 0.7)
            value = math.sin(2 * math.pi * freq * t)
            
            # Add distortion
            if value > 0.3:
                value = 0.3
            elif value < -0.3:
                value = -0.3
                
            # Apply envelope
            envelope = math.exp(-progress * 5)
            wave.append(int(value * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_pickup(self, sample_rate: int, duration: float, 
                        start_freq: float, end_freq: float) -> pygame.mixer.Sound:
        """Generate pickup sound effect"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Ascending tone
            freq = start_freq + (end_freq - start_freq) * progress
            value = math.sin(2 * math.pi * freq * t)
            
            # Apply bell-like envelope
            envelope = math.sin(progress * math.pi)
            wave.append(int(value * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_beep(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate simple beep sound"""
        wave = self._generate_wave(sample_rate, duration, frequency, 'square')
        wave_int = [int(sample * 32767 * 0.3) for sample in wave]
        return pygame.sndarray.make_sound(pygame.array.array('h', wave_int))
        
    def _generate_mechanical(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate mechanical sound (reload, door, etc.)"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Mix of noise and metallic tones
            noise = random.uniform(-0.3, 0.3)
            tone1 = math.sin(2 * math.pi * frequency * t) * 0.2
            tone2 = math.sin(2 * math.pi * frequency * 1.5 * t) * 0.1
            
            value = noise + tone1 + tone2
            envelope = 1.0 - progress * 0.5
            
            wave.append(int(value * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_footstep(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate footstep sound"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            # Short burst of noise
            noise = random.uniform(-1, 1) * 0.5
            envelope = math.exp(-i / samples * 10)
            wave.append(int(noise * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_thud(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate thud/landing sound"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Low frequency thump
            thump = math.sin(2 * math.pi * frequency * t) * 0.7
            noise = random.uniform(-0.2, 0.2)
            
            envelope = math.exp(-progress * 8)
            value = (thump + noise) * envelope
            
            wave.append(int(value * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_death(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate death sound"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Descending dramatic tone
            freq = frequency * (1.0 - progress * 0.8)
            value = math.sin(2 * math.pi * freq * t)
            
            # Add harmonics
            value += math.sin(2 * math.pi * freq * 0.5 * t) * 0.3
            
            # Apply dramatic envelope
            envelope = (1.0 - progress) * math.sin(progress * math.pi * 2)
            wave.append(int(value * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def _generate_enemy_hurt(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate enemy hurt sound"""
        return self._generate_hurt(sample_rate, duration, frequency * 0.8)
        
    def _generate_enemy_death(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate enemy death sound"""
        return self._generate_death(sample_rate, duration, frequency * 0.6)
        
    def _generate_enemy_attack(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate enemy attack sound"""
        return self._generate_gunshot(sample_rate, duration, frequency, frequency * 0.5)
        
    def _generate_powerup(self, sample_rate: int, duration: float, frequency: float) -> pygame.mixer.Sound:
        """Generate powerup sound"""
        samples = int(sample_rate * duration)
        wave = []
        
        for i in range(samples):
            t = float(i) / sample_rate
            progress = i / samples
            
            # Ascending arpeggio
            freq_mult = 1.0 + progress * 2.0
            value = math.sin(2 * math.pi * frequency * freq_mult * t)
            
            # Add sparkle effect
            sparkle = math.sin(2 * math.pi * frequency * 4 * t) * 0.3 * math.sin(progress * math.pi * 8)
            
            envelope = math.sin(progress * math.pi)
            wave.append(int((value + sparkle) * envelope * 32767))
            
        return pygame.sndarray.make_sound(pygame.array.array('h', wave))
        
    def play_sound(self, sound_name: str, volume: float = 1.0, channel: Optional[pygame.mixer.Channel] = None):
        """Play a sound effect"""
        if sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        final_volume = volume * self.sfx_volume * self.master_volume
        sound.set_volume(final_volume)
        
        if channel:
            channel.play(sound)
        else:
            pygame.mixer.Sound.play(sound)
            
    def play_weapon_sound(self, weapon_type: str):
        """Play weapon-specific sound"""
        sound_map = {
            'PISTOL': 'pistol_fire',
            'SHOTGUN': 'shotgun_fire',
            'ROCKET_LAUNCHER': 'rocket_fire'
        }
        
        sound_name = sound_map.get(weapon_type, 'pistol_fire')
        self.play_sound(sound_name, channel=self.weapon_channel)
        
    def play_player_sound(self, action: str):
        """Play player action sound"""
        sound_map = {
            'jump': 'jump',
            'land': 'land',
            'hurt': 'hurt',
            'death': 'death',
            'footstep': 'footstep'
        }
        
        sound_name = sound_map.get(action)
        if sound_name:
            self.play_sound(sound_name, channel=self.player_channel)
            
    def play_enemy_sound(self, action: str):
        """Play enemy action sound"""
        sound_map = {
            'hurt': 'enemy_hurt',
            'death': 'enemy_death',
            'attack': 'enemy_attack'
        }
        
        sound_name = sound_map.get(action)
        if sound_name:
            self.play_sound(sound_name, channel=self.enemy_channel)
            
    def play_ui_sound(self, action: str):
        """Play UI sound"""
        sound_map = {
            'select': 'menu_select',
            'confirm': 'menu_confirm',
            'back': 'menu_back'
        }
        
        sound_name = sound_map.get(action)
        if sound_name:
            self.play_sound(sound_name)
            
    def play_pickup_sound(self, item_type: str):
        """Play pickup sound based on item type"""
        sound_map = {
            'health_pack': 'pickup_health',
            'ammo': 'pickup_ammo',
            'powerup': 'pickup_powerup'
        }
        
        sound_name = sound_map.get(item_type, 'pickup_ammo')
        self.play_sound(sound_name)
        
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
        
    def play_music(self, track_name: str, loops: int = -1):
        """Play background music"""
        # For now, we'll use a simple tone generator for background music
        # In a full implementation, you would load actual music files
        self.current_music = track_name
        
    def stop_music(self):
        """Stop background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def pause_music(self):
        """Pause background music"""
        pygame.mixer.music.pause()
        self.music_paused = True
        
    def resume_music(self):
        """Resume background music"""
        pygame.mixer.music.unpause()
        self.music_paused = False
        
    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()