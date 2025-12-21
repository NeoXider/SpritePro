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
from pygame import Vector2
from random import choice
from event_bus import ball_out_screen


class Ball(s.Sprite):
    dirs = (Vector2(1, 1), Vector2(1, -1), Vector2(-1, -1), Vector2(-1, 1))

    def random_push(self):
        dir = choice(self.dirs)
        self.velocity = dir * self.speed

    def update(self, screen = None):
        super().update(screen)

        if self.rect.y < 0:
            self.velocity.y *= -1
        elif self.rect.bottom > s.WH.y:
            self.velocity.y *= -1

        if self.rect.left > s.WH.x:
            self.reset_sprite()
            ball_out_screen.send("ball", side = False)
        elif self.rect.right < 0:
            self.reset_sprite()
            ball_out_screen.send("ball", side = True)


    