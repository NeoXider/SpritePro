# Color Effects (Цветовые эффекты)

Модуль `color_effects` предоставляет динамические цветовые эффекты для игр.

## Обзор

Все эффекты возвращают RGB-кортежи для использования со спрайтами и pygame.

## Эффекты

### Пульсация (Pulse)

Плавное переключение между двумя цветами.

```python
# Чёрно-белая пульсация
color = s.utils.pulse(speed=1.0)

# Пульсация с цветами
color = s.utils.pulse(
    speed=2.0,
    base_color=(50, 0, 0),      # Тёмно-красный
    target_color=(255, 0, 0)    # Ярко-красный
)
```

### Радуга (Rainbow)

Плавный переход по всему спектру.

```python
color = s.utils.rainbow(speed=1.0)
```

### Дыхание (Breathing)

Плавное изменение интенсивности.

```python
color = s.utils.breathing(
    speed=1.0,
    color=(100, 150, 200)
)
```

### Волна (Wave)

Волнообразное изменение цвета.

```python
color = s.utils.wave(
    speed=1.0,
    color=(255, 100, 100)
)
```

## Утилиты

### Преобразование HSV → RGB

```python
from spritePro.utils.color_effects import hsv_to_rgb

color = hsv_to_rgb(hue=0.5, saturation=1.0, value=1.0)
```

## Связанное

- [Sprite](sprite.md) — использование цветов
- [Text](text.md) — цвет текста
