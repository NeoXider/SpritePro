# Исключения SpritePro

Модуль `exceptions.py` содержит набор пользовательских исключений для обработки ошибок в SpritePro.

## Обзор

SpritePro определяет собственные исключения для более точной идентификации и обработки ошибок, связанных с игровой логикой, графикой и системами движка.

## Исключения

### SpriteProException

Базовый класс для всех исключений SpritePro.

```python
from spritePro.exceptions import SpriteProException

try:
    # код
except SpriteProException as e:
    print(f"Ошибка SpritePro: {e}")
```

### SpriteLoadError

Возникает при ошибке загрузки спрайта.

```python
from spritePro.exceptions import SpriteLoadError

try:
    sprite = load_image("nonexistent.png")
except SpriteLoadError as e:
    print(f"Не удалось загрузить спрайт: {e.filename}")
```

**Атрибуты:**
- `filename` — путь к файлу, который не удалось загрузить

### SpriteNotFoundError

Возникает, когда запрошенный спрайт не найден.

```python
from spritePro.exceptions import SpriteNotFoundError

try:
    sprite = SpritePro.get_sprite("player_v2")
except SpriteNotFoundError:
    print("Спрайт не найден в кэше")
```

### InvalidSpriteError

Возникает при недопустимых параметрах спрайта.

```python
from spritePro.exceptions import InvalidSpriteError

try:
    sprite.set_position("invalid")  # Неверный тип
except InvalidSpriteError:
    print("Недопустимое значение позиции")
```

### AnimationError

Возникает при ошибках анимации.

```python
from spritePro.exceptions import AnimationError

try:
    anim.play_frame(999)  # Кадр не существует
except AnimationError as e:
    print(f"Ошибка анимации: {e}")
```

### SceneNotFoundError

Возникает, когда сцена не найдена.

```python
from spritePro.exceptions import SceneNotFoundError

try:
    game.set_scene("NonExistentScene")
except SceneNotFoundError:
    print("Сцена не найдена")
```

### InvalidSceneError

Возникает при ошибке инициализации сцены.

```python
from spritePro.exceptions import InvalidSceneError

try:
    class BadScene(Scene):
        def __init__(self):
            raise ValueError("Ошибка в сцене")
except InvalidSceneError:
    print("Неверная конфигурация сцены")
```

### PhysicsError

Возникает при ошибках физической системы.

```python
from spritePro.exceptions import PhysicsError

try:
    body.set_velocity("invalid")
except PhysicsError:
    print("Ошибка в физическом теле")
```

### CollisionError

Возникает при ошибках коллизий.

```python
from spritePro.exceptions import CollisionError

try:
    collider.check_collision(None)
except CollisionError:
    print("Недопустимый объект для проверки коллизий")
```

### AssetLoadError

Возникает при ошибке загрузки ассета.

```python
from spritePro.exceptions import AssetLoadError

try:
    asset = load_asset("sound.wav")
except AssetLoadError:
    print("Не удалось загрузить ассет")
```

### NetworkError

Возникает при сетевых ошибках.

```python
from spritePro.exceptions import NetworkError

try:
    mp.connect("192.168.1.100", 5000)
except NetworkError:
    print("Ошибка сетевого подключения")
```

### InvalidStateError

Возникает при недопустимом состоянии объекта.

```python
from spritePro.exceptions import InvalidStateError

try:
    anim.pause()  # Анимация уже запущена
except InvalidStateError:
    print("Недопустимое состояние для этой операции")
```

### ConfigurationError

Возникает при ошибках конфигурации.

```python
from spritePro.exceptions import ConfigurationError

try:
    game.load_config("invalid.json")
except ConfigurationError:
    print("Ошибка в конфигурации")
```

## Обработка исключений

### Иерархия исключений

```
SpriteProException (базовый класс)
├── SpriteLoadError
│   └── SpriteNotFoundError
├── InvalidSpriteError
├── AnimationError
├── SceneException
│   ├── SceneNotFoundError
│   └── InvalidSceneError
├── PhysicsException
│   ├── PhysicsError
│   └── CollisionError
├── AssetLoadError
├── NetworkError
├── InvalidStateError
└── ConfigurationError
```

### Перехват всех исключений SpritePro

```python
from spritePro.exceptions import SpriteProException

try:
    game.setup()
except SpriteProException as e:
    print(f"Ошибка SpritePro: {e}")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
```

### Перехват группы исключений

```python
from spritePro.exceptions import (
    SpriteLoadError,
    AssetLoadError,
    NetworkError
)

try:
    load_game_content()
except (SpriteLoadError, AssetLoadError, NetworkError):
    print("Ошибка загрузки контента")
```

## Практические примеры

### Обработка ошибок загрузки

```python
def safe_load_sprite(path):
    from spritePro.exceptions import SpriteLoadError
    
    try:
        return load_image(path)
    except SpriteLoadError:
        return load_image("default.png")
        print(f"Используем спрайт по умолчанию вместо {path}")
```

### Валидация спрайтов

```python
def validate_sprite(sprite):
    from spritePro.exceptions import InvalidSpriteError
    
    if sprite is None:
        raise InvalidSpriteError("Спрайт не может быть None")
        
    if not hasattr(sprite, 'position'):
        raise InvalidSpriteError("Спрайт не имеет позиции")
        
    return True
```

### Обработка ошибок сцены

```python
from spritePro.exceptions import SceneNotFoundError

class Game(SpritePro):
    def __init__(self):
        super().__init__()
        self.scenes = {
            'menu': MenuScene,
            'game': GameScene,
            'pause': PauseScene
        }
        
    def set_scene(self, name):
        if name not in self.scenes:
            raise SceneNotFoundError(f"Сцена '{name}' не найдена")
            
        scene_class = self.scenes[name]
        super().set_scene(scene_class())
```

## Создание собственных исключений

```python
from spritePro.exceptions import SpriteProException

class GameSpecificError(SpriteProException):
    """Исключение для специфических ошибок игры"""
    
    def __init__(self, message, game_state=None):
        super().__init__(message)
        self.game_state = game_state
```

## Лучшие практики

1. **Используйте специфичные исключения** — перехватывайте конкретные типы
2. **Обрабатывайте базовые исключения последними** — для неожиданных ошибок
3. **Логируйте ошибки** — записывайте информацию для отладки
4. **Предоставляйте fallback** — используйте значения по умолчанию
5. **Не скрывайте ошибки без причины** — информация об ошибках важна
