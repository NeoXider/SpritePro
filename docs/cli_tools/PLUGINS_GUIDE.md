# Система плагинов в SpritePro

## Обзор

Система плагинов SpritePro предоставляет гибкий механизм расширения функциональности через хуки (hooks). Плагины позволяют:
- Автоматически реагировать на события игры
- Расширять функциональность без изменения ядра библиотеки
- Создавать кросс-модульные решения
- Интегрировать сторонние сервисы

## Встроенный плагин fps_logger

В комплекте есть плагин, который раз в 2 секунды пишет в debug-лог текущий FPS. Подключение:

```python
import spritePro.plugin_fps_logger  # до get_screen/update
import spritePro as s
s.get_screen((800, 600), "Game")
# ... в логе будут сообщения [fps_logger] FPS: ...
```

Отключить: `get_plugin_manager().disable_plugin("fps_logger")`.

## Основные компоненты

### PluginManager

Централизованный менеджер для регистрации и управления плагинами.

```python
from spritePro.plugins import get_plugin_manager

pm = get_plugin_manager()
```

### Хуки (Hooks)

Хуки — это точки входа, которые вызываются при наступлении определённых событий. Предопределённые хуки:

- **HOOKS_LIFECYCLE**: `game_init`, `game_update`, `game_shutdown`
- **HOOKS_SPRITE**: `sprite_created`, `sprite_removed`, `sprite_updated`
- **HOOKS_SCENE**: `scene_loaded`, `scene_unloaded`, `scene_switched`
- **HOOKS_INPUT**: `key_pressed`, `key_released`, `mouse_clicked`

## Регистрация плагина

### Способ 1: Плагин с именем (register_plugin + hook на одной функции)

Декораторы нужно вешать на **одну и ту же** функцию: сначала `@hook`, затем `@register_plugin`.

```python
from spritePro.plugins import register_plugin, hook
import spritePro as s

@register_plugin("my_plugin", "1.0.0", "Author")
@hook("game_update")
def on_update(dt):
    s.debug_log_info(f"Update: {dt}")
```

### Способ 2: Хуки без имени плагина (только hook)

Подходит для быстрого расширения. Обработчик регистрируется как `_global` и вызывается при каждом `emit`.

```python
from spritePro.plugins import hook
import spritePro as s

@hook("game_update")
def on_game_update(dt):
    s.debug_log_info(f"Game update: {dt}")

@hook("key_pressed")
def on_key_pressed(key, event):
    key_names = {257: 'SPACE', 256: 'ENTER'}
    key_name = key_names.get(key, f"KEY_{key}")
    s.debug_log_info(f"Key pressed: {key_name}")
```

## Использование плагина

### Инициализация

```python
from examples.plugin_log_events import init_plugin

# Вызывается при старте игры
init_plugin()
```

### Очистка ресурсов

```python
from examples.plugin_log_events import shutdown_plugin

# Вызывается при завершении игры
shutdown_plugin()
```

## Пример: Плагин логирования событий

Создайте файл `examples/plugin_log_events.py`:

```python
from spritePro.plugins import hook, get_plugin_manager
import spritePro as s

def log_events_plugin():
    """Плагин для логирования событий."""
    pass

@hook("sprite_created")
def on_sprite_created(sprite):
    s.debug_log_info(f"[LOG_EVENTS] Created: {type(sprite).__name__}")

@hook("scene_loaded")
def on_scene_loaded(scene_name):
    s.debug_log_info(f"[LOG_EVENTS] Scene loaded: {scene_name}")

# Инициализация и очистка
def init_plugin():
    pm = get_plugin_manager()
    s.debug_log_info("[LOG_EVENTS] Plugin initialized")

def shutdown_plugin():
    pm = get_plugin_manager()
    s.debug_log_info("[LOG_EVENTS] Plugin shutdown")
```

## Управление плагинами

### Получение информации о плагине

```python
from spritePro.plugins import get_plugin_manager

pm = get_plugin_manager()
plugin_info = pm.get_plugin("log_events")
print(f"Plugin: {plugin_info.name}, Version: {plugin_info.version}")
```

### Список плагинов

```python
pm = get_plugin_manager()
plugins_list = pm.list_plugins()
print(f"Active plugins: {plugins_list}")
```

### Статистика

```python
stats = pm.get_stats()
print(f"Total hooks: {stats['total_hooks']}")
print(f"Enabled plugins: {stats['enabled_plugins']}")
```

## Расширение системы хуков

Вы можете добавить собственные хуки для специфичных задач:

```python
# В вашем модуле
from spritePro.plugins import hook
import spritePro as s

@hook("custom_event")
def on_custom_event(data):
    """Обработчик пользовательского события."""
    s.debug_log_info(f"Custom event: {data}")
```

## Пример: Плагин для сохранения состояния

```python
from spritePro.plugins import hook, get_plugin_manager
import json
import os

def save_state_plugin():
    """Плагин для автоматического сохранения состояния."""
    pass

@hook("game_shutdown")
def on_game_shutdown():
    pm = get_plugin_manager()
    # Сохраняем состояние игры
    state = {
        'score': current_score,
        'level': current_level
    }
    with open('save_state.json', 'w') as f:
        json.dump(state, f)
    s.debug_log_info("Game state saved")
```

## Лучшие практики

1. **Используйте уникальные имена плагинов** для избежания конфликтов
2. **Обрабатывайте ошибки в хуках** с помощью try-except
3. **Освобождайте ресурсы** при shutdown плагина
4. **Документируйте хуки** которые использует ваш плагин
5. **Следуйте семантике версий** (SemVer)

## Отладка плагинов

```python
pm = get_plugin_manager()

# Проверка наличия хуков
handlers = pm.get_hook_handlers("sprite_created")
print(f"Handlers for sprite_created: {len(handlers)}")

# Статистика всех плагинов
stats = pm.get_stats()
print(f"Registry: {stats['hooks_registry']}")
```

## См. также

- [Руководство по валидации](./VALIDATION_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Основы SpritePro](./GETTING_STARTED.md)

