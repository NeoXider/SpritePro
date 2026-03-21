# Валидация входных данных в SpritePro

## Обзор

Модуль `spritePro.utils.validation` предоставляет набор функций для валидации различных типов данных. Это помогает предотвращать ошибки на этапе разработки и обеспечивает корректность передаваемых параметров.

## Доступные функции

### validate_color(color, name="color")

Валидирует RGB-цвет (кортеж или список из 3 целых чисел от 0 до 255).

**Пример:**
```python
from spritePro.utils.validation import validate_color

# Корректное использование
validate_color((255, 0, 0), "background")
validate_color([128, 128, 128], "text_color")

# Ошибка: неверный тип
try:
    validate_color("red", "color")
except ValidationError as e:
    print(e)
```

### validate_vector2(vec, name="vector")

Валидирует координаты или вектор (Vector2, кортеж или список из 2 чисел).

**Пример:**
```python
from spritePro.utils.validation import validate_vector2
import pygame.math as pm

# Корректное использование
validate_vector2((100, 200), "position")
validate_vector2(pm.Vector2(50.5, 75.3), "offset")
validate_vector2([10.0, 20.0], "scale")
```

### validate_float(value, name="value", min_val=None, max_val=None)

Валидирует числовое значение с возможностью указания диапазона.

**Пример:**
```python
from spritePro.utils.validation import validate_float

# Без ограничений
validate_float(60, "fps")

# С диапазоном
validate_float(0.5, "zoom", min_val=0.1, max_val=5.0)
validate_float(100, "score", min_val=0)
```

### validate_string(value, name="string", min_length=None, max_length=None, allow_empty=True)

Валидирует строковое значение с проверкой длины.

**Пример:**
```python
from spritePro.utils.validation import validate_string

# Корректное использование
validate_string("player_name", "username", min_length=3, max_length=20)
validate_string("", "description", allow_empty=True)

# Ошибка: пустая строка
try:
    validate_string("", "required_field", allow_empty=False)
except ValidationError as e:
    print(e)
```

### validate_enum(value, enum_class, name="value")

Валидирует значение на соответствие перечислению (Enum).

**Пример:**
```python
from spritePro.utils.validation import validate_enum
from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

# Корректное использование
validate_enum("up", Direction, "direction")

# Ошибка: неверное значение
try:
    validate_enum("diagonal", Direction, "direction")
except ValidationError as e:
    print(e)
```

### validate_list(value, item_type, name="list", min_length=None, max_length=None)

Валидирует список элементов определённого типа.

**Пример:**
```python
from spritePro.utils.validation import validate_list

# Корректное использование
validate_list([1, 2, 3], int, "numbers")
validate_list(["a", "b"], str, "tags", min_length=2)

# Ошибка: неверный тип элемента
try:
    validate_list([1, "two", 3], int, "mixed_list")
except ValidationError as e:
    print(e)
```

### validate_dict(value, name="dict", required_keys=None, allowed_keys=None)

Валидирует словарь с проверкой ключей.

**Пример:**
```python
from spritePro.utils.validation import validate_dict

# Корректное использование
validate_dict(
    {"name": "test", "value": 42}, 
    "config",
    required_keys=["name"], 
    allowed_keys=["name", "value"]
)

# Ошибка: отсутствуют обязательные ключи
try:
    validate_dict({"value": 42}, "config", required_keys=["name"])
except ValidationError as e:
    print(e)
```

## Обработка ошибок

Все функции валидации выбрасывают `ValidationError` при неудачной проверке. Рекомендуется обрабатывать эти ошибки:

```python
from spritePro.utils.validation import validate_color, validate_vector2
from spritePro.exceptions import ValidationError

def create_button(x, y, color):
    try:
        validate_vector2((x, y), "position")
        validate_color(color, "button_color")
        # Создаём кнопку...
    except ValidationError as e:
        debug_log_error(f"Invalid button parameters: {e}")
```

## Интеграция с существующим кодом

Функции валидации могут быть использованы для проверки параметров перед созданием объектов:

```python
import spritePro as s
from spritePro.utils.validation import validate_float, validate_string

def create_game_button(text, x, y, width, height):
    # Валидация параметров
    validate_string(text, "button_text", min_length=1)
    validate_vector2((x, y), "position")
    validate_float(width, "width", min_val=50)
    validate_float(height, "height", min_val=30)
    
    button = s.Button(
        "",
        (width, height),
        (x, y),
        text
    )
    return button
```

## Лучшие практики

1. **Валидируйте входные данные** перед использованием в критических операциях
2. **Используйте понятные имена параметров** для сообщений об ошибках
3. **Указывайте диапазоны** для числовых значений (например, FPS от 30 до 144)
4. **Проверяйте типы данных** для списков и словарей
5. **Обрабатывайте ошибки валидации** с помощью try-except блоков

## Пример: Валидация конфигурации игры

```python
from spritePro.utils.validation import validate_dict, validate_float, validate_string

def load_game_config(config):
    """
    Валидирует конфигурацию игры.
    
    Args:
        config: Словарь с параметрами игры
    """
    try:
        # Проверка структуры
        validate_dict(
            config,
            "game_config",
            required_keys=["title", "width", "height"],
            allowed_keys=["title", "width", "height", "fullscreen"]
        )
        
        # Валидация значений
        validate_string(config["title"], "title", min_length=1, max_length=50)
        validate_float(config["width"], "width", min_val=320, max_val=3840)
        validate_float(config["height"], "height", min_val=240, max_val=2160)
        
        return True
    except ValidationError as e:
        debug_log_error(f"Configuration error: {e}")
        return False
```

## См. также

- [Руководство по плагинам](./PLUGINS_GUIDE.md)
- [API Reference](./API_REFERENCE.md)
- [Основы SpritePro](./GETTING_STARTED.md)
