# Save/Load System - SpritePro

Профессиональная система сохранения и загрузки данных для игр, поддерживающая множество типов данных и форматов файлов.

## 🎯 Основные возможности

- **Множественные форматы**: JSON, Pickle, Text, Binary
- **Автоматическое определение формата** по расширению файла
- **Поддержка сжатия** с помощью gzip
- **Автоматическое создание резервных копий**
- **Сериализация пользовательских классов**
- **Потокобезопасность**
- **Обработка ошибок** с подробными сообщениями
- **Поддержка SpritePro объектов**

## 📦 Поддерживаемые типы данных

- **Простые типы**: числа, строки, булевы значения
- **Коллекции**: списки, словари, множества, кортежи
- **Сложные объекты**: пользовательские классы, спрайты SpritePro
- **Бинарные данные**: bytes, изображения
- **Текстовые данные**: обычный текст, конфигурации

## 🚀 Быстрый старт

### Простое использование

```python
import spritePro as s

# Сохранение данных
game_data = {
    'player_name': 'Hero',
    'score': 15000,
    'level': 8,
    'inventory': ['sword', 'potion', 'key']
}

# Сохранить (автоматически определит JSON формат)
s.utils.save(game_data, 'save_game.json')

# Загрузить
loaded_data = s.utils.load('save_game.json')
print(f"Игрок: {loaded_data['player_name']}, Очки: {loaded_data['score']}")
```

## 🎛 PlayerPrefs — быстрые сохранения

`PlayerPrefs` добавляет лёгкую обёртку поверх `SaveLoadManager` с API, знакомым пользователям Unity. Компонент автоматически пишет JSON-файл и поддерживает четыре базовых типа:

- числа с плавающей точкой (`get_float` / `set_float`)
- целые числа (`get_int` / `set_int`)
- строки (`get_string` / `set_string`)
- координаты из двух значений (`get_vector2` / `set_vector2`)

```python
import spritePro as s

# Создаём prefs-файл без резервных копий
prefs = s.PlayerPrefs("player_prefs.json")

# Читаем значения (если ключ не найден — вернётся значение по умолчанию)
spawn = prefs.get_vector2("player/spawn", (400, 300))
volume = prefs.get_float("audio/master", 0.8)
name = prefs.get_string("profile/name", "New Player")

# Сохраняем новые данные
prefs.set_vector2("player/spawn", (512, 384))
prefs.set_float("audio/master", 0.5)
prefs.set_int("progress/level", 6)
prefs.set_string("profile/name", "Hero")

# Управление ключами
prefs.delete_key("progress/level")
prefs.clear()  # полностью очищает JSON-файл
```

`PlayerPrefs` удобно использовать для настроек, сохранения позиции персонажа, хранения небольших числовых флагов. Для сложных структур по-прежнему используйте `SaveLoadManager` или сокращения `s.utils.save` / `s.utils.load`.

### Использование менеджера

```python
from spritePro.utils import SaveLoadManager

# Создать менеджер с настройками
manager = SaveLoadManager(
    default_file="game_save.json",
    auto_backup=True,
    compression=True
)

# Сохранение и загрузка
manager.save(game_data)
data = manager.load()
```

## 📋 Подробное руководство

### Форматы файлов

#### JSON (по умолчанию)
Лучший выбор для большинства игровых данных:

```python
# Автоматически использует JSON для .json файлов
data = {
    'settings': {'volume': 0.8, 'difficulty': 'normal'},
    'progress': [1, 2, 3, 4, 5],
    'achievements': {'first_win', 'speedrun', 'perfectionist'}
}

s.utils.save(data, 'game_config.json')
loaded = s.utils.load('game_config.json')
```

#### Pickle
Для сложных объектов и классов:

```python
# Сохранение пользовательского класса
class Player:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.inventory = []

player = Player("Hero", 10)
s.utils.save(player, 'player.pkl')
loaded_player = s.utils.load('player.pkl')
```

#### Text
Для простого текста и конфигураций:

```python
# Сохранение настроек как текст
settings_text = """
volume=0.8
difficulty=normal
fullscreen=true
"""

s.utils.save(settings_text, 'config.txt', 'text')
config = s.utils.load('config.txt', 'text')
```

#### Binary
Для бинарных данных:

```python
# Сохранение бинарных данных
binary_data = b'\x89PNG\r\n\x1a\n...'  # Например, изображение
s.utils.save(binary_data, 'image.bin', 'binary')
loaded_binary = s.utils.load('image.bin', 'binary')
```

### Работа с SpritePro объектами

Система автоматически поддерживает сериализацию спрайтов:

```python
import spritePro as s

# Создать спрайт
player_sprite = s.Sprite("player.png", (64, 64), (100, 200))
player_sprite.speed = 5
player_sprite.angle = 45

# Сохранить спрайт
s.utils.save(player_sprite, 'player_sprite.json')

# Загрузить спрайт
loaded_sprite = s.utils.load('player_sprite.json')
```

### Продвинутые возможности

#### Резервные копии

```python
# Менеджер автоматически создает резервные копии
manager = SaveLoadManager(auto_backup=True)

# Посмотреть список резервных копий
backups = manager.list_backups('save_game.json')
for backup in backups:
    print(f"Резервная копия: {backup}")

# Удалить файл с резервными копиями
manager.delete('save_game.json', include_backups=True)
```

#### Сжатие

```python
# Включить сжатие для экономии места
manager = SaveLoadManager(compression=True)

# Файлы будут автоматически сжиматься
large_data = {'map_data': [0] * 1000000}
manager.save(large_data, 'large_save.json')  # Создаст large_save.json.gz
```

#### Значения по умолчанию

```python
# Загрузка с значением по умолчанию
default_settings = {
    'volume': 1.0,
    'difficulty': 'easy',
    'controls': 'keyboard'
}

settings = s.utils.load('settings.json', default_value=default_settings)
```

#### Проверка существования файлов

```python
# Проверить, существует ли файл сохранения
if s.utils.exists('save_game.json'):
    game_data = s.utils.load('save_game.json')
    print("Игра загружена!")
else:
    print("Новая игра!")
    game_data = create_new_game()
```

### Регистрация пользовательских классов

Для сложных классов можно зарегистрировать собственные методы сериализации:

```python
from spritePro.utils.save_load import DataSerializer

class CustomGameObject:
    def __init__(self, x, y, data):
        self.x = x
        self.y = y
        self.data = data

# Функция сериализации
def serialize_game_object(obj):
    return {
        'position': (obj.x, obj.y),
        'data': obj.data
    }

# Функция десериализации
def deserialize_game_object(data):
    obj = CustomGameObject(0, 0, {})
    obj.x, obj.y = data['position']
    obj.data = data['data']
    return obj

# Регистрация класса
DataSerializer.register_class(
    CustomGameObject,
    serialize_game_object,
    deserialize_game_object
)

# Теперь можно сохранять/загружать объекты этого класса
obj = CustomGameObject(100, 200, {'health': 100})
s.utils.save(obj, 'custom_object.json')
loaded_obj = s.utils.load('custom_object.json')
```

## 🛠️ API Reference

### Функции быстрого доступа

#### `save(data, filename=None, format_type=None)`
Сохранить данные в файл.

**Параметры:**
- `data`: Данные для сохранения
- `filename`: Имя файла (опционально)
- `format_type`: Принудительный формат ('json', 'pickle', 'text', 'binary')

**Возвращает:** `bool` - успешность операции

#### `load(filename=None, format_type=None, default_value=None)`
Загрузить данные из файла.

**Параметры:**
- `filename`: Имя файла (опционально)
- `format_type`: Принудительный формат
- `default_value`: Значение по умолчанию если файл не найден

**Возвращает:** Загруженные данные или значение по умолчанию

#### `exists(filename=None)`
Проверить существование файла.

**Параметры:**
- `filename`: Имя файла (опционально)

**Возвращает:** `bool` - существует ли файл

#### `delete(filename=None, include_backups=False)`
Удалить файл.

**Параметры:**
- `filename`: Имя файла (опционально)
- `include_backups`: Удалить также резервные копии

**Возвращает:** `bool` - успешность операции

### Класс SaveLoadManager

#### `__init__(default_file="game_data.json", auto_backup=True, compression=False)`
Создать менеджер сохранений.

**Параметры:**
- `default_file`: Файл по умолчанию
- `auto_backup`: Создавать резервные копии
- `compression`: Использовать сжатие

