# Валидация ввода

Модуль `input_validation.py` предоставляет функции для валидации пользовательского ввода, включая клавиатуру, мышь и геймпад.

## Обзор

Система валидации ввода обеспечивает:
- Проверку допустимости ввода
- Фильтрацию нежелательных символов
- Ограничение диапазонов значений
- Предотвращение инъекций

## Функции валидации

### validate_key(key)

Проверка допустимости клавиши.

```python
from spritePro.input_validation import validate_key

if validate_key(pygame.K_SPACE):
    print("Клавиша допустима")
```

### validate_mouse_button(button)

Проверка допустимости кнопки мыши.

```python
if validate_mouse_button(1):  # Левая кнопка
    print("Кнопка мыши допустима")
```

### validate_position(x, y, bounds)

Проверка позиции в пределах границ.

```python
from spritePro.input_validation import validate_position

if validate_position(100, 200, (0, 0, 800, 600)):
    print("Позиция в пределах экрана")
```

### validate_range(value, min_val, max_val)

Проверка значения в диапазоне.

```python
from spritePro.input_validation import validate_range

health = validate_range(health_input, 0, 100)
```

### validate_text_input(text, max_length, allowed_chars=None)

Валидация текстового ввода.

```python
from spritePro.input_validation import validate_text_input

name = validate_text_input(
    raw_input,
    max_length=20,
    allowed_chars=string.ascii_letters + string.digits
)
```

## Класс InputValidator

```python
from spritePro.input_validation import InputValidator

validator = InputValidator()
```

### Методы

#### `validate(event)`

Валидация игрового события.

```python
result = validator.validate(event)
if result.is_valid:
    handle_input(result.data)
```

#### `add_rule(validation_type, rule)`

Добавление правила валидации.

```python
validator.add_rule('position', lambda x, y: x >= 0 and y >= 0)
```

#### `clear_rules()`

Очистка всех правил.

```python
validator.clear_rules()
```

## Класс InputFilter

```python
from spritePro.input_validation import InputFilter

filter = InputFilter()
```

### Методы

#### `filter_text(text, filters)`

Фильтрация текста по правилам.

```python
filtered = filter.filter_text(
    user_input,
    filters=['no_spaces', 'no_special']
)
```

#### `sanitize(text)`

Санитизация ввода (удаление опасных символов).

```python
safe_input = filter.sanitize(user_input)
```

## Практические примеры

### Валидация ввода игрока

```python
class PlayerInput:
    def __init__(self):
        self.validator = InputValidator()
        self.setup_rules()
        
    def setup_rules(self):
        self.validator.add_rule(
            'position',
            lambda x, y: 0 <= x <= 800 and 0 <= y <= 600
        )
        self.validator.add_rule(
            'velocity',
            lambda v: -100 <= v <= 100
        )
        
    def handle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.validator.validate({'type': 'position', 'x': x, 'y': y}).is_valid:
                self.move_player(x, y)
```

### Фильтрация чата

```python
class ChatFilter(InputFilter):
    def __init__(self):
        super().__init__()
        self.banned_words = ['спам', 'реклама']
        
    def filter_chat_message(self, message):
        filtered = self.sanitize(message)
        filtered = self.remove_banned_words(filtered, self.banned_words)
        filtered = self.filter_text(filtered, ['no_excessive_caps'])
        return filtered
        
    def remove_banned_words(self, text, banned):
        for word in banned:
            text = text.replace(word, '*' * len(word))
        return text
```

### Защита от инъекций

```python
class SecureInput:
    @staticmethod
    def validate_command(command, allowed_commands):
        if command not in allowed_commands:
            return False
            
        filter = InputFilter()
        sanitized = filter.sanitize(command)
        
        dangerous_patterns = [';', '&&', '||', '`', '$(']
        for pattern in dangerous_patterns:
            if pattern in sanitized:
                return False
                
        return True
```

### Валидация числового ввода

```python
def get_player_stats():
    print("Введите здоровье (0-100):")
    health_input = input()
    health = validate_range(int(health_input), 0, 100)
    
    print("Введите скорость (0-50):")
    speed_input = input()
    speed = validate_range(float(speed_input), 0, 50)
    
    return {'health': health, 'speed': speed}
```

## Фильтры текста

```python
FILTER_NO_SPACES = 'no_spaces'
FILTER_NO_SPECIAL = 'no_special'
FILTER_NO_DIGITS = 'no_digits'
FILTER_ONLY_DIGITS = 'only_digits'
FILTER_NO_CAPS = 'no_caps'
FILTER_NO_WHITESPACE = 'no_whitespace'
```

## Обработка ошибок

```python
from spritePro.input_validation import ValidationError

def safe_validate(value, validation_type):
    try:
        return validate(value, validation_type)
    except ValidationError as e:
        print(f"Ошибка валидации: {e}")
        return None
```

## Лучшие практики

1. **Валидируйте на стороне клиента** — для быстрой обратной связи
2. **Валидируйте на стороне сервера** — для безопасности
3. **Используйте белые списки** — разрешайте только допустимое
4. **Обрабатывайте ошибки** — информируйте пользователя
5. **Санитизируйте ввод** — удаляйте потенциально опасные символы
