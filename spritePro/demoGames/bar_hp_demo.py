"""
Bar HP Demo - Демонстрация HP бара с BarWithBackground

Демонстрация полосы здоровья с темно-красным фоном и красным заполнением.
Показывает возможность изменения цвета через set_color.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from spritePro.readySprites import BarWithBackground
from spritePro.constants import FillDirection


def main():
    """Основная функция демо."""
    # Инициализация SpritePro
    s.init()
    screen = s.get_screen((1000, 600), "HP Bar Demo - SpritePro")
    
    # Создаем HP бар с темно-красным фоном и красным заполнением
    hp_bar = BarWithBackground(
        background_image="",  # Пустая строка - создастся по умолчанию
        fill_image="",  # Пустая строка - создастся по умолчанию
        size=(400, 50),
        pos=(500, 200),
        fill_amount=0.75,  # 75% HP
        fill_direction=FillDirection.LEFT_TO_RIGHT,
        animate_duration=0.3,
        sorting_order=1,
    )
    # Устанавливаем цвета через bg и fill свойства
    hp_bar.bg.color = (139, 0, 0)  # Темно-красный фон (DarkRed)
    hp_bar.bg.alpha = 50
    hp_bar.fill.color = (255, 0, 0)  # Красный fill
    hp_bar.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)
    
    # Создаем второй HP бар для демонстрации изменения цвета
    hp_bar2 = BarWithBackground(
        background_image="",
        fill_image="",
        size=(400, 50),
        pos=(500, 300),
        fill_amount=0.5,  # 50% HP
        fill_direction=FillDirection.LEFT_TO_RIGHT,
        animate_duration=0.3,
        sorting_order=1,
    )
    hp_bar2.bg.color = (139, 0, 0)  # Темно-красный фон
    hp_bar2.fill.color = (255, 0, 0)  # Красный fill
    hp_bar2.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)
    
    # Создаем третий HP бар с низким HP
    hp_bar3 = BarWithBackground(
        background_image="",
        fill_image="",
        size=(400, 50),
        pos=(500, 400),
        fill_amount=0.2,  # 20% HP (критический уровень)
        fill_direction=FillDirection.LEFT_TO_RIGHT,
        animate_duration=0.3,
        sorting_order=1,
    )
    hp_bar3.bg.color = (139, 0, 0)  # Темно-красный фон
    hp_bar3.fill.color = (255, 0, 0)  # Красный fill
    hp_bar3.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)
    
    # Создаем текстовые метки
    title = s.TextSprite(
        text="HP Bar Demo - Демонстрация полосы здоровья",
        pos=(500, 50),
        font_size=28,
        color=(255, 255, 255)
    )
    
    hp_label1 = s.TextSprite(
        text="HP: 75%",
        pos=(200, 200),
        font_size=20,
        color=(255, 255, 255)
    )
    
    hp_label2 = s.TextSprite(
        text="HP: 50%",
        pos=(200, 300),
        font_size=20,
        color=(255, 255, 255)
    )
    
    hp_label3 = s.TextSprite(
        text="HP: 20% (Критический)",
        pos=(200, 400),
        font_size=20,
        color=(255, 100, 100)
    )
    
    instructions = s.TextSprite(
        text="Управление:",
        pos=(500, 500),
        font_size=18,
        color=(255, 255, 255)
    )
    
    controls = [
        s.TextSprite(
            text="A/D: Уменьшить/Увеличить HP",
            pos=(500, 530),
            font_size=14,
            color=(200, 200, 200)
        ),
        s.TextSprite(
            text="C: Изменить цвет fill (красный/зеленый/синий)",
            pos=(500, 550),
            font_size=14,
            color=(200, 200, 200)
        ),
        s.TextSprite(
            text="R: Сбросить HP на 100%",
            pos=(500, 570),
            font_size=14,
            color=(200, 200, 200)
        ),
        s.TextSprite(
            text="T: Изменить прозрачность (альфа-канал)",
            pos=(500, 590),
            font_size=14,
            color=(200, 200, 200)
        ),
    ]
    
    # Состояние для изменения цвета
    color_index = 0
    colors = [
        (255, 0, 0),    # Красный
        (0, 255, 0),    # Зеленый
        (0, 0, 255),    # Синий
    ]
    color_names = ["Красный", "Зеленый", "Синий"]
    
    # Демонстрация альфа-канала - создаем полупрозрачный бар
    hp_bar_transparent = BarWithBackground(
        background_image="",
        fill_image="",
        size=(400, 50),
        pos=(500, 500),
        fill_amount=0.6,
        fill_direction=FillDirection.LEFT_TO_RIGHT,
        animate_duration=0.3,
        sorting_order=1,
    )
    # Используем RGBA для установки цвета с альфа-каналом
    hp_bar_transparent.bg.color = (139, 0, 0, 200)  # Темно-красный фон с альфа=200
    hp_bar_transparent.fill.color = (255, 0, 0, 180)  # Красный fill с альфа=180
    
    # Или можно использовать отдельное свойство alpha
    # hp_bar_transparent.fill.alpha = 180
    
    # Основной цикл
    running = True
    while running:
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    # Уменьшить HP всех баров (используем удобное свойство amount)
                    for bar in [hp_bar, hp_bar2, hp_bar3]:
                        bar.amount = max(0.0, bar.amount - 0.1)
                    
                    # Обновить метки (используем свойство amount)
                    hp_label1.text = f"HP: {int(hp_bar.amount * 100)}%"
                    hp_label2.text = f"HP: {int(hp_bar2.amount * 100)}%"
                    hp_label3.text = f"HP: {int(hp_bar3.amount * 100)}%"
                    
                elif event.key == pygame.K_d:
                    # Увеличить HP всех баров (используем удобное свойство amount)
                    for bar in [hp_bar, hp_bar2, hp_bar3]:
                        bar.amount = min(1.0, bar.amount + 0.1)
                    
                    # Обновить метки (используем свойство amount)
                    hp_label1.text = f"HP: {int(hp_bar.amount * 100)}%"
                    hp_label2.text = f"HP: {int(hp_bar2.amount * 100)}%"
                    hp_label3.text = f"HP: {int(hp_bar3.amount * 100)}%"
                    
                elif event.key == pygame.K_c:
                    # Изменить цвет fill всех баров
                    color_index = (color_index + 1) % len(colors)
                    new_color = colors[color_index]
                    
                    # Изменяем цвет fill через fill.color (удобный способ)
                    for bar in [hp_bar, hp_bar2, hp_bar3]:
                        bar.fill.color = new_color
                    
                    print(f"Цвет fill изменен на: {color_names[color_index]}")
                    
                elif event.key == pygame.K_r:
                    # Сбросить HP на 100% (используем удобное свойство amount)
                    for bar in [hp_bar, hp_bar2, hp_bar3]:
                        bar.amount = 1.0
                    
                    # Обновить метки
                    hp_label1.text = "HP: 100%"
                    hp_label2.text = "HP: 100%"
                    hp_label3.text = "HP: 100%"
                    
                elif event.key == pygame.K_t:
                    # Изменить прозрачность (альфа-канал)
                    current_alpha = hp_bar_transparent.fill.alpha
                    new_alpha = 255 if current_alpha < 128 else 128  # Переключаем между 255 и 128
                    hp_bar_transparent.fill.alpha = new_alpha
                    hp_bar_transparent.bg.alpha = new_alpha + 20  # Фон чуть более непрозрачный
                    print(f"Альфа-канал изменен на: {new_alpha}")
        
        # Обновление и отрисовка
        s.update(fps=60, update_display=True, fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()

