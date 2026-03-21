# Система управления ресурсами

Модуль `resources.py` предоставляет централизованную систему кэширования и управления игровыми ресурсами (текстуры, звуки, шрифты и т.д.).

## Обзор

ResourceCache обеспечивает:
- Централизованное хранение загруженных ресурсов
- Повторное использование ресурсов
- Автоматическую очистку памяти
- Ленивую загрузку ресурсов

## ResourceCache

```python
from spritePro.resources import ResourceCache

cache = ResourceCache()
```

### Методы класса

#### `load(path, resource_type=None)`

Загрузка ресурса с кэшированием.

**Параметры:**
- `path` (str) — путь к файлу ресурса
- `resource_type` (str) — тип ресурса ('image', 'sound', 'font')

**Возвращает:** загруженный ресурс

```python
texture = cache.load("assets/player.png", 'image')
sound = cache.load("assets/explosion.wav", 'sound')
```

#### `get(path)`

Получение ресурса из кэша (без загрузки).

```python
texture = cache.get("assets/player.png")
if texture is None:
    print("Ресурс не загружен")
```

#### `has(path)`

Проверка наличия ресурса в кэше.

```python
if cache.has("assets/player.png"):
    print("Ресурс в кэше")
```

#### `unload(path)`

Выгрузка ресурса из кэша.

```python
cache.unload("assets/player.png")
```

#### `clear()`

Очистка всего кэша.

```python
cache.clear()
```

#### `clear_type(resource_type)`

Очистка ресурсов определенного типа.

```python
cache.clear_type('image')  # Очистить все текстуры
```

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `cached_count` | int | Количество кэшированных ресурсов |
| `memory_usage` | int | Примерный объем используемой памяти |
| `keys` | list | Список всех ключей в кэше |

## Практические примеры

### Базовое использование

```python
from spritePro import SpritePro
from spritePro.resources import ResourceCache

class Game(SpritePro):
    def __init__(self):
        super().__init__()
        self.cache = ResourceCache()
        
    def load_all_assets(self):
        self.cache.load("assets/player.png", 'image')
        self.cache.load("assets/enemy.png", 'image')
        self.cache.load("assets/background.png", 'image')
        self.cache.load("assets/jump.wav", 'sound')
        
    def get_player(self):
        return self.cache.get("assets/player.png")
```

### Ленивая загрузка

```python
class LazyResourceCache(ResourceCache):
    def __init__(self):
        super().__init__()
        self.load_callbacks = {}
        
    def register_loader(self, path, callback, resource_type='image'):
        self.load_callbacks[path] = (callback, resource_type)
        
    def get(self, path):
        if not super().has(path):
            if path in self.load_callbacks:
                callback, rtype = self.load_callbacks[path]
                resource = callback()
                self._cache[path] = (resource, rtype)
        return super().get(path)
```

### Автоматическая очистка

```python
class AutoCleanupCache(ResourceCache):
    def __init__(self, max_memory_mb=256):
        super().__init__()
        self.max_memory = max_memory_mb * 1024 * 1024
        
    def load(self, path, resource_type=None):
        if self.memory_usage > self.max_memory:
            self.cleanup_least_used()
        return super().load(path, resource_type)
        
    def cleanup_least_used(self):
        least_used = self.get_least_used(5)
        for path in least_used:
            self.unload(path)
```

### Профилирование памяти

```python
def print_cache_stats():
    print(f"Кэшировано объектов: {cache.cached_count}")
    print(f"Использование памяти: {cache.memory_usage / 1024 / 1024:.2f} MB")
    print("Ресурсы:")
    for path in cache.keys:
        resource = cache.get(path)
        size = get_resource_size(resource)
        print(f"  {path}: {size / 1024:.2f} KB")
```

## Предзагрузка ресурсов

```python
class Preloader:
    def __init__(self, cache):
        self.cache = cache
        self.loading_queue = []
        self.loaded = 0
        self.total = 0
        
    def queue(self, path, resource_type):
        self.loading_queue.append((path, resource_type))
        self.total += 1
        
    def update(self):
        if self.loading_queue:
            path, rtype = self.loading_queue.pop(0)
            self.cache.load(path, rtype)
            self.loaded += 1
            return self.loaded / self.total
        return 1.0
        
    def is_complete(self):
        return len(self.loading_queue) == 0
```

## Интеграция с асинхронной загрузкой

```python
import asyncio

class AsyncResourceCache(ResourceCache):
    async def load_async(self, path, resource_type=None):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.load,
            path,
            resource_type
        )
        
    async def preload_all_async(self, resources):
        tasks = [
            self.load_async(path, rtype)
            for path, rtype in resources
        ]
        await asyncio.gather(*tasks)
```

## Обработка ошибок

```python
def safe_load(cache, path, resource_type, fallback=None):
    try:
        return cache.load(path, resource_type)
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
        return fallback
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
        return fallback
```

## Лучшие практики

1. **Группируйте загрузку** — загружайте связанные ресурсы вместе
2. **Используйте предзагрузку** — загружайте критичные ресурсы заранее
3. **Очищайте неиспользуемое** — выгружайте ресурсы уровня при смене сцены
4. **Следите за памятью** — ограничивайте максимальный размер кэша
5. **Кэшируйте повторно используемое** — не загружайте одно и то же дважды
