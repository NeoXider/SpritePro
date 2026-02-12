# Модуль Sprite

Класс `Sprite` является основой библиотеки spritePro, предоставляя мощную базу для всех визуальных игровых объектов.

## Обзор

Класс Sprite расширяет pygame.sprite.Sprite с расширенной функциональностью для движения, визуальных эффектов и управления состоянием. Он служит базовым классом для всех других типов спрайтов в spritePro.

## Основные возможности

- **Система движения**: Движение на основе скорости с автоматической обработкой направления
- **Визуальные эффекты**: Вращение, масштабирование, прозрачность и цветовая тонировка
- **Управление состоянием**: Активные/неактивные состояния и автоматическое отражение
- **Обнаружение столкновений**: Встроенная проверка границ и вспомогательные функции для столкновений
- **Управление ресурсами**: Автоматическая загрузка изображений и работа с поверхностями

## Параметры конструктора

- `sprite` (str): Путь к изображению спрайта или имя ресурса
- `size` (tuple): Размеры спрайта (ширина, высота). По умолчанию: (50, 50)
- `pos` (tuple): Начальная позиция (x, y). По умолчанию: (0, 0)
- `speed` (float): Скорость движения в пикселях за кадр. По умолчанию: 0
- `sorting_order` (int | None): Порядок слоя отрисовки. Меньшие значения рисуются сзади, большие спереди. По умолчанию: None (естественный порядок добавления)
- `anchor` (str | Anchor): Якорь для позиционирования. По умолчанию: Anchor.CENTER

**Доступные якоря:**
- `Anchor.CENTER` - центр спрайта (по умолчанию)
- `Anchor.TOP_LEFT` - верхний левый угол
- `Anchor.TOP_RIGHT` - верхний правый угол
- `Anchor.BOTTOM_LEFT` - нижний левый угол
- `Anchor.BOTTOM_RIGHT` - нижний правый угол
- `Anchor.MID_TOP` - середина верхней стороны
- `Anchor.MID_BOTTOM` - середина нижней стороны
- `Anchor.MID_LEFT` - середина левой стороны
- `Anchor.MID_RIGHT` - середина правой стороны

**Пример использования якоря:**
```python
# Спрайт в левом верхнем углу экрана
sprite = s.Sprite("image.png", pos=(10, 10), anchor=s.Anchor.TOP_LEFT)

# Текст в правом верхнем углу
text = s.TextSprite("Score: 100", pos=(s.WH.x - 10, 10), anchor=s.Anchor.TOP_RIGHT)

# Кнопка внизу по центру
button = s.Button("", (200, 50), (s.WH_C.x, s.WH.y - 20), "Menu", anchor=s.Anchor.MID_BOTTOM)
```

## Основные методы

### Движение
- `move_towards(target_pos, speed=None, use_dt=False)`: Переместить спрайт к целевой позиции. `use_dt=True` для независимого от частоты кадров движения
- `move(dx, dy)`: Переместить спрайт на относительное смещение (с учетом `speed`)
- `move_up(speed=None)`: Переместить спрайт вверх
- `move_down(speed=None)`: Переместить спрайт вниз
- `move_left(speed=None)`: Переместить спрайт влево
- `move_right(speed=None)`: Переместить спрайт вправо
- `stop()`: Остановить все движение
- `set_velocity(vx, vy)`: Установить скорость напрямую
- `get_velocity()`: Получить текущую скорость (vx, vy)
- `handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT)`: Обработать ввод с клавиатуры для движения с настраиваемыми клавишами

**Пример:**
```python
import pygame

# ...
sprite.handle_keyboard_input(
    up_key=pygame.K_w,
    down_key=pygame.K_s,
    left_key=pygame.K_a,
    right_key=pygame.K_d
)
```

### Визуальные эффекты (через свойства)

Для управления визуальными эффектами рекомендуется использовать свойства. Это делает код более чистым и интуитивно понятным.

**Пример:**
```python
# Рекомендуемый способ:
sprite.scale = 1.5
sprite.angle = 45
sprite.alpha = 128
sprite.color = (255, 100, 100)

# Получение значений
current_scale = sprite.scale
```

Такой подход предпочтительнее, чем использование методов `set_*()` и `get_*()`.

