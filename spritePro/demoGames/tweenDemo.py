import pygame
import sys
from pathlib import Path
import math

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
import spritePro
from spritePro.components.tween import TweenManager, EasingType

def run_single_tween_demo(tween_manager, sprite, is_initialized):
    """Демонстрация одного твина с несколькими свойствами."""
    if not is_initialized:
        # Создаем спрайт
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (25, 25), 20)
        sprite.set_image(surface)
        
        # Добавляем твин для движения по кругу
        def update_position(angle):
            radius = 150
            angle_rad = math.radians(angle)
            x = 400 + radius * math.cos(angle_rad)
            y = 300 + radius * math.sin(angle_rad)
            sprite.rect.center = (int(x), int(y))
        
        tween_manager.add_tween(
            "rotation",
            start_value=0,
            end_value=360,
            duration=3.0,
            easing=EasingType.LINEAR,
            loop=True,
            on_update=update_position
        )
        
        # Добавляем твин для изменения цвета
        tween_manager.add_tween(
            "color",
            start_value=0,
            end_value=360,
            duration=2.0,
            easing=EasingType.SINE,
            loop=True,
            on_update=lambda x: sprite.set_color((
                int(128 + 127 * math.cos(math.radians(x))),
                int(128 + 127 * math.cos(math.radians(x + 120))),
                int(128 + 127 * math.cos(math.radians(x + 240)))
            ))
        )
        
        # Добавляем твин для масштабирования
        tween_manager.add_tween(
            "scale",
            start_value=0.5,
            end_value=1.5,
            duration=1.5,
            easing=EasingType.EASE_IN_OUT,
            loop=True,
            yoyo=True,
            on_update=lambda x: sprite.set_scale(x)
        )
        return True
    
    # Рисуем круг траектории
    pygame.draw.circle(spritePro.screen, (50, 50, 50), (400, 300), 150, 2)
    sprite.update(spritePro.screen)
    return is_initialized

def run_dual_tween_demo(tween_manager, sprites, is_initialized):
    """Демонстрация двух спрайтов с разными твинами."""
    if not is_initialized:
        sprite1, sprite2 = sprites
        
        # Создаем поверхности для спрайтов
        surface1 = pygame.Surface((50, 50), pygame.SRCALPHA)
        surface2 = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surface1, (255, 255, 255), (25, 25), 20)
        pygame.draw.circle(surface2, (255, 255, 255), (25, 25), 20)
        sprite1.set_image(surface1)
        sprite2.set_image(surface2)
        
        # Твин для первого спрайта (движение вверх-вниз)
        tween_manager.add_tween(
            "sprite1_y",
            start_value=100,
            end_value=500,
            duration=2.0,
            easing=EasingType.EASE_IN_OUT,
            loop=True,
            yoyo=True,
            on_update=lambda y, s=sprite1: setattr(s.rect, 'y', int(y))
        )
        
        # Твин для второго спрайта (движение по горизонтали)
        tween_manager.add_tween(
            "sprite2_x",
            start_value=200,
            end_value=600,
            duration=3.0,
            easing=EasingType.SINE,
            loop=True,
            on_update=lambda x, s=sprite2: setattr(s.rect, 'x', int(x))
        )
        
        # Добавляем твин для вертикального движения второго спрайта
        tween_manager.add_tween(
            "sprite2_y",
            start_value=100,
            end_value=500,
            duration=2.5,
            easing=EasingType.EASE_IN_OUT,
            loop=True,
            yoyo=True,
            on_update=lambda y, s=sprite2: setattr(s.rect, 'y', int(y))
        )
        
        # Твин для изменения цвета первого спрайта
        tween_manager.add_tween(
            "sprite1_color",
            start_value=0,
            end_value=255,
            duration=1.5,
            easing=EasingType.EASE_IN_OUT,
            loop=True,
            yoyo=True,
            on_update=lambda x, s=sprite1: s.set_color((int(x), 0, int(255 - x)))
        )
        
        # Твин для изменения цвета второго спрайта
        tween_manager.add_tween(
            "sprite2_color",
            start_value=0,
            end_value=255,
            duration=1.5,
            easing=EasingType.EASE_IN_OUT,
            loop=True,
            yoyo=True,
            on_update=lambda x, s=sprite2: s.set_color((0, int(x), int(255 - x)))
        )
        return True
    
    # Рисуем линии траектории
    pygame.draw.line(spritePro.screen, (50, 50, 50), (200, 100), (200, 500), 2)  # Для sprite1
    pygame.draw.line(spritePro.screen, (50, 50, 50), (200, 300), (600, 300), 2)  # Для sprite2
    pygame.draw.line(spritePro.screen, (50, 50, 50), (600, 100), (600, 500), 2)  # Для sprite2 вертикаль
    
    sprite1, sprite2 = sprites
    sprite1.update(spritePro.screen)
    sprite2.update(spritePro.screen)
    return is_initialized

