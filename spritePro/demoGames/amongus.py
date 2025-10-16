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


def on_click():
    global k_space
    k_space = True

def on_canistra():
    global cacanistra_count
    cacanistra_count+=1
    print(cacanistra_count)
    canistra_bar.set_image("", (400, cacanistra_count/canistra_max*400))
    if cacanistra_count >= canistra_max+1:
        canistra_bg.set_active(False)
        canistra_bar.set_active(False)

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

canistra = s.Sprite("", (50,50), (-35, 580))
canistra.set_alpha(50)


btn_interactive = s.Button("", (200,200), (950,750), "Взаимодействовать!", base_color= (255,100,100), on_click=on_click)
circle = s.utils.round_corners(btn_interactive.image, 500)
btn_interactive.set_image(circle)
btn_interactive.text_sprite.set_screen_space(True)
btn_interactive.set_screen_space(True)

interacts = [t1,t2,canistra]

canistra_bg = s.Button("", (400, 400), s.WH_C, "", on_click=on_canistra, base_color=(0,0,0))
canistra_bar = s.Sprite("", (400, 0), s.WH_C)
cacanistra_count = 0
canistra_max = 5
canistra_bg.set_screen_space(True)
canistra_bar.set_screen_space(True)
canistra_bar.set_sorting_order(1010)
canistra_bar.set_color((255,255,0))
canistra_bar.set_position(canistra_bg.rect.bottomleft, s.Anchor.BOTTOM_LEFT)
canistra_bg.set_active(False)
canistra_bar.set_active(False)

k_space = False

# Main game loop
while True:
    k_space = False
    
    # for e in s.events:
    #     if e.type == pygame.KEYDOWN:
    #         if e.key == pygame.K_SPACE:
    #             k_space = True
    #             print("Пробел нажат")
    #         else:
    #             k_space = False


    s.update(fill_color=(0,0,0))
    player.handle_keyboard_input()
    s.set_camera_follow(player)
    text_cord.text = f"player cord: x:{player.rect.centerx}, y:{player.rect.centery}"

    if k_space:
        if t1.rect.colliderect(player.rect):
            player.set_position(t2.rect.center)
        elif t2.rect.colliderect(player.rect):
            player.set_position(t1.rect.center)
        elif canistra.rect.colliderect(player.rect):
            canistra_bg.set_active(True)
            canistra_bar.set_active(True)
        k_space = False

    colide = False
    for i in interacts:
        if i.rect.colliderect(player.rect):
            colide = True
            break

    btn_interactive.set_active(colide)