### Примитивы (pygame.draw)

Sprite может создавать простые формы без изображений:

- `set_rect_shape(size=None, color=(255,255,255), width=0, border_radius=0)`
- `set_circle_shape(radius=None, color=(255,255,255), width=0)`
- `set_ellipse_shape(size=None, color=(255,255,255), width=0)`
- `set_polygon_shape(points, color=(255,255,255), width=0, padding=2)`
- `set_polyline(points, color=(255,255,255), width=2, closed=False, padding=2, world_points=False)`

**Пример:**
```python
box = s.Sprite("", (120, 80), (150, 150))
box.set_rect_shape(color=(120, 200, 255), border_radius=12)

ball = s.Sprite("", (80, 80), (320, 150))
ball.set_circle_shape(radius=40, color=(255, 180, 100))

line = s.Sprite("", (1, 1), (520, 360))
line.set_polyline([(0, 0), (40, 30), (80, -10), (140, 40)], color=(200, 200, 255), width=3)
```


### Управление состоянием
- `set_sorting_order(order: int)`: Изменить порядок отрисовки (меньше = сзади, больше = спереди)
- `set_active(active)`: Включить/выключить спрайт
- `set_state(state)`: Установить текущее состояние спрайта
- `is_in_state(state)`: Проверить, находится ли спрайт в конкретном состоянии
- `reset_sprite()`: Сбросить спрайт в начальную позицию и состояние

### Установка позиции с якорем

В то время как свойство `.position` всегда относится к центру спрайта, метод `set_position()` предоставляет уникальную возможность устанавливать позицию, используя якоря. Это особенно полезно для точного выравнивания UI элементов или размещения объектов относительно краев экрана.

- `set_position(position, anchor=Anchor.CENTER)`: Установить позицию спрайта, используя указанный якорь.
- `set_world_position(position, anchor=Anchor.CENTER)`: Установить мировую позицию с учетом якоря и иерархии.

**Пример:**
```python
# Поставить спрайт в правый нижний угол экрана с отступом в 10px
sprite.set_position((s.WH.x - 10, s.WH.y - 10), anchor=s.Anchor.BOTTOM_RIGHT)

# Установить мировую позицию напрямую
sprite.set_world_position((400, 300))

# С якорем (например, верхний левый)
sprite.set_world_position((10, 10), anchor=s.Anchor.TOP_LEFT)
```

### Цепочки вызовов

Методы установки и действия возвращают сам объект (`self`), поэтому их можно вызывать цепочкой.

**Sprite** — возвращают `self`:
- Установка: `set_position`, `set_scale`, `set_angle`, `rotate_to`, `set_alpha`, `set_color`, `set_sorting_order`, `look_at`, `set_screen_space`, `set_parent`, `set_world_position`, `set_image`, `set_rect_shape`, `set_circle_shape`, `set_ellipse_shape`, `set_polygon_shape`, `set_polyline`, `set_native_size`, `set_flip`, `set_active`, `set_scene`, `set_velocity`, `set_state`, `set_collision_targets`, `add_collision_target`, `add_collision_targets`, `remove_collision_target`, `remove_collision_targets`, `clear_collision_targets`, `limit_movement`.
- Движение и действие: `reset_sprite`, `move`, `move_towards`, `move_up`, `move_down`, `move_left`, `move_right`, `stop`, `rotate_by`, `fade_by`, `scale_by`, `handle_keyboard_input`.

**TextSprite**: `set_text`, `set_color`, `set_font`. **Button**: `set_base_color`, `set_all_colors`, `set_all_scales`, `set_scale`, `set_sorting_order`, `on_click`, `on_hover`. **ToggleButton**: `set_state`, `set_colors`, `set_texts`, `toggle`. **Bar**: `set_fill_amount`, `set_fill_direction`, `set_image`, `set_fill_color` и др.

```python
# Установка и стиль
sprite.set_position((100, 200)).set_scale(1.5).set_alpha(200).set_color((255, 100, 100))
sprite.set_rect_shape((80, 40), color=(200, 100, 50)).set_position((200, 300))

# Движение и границы (в цикле update)
player.handle_keyboard_input().limit_movement(screen.get_rect())

# Текст и кнопка
text.set_text("Hello").set_color((255, 0, 0)).set_font(None, 32)
btn.on_click(clicked).on_hover(hovered).set_base_color((200, 100, 100))
```