if __name__ == "__main__":
    spritePro.init()
    screen = spritePro.get_screen((800, 600), "Tween Demo")
    
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)
    
    # Создаем тексты для демо
    demo_instructions = font.render("Press 1 for single sprite demo, 2 for dual sprite demo, ESC to exit", True, (255, 255, 255))
    instructions_pos = (screen.get_width() // 2 - demo_instructions.get_width() // 2, 10)
    
    demo1_title = title_font.render("Single Sprite Demo", True, (255, 255, 255))
    demo1_desc = font.render("Circular motion, color cycling, and scaling", True, (200, 200, 200))
    
    demo2_title = title_font.render("Dual Sprite Demo", True, (255, 255, 255))
    demo2_desc = font.render("Independent movement and color transitions", True, (200, 200, 200))
    
    current_demo = 1  # 1 для одиночного демо, 2 для двойного
    paused = False
    
    # Инициализация спрайтов и твин-менеджера
    tween_manager = TweenManager()
    single_sprite = spritePro.Sprite("", size=(50, 50), pos=(400, 300))
    sprite1 = spritePro.Sprite("", size=(50, 50), pos=(200, 300))
    sprite2 = spritePro.Sprite("", size=(50, 50), pos=(600, 300))
    
    # Флаги инициализации для каждого демо
    single_demo_initialized = False
    dual_demo_initialized = False
    
    while True:
        spritePro.update(fill_color=(0, 0, 0))
        
        # Обновляем твины
        if not paused:
            tween_manager.update(spritePro.dt)
        
        # Запускаем текущее демо
        if current_demo == 1:
            single_demo_initialized = run_single_tween_demo(tween_manager, single_sprite, single_demo_initialized)
        else:
            dual_demo_initialized = run_dual_tween_demo(tween_manager, (sprite1, sprite2), dual_demo_initialized)
        
        # Отображаем общие инструкции
        spritePro.screen.blit(demo_instructions, instructions_pos)
        
        # Отображаем информацию о текущем демо
        if current_demo == 1:
            spritePro.screen.blit(demo1_title, (20, 50))
            spritePro.screen.blit(demo1_desc, (20, 90))
        else:
            spritePro.screen.blit(demo2_title, (20, 50))
            spritePro.screen.blit(demo2_desc, (20, 90))
        
        for event in spritePro.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_demo = 1
                    tween_manager = TweenManager()  # Сбрасываем твин-менеджер при смене демо
                    single_demo_initialized = False  # Сбрасываем флаг инициализации
                elif event.key == pygame.K_2:
                    current_demo = 2
                    tween_manager = TweenManager()  # Сбрасываем твин-менеджер при смене демо
                    dual_demo_initialized = False  # Сбрасываем флаг инициализации
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        tween_manager.pause_all()
                    else:
                        tween_manager.resume_all()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit() 