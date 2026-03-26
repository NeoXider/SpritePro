# TextSprite (Текст)

Класс `TextSprite` предоставляет расширенные возможности рендеринга текста с поддержкой пользовательских шрифтов, цветов и динамического обновления.

## Обзор

TextSprite расширяет Sprite для отображения текста. Поддерживает пользовательские шрифты, несколько цветов и автоматическое позиционирование.

## Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `text` | str | "Text" | Начальный текст |
| `font_size` | int | 24 | Размер шрифта |
| `color` | (int,int,int) | (255,255,255) | Цвет текста |
| `font_name` | str | None | Путь к TTF шрифту |
| `pos` | (int, int) | (0, 0) | Позиция |
| `sorting_order` | int | 1000 | Слой отрисовки |
| `anchor` | Anchor | CENTER | Якорь позиционирования |
| `scene` | Scene | None | Сцена |

По умолчанию `screen_space=True`: позиция не зависит от камеры. Для мировых координат вызовите `.set_screen_space(False)`.

## Основные операции

```python
# Установить текст
text.set_text("Новое сообщение")

# Получить текст
current = text.text

# Форматирование
text.set_text(f"Счёт: {player.score}")
text.set_text(f"HP: {player.health}/100")

# Через свойство
text.text = "Новый текст"
```

## Шрифты

```python
# Пользовательский шрифт
text = s.TextSprite(
    text="Свой шрифт",
    font_name="assets/fonts/game.ttf",
    font_size=28
)

# Изменить шрифт
text.set_font("assets/fonts/title.ttf", font_size=48)

# Системный шрифт
text.set_font(None, font_size=24)
```

## Цвета

```python
text.set_color((255, 100, 100))  # Красный
text.set_color((100, 255, 100))  # Зелёный
text.set_color((100, 100, 255))  # Синий
```

## Якоря

```python
# Текст в левом верхнем углу
text_score = s.TextSprite(
    f"Счёт: {score}", 36, (255, 255, 255), (10, 10),
    anchor=s.Anchor.TOP_LEFT
)

# Текст в правом верхнем углу
text_lost = s.TextSprite(
    f"Пропущено: {lost}", 36, (255, 255, 255), (s.WH.x - 10, 10),
    anchor=s.Anchor.TOP_RIGHT
)

# Текст по центру
text_center = s.TextSprite("Центр", 36, (255, 255, 255), s.WH_C)
```

## Многострочный текст

TextSprite поддерживает `\n` для переноса строк:

```python
multiline = s.TextSprite(
    text="Строка 1\nСтрока 2\nСтрока 3",
    font_size=20,
    pos=(400, 300)
)

# Динамический многострочный
lines = ["Статистика:", f"HP: {health}", f"Счёт: {score}"]
text.set_text("\n".join(lines))

# Список игроков
roster_text.set_text("Игроки:\n" + "\n".join(["Хост", "Игрок 1", "Игрок 2"]))
```

## Анимация цвета

```python
import math
import time

def animate_text():
    t = time.time() * 2
    r = int(127 + 127 * math.sin(t))
    g = int(127 + 127 * math.sin(t + 2))
    b = int(127 + 127 * math.sin(t + 4))
    text.set_color((r, g, b))  # Радуга
```

## HUD элементы

```python
class GameHUD:
    def __init__(self):
        self.health_text = s.TextSprite(
            text="HP: 100", font_size=24, color=(255, 255, 255), pos=(50, 50)
        )
        self.score_text = s.TextSprite(
            text="Счёт: 0", font_size=24, color=(255, 255, 0), pos=(50, 80)
        )
        self.ammo_text = s.TextSprite(
            text="Патроны: 30/30", font_size=20, color=(200, 200, 200), pos=(50, 110)
        )

    def update(self, player):
        self.health_text.set_text(f"HP: {player.health}")
        self.score_text.set_text(f"Счёт: {player.score}")
        self.ammo_text.set_text(f"Патроны: {player.ammo}/{player.max_ammo}")
```

## Урон (Damage Numbers)

```python
class DamageNumber(s.TextSprite):
    def __init__(self, damage, pos):
        super().__init__(str(damage), font_size=20, color=(255, 100, 100), pos=pos)
        self.velocity_y = -2
        self.lifetime = 2.0
        self.start_time = time.time()

    def update(self):
        super().update()
        self.rect.y += self.velocity_y
        elapsed = time.time() - self.start_time
        alpha = max(0, 255 * (1 - elapsed / self.lifetime))
        self.set_alpha(alpha)
        if elapsed > self.lifetime:
            self.kill()
```

## Базовое использование

```python
import spritePro as s

text = s.TextSprite(
    text="Привет мир!",
    font_size=32,
    color=(255, 255, 255),
    pos=(400, 300)
)

text.set_text("Новый текст!")
```

## Методы

| Метод | Описание |
|-------|----------|
| `set_text(text)` | Установить текст |
| `set_color(color)` | Изменить цвет |
| `set_font(name, size)` | Изменить шрифт |
| `set_position(pos, anchor)` | Изменить позицию |
| `set_scale(scale)` | Изменить масштаб |
| `set_alpha(alpha)` | Изменить прозрачность |

## Связанное

- [Button](button.md) — текст в кнопках
- [Sprite](sprite.md) — базовый класс
- [Animation](animation.md) — анимация текста
