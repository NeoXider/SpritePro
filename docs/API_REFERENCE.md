# API Reference — SpritePro v2.1.0

## Валидация данных

### `validate_color(color, name="color")`
Валидирует RGB-цвет (кортеж или список из 3 целых чисел от 0 до 255).

**Параметры:**
- `color` (`tuple` | `list`): Цвет в формате (R, G, B)
- `name` (`str`, optional): Имя параметра для сообщений об ошибках

**Пример:**
```python
from spritePro.utils.validation import validate_color
validate_color((255, 0, 0), "background")
```

### `validate_vector2(vec, name="vector")`
Валидирует координаты или вектор (Vector2, кортеж или список из 2 чисел).

**Параметры:**
- `vec` (`Vector2` | `tuple` | `list`): Координаты или вектор
- `name` (`str`, optional): Имя параметра для сообщений об ошибках

**Пример:**
```python
from spritePro.utils.validation import validate_vector2
validate_vector2((100, 200), "position")
```

### `validate_float(value, name="value", min_val=None, max_val=None)`
Валидирует числовое значение с возможностью указания диапазона.

**Параметры:**
- `value` (`int` | `float`): Числовое значение
- `name` (`str`, optional): Имя параметра для сообщений об ошибках
- `min_val` (`float`, optional): Минимально допустимое значение
- `max_val` (`float`, optional): Максимально допустимое значение

**Пример:**
```python
from spritePro.utils.validation import validate_float
validate_float(0.5, "zoom", min_val=0.1, max_val=5.0)
```

### `validate_string(value, name="string", min_length=None, max_length=None, allow_empty=True)`
Валидирует строковое значение с проверкой длины.

**Параметры:**
- `value` (`str`): Строковое значение
- `name` (`str`, optional): Имя параметра для сообщений об ошибках
- `min_length` (`int`, optional): Минимальная длина строки
- `max_length` (`int`, optional): Максимальная длина строки
- `allow_empty` (`bool`, optional): Разрешить ли пустые строки

**Пример:**
```python
from spritePro.utils.validation import validate_string
validate_string("player_name", "username", min_length=3, max_length=20)
```

### `validate_enum(value, enum_class, name="value")`
Валидирует значение на соответствие перечислению (Enum).

**Параметры:**
- `value`: Проверяемое значение
- `enum_class` (`type`): Класс перечисления (Enum)
- `name` (`str`, optional): Имя параметра для сообщений об ошибках

**Пример:**
```python
from spritePro.utils.validation import validate_enum
from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"

validate_enum("up", Direction, "direction")
```

### `validate_list(value, item_type, name="list", min_length=None, max_length=None)`
Валидирует список элементов определённого типа.

**Параметры:**
- `value` (`list`): Список для проверки
- `item_type` (`type`): Ожидаемый тип элементов
- `name` (`str`, optional): Имя параметра для сообщений об ошибках
- `min_length` (`int`, optional): Минимальная длина списка
- `max_length` (`int`, optional): Максимальная длина списка

**Пример:**
```python
from spritePro.utils.validation import validate_list
validate_list([1, 2, 3], int, "numbers")
```

### `validate_dict(value, name="dict", required_keys=None, allowed_keys=None)`
Валидирует словарь с проверкой ключей.

**Параметры:**
- `value` (`dict`): Словарь для проверки
- `name` (`str`, optional): Имя параметра для сообщений об ошибках
- `required_keys` (`List[str]`, optional): Список обязательных ключей
- `allowed_keys` (`List[str]`, optional): Список разрешённых ключей

**Пример:**
```python
from spritePro.utils.validation import validate_dict
validate_dict(
    {"name": "test", "value": 42}, 
    "config",
    required_keys=["name"], 
    allowed_keys=["name", "value"]
)
```

## Система плагинов

### `PluginManager`
Менеджер плагинов для SpritePro.

**Пример:**
```python
from spritePro.plugins import PluginManager
pm = PluginManager()
```

### `get_plugin_manager()`
Получает глобальный экземпляр менеджера плагинов.

**Возвращает:** `PluginManager`

### `register_plugin(name, version="1.0.0", author="Unknown")`
Декоратор для регистрации плагина с хуками.

**Параметры:**
- `name` (`str`): Имя плагина
- `version` (`str`, optional): Версия плагина
- `author` (`str`, optional): Автор плагина

**Пример:**
```python
from spritePro.plugins import register_plugin, hook

@register_plugin("my_plugin", "1.0.0", "NeoXider")
def my_plugin_init():
    pass

@hook("game_update")
def on_game_update(dt):
    debug_log_info(f"Update: {dt}")
```

### `hook(hook_name)`
Декоратор для регистрации хука в существующем плагине.

**Параметры:**
- `hook_name` (`str`): Имя хука

**Пример:**
```python
from spritePro.plugins import hook

@hook("sprite_created")
def on_sprite_created(sprite):
    debug_log_info(f"Sprite created: {sprite}")
```

### `PluginInfo`
Класс для хранения информации о плагине.

**Атрибуты:**
- `name` (`str`): Имя плагина
- `version` (`str`): Версия плагина
- `author` (`str`): Автор плагина
- `hooks` (`Dict[str, Callable]`): Хуки плагина
- `loaded_at` (`float`): Время загрузки
- `enabled` (`bool`): Статус включения
- `metadata` (`Dict[str, Any]`): Метаданные

## Предопределённые хуки

### HOOKS_LIFECYCLE
События жизненного цикла игры:
- `game_init`
- `game_update`
- `game_shutdown`

### HOOKS_SPRITE
События спрайтов:
- `sprite_created`
- `sprite_removed`
- `sprite_updated`

### HOOKS_SCENE
События сцен:
- `scene_loaded`
- `scene_unloaded`
- `scene_switched`

### HOOKS_INPUT
События ввода:
- `key_pressed`
- `key_released`
- `mouse_clicked`

## Примеры использования

### Валидация параметров кнопки
```python
from spritePro.utils.validation import validate_color, validate_vector2
import spritePro as s

def create_button(x, y, color):
    try:
        validate_vector2((x, y), "position")
        validate_color(color, "button_color")
        button = s.Button("", (100, 30), (x, y), "Click Me")
        return button
    except ValidationError as e:
        debug_log_error(f"Button creation failed: {e}")
```

### Плагин логирования событий
```python
from spritePro.plugins import hook, get_plugin_manager
import spritePro as s

@hook("sprite_created")
def on_sprite_created(sprite):
    s.debug_log_info(f"Sprite created: {type(sprite).__name__}")

@hook("scene_loaded")
def on_scene_loaded(scene_name):
    s.debug_log_info(f"Scene loaded: {scene_name}")
```

## См. также
- [Руководство по валидации](./VALIDATION_GUIDE.md)
- [Руководство по плагинам](./PLUGINS_GUIDE.md)
- [Основы SpritePro](./GETTING_STARTED.md)
