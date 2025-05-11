import pygame
import pymunk
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from spritePro import PymunkGameSprite

path = Path(__file__).parent

pygame.init()
WIDTH, HEIGHT = 800, 600
FPS = 60
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

space = pymunk.Space()
space.gravity = (0, 900)

# Фон
bg = pygame.transform.scale(
    pygame.image.load(path / "Sprites" / "bg.jpg").convert(), (WIDTH, HEIGHT)
)

# Мячик (динамический)
ball = PymunkGameSprite(
    sprite=path / "Sprites" / "ball.png",
    pos=(400, 290),
    size=(50, 50),
    mass=1.0,
    friction=0.7,
    elasticity=0.8,
    space=space,
)
ball.setup_platformer_handlers(platform_collision_type=2)

# Платформы (статические)
platforms = []
platform1 = PymunkGameSprite(
    sprite=path / "Sprites" / "platforma.png",
    pos=(400, 500),
    size=(100, 50),
    mass=1.0,
    body_type=pymunk.Body.STATIC,
    space=space,
    collision_type=2,
)
platforms.append(platform1)
platform2 = PymunkGameSprite(
    sprite=path / "Sprites" / "platforma.png",
    pos=(500, 350),
    size=(100, 50),
    mass=1.0,
    body_type=pymunk.Body.STATIC,
    space=space,
    collision_type=2,
)
platforms.append(platform2)

sprites = pygame.sprite.Group([ball] + platforms)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    SCREEN.blit(bg, (0, 0))

    # Управление мячом с клавиатуры
    ball.handle_keyboard_input()
    ball.limit_movement(SCREEN.get_rect())

    # Физика
    space.step(1 / FPS)

    # Обновление позиций спрайтов
    sprites.update()

    # Отрисовка
    sprites.draw(SCREEN)

    pygame.display.update()
    CLOCK.tick(FPS)
