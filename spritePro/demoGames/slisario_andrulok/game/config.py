"""Настройки игры: окно, мир, змейки, еда, боты и сетевые интервалы."""

from pathlib import Path

import pygame

GAME_ROOT = Path(__file__).resolve().parent.parent
BG_IMAGE = GAME_ROOT / "images" / "bg.jpg"

WINDOW_SIZE = (1024, 768)
FPS = 60
TITLE = "Слизарио"
FILL_COLOR = (15, 15, 25)

WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000
WORLD_RECT = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

HEAD_SIZE = 28
SEGMENT_SIZE = 22
SEGMENT_SPACING = 4
SNAKE_SPEED = 280.0
INITIAL_LENGTH = 3
# Сколько съеденной еды даёт +1 сегмент.
FOOD_PER_SEGMENT = 3
# Отступ от стен при спавне змей.
SPAWN_MARGIN = 200

FOOD_COUNT = 80
FOOD_SIZE = 10
# Еда не появляется вплотную к стенам: боты, идущие к ней, гибли бы о стену.
FOOD_MARGIN = 60
FOOD_COLORS = [
    (255, 50, 50),
    (50, 255, 50),
    (50, 50, 255),
    (255, 255, 50),
    (255, 50, 255),
    (50, 255, 255),
    (255, 150, 50),
    (150, 50, 255),
]

BOT_COUNT = 3
BOT_SPEED = 220.0
BOT_INITIAL_LENGTH = 3
BOT_AVOID_WALL_DIST = 150
BOT_RESPAWN_DELAY = 3.0

# --- Сеть (host-authoritative) ---
# Частота рассылки своей змейки каждым игроком.
SNAKE_SYNC_INTERVAL = 1.0 / 30.0
# Частота рассылки ботов хостом.
BOT_SYNC_INTERVAL = 1.0 / 20.0
# Периодический полный снапшот еды от хоста (сверка после событий).
FOOD_SNAPSHOT_INTERVAL = 0.5
# Если от игрока нет пакетов дольше этого времени — убираем его змейку.
REMOTE_TIMEOUT = 5.0
