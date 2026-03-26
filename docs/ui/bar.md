# Bar (Прогресс-бар)

Готовая полоса прогресса в стиле Unity с анимацией.

## Импорт

```python
import spritePro as s
from spritePro.readySprites import Bar, create_bar, BarWithBackground
from spritePro.constants import FillDirection
```

## Конструктор

```python
Bar(image="", pos=(0, 0), size=None, fill_direction=FillDirection.HORIZONTAL_LEFT_TO_RIGHT, fill_amount=1.0, animate_duration=0.3)
```

| Параметр | Тип | Описание |
|----------|-----|----------|
| `image` | str/Surface | Путь к изображению или "" |
| `size` | tuple | Размер (w, h) |
| `fill_direction` | FillDirection | Направление заполнения |
| `fill_amount` | float | Заполнение 0.0-1.0 |
| `animate_duration` | float | Длительность анимации |

## FillDirection

```python
FillDirection.HORIZONTAL_LEFT_TO_RIGHT   # ←→ (по умолчанию)
FillDirection.HORIZONTAL_RIGHT_TO_LEFT   # →←
FillDirection.VERTICAL_BOTTOM_TO_TOP     # ↑
FillDirection.VERTICAL_TOP_TO_BOTTOM     # ↓
```

## Методы

```python
bar.set_fill_amount(0.5)           # 50% с анимацией
bar.set_fill_amount(0.75, animate=False)  # Без анимации
bar.amount = 0.5                   # Через свойство
bar.set_fill_direction(FillDirection.VERTICAL_BOTTOM_TO_TOP)
bar.set_animate_duration(0.5)
bar.set_image("new_bar.png")
bar.set_color((255, 0, 0))         # Наследуется от Sprite
```

## Примеры

```python
# Полоса здоровья
health_bar = Bar("health_bar.png", pos=(100, 100), fill_amount=0.8)

# С пустым изображением
bar = Bar(image="", size=(300, 40), pos=(400, 200))
bar.color = (255, 0, 0)

# Вертикальная полоса маны
mana_bar = Bar("mana_bar.png", pos=(50, 50), fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP)

# Обновление в игре
def update_health(current, max_health):
    health_bar.set_fill_amount(current / max_health)
```

## BarWithBackground

```python
bar = BarWithBackground(
    background_image="bar_bg.png",
    fill_image="bar_fill.png",
    size=(200, 30),
    pos=(400, 300),
    fill_amount=0.7,
    fill_direction=FillDirection.LEFT_TO_RIGHT
)

bar.set_fill_amount(0.5)
bar.set_fill_image("new_fill.png")
bar.set_background_image("new_bg.png")
```

## Удобная функция

```python
bar = create_bar("bar.png", pos=(100, 100), fill_amount=0.8)
```

## Демо

```bash
python -m spritePro.demoGames.bar_demo
```

## См. также

- [Sprite](sprite.md)
- [Bar с фоном](bar_background.md)
