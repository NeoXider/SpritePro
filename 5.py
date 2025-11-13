from pygame import *

#создай окно игры
window = display.set_mode((700,500))

display.set_caption('Догонялки')

background = transform.scale(image.load('spritePro/demoGames/Sprites/bg.jpg'),(700,500))

sprite1 = transform.scale(image.load('spritePro/demoGames/Sprites/c.png'),(100,100))

sprite2 = transform.scale(image.load('spritePro/demoGames/Sprites/c.png'),(100,100))

is_game = True

clock = time.Clock()

FPS = 60


pos1 = Vector2(0,0)

pos2 = Vector2(150,0)

while is_game :
    display.update()
    clock.tick(FPS)
    window.blit(background,(0,0))
    window.blit(sprite1,(pos1))
    window.blit(sprite2,(pos2))
    for e in event.get():
        if e.type == QUIT:
            is_game = False
    key_pressed = key.get_pressed()

    if key_pressed[K_UP]:
        pos1.y -= 10
        print(pos1)

