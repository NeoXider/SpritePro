import pygame
import spritePro as s
s.init()
s.get_screen((1260, 920))
player = s.Sprite("", (200,200), (300,500), 5, 2)
enemy = s.Sprite("", (200,200), (800,500), 2)
enemy.set_color((255,100,100))
btn = s.Button("", (300,300), s.WH_C)

#player.set_sorting_order(1)

while True:
    s.update(fill_color=(150,150,255))
    player.handle_keyboard_input()
    player.rotate_by(5)
    enemy.move_towards(player.rect.center)