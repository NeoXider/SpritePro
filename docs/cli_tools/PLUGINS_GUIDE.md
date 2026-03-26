# Система плагинов

Расширение функциональности через хуки (hooks).

## PluginManager

```python
from spritePro.plugins import get_plugin_manager

pm = get_plugin_manager()
pm.disable_plugin("fps_logger")
```

## Встроенный плагин fps_logger

```python
import spritePro.plugin_fps_logger
import spritePro as s

s.get_screen((800, 600), "Game")
# В логе: [fps_logger] FPS: ...
```

## Хуки (Hooks)

- `game_init`, `game_update`, `game_shutdown`
- `sprite_created`, `sprite_removed`, `sprite_updated`
- `scene_loaded`, `scene_unloaded`, `scene_switched`
- `key_pressed`, `key_released`, `mouse_clicked`

## Регистрация плагина

### Способ 1: Именованный плагин

```python
from spritePro.plugins import register_plugin, hook

@register_plugin("my_plugin", "1.0.0", "Author")
@hook("game_update")
def on_update(dt):
    s.debug_log_info(f"Update: {dt}")
```

### Способ 2: Без имени (global)

```python
from spritePro.plugins import hook

@hook("game_update")
def on_game_update(dt):
    s.debug_log_info(f"Game update: {dt}")

@hook("key_pressed")
def on_key_pressed(key, event):
    s.debug_log_info(f"Key: {key}")
```

## Пример: логирование событий

```python
# examples/plugin_log_events.py
from spritePro.plugins import hook, get_plugin_manager

@hook("sprite_created")
def on_sprite_created(sprite):
    s.debug_log_info(f"Created: {type(sprite).__name__}")

@hook("scene_loaded")
def on_scene_loaded(scene_name):
    s.debug_log_info(f"Scene: {scene_name}")

def init_plugin():
    s.debug_log_info("[LOG_EVENTS] Initialized")

def shutdown_plugin():
    s.debug_log_info("[LOG_EVENTS] Shutdown")
```

## Управление плагинами

```python
pm = get_plugin_manager()

# Информация о плагине
info = pm.get_plugin("log_events")
print(f"Plugin: {info.name}, Version: {info.version}")

# Список плагинов
plugins = pm.list_plugins()

# Статистика
stats = pm.get_stats()
print(f"Hooks: {stats['total_hooks']}")

# Статистика хуков
handlers = pm.get_hook_handlers("sprite_created")
```

## Рекомендации

- Используйте уникальные имена плагинов
- Обрабатывайте ошибки в хуках
- Освобождайте ресурсы при shutdown
- Следуйте семантике версий (SemVer)

## См. также

- [API Reference](../API_REFERENCE.md)
- [Getting Started](../GETTING_STARTED.md)
