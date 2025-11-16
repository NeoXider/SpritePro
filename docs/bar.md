# Bar - Готовый спрайт полосы прогресса

Класс `Bar` - это готовый к использованию спрайт полосы прогресса, который предоставляет функциональность fillAmount в стиле Unity с настраиваемыми направлениями заполнения и плавной анимацией.

## Возможности

- **4 направления заполнения**: Горизонтальные и вертикальные, каждое с 2 ориентациями
- **Плавная анимация**: Настраиваемая длительность анимации для изменений заполнения
- **Поддержка якорей**: Правильное позиционирование с любой точкой якоря
- **Стиль Unity**: Аналогично поведению Image.fillAmount в Unity
- **Производительность**: Использует `set_clip()` pygame для оптимальной отрисовки

## Импорт

```python
import spritePro as s
from spritePro.readySprites import Bar, create_bar, BarWithBackground, create_bar_with_background
from spritePro.constants import FillDirection
```

## Конструктор

```python
Bar(
    image: Union[str, Path, pygame.Surface],
    pos: Tuple[int, int] = (0, 0),
    size: Optional[Tuple[int, int]] = None,
    fill_direction: Union[str, FillDirection] = FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
    fill_amount: float = 1.0,
    animate_duration: float = 0.3,
    sorting_order: Optional[int] = None,
)
```

### Параметры

- **`image`**: Путь к изображению полосы, объект Path, pygame Surface или пустая строка (""). Если пустая строка, создается прозрачная поверхность. По умолчанию: ""
- **`pos`**: Позиция на экране (x, y). По умолчанию: (0, 0)
- **`size`**: Размеры полосы (ширина, высота). Если None, использует размер изображения или (100, 20) по умолчанию
- **`fill_direction`**: Направление заполнения. По умолчанию: `HORIZONTAL_LEFT_TO_RIGHT`
- **`fill_amount`**: Начальное количество заполнения (0.0-1.0). По умолчанию: 1.0
- **`animate_duration`**: Длительность анимации в секундах. По умолчанию: 0.3
- **`sorting_order`**: Порядок слоя отрисовки. Опционально

## Направления заполнения

Константы `FillDirection` предоставляют 4 направления заполнения:

```python
# Горизонтальные направления
FillDirection.HORIZONTAL_LEFT_TO_RIGHT    # ←→ (по умолчанию)
FillDirection.HORIZONTAL_RIGHT_TO_LEFT    # →←
FillDirection.LEFT_TO_RIGHT               # Алиас для HORIZONTAL_LEFT_TO_RIGHT
FillDirection.RIGHT_TO_LEFT               # Алиас для HORIZONTAL_RIGHT_TO_LEFT

# Вертикальные направления  
FillDirection.VERTICAL_BOTTOM_TO_TOP      # ↑
FillDirection.VERTICAL_TOP_TO_BOTTOM      # ↓
FillDirection.BOTTOM_TO_TOP               # Алиас для VERTICAL_BOTTOM_TO_TOP
FillDirection.TOP_TO_BOTTOM               # Алиас для VERTICAL_TOP_TO_BOTTOM
```

## Основные методы

### `set_fill_amount(value: float, animate: bool = True)`

Установить количество заполнения полосы.

```python
# Установить на 50% с анимацией
bar.set_fill_amount(0.5)

# Установить на 75% без анимации (мгновенно)
bar.set_fill_amount(0.75, animate=False)
```

### `get_fill_amount() -> float`

Получить текущее количество заполнения.

```python
current_fill = bar.get_fill_amount()
print(f"Полоса заполнена на {current_fill * 100:.1f}%")
```

### `set_fill_direction(direction: Union[str, FillDirection])`

Изменить направление заполнения.

```python
# Изменить на вертикальное снизу вверх
bar.set_fill_direction(FillDirection.VERTICAL_BOTTOM_TO_TOP)
```

### `set_fill_type(fill_direction: Union[str, FillDirection], anchor: Union[str, Anchor] = Anchor.CENTER)`

Установить направление заполнения и якорь одним удобным методом.

```python
# Установить тип заполнения и якорь вместе
bar.set_fill_type("left_to_right", s.Anchor.TOP_LEFT)
bar.set_fill_type(FillDirection.BOTTOM_TO_TOP, "center")
```

### `set_animate_duration(duration: float)`

Установить длительность анимации для изменений заполнения.

```python
# Быстрая анимация (0.1 секунды)
bar.set_animate_duration(0.1)

# Без анимации (мгновенные изменения)
bar.set_animate_duration(0.0)
```

