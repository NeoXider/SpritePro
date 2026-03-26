# Save/Load (Сохранения)

Система сохранения и загрузки данных в нескольких форматах.

## Быстрый старт

```python
import spritePro as s

data = {'score': 15000, 'level': 8}
s.utils.save(data, 'save.json')
loaded = s.utils.load('save.json')
```

## PlayerPrefs (Unity-style)

Лёгкая обёртка для настроек:

```python
prefs = s.PlayerPrefs("player_prefs.json")

# Чтение
spawn = prefs.get_vector2("player/spawn", (400, 300))
volume = prefs.get_float("audio/master", 0.8)
name = prefs.get_string("profile/name", "Player")

# Запись
prefs.set_vector2("player/spawn", (512, 384))
prefs.set_float("audio/master", 0.5)
prefs.set_int("progress/level", 6)
prefs.set_string("profile/name", "Hero")

prefs.delete_key("progress/level")
prefs.clear()
```

## Форматы

| Формат | Расширение | Описание |
|--------|------------|----------|
| JSON | .json | Текстовый, читаемый |
| Pickle | .pkl | Для классов |
| Text | .txt | Простой текст |
| Binary | .bin | Бинарные данные |

```python
# JSON (по умолчанию)
s.utils.save(data, 'game.json')

# Pickle (классы)
s.utils.save(player, 'player.pkl')

# Text
s.utils.save("настройки", 'config.txt', 'text')
```

## SpritePro объекты

```python
player_sprite = s.Sprite("player.png", (64, 64), (100, 200))
s.utils.save(player_sprite, 'sprite.json')
loaded = s.utils.load('sprite.json')
```

## Расширенные возможности

### Резервные копии

```python
manager = s.utils.SaveLoadManager(auto_backup=True)
backups = manager.list_backups('save.json')
manager.delete('save.json', include_backups=True)
```

### Сжатие

```python
manager = s.utils.SaveLoadManager(compression=True)
large_data = {'map_data': [0] * 1000000}
manager.save(large_data, 'large_save.json')  # .gz
```

### Значения по умолчанию

```python
settings = s.utils.load('settings.json', default_value={'volume': 1.0})
```

### Проверка файлов

```python
if s.utils.exists('save.json'):
    data = s.utils.load('save.json')
```

## Кастомные классы

```python
from spritePro.utils.save_load import DataSerializer

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

DataSerializer.register_class(
    Player,
    serialize=lambda p: {'pos': (p.x, p.y)},
    deserialize=lambda d: Player(d['pos'][0], d['pos'][1])
)

s.utils.save(Player(100, 200), 'player.json')
```

## API

```python
s.utils.save(data, filename, format_type)
s.utils.load(filename, format_type, default_value)
s.utils.exists(filename)
s.utils.delete(filename, include_backups)

manager = s.utils.SaveLoadManager(
    default_file="save.json",
    auto_backup=True,
    compression=True
)
```

## Рекомендации

- JSON для данных, Pickle для классов
- Включайте резервные копии для важных данных
- Используйте сжатие для больших файлов
