import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pygame
from spritePro import PhysicalSprite

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
FONT_LABEL = pygame.font.Font(None, 72)
FPS = 60
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

STATE_GAME = 0
STATE_WIN_LEFT = 1
STATE_WIN_RIGHT = 2

current_state = STATE_GAME


def render_game():
    SCREEN.blit(bg, (0, 0))

def create_music():
    pygame.mixer.music.load("Audio/fon_musik.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)



pygame.display.set_caption("pin pong")
bg = pygame.transform.scale(pygame.image.load("Sprites/bg.jpg"), (WIDTH, HEIGHT))

create_music()

planes = pygame.sprite.Group()

physic = PhysicalSprite("Sprites/ball.png", (50, 50), (400, 290), 2)
plane = PhysicalSprite("Sprites/platforma.png", (120, 50), (400, 500), 6, gravity=0)
planes.add(plane)
plane1 = PhysicalSprite("Sprites/platforma.png", (120, 50), (500, 350), 6, gravity=0)
planes.add(plane1)

physic.jump_force = 8

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    render_game()

    physic.handle_keyboard_input()
    physic.update_physics(FPS)
    physic.resolve_collisions(planes)
    physic.limit_movement(SCREEN.get_rect())

    planes.update(SCREEN)
    physic.update(SCREEN)



    pygame.display.update()
    CLOCK.tick(FPS)