### `set_image(image_source: Union[str, Path, pygame.Surface] = "", size: Optional[Tuple[int, int]] = None)`

Установить новое изображение для полосы и обновить обрезку.

```python
# Изменить изображение полосы
bar.set_image("new_bar.png")

# Изменить изображение с новым размером
bar.set_image("new_bar.png", size=(200, 30))

# Использовать пустую строку для создания по умолчанию
bar.set_image("")  # Создаст прозрачную поверхность
```

### Изменение цвета

Так как `Bar` наследуется от `Sprite`, можно использовать `set_color()` или свойство `color` для тонировки изображения:

```python
# Установить цвет через метод
bar.set_color((255, 0, 0))  # Красный

# Или через свойство
bar.color = (0, 255, 0)  # Зеленый

# Создать бар с пустым изображением и установить цвет
bar = Bar(image="", size=(200, 30))
bar.color = (255, 0, 0)  # Красный цвет
```

## Примеры использования

### Базовая полоса прогресса

```python
import spritePro as s
from spritePro.readySprites import Bar

# Создать полосу здоровья
health_bar = Bar(
    image="health_bar.png",
    pos=(100, 100),
    fill_amount=0.8,  # 80% здоровья
    animate_duration=0.5
)

# В игровом цикле
health_bar.update(s.screen)
```

### Полоса с пустым изображением и цветом

```python
# Создать полосу с пустым изображением
bar = Bar(
    image="",  # Пустая строка - создастся по умолчанию
    size=(300, 40),
    pos=(400, 200),
    fill_amount=0.75
)

# Установить цвет через свойство color (наследуется от Sprite)
bar.color = (255, 0, 0)  # Красный цвет
```

### Вертикальная полоса маны

```python
# Создать вертикальную полосу маны
mana_bar = Bar(
    image="mana_bar.png",
    pos=(50, 50),
    fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
    fill_amount=0.6,  # 60% маны
    animate_duration=0.3
)

# Обновить ману
mana_bar.set_fill_amount(0.9)  # Восстановить до 90%
```

### Несколько полос

```python
# Полоса здоровья (горизонтальная, слева направо)
health = Bar("health.png", pos=(100, 100), fill_amount=0.7)

# Полоса маны (горизонтальная, справа налево)  
mana = Bar("mana.png", pos=(100, 150), 
          fill_direction=FillDirection.HORIZONTAL_RIGHT_TO_LEFT,
          fill_amount=0.5)

# Полоса опыта (вертикальная, снизу вверх)
exp = Bar("exp.png", pos=(50, 200),
         fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
         fill_amount=0.3)

# Использование удобного метода set_fill_type
health.set_fill_type("left_to_right", s.Anchor.TOP_LEFT)
mana.set_fill_type(FillDirection.RIGHT_TO_LEFT, s.Anchor.CENTER)
exp.set_fill_type("bottom_to_top", s.Anchor.BOTTOM_RIGHT)
```

### Позиционирование с якорями

```python
# Позиционировать полосу с разными якорями
bar = Bar("bar.png", pos=(400, 300))

# Установить позицию с якорем
bar.set_position((400, 300), s.Anchor.TOP_LEFT)    # Верхний левый угол
bar.set_position((400, 300), s.Anchor.CENTER)       # Центр (по умолчанию)
bar.set_position((400, 300), s.Anchor.BOTTOM_RIGHT) # Нижний правый угол
```

## Управление анимацией

### Включить/выключить анимацию

```python
# Отключить анимацию для мгновенных изменений
bar.set_animate_duration(0.0)

# Включить плавную анимацию
bar.set_animate_duration(0.5)
```

### Анимированные изменения заполнения

```python
# Плавный переход к 50%
bar.set_fill_amount(0.5)  # Использует текущую animate_duration

# Мгновенное изменение до 25%
bar.set_fill_amount(0.25, animate=False)
```

## Удобная функция

Используйте `create_bar()` для быстрого создания полосы:

```python
from spritePro.readySprites import create_bar

# Быстрая горизонтальная полоса
bar = create_bar("bar.png", pos=(100, 100), fill_amount=0.8)

# С пользовательскими настройками
bar = create_bar(
    "mana.png", 
    pos=(50, 50),
    fill_amount=0.6,
    fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
    animate_duration=0.2
)
```

## BarWithBackground

Класс `BarWithBackground` расширяет `Bar` для включения фонового изображения, которое остается видимым, пока область заполнения обрезается поверх него.

