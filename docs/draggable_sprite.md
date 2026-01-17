# DraggableSprite

`DraggableSprite` — компонент для drag-and-drop в стиле Unity. Наследуется от `Sprite`, поэтому поддерживает все базовые возможности спрайта.

## Возможности

- Перетаскивание мышью за объект
- Колбэки начала/процесса/конца перетаскивания
- Принудительный возврат на стартовую позицию
- Ограничение осей перетаскивания

## Быстрый старт

```python
import spritePro as s

box = s.DraggableSprite("", size=(80, 80), pos=(200, 150))
box.set_color((255, 170, 100))
```

## API

### Свойства

- `drag_enabled: bool` — можно ли перетаскивать.
- `drag_button: int` — кнопка мыши (1=ЛКМ, 2=СКМ, 3=ПКМ).
- `drag_axis: str` — ограничение оси: `"both"`, `"x"` или `"y"`.
- `dragging: bool` — идет ли перетаскивание.

### Методы

- `set_drag_enabled(enabled: bool)` — включить/выключить перетаскивание.
- `return_to_start()` — вернуть объект в позицию, где началось перетаскивание.

### Колбэки

Можно переопределить методы или передать функции в конструктор:

- `on_drag_start(world_pos, mouse_pos)`
- `on_drag(world_pos, mouse_pos)`
- `on_drag_end(world_pos, mouse_pos)` — если вернуть `False`, объект вернется на стартовую позицию.

Для внешних колбэков сигнатура:

```python
def on_drag_end(sprite, world_pos, mouse_pos) -> bool | None:
    ...
```

## Пример с проверкой дропа

```python
def handle_drop(sprite, world_pos, mouse_pos):
    if is_valid_drop(sprite):
        return True
    return False  # вернет на место

box = s.DraggableSprite(
    "",
    size=(80, 80),
    pos=(200, 150),
    on_drag_end=handle_drop,
)
```
