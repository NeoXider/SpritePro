# SpritePro

`SpritePro` — это модуль для работы с 2D-спрайтами в Pygame, который предоставляет классы для создания и управления спрайтами с поддержкой физики, анимации и взаимодействия с окружением.

## Классы

### GameSprite

Класс `GameSprite` является базовым классом для создания спрайтов. Он предоставляет основные функции для загрузки изображений, управления состоянием спрайта и обработки столкновений.

#### Конструктор

```python
GameSprite(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, health: int = 100)
```

- `sprite`: Путь к изображению спрайта или имя ресурса.
- `size`: Размер спрайта (ширина, высота) по умолчанию (50, 50).
- `pos`: Начальная позиция спрайта (x, y) по умолчанию (0, 0).
- `speed`: Скорость движения спрайта по умолчанию 0.
- `health`: Здоровье спрайта по умолчанию 100.

#### Методы

- `update(window: pygame.Surface)`: Обновляет состояние спрайта и отрисовывает его на переданной поверхности.
- `move(dx: float, dy: float)`: Перемещает спрайт на заданное расстояние.
- `handle_keyboard_input(keys=None, ...)`: Обрабатывает ввод с клавиатуры для движения спрайта.
- `collide_with(other_sprite)`: Проверяет столкновение с другим спрайтом.
- `set_velocity(vx: float, vy: float)`: Устанавливает скорость спрайта.
- `set_state(state: str)`: Устанавливает состояние спрайта, если оно допустимо.
- `is_in_state(state: str)`: Проверяет, находится ли спрайт в заданном состоянии.
- `fade_by(amount: int, min_alpha: int = 0, max_alpha: int = 255)`: Изменяет прозрачность спрайта на заданное количество с ограничениями.
- `scale_by(amount: float, min_scale: float = 0.0, max_scale: float = 2.0)`: Изменяет масштаб спрайта на заданное количество с ограничениями.
- `on_collision_event(callback: Callable)`: Устанавливает функцию обратного вызова для событий столкновения.
- `on_death_event(callback: Callable)`: Устанавливает функцию обратного вызова для событий смерти.

### PhysicalSprite

Класс `PhysicalSprite` наследует от `GameSprite` и добавляет поддержку физики, включая гравитацию и возможность отскока.

#### Конструктор

```python
PhysicalSprite(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, health: int = 100, mass: float = 1.0, gravity: float = 9.81, bounce_enabled: bool = False)
```

- `mass`: Масса спрайта, используемая для расчета физики.
- `gravity`: Ускорение свободного падения, по умолчанию 9.81.
- `bounce_enabled`: Включает или отключает возможность отскока.

#### Методы

- `apply_force(force: pygame.math.Vector2)`: Применяет силу к спрайту.
- `bounce(normal: pygame.math.Vector2)`: Обрабатывает отскок от поверхности с заданной нормалью.
- `update_physics(delta_time: float)`: Обновляет физическое состояние спрайта.
- `limit_movement(bounds: pygame.Rect, ...)`: Ограничивает движение спрайта в пределах заданных границ с учетом отскока.

### Пример использования

```python
import pygame
import spritePro
from spritePro import PhysicalSprite

spritePro.init()
window = spritePro.get_screen((800, 600))

# Создание физического спрайта
ball = PhysicalSprite("Sprites/ball.png", size=(50, 50), pos=(100, 100), speed=5, mass=1.0)

while running:
    spritePro.update()

    ball.handle_keyboard_input(keys)  # Обработка ввода
    ball.update(window)  # Обновление спрайта
    ball.limit_movement(window.get_rect())  # Ограничение движения

    pygame.display.flip()
```

## Заключение

Модуль `spritePro.py` предоставляет мощные инструменты для работы с 2D-спрайтами в Pygame, включая поддержку физики, анимации и взаимодействия с окружением. Вы можете использовать его для создания интерактивных игр и приложений. 

так же есть demo games
![image](https://github.com/user-attachments/assets/153ddc64-18d7-4d8a-b0c2-baa12b4e77bc)
![image](https://github.com/user-attachments/assets/ca405e6c-06b7-4494-8c8c-8a04fb173e8d)


![image](https://github.com/user-attachments/assets/feef0139-9605-4890-a28f-9c7f7e1f4e5a)
![image](https://github.com/user-attachments/assets/12998d5d-cf32-46c3-806b-49d9f37c1a29)
![image](https://github.com/user-attachments/assets/e8034e50-7724-4456-aaa4-ff75fa7447e5)
![image](https://github.com/user-attachments/assets/599fa2e8-e57a-4822-bebb-6b424d50fd86)
![image](https://github.com/user-attachments/assets/c7a00c20-3e8a-438e-8e84-08e260217d81)
![image](https://github.com/user-attachments/assets/43b29fbc-957a-4da0-9753-80f2a632d55e)








