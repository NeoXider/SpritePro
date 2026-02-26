import pygame
import math
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro
from spritePro.components.animation import Animation


def run_animation_demo():
    """Демонстрация простой анимации с использованием Animation."""
    # Инициализация
    spritePro.init()
    screen = spritePro.get_screen((800, 600))
    clock = spritePro.clock

    # Создание спрайта
    sprite = spritePro.Sprite("", (100, 100), (400, 300))
    sprite.set_color((255, 0, 0))  # Красный цвет

    # Создание кадров анимации
    frames = []

    # Вспомогательный спрайт для генерации линии через set_polyline
    line_sprite = spritePro.Sprite("", (1, 1), (0, 0))
    line_sprite.set_active(False)

    count = 60
    for i in range(count):  # кадров для плавного вращения
        angle = i * 360 / count  # градусов между кадрами
        end_x = 50 + 40 * math.cos(math.radians(angle))
        end_y = 50 + 40 * math.sin(math.radians(angle))
        points = [(50, 50), (end_x, end_y)]

        padding = 2
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x = min(xs)
        min_y = min(ys)
        origin_x = 50 - min_x + padding
        origin_y = 50 - min_y + padding

        line_sprite.set_polyline(points, color=(255, 255, 255), width=3, padding=padding)
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        frame.blit(
            line_sprite.image,
            (int(50 - origin_x), int(50 - origin_y)),
        )
        frames.append(frame)

    line_sprite.kill()

    # Создание анимации
    animation = Animation(
        sprite,
        frames=frames,
        frame_duration=0.01,  # 0.01 секунды = 10 мс на кадр
        loop=True,
    )

    # Запуск анимации
    animation.play()

    # Шрифт для инструкций
    font = pygame.font.Font(None, 36)
    instructions = [
        "Простая анимация:",
        "Вращающаяся стрелка",
        "SPACE - пауза/продолжить",
        "ESC - выход",
    ]

    # Основной цикл
    running = True
    paused = False
    while running:
        spritePro.update()

        if spritePro.input.was_pressed(pygame.K_ESCAPE):
            running = False

        if spritePro.input.was_pressed(pygame.K_SPACE):
            paused = not paused
            if paused:
                animation.pause()
            else:
                animation.resume()

        # Обновление анимации
        animation.update()

        # Отрисовка
        screen.fill((0, 0, 0))

        # Отрисовка спрайта
        sprite.update(screen)

        # Отрисовка инструкций
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 30))


if __name__ == "__main__":
    run_animation_demo()