**Удобные свойства для быстрого доступа:**
```python
# Установка позиции через свойство
sprite.position = (400, 300)  # Устанавливает центральную позицию
sprite.x = 400  # Устанавливает только X координату
sprite.y = 300  # Устанавливает только Y координату

# Получение позиции
pos = sprite.position  # (x, y)
x = sprite.x  # x координата
y = sprite.y  # y координата

# Установка размера
sprite.width = 100  # Устанавливает ширину
sprite.height = 50  # Устанавливает высоту

# Получение размера
w = sprite.width  # ширина
h = sprite.height  # высота
```

## Свойства

### Основные свойства позиционирования
- `position` (tuple): Центральная позиция спрайта (x, y). Можно устанавливать напрямую: `sprite.position = (100, 200)`
- `local_position` (tuple): Локальная позиция относительно родителя. Если родителя нет, совпадает с `position`.
- `x` (int): X координата центра спрайта. Можно устанавливать: `sprite.x = 100`
- `y` (int): Y координата центра спрайта. Можно устанавливать: `sprite.y = 200`
- `width` (int): Ширина спрайта. Можно устанавливать: `sprite.width = 50`
- `height` (int): Высота спрайта. Можно устанавливать: `sprite.height = 50`
- `anchor` (Anchor): Текущий якорь позиционирования. Изменение якоря не сдвигает спрайт.

### Свойства визуальных эффектов
- `scale` (float): Коэффициент масштабирования. Можно устанавливать: `sprite.scale = 1.5`
- `angle` (float): Угол поворота в градусах. Можно устанавливать: `sprite.angle = 45`
- `alpha` (int): Прозрачность (0-255). Можно устанавливать: `sprite.alpha = 128`
- `color` (tuple | None): Текущая цветовая тонировка. `None` означает отсутствие тонировки. Можно устанавливать: `sprite.color = (255, 100, 100)`

### Поворот к цели

```python
# Поворот к позиции
sprite.look_at((400, 300))

# Поворот к другому спрайту с оффсетом
sprite.look_at(enemy, offset=-90)
```

### Свойства состояния
- `active` (bool): Активен ли спрайт и отрисовывается ли он. При изменении автоматически синхронизируется с дочерними спрайтами. Можно устанавливать: `sprite.active = False`
- `state` (str): Текущее состояние спрайта (например, "idle", "moving", "hit")
- `states` (set): Доступные состояния спрайта

### Свойства движения
- `velocity` (Vector2): Текущая скорость спрайта (vx, vy)
- `speed` (float): Базовая скорость движения в пикселях за кадр

### Свойства иерархии
- `parent` (Sprite | None): Родительский спрайт в иерархии
- `children` (List[Sprite]): Список дочерних спрайтов
- `local_offset` (Vector2): Локальное смещение относительно родителя

### Другие свойства
- `auto_flip` (bool): Автоматически отражать спрайт при движении влево/вправо. По умолчанию: True
- `stop_threshold` (float): Порог расстояния для остановки движения. По умолчанию: 1.0
- `sorting_order` (int | None): Текущий слой, используемый для порядка отрисовки
- `anchor_key` (Anchor): Текущий якорь позиционирования (внутреннее поле, используйте `anchor`)
- `screen_space` (bool): Фиксирован ли спрайт к экрану (игнорирует камеру)
- `flipped_h` (bool): Отражен ли спрайт по горизонтали
- `flipped_v` (bool): Отражен ли спрайт по вертикали

## Свойства для получения значений

Все ключевые визуальные и связанные с движением параметры доступны как свойства. Это предпочтительный способ получения их значений.

- `color`: Возвращает текущую цветовую тонировку
- `scale`: Возвращает текущий коэффициент масштабирования
- `alpha`: Возвращает текущее значение альфа-канала (0-255)
- `angle`: Возвращает текущий угол поворота в градусах
- `position`: Возвращает текущую центральную позицию (x, y)
- `size`: Возвращает текущий размер (ширина, высота)
- `velocity`: Возвращает текущую скорость (vx, vy)

## Порядок отрисовки (sorting_order)

Спрайты отрисовываются с использованием порядка на основе слоев, аналогично sortingOrder в Unity:

- Меньшие значения `sorting_order` рисуются первыми (появляются сзади)
- Большие значения рисуются позже (появляются спереди)
- Если `sorting_order` не установлен, спрайт использует свой естественный порядок вставки

Базовое использование:

```python
import spritePro as s

bg = s.Sprite("bg.png", pos=(400, 300), sorting_order=-100)   # далеко сзади
player = s.Sprite("player.png", pos=(420, 320), sorting_order=0)
ui_text = s.TextSprite("Score", pos=(780, 30), sorting_order=1000)  # UI сверху

# Изменить во время выполнения
player.set_sorting_order(10)
```

См. демо `spritePro/demoGames/sorting_order_demo.py` для интерактивного примера (стрелки Вверх/Вниз изменяют порядок).

## Продвинутые возможности

### Автоматическое отражение
```python
sprite.auto_flip = True  # Спрайт отражается при движении влево/вправо
```

### Границы движения
```python
# Ограничить движение в пределах границ
bounds = pygame.Rect(0, 0, 800, 600)
sprite.limit_movement(bounds)

# С настройками проверки границ и отступов
sprite.limit_movement(
    bounds,
    check_left=True,
    check_right=True,
    check_top=True,
    check_bottom=True,
    padding_left=10,
    padding_right=10,
    padding_top=10,
    padding_bottom=10
)
```

### Цветовые эффекты
```python
# Применить цветовую тонировку
sprite.set_color((255, 100, 100))  # Красная тонировка

# Убрать цветовую тонировку
sprite.set_color(None)
```

### Иерархия спрайтов (родитель-потомок)

SpritePro поддерживает иерархию спрайтов, где дочерние спрайты автоматически следуют за родителем:

```python
# Создать родительский спрайт
parent = s.Sprite("parent.png", pos=(400, 300))

# Создать дочерний спрайт
child = s.Sprite("child.png", pos=(400, 300))

# Прикрепить дочерний спрайт к родителю
child.set_parent(parent, keep_world_position=True)

# Установить локальное смещение относительно родителя
child.local_offset = Vector2(50, 0)  # 50 пикселей справа от родителя

# Дочерний спрайт автоматически следует за родителем
parent.move_towards((500, 400))
# child автоматически переместится вместе с parent

# Отсоединить дочерний спрайт
child.set_parent(None, keep_world_position=True)
```

**Важные нюансы:**
- При установке родителя с `keep_world_position=True` дочерний спрайт сохраняет свою мировую позицию
- При `keep_world_position=False` дочерний спрайт принимает локальные координаты относительно родителя
- Если родитель имеет `screen_space=True`, дочерний спрайт автоматически также получает `screen_space=True`
- При вызове `kill()` на родителе все дочерние спрайты автоматически отсоединяются
- Дочерние спрайты автоматически обновляют свою позицию при движении родителя

### Фиксация к экрану (Screen Space)

Спрайты могут быть зафиксированы к экрану, игнорируя движение камеры:

```python
# Зафиксировать спрайт к экрану (для UI элементов)
ui_element = s.Sprite("ui.png", pos=(10, 10))
ui_element.set_screen_space(True)

# Вернуть в мировое пространство
ui_element.set_screen_space(False)
```

**Примечание:** UI компоненты (Button, TextSprite) автоматически используют `screen_space=True`

### Работа с изображениями

```python
# Установить новое изображение
sprite.set_image("new_image.png")

# Установить изображение с изменением размера
sprite.set_image("image.png", size=(100, 100))

# Использовать pygame.Surface напрямую
surface = pygame.Surface((50, 50))
sprite.set_image(surface)

# Вернуть к оригинальному размеру изображения
sprite.set_native_size()

# Отражение спрайта
sprite.set_flip(True, False)  # Отразить по горизонтали
sprite.set_flip(False, True)  # Отразить по вертикали
sprite.set_flip(True, True)   # Отразить по обеим осям
```

### Якоря позиционирования (Anchor)

Доступны следующие якоря для точного позиционирования:

```python
import spritePro as s

# Доступные якоря:
s.Anchor.CENTER        # Центр (по умолчанию)
s.Anchor.TOP_LEFT      # Верхний левый угол
s.Anchor.TOP_RIGHT     # Верхний правый угол
s.Anchor.BOTTOM_LEFT   # Нижний левый угол
s.Anchor.BOTTOM_RIGHT   # Нижний правый угол
s.Anchor.MID_TOP        # Верхняя середина
s.Anchor.MID_BOTTOM    # Нижняя середина
s.Anchor.MID_LEFT       # Левая середина
s.Anchor.MID_RIGHT      # Правая середина

# Использование
sprite.set_position((100, 50), anchor=s.Anchor.TOP_LEFT)
sprite.set_position((400, 300), anchor="center")  # Можно использовать строку
```

### Расстояния и видимость

```python
# Вычислить расстояние до другого спрайта или позиции
distance = sprite.distance_to(other_sprite)
distance = sprite.distance_to((500, 400))
distance = sprite.distance_to(Vector2(500, 400))

# Проверить, виден ли спрайт на экране
if sprite.is_visible_on_screen(screen):
    print("Спрайт виден на экране")
```

### Система коллизий

SpritePro предоставляет автоматическое разрешение столкновений:

```python
# Установить цели для столкновений
obstacles = [wall1, wall2, wall3]
sprite.set_collision_targets(obstacles)

# Добавить одну цель
sprite.add_collision_target(wall4)

# Добавить несколько целей
sprite.add_collision_targets([wall5, wall6])

# Удалить цель
sprite.remove_collision_target(wall1)

# Удалить несколько целей
sprite.remove_collision_targets([wall2, wall3])

# Очистить все цели
sprite.clear_collision_targets()
```

**Важно:** Столкновения разрешаются автоматически в методе `update()`, если установлены `collision_targets`

**Примечание:** Для работы со звуком используйте `spritePro.audio_manager` (см. документацию по AudioManager)

### Независимое от частоты кадров движение

```python
# Использовать delta time для плавного движения независимо от FPS
sprite.move_towards(target_pos, speed=180, use_dt=True)
```

**Совет:** Используйте `use_dt=True` для движения, которое должно быть одинаковым на разных частотах кадров

### Расширенные примеры

#### Анимация прозрачности с ограничениями
```python
# Плавное исчезновение с ограничениями
sprite.fade_by(-5, min_alpha=0, max_alpha=255)  # Уменьшить на 5, но не ниже 0
```

#### Анимация масштаба с ограничениями
```python
# Пульсация с ограничениями
sprite.scale_by(0.1, min_scale=0.5, max_scale=2.0)  # Увеличить на 0.1, но в пределах 0.5-2.0
```

#### Сложная иерархия спрайтов
```python
# Создать персонажа с оружием и эффектами
character = s.Sprite("character.png", pos=(400, 300))
weapon = s.Sprite("weapon.png", pos=(400, 300))
effect = s.Sprite("effect.png", pos=(400, 300))

# Прикрепить оружие к персонажу
weapon.set_parent(character, keep_world_position=False)
weapon.local_offset = Vector2(30, -10)  # Справа и немного выше

# Прикрепить эффект к оружию
effect.set_parent(weapon, keep_world_position=False)
effect.local_offset = Vector2(0, -20)  # Выше оружия

# При движении персонажа все автоматически следует за ним
character.move_towards((500, 400))
```

## Базовое использование

```python
import spritePro as s

# Создать базовый спрайт
player = s.Sprite(
    "player.png",
    size=(64, 64),
    pos=(400, 300),
    speed=5
)

# Переместить спрайт
player.move_towards((500, 400))

# Применить визуальные эффекты через свойства
player.scale = 1.5
player.alpha = 200
player.angle = 45

# Удобная работа с позицией
player.position = (400, 300)  # Установить позицию
player.x += 10  # Сдвинуть по X
player.y -= 5   # Сдвинуть по Y

# Удобная работа с размером
player.width = 100
player.height = 100
```

## Интеграция с другими модулями

Класс Sprite разработан для бесшовной работы с другими компонентами spritePro:

- **Components**: Анимация, взаимодействие с мышью, здоровье и т.д.

Для более продвинутой функциональности см.:
- [Компонент анимации](animation.md)
- [Компонент здоровья](health.md)
- [Компонент таймера](timer.md)
