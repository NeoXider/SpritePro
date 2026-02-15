# Slider

Горизонтальный слайдер для UI на базе Sprite. Наследует от Sprite, поддерживает два режима работы: в игровом цикле (авто-регистрация) и ручная отрисовка.

## Обзор

- **Наследование**: `Slider(Sprite)` — участвует в иерархии спрайтов, поддерживает `screen_space`, позицию и размер.
- **События**: **on_change** — при каждом изменении значения; **on_release** — при отпускании ползунка (применение).
- **Два режима**:
  - `auto_register=True` (по умолчанию): спрайт регистрируется в игровом контексте, получает события из `spritePro.pygame_events` и рисуется в общем цикле.
  - `auto_register=False`: спрайт не регистрируется; события передаются вручную через `handle_event()`, отрисовка — через `draw(screen)`.

## Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `size` | (int, int) | (200, 16) | Ширина и высота слайдера |
| `pos` | (int, int) | (100, 100) | Позиция центра |
| `min_value` | float | 0.0 | Минимальное значение |
| `max_value` | float | 1.0 | Максимальное значение |
| `value` | float | 0.0 | Текущее значение |
| `on_change` | Callable[[float], None] | None | Вызывается при каждом изменении значения (в т.ч. во время перетаскивания) |
| `on_release` | Callable[[float], None] | None | Вызывается при отпускании ползунка (применение/финальное значение) |
| `step` | float \| None | None | Шаг (дискретные значения) |
| `track_color` | (int,int,int) | (60,60,70) | Цвет трека |
| `fill_color` | (int,int,int) | (0,150,255) | Цвет заполнения |
| `thumb_color` | (int,int,int) | (220,220,220) | Цвет ползунка |
| `sorting_order` | int | 1000 | Слой отрисовки |
| `auto_register` | bool | True | Регистрировать в игровом контексте |
| `scene` | Scene \| str \| None | None | Сцена |

## События: изменение и применение

- **on_change(value)** — вызывается при каждом изменении значения (клик по треку, перетаскивание ползунка). Подходит для обновления превью в реальном времени.
- **on_release(value)** — вызывается при отпускании кнопки мыши после перетаскивания; передаётся финальное значение. Подходит для «применить» (например, сохранить громкость, применить настройку).

## Пример в сцене (auto_register=True)

```python
import spritePro as s

class MenuScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.volume = 0.8
        self.slider = s.Slider(
            size=(280, 16),
            pos=(400, 200),
            min_value=0.0,
            max_value=1.0,
            value=self.volume,
            on_change=self._on_volume,
            scene=self,
        )

    def _on_volume(self, value: float) -> None:
        self.volume = value  # обновление в реальном времени

    def _on_volume_apply(self, value: float) -> None:
        # вызывается когда пользователь отпустил ползунок
        self.volume = value
        # применить громкость к аудио
```

С передачей обоих колбэков:

```python
self.slider = s.Slider(
    ...,
    on_change=self._on_volume,
    on_release=self._on_volume_apply,
    scene=self,
)
```

## Ручной режим (auto_register=False)

Подходит для кастомных циклов (например, редактор без игрового контекста):

```python
import pygame
import spritePro as s

slider = s.Slider(
    size=(140, 9),
    pos=(200, 400),
    min_value=0.01,
    max_value=10.0,
    value=1.0,
    on_change=lambda v: print("Zoom:", v),
    auto_register=False,
    scene=None,
)

# В цикле:
for event in pygame.event.get():
    slider.handle_event(event)
# ...
slider.draw(screen)
```

## Методы

- **set_value(value, emit=True)** — устанавливает значение, при `emit=True` вызывает `on_change` при изменении.
- **set_range(min_value, max_value)** — меняет диапазон.
- **get_ratio()** — возвращает отношение (0.0–1.0) текущего значения к диапазону.
- **set_rect(rect)** — задаёт позицию и размер через `pygame.Rect` или (x, y, w, h).
- **handle_event(event)** — обрабатывает `MOUSEBUTTONDOWN`, `MOUSEBUTTONUP`, `MOUSEMOTION`; при отпускании кнопки мыши вызывает `on_release(value)`; возвращает `True`, если событие обработано.
- **draw(screen)** — рисует слайдер на поверхности (для ручного режима).

## Связанное

- [Button](button.md) — кнопки UI.
- [TextInput](text_input.md) — поле ввода текста.
- [Sprite](sprite.md) — базовый класс и параметр `auto_register`.
