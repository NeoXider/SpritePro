# Мониторинг ресурсов

Модуль `resource_watcher.py` предоставляет систему автоматического мониторинга и перезагрузки ассетов при их изменении на диске. Это позволяет обновлять игровые ресурсы без перезапуска приложения.

## Обзор системы

Resource Watcher отслеживает изменения в файлах ассетов (изображения, звуки, шрифты и т.д.) и автоматически обновляет кэшированные версии этих ресурсов.

## Основные компоненты

### ResourceWatcher

```python
from spritePro.resource_watcher import ResourceWatcher

watcher = ResourceWatcher()
```

### Методы класса

#### `watch(path, callback)`

Начинает отслеживание изменений в указанном пути.

**Параметры:**
- `path` (str) — путь к файлу или директории для мониторинга
- `callback` (callable) — функция обратного вызова при изменении

**Пример:**
```python
def on_image_changed(new_path):
    print(f"Изображение обновлено: {new_path}")
    SpritePro.textures.reload(new_path)

watcher.watch("assets/sprites/", on_image_changed)
```

#### `unwatch(path)`

Останавливает отслеживание указанного пути.

**Параметры:**
- `path` (str) — путь для прекращения мониторинга

```python
watcher.unwatch("assets/sprites/")
```

#### `start()`

Запускает фоновый поток мониторинга.

```python
watcher.start()
```

#### `stop()`

Останавливает мониторинг и освобождает ресурсы.

```python
watcher.stop()
```

#### `update()`

Проверяет изменения в синхронном режиме (вызывается вручную).

```python
watcher.update()
```

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `watched_paths` | list | Список отслеживаемых путей |
| `is_running` | bool | Статус мониторинга |

## Практические примеры

### Автоматическая перезагрузка текстур

```python
from spritePro import SpritePro
from spritePro.resource_watcher import ResourceWatcher

class Game(SpritePro):
    def __init__(self):
        super().__init__()
        self.watcher = ResourceWatcher()
        self.sprites = {}
        
    def setup_assets(self):
        self.sprites['player'] = self.load_image("player.png")
        
        self.watcher.watch("assets/", self.on_asset_changed)
        self.watcher.start()
        
    def on_asset_changed(self, path):
        print(f"Изменение обнаружено: {path}")
        if path.endswith('.png'):
            self.reload_sprite(path)
            
    def reload_sprite(self, path):
        if path in self.sprites:
            self.sprites[path] = self.load_image(path)
            print(f"Спрайт перезагружен: {path}")
```

### Режим разработки с Hot Reload

```python
class DevGame(SpritePro):
    DEV_MODE = True
    
    def __init__(self):
        super().__init__()
        if self.DEV_MODE:
            self.setup_hot_reload()
            
    def setup_hot_reload(self):
        self.watcher = ResourceWatcher()
        
        asset_paths = [
            ("assets/images/", self.on_image_changed),
            ("assets/audio/", self.on_audio_changed),
            ("assets/fonts/", self.on_font_changed),
        ]
        
        for path, callback in asset_paths:
            self.watcher.watch(path, callback)
            
        self.watcher.start()
        
    def on_image_changed(self, path):
        print(f"[HotReload] Изображение обновлено: {path}")
        
    def on_audio_changed(self, path):
        print(f"[HotReload] Звук обновлен: {path}")
        
    def on_font_changed(self, path):
        print(f"[HotReload] Шрифт обновлен: {path}")
```

### Фильтрация по расширению

```python
def filtered_watcher(path):
    ext = path.split('.')[-1].lower()
    if ext in ('png', 'jpg', 'bmp'):
        print(f"Изображение изменено: {path}")
    elif ext in ('wav', 'ogg', 'mp3'):
        print(f"Звук изменен: {path}")

watcher.watch("assets/", filtered_watcher)
```

## Интеграция с системой кэширования

```python
from spritePro.resources import ResourceCache

class CachedGame(SpritePro):
    def __init__(self):
        super().__init__()
        self.cache = ResourceCache()
        self.watcher = ResourceWatcher()
        
    def load_cached_image(self, path):
        if self.cache.has(path):
            return self.cache.get(path)
        return self.load_and_cache(path)
        
    def load_and_cache(self, path):
        image = self.load_image(path)
        self.cache.set(path, image)
        return image
        
    def on_asset_changed(self, path):
        self.cache.invalidate(path)
        print(f"Кэш сброшен для: {path}")
```

## Настройки интервала проверки

```python
watcher = ResourceWatcher(check_interval=0.5)  # Проверка каждые 0.5 секунды
```

## Обработка ошибок

```python
def safe_asset_loader(path):
    try:
        return watcher.watch(path, on_change)
    except FileNotFoundError:
        print(f"Файл не найден: {path}")
    except PermissionError:
        print(f"Нет доступа к файлу: {path}")
```

## Лучшие практики

1. **Используйте в режиме разработки** — отключайте мониторинг в продакшене для производительности
2. **Фильтруйте события** — проверяйте расширения файлов перед обработкой
3. **Очищайте ресурсы** — останавливайте watcher при выходе из приложения
4. **Кэшируйте умеренно** — не перезагружайте все ресурсы при каждом изменении

## Полный пример

```python
from spritePro import SpritePro
from spritePro.resource_watcher import ResourceWatcher

class HotReloadGame(SpritePro):
    def __init__(self):
        super().__init__("Hot Reload Demo", 800, 600)
        self.watcher = ResourceWatcher()
        self.loaded_assets = {}
        
    def on_ready(self):
        self.setup_hot_reload()
        self.load_all_assets()
        
    def setup_hot_reload(self):
        callbacks = {
            'images': self.reload_image,
            'audio': self.reload_audio,
        }
        
        for category, callback in callbacks.items():
            self.watcher.watch(f"assets/{category}/", callback)
            
        self.watcher.start()
        
    def load_all_assets(self):
        for name, path in [("player", "assets/images/player.png")]:
            self.loaded_assets[name] = self.load_image(path)
            
    def reload_image(self, path):
        print(f"Перезагрузка изображения: {path}")
        self.loaded_assets[path] = self.load_image(path)
        
    def reload_audio(self, path):
        print(f"Перезагрузка звука: {path}")
        
    def on_exit(self):
        self.watcher.stop()
        super().on_exit()
```
