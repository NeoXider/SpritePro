import sys
from pathlib import Path
from typing import Tuple

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
path = Path(__file__).parent
# ====================================================

import pygame
import spritePro as s


def create_bar():
    return s.readySprites.BarWithBackground(
        path_sprites + "bar_bg.png",
        path_sprites + "bar_fill.png",
        (150, 30),
    )


class Hero(s.Sprite):
    def set_bar(
        self, bar: s.readySprites.BarWithBackground, pos: Tuple[int, int] = (0, -120)
    ):
        self.bar = bar
        self.bar.set_parent(self)
        self.bar.local_offset = pos
        self.bar.set_fill_size((self.bar.size[0] // 1.02, self.bar.size[1] // 1.4))
    
    def update(self, screen: pygame.Surface = None):
        self.velocity = pygame.Vector2(self.velocity.x, 0)
        super().update(screen)


path_sprites = "spritePro\\demoGames\\Sprites\\"
s.init()
screen = s.get_screen((1260, 960), "Game")

bg = s.Sprite(path_sprites + "background_game.png", s.WH, s.WH_C)
bg.set_color((150, 150, 150))

player = Hero(path_sprites + "hero.png", speed=5)
player.set_native_size()
player.set_position((s.WH_C.x, 730))
player.set_scale(0.5)
player.set_bar(create_bar())

enemy = Hero(path_sprites + "enemy.png", speed=1)
enemy.set_native_size()
enemy.set_position((s.WH_C.x+500, 730))
enemy.set_scale(0.5)
enemy.set_bar(create_bar())

while True:
    s.update(60, fill_color=(0, 0, 0))
    player.handle_keyboard_input(None, None, pygame.K_a, pygame.K_d)
    s.set_camera_follow(player, (0, -250))
    enemy.move_towards(player.get_position())