#### Методы
- `save(data, filename=None, format_type=None)` - сохранить данные
- `load(filename=None, format_type=None, default_value=None)` - загрузить данные
- `exists(filename=None)` - проверить существование
- `delete(filename=None, include_backups=False)` - удалить файл
- `list_backups(filename=None)` - список резервных копий

### Исключения

#### `SaveLoadError`
Базовое исключение для операций сохранения/загрузки.

```python
try:
    data = s.utils.load('missing_file.json')
except s.utils.SaveLoadError as e:
    print(f"Ошибка загрузки: {e}")
```

## 💡 Примеры использования

### Система сохранения игры

```python
import spritePro as s

class GameSaveSystem:
    def __init__(self):
        self.manager = s.utils.SaveLoadManager(
            default_file="game_save.json",
            auto_backup=True,
            compression=True
        )
    
    def save_game(self, player, world, settings):
        """Сохранить полное состояние игры"""
        save_data = {
            'version': '1.0',
            'timestamp': time.time(),
            'player': {
                'name': player.name,
                'level': player.level,
                'position': (player.x, player.y),
                'inventory': player.inventory,
                'stats': player.stats
            },
            'world': {
                'current_level': world.current_level,
                'completed_levels': world.completed_levels,
                'discovered_areas': world.discovered_areas
            },
            'settings': settings
        }
        
        return self.manager.save(save_data)
    
    def load_game(self):
        """Загрузить состояние игры"""
        default_data = {
            'player': {'name': 'NewPlayer', 'level': 1},
            'world': {'current_level': 1},
            'settings': {'volume': 1.0}
        }
        
        return self.manager.load(default_value=default_data)
    
    def has_save(self):
        """Проверить наличие сохранения"""
        return self.manager.exists()

# Использование
save_system = GameSaveSystem()

# Сохранение
if save_system.save_game(player, world, settings):
    print("Игра сохранена!")

# Загрузка
if save_system.has_save():
    game_data = save_system.load_game()
    print("Игра загружена!")
```

### Система настроек

```python
class SettingsManager:
    def __init__(self):
        self.manager = s.utils.SaveLoadManager("settings.json")
        self.default_settings = {
            'graphics': {
                'resolution': (1920, 1080),
                'fullscreen': False,
                'vsync': True,
                'quality': 'high'
            },
            'audio': {
                'master_volume': 1.0,
                'music_volume': 0.8,
                'sfx_volume': 0.9
            },
            'controls': {
                'move_up': 'W',
                'move_down': 'S',
                'move_left': 'A',
                'move_right': 'D',
                'jump': 'SPACE'
            }
        }
    
    def load_settings(self):
        return self.manager.load(default_value=self.default_settings)
    
    def save_settings(self, settings):
        return self.manager.save(settings)
    
    def reset_to_defaults(self):
        return self.save_settings(self.default_settings)

# Использование
settings_mgr = SettingsManager()
settings = settings_mgr.load_settings()

# Изменить настройки
settings['audio']['master_volume'] = 0.7
settings_mgr.save_settings(settings)
```

## ⚠️ Важные замечания

1. **Безопасность**: Pickle формат может выполнять произвольный код. Используйте только для доверенных данных.

2. **Производительность**: JSON быстрее для простых данных, Pickle лучше для сложных объектов.

3. **Совместимость**: JSON файлы читаемы человеком и совместимы между платформами.

4. **Размер файлов**: Используйте сжатие для больших файлов сохранений.

5. **Резервные копии**: Включайте автоматическое создание резервных копий для важных данных.

## 🔧 Настройка и оптимизация

### Для небольших игр
```python
# Простая настройка
manager = s.utils.SaveLoadManager("save.json")
```

### Для больших игр
```python
# Продвинутая настройка
manager = s.utils.SaveLoadManager(
    default_file="game_save.json",
    auto_backup=True,
    compression=True
)
```

### Для мобильных игр
```python
# Оптимизация для мобильных устройств
manager = s.utils.SaveLoadManager(
    default_file="mobile_save.json",
    auto_backup=False,  # Экономия места
    compression=True    # Уменьшение размера
)
```

Система сохранения/загрузки SpritePro предоставляет все необходимые инструменты для надежного управления данными в ваших играх!
