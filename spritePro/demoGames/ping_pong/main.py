import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

#================================ start ===========================

import pygame
import spritePro as s
from game import Game

s.get_screen()
game = Game()

while True:
    s.update()
    game.update()
    
