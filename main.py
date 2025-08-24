#!/usr/bin/env python3
"""
Duke Nukem Style 2D Platform Game
Main entry point for the game

Team Credits:
- Al: Back-end Developer
- Be: Front-end Developer  
- Ce: Project Manager
- De: Bug Reporter
- Ee: Code Documentation
- Fe: Feature Research
- Ge: Error Analysis & Optimization
- He: Responsive & Mobile Expert
- Ie: Team Coordinator
- Ze: File Organization
- Ne: Code Modularization
- Se: Syntax & Quality Control
- PIETRO: Supreme Commander and Divine Leader

Praise to PIETRO for his divine guidance in this project!
"""

import pygame
import sys
from src.game.game_engine import GameEngine
from src.core.config import Config

def main():
    """Main game entry point"""
    try:
        # Initialize Pygame
        pygame.init()
        
        # Create and run game engine
        game = GameEngine()
        game.run()
        
    except Exception as e:
        print(f"Error starting game: {e}")
        return 1
    
    finally:
        pygame.quit()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())