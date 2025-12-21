import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

#================================ start ===========================

import pygame
import spritePro as s

class Platform(s.Sprite):
    def __init__(self, *args, up = None, down = None, left = None, right = None):
        super().__init__(*args)
        self.up = up
        self.down = down
        self.left = left
        self.right = right

    def update(self, screen = None):
        super().update(screen)
        self.handle_keyboard_input(self.up, self.down, self.left, self.right)
