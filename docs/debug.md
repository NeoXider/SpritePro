# Debug Overlay

Debug Overlay — встроенная визуализация для разработки: сетка мира, координаты камеры и отладочные логи.

## Быстрый старт

```python
import spritePro as s

s.enable_debug(True)
s.set_debug_grid(size=80, label_every=2)
s.set_debug_log_anchor("bottom_left")
s.debug_log_info("Debug enabled")
```

## Возможности

- Сетка мира (не привязана к камере)
- Координаты камеры и точка в центре экрана
- Логи в углу экрана с авто‑исчезновением

## API (через spritePro)

### Включение/выключение
- `s.enable_debug(True/False)`
- `s.disable_debug()`
- `s.toggle_debug()`

### Логи
- `s.debug_log_info(text, ttl=None)`
- `s.debug_log_warning(text, ttl=None)`
- `s.debug_log_error(text, ttl=None)`
- `s.debug_log_custom(prefix, text, color, ttl=None)`
- `s.set_debug_logs_enabled(True/False)`
- `s.set_debug_log_anchor("top_left" | "top_right" | "bottom_left" | "bottom_right")`

### Сетка
- `s.set_debug_grid(size=None, color=None, alpha=None, label_every=None, label_color=None, labels_enabled=None)`
- `s.set_debug_grid_enabled(True/False)`

### Стиль и файл логов
- `s.set_debug_log_style(font_size=None, line_height=None, padding=None, max_lines=None, anchor=None)`
- `s.set_debug_camera_style(color=None, font_size=None)`
- `s.set_debug_log_file(enabled=None, path=None)`
- `s.set_debug_log_palette(info=None, warning=None, error=None)`
- `s.set_debug_log_prefixes(info=None, warning=None, error=None)`
- `s.set_debug_log_stack_enabled(True/False)`
- `s.set_debug_hud_style(font_size=None, color=None, padding=None, anchor=None)`
- `s.set_debug_hud_enabled(show_fps=None, show_camera=None)`
- `s.set_debug_camera_input(mouse_button)`

## Параметры сетки

```python
s.set_debug_grid(
    size=64,            # шаг сетки
    color=(80, 80, 80), # цвет линий
    alpha=120,          # прозрачность (0..255)
    label_every=2,      # подписи через N линий
    label_color=(140, 140, 140),
    labels_enabled=True,
)
```

## Пример

```python
def update():
    if s.input.was_pressed(pygame.K_1):
        s.debug_log_info("Info log")
    if s.input.was_pressed(pygame.K_2):
        s.debug_log_warning("Warning log")
    if s.input.was_pressed(pygame.K_3):
        s.debug_log_error("Error log")
    if s.input.was_pressed(pygame.K_4):
        s.debug_log_custom("[net]", "Custom log", (120, 220, 160))
```
