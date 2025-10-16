import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
#====================================================
path = Path(__file__).parent

import spritePro as s
import pygame


s.init()

s.get_screen((1280, 960))

bg = s.Sprite("spritePro\demoGames\Sprites\map.jpg")
bg.set_native_size()
player = s.Sprite("spritePro\demoGames\Sprites\\amogus.png")
player.set_native_size()
player.set_position((400,300))
player.set_scale(0.07)
player.speed = 5

text_cord = s.TextSprite("", 46)
text_cord.set_position((s.WH_C.x, 10), s.Anchor.MID_TOP)
text_cord.set_screen_space(True)

t1 = s.Sprite("", (50,50), (810, 610))
t1.set_alpha(50)
t1.set_color((0,0,255))

t2 = s.Sprite("", (50,50), (332, 295))
t2.set_alpha(50)
t2.set_color((255,0,0))

k_space = False

# Main game loop
while True:
    for e in s.events:
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                k_space = True
                print("Пробел нажат")
            else:
                k_space = False
                

    s.update(fill_color=(0,0,0))
    player.handle_keyboard_input()
    s.set_camera_follow(player)
    text_cord.text = f"player cord: x:{player.rect.centerx}, y:{player.rect.centery}"

    if k_space:
        if t1.rect.colliderect(player.rect):
            player.set_position(t2.rect.center)
        elif t2.rect.colliderect(player.rect):
            player.set_position(t1.rect.center)

        k_space = False


    