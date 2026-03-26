# Валидация в SpritePro

Функции для валидации данных.

## Импорт

```python
from spritePro.utils.validation import (
    validate_color,
    validate_vector2,
    validate_float,
    validate_string,
    validate_enum,
    validate_list,
    validate_dict,
)
```

## Функции

| Функция | Описание |
|---------|---------|
| `validate_color(color)` | RGB (0-255) |
| `validate_vector2(vec)` | Vector2 или (x, y) |
| `validate_float(value, min_val, max_val)` | Число в диапазоне |
| `validate_string(value, min_length, max_length)` | Строка |
| `validate_enum(value, enum_class)` | Значение enum |
| `validate_list(value, item_type)` | Список элементов |
| `validate_dict(value, required_keys)` | Словарь |

## Примеры

```python
validate_color((255, 0, 0))
validate_vector2((100, 200))
validate_float(60, min_val=30, max_val=144)
validate_string("player", min_length=1, max_length=20)
```

## Обработка ошибок

```python
from spritePro.exceptions import ValidationError

try:
    validate_color("red")
except ValidationError as e:
    print(f"Ошибка: {e}")
```

## Валидация конфигурации

```python
def load_game_config(config):
    try:
        validate_dict(config, required_keys=["title", "width", "height"])
        validate_float(config["width"], min_val=320, max_val=3840)
        return True
    except ValidationError:
        return False
```

## Лучшие практики

- Валидируйте входные данные перед использованием
- Используйте понятные имена для ошибок
- Указывайте диапазоны для числовых значений
- Обрабатывайте ошибки с try-except
