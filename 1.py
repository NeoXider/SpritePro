import spritePro as s
import pygame

s.get_screen((1260, 920))
player = s.Sprite("", (200,200), (300,500), 5, 2)
enemy = s.Sprite("", (200,200), (800,500), 2)
enemy.set_color((255,100,100))
btn = s.Button("", (300,300), s.WH_C)

#player.set_sorting_order(1)

def info():
    print("info")
    timer.start(0.5)

timer = s.Timer(1,info)
timer.start()

a: pygame.sprite.Group = pygame.sprite.Group()

while True:
    s.update(fill_color=(150,150,255))
    timer.update()
    player.handle_keyboard_input()
    player.rotate_by(5)
    enemy.move_towards(player.rect.center)
    for i in a:
        i.move_up()