# Валидация ввода

Функции для валидации пользовательского ввода.

## Функции

| Функция | Описание |
|---------|---------|
| `validate_key(key)` | Клавиша допустима |
| `validate_mouse_button(button)` | Кнопка мыши допустима |
| `validate_position(x, y, bounds)` | Позиция в пределах |
| `validate_range(value, min, max)` | Значение в диапазоне |
| `validate_text_input(text, max_length, allowed_chars)` | Текстовый ввод |

## Примеры

```python
from spritePro.input_validation import validate_key, validate_position

if validate_key(pygame.K_SPACE):
    print("Клавиша допустима")

if validate_position(100, 200, (0, 0, 800, 600)):
    print("В пределах экрана")
```

## InputValidator

```python
from spritePro.input_validation import InputValidator

validator = InputValidator()
validator.add_rule('position', lambda x, y: 0 <= x <= 800 and 0 <= y <= 600)
result = validator.validate({'type': 'position', 'x': 100, 'y': 200})
if result.is_valid:
    handle_input(result.data)
validator.clear_rules()
```

## InputFilter

```python
from spritePro.input_validation import InputFilter

filter = InputFilter()
safe = filter.sanitize(user_input)
filtered = filter.filter_text(user_input, filters=['no_spaces', 'no_special'])
```

## Фильтры текста

```python
FILTER_NO_SPACES = 'no_spaces'
FILTER_NO_SPECIAL = 'no_special'
FILTER_NO_DIGITS = 'no_digits'
FILTER_ONLY_DIGITS = 'only_digits'
```

## Защита от инъекций

```python
dangerous_patterns = [';', '&&', '||', '`', '$(']
for pattern in dangerous_patterns:
    if pattern in sanitized:
        return False
```

## Лучшие практики

- Валидируйте на клиенте и сервере
- Используйте белые списки
- Санитизируйте ввод
- Обрабатывайте ошибки

## См. также

- [Input](input_system.md)
