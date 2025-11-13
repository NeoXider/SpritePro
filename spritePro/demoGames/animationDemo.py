import pygame
import math
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

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

    count = 60
    for i in range(count):  # кадров для плавного вращения
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        angle = i * 360 / count  # градусов между кадрами
        # Рисуем стрелку
        pygame.draw.line(frame, (255, 255, 255), (50, 50), 
                        (50 + 40 * math.cos(math.radians(angle)),
                         50 + 40 * math.sin(math.radians(angle))), 3)
        frames.append(frame)
    
    # Создание анимации
    animation = Animation(
        sprite,
        frames=frames,
        frame_duration=0.01,  # 0.01 секунды = 10 мс на кадр
        loop=True
    )
    
    # Запуск анимации
    animation.play()
    
    # Шрифт для инструкций
    font = pygame.font.Font(None, 36)
    instructions = [
        "Простая анимация:",
        "Вращающаяся стрелка",
        "ESC - выход"
    ]
    
    # Основной цикл
    running = True
    while running:
        spritePro.update()
        
        for event in spritePro.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
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