### Конструктор BarWithBackground

```python
BarWithBackground(
    background_image: Union[str, Path, pygame.Surface],
    fill_image: Union[str, Path, pygame.Surface],
    size: Tuple[int, int],
    pos: Tuple[float, float] = (0, 0),
    fill_amount: float = 1.0,
    fill_direction: Union[str, FillDirection] = FillDirection.LEFT_TO_RIGHT,
    animate_duration: float = 0.3,
    sorting_order: int = 0,
    background_size: Optional[Tuple[int, int]] = None,
    fill_size: Optional[Tuple[int, int]] = None
)
```

### Параметры BarWithBackground

- **`background_image`**: Изображение для фона (всегда видимо)
- **`fill_image`**: Изображение для области заполнения (обрезается на основе fill_amount)
- **`size`**: Размер полосы по умолчанию (ширина, высота)
- **`pos`**: Позиция на экране
- **`fill_amount`**: Начальное количество заполнения (0.0-1.0)
- **`fill_direction`**: Направление заполнения
- **`animate_duration`**: Длительность анимации заполнения в секундах
- **`sorting_order`**: Порядок отрисовки (больше = сверху)
- **`background_size`**: Опциональный отдельный размер для фонового изображения
- **`fill_size`**: Опциональный отдельный размер для изображения заполнения

### Методы BarWithBackground

- `set_fill_image(fill_image: Union[str, Path, pygame.Surface])`: Установить новое изображение заполнения
- `set_background_image(background_image: Union[str, Path, pygame.Surface])`: Установить новое фоновое изображение
- `set_background_size(size: Tuple[int, int])`: Установить новый размер фона
- `set_fill_size(size: Tuple[int, int])`: Установить новый размер заполнения
- `set_both_sizes(background_size: Tuple[int, int], fill_size: Tuple[int, int])`: Установить оба размера одновременно
- `set_fill_amount(value: float, animate: bool = True)`: Установить количество заполнения
- `get_fill_amount() -> float`: Получить текущее количество заполнения

### Пример использования BarWithBackground

```python
from spritePro.readySprites import BarWithBackground, create_bar_with_background

# Создать полосу с фоном и заполнением
bar = BarWithBackground(
    background_image="bar_bg.png",
    fill_image="bar_fill.png",
    size=(200, 30),
    pos=(400, 300),
    fill_amount=0.7,
    fill_direction=FillDirection.HORIZONTAL_LEFT_TO_RIGHT
)

# Или использовать удобную функцию
bar = create_bar_with_background(
    background_image="bar_bg.png",
    fill_image="bar_fill.png",
    pos=(400, 300),
    fill_amount=0.7
)

# Обновить заполнение
bar.set_fill_amount(0.5)

# Изменить изображения
bar.set_fill_image("new_fill.png")
bar.set_background_image("new_bg.png")
```

## Типичные случаи использования

### Полоса здоровья

```python
class Player:
    def __init__(self):
        self.max_health = 100
        self.health = 100
        self.health_bar = Bar("health_bar.png", pos=(10, 10))
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        fill_amount = self.health / self.max_health
        self.health_bar.set_fill_amount(fill_amount)
```

### Полоса загрузки

```python
# Прогресс загрузки
loading_bar = Bar("loading_bar.png", pos=(200, 300))

def update_loading(progress):
    loading_bar.set_fill_amount(progress / 100.0)
```

### Полосы ресурсов

```python
# Несколько полос ресурсов
health = Bar("red_bar.png", pos=(10, 10), fill_amount=1.0)
mana = Bar("blue_bar.png", pos=(10, 50), 
          fill_direction=FillDirection.HORIZONTAL_RIGHT_TO_LEFT,
          fill_amount=1.0)
stamina = Bar("green_bar.png", pos=(10, 90), fill_amount=1.0)
```

## Заметки о производительности

- Использует `set_clip()` pygame для эффективной отрисовки
- Нет влияния на производительность, когда количество заполнения не изменяется
- Обновления анимации только при необходимости
- Эффективно по памяти - переиспользует оригинальную поверхность изображения

## Демо

См. `spritePro/demoGames/bar_demo.py` для полной демонстрации всех направлений заполнения и интерактивных элементов управления.

## Связанные компоненты

- [Документация по спрайтам](sprite.md) - Базовая функциональность спрайтов
- [Готовые спрайты](readySprites.md) - Другие готовые к использованию спрайты
- [Bar с фоном](bar_background.md) - Полоса с фоновым изображением
