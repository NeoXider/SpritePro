# Мониторинг ресурсов (Hot Reload)

Автоматическая перезагрузка ассетов при изменении на диске.

## ResourceWatcher

```python
from spritePro.resource_watcher import ResourceWatcher

watcher = ResourceWatcher()
```

## Методы

| Метод | Описание |
|-------|----------|
| `watch(path, callback)` | Начать отслеживание |
| `unwatch(path)` | Прекратить отслеживание |
| `start()` | Запустить мониторинг |
| `stop()` | Остановить мониторинг |
| `update()` | Проверить изменения синхронно |

## Свойства

```python
watcher.watched_paths   # Список путей
watcher.is_running     # Статус
```

## Пример: автоматическая перезагрузка

```python
def on_asset_changed(path):
    print(f"Изменено: {path}")
    if path.endswith('.png'):
        self.reload_sprite(path)

watcher.watch("assets/", on_asset_changed)
watcher.start()
```

## Hot Reload в режиме разработки

```python
class DevGame(s.Scene):
    DEV_MODE = True
    
    def __init__(self):
        super().__init__()
        if self.DEV_MODE:
            self.setup_hot_reload()
            
    def setup_hot_reload(self):
        self.watcher = ResourceWatcher()
        self.watcher.watch("assets/images/", self.on_image_changed)
        self.watcher.watch("assets/audio/", self.on_audio_changed)
        self.watcher.start()
        
    def on_image_changed(self, path):
        print(f"[HotReload] Изображение: {path}")
```

## Фильтрация

```python
def filtered_watcher(path):
    ext = path.split('.')[-1].lower()
    if ext in ('png', 'jpg'):
        print(f"Изображение: {path}")
    elif ext in ('wav', 'ogg', 'mp3'):
        print(f"Звук: {path}")

watcher.watch("assets/", filtered_watcher)
```

## Настройки

```python
watcher = ResourceWatcher(check_interval=0.5)  # Проверка каждые 0.5 сек
```

## Рекомендации

- Используйте только в режиме разработки
- Фильтруйте события по расширению
- Останавливайте watcher при выходе
- Не перезагружайте все ресурсы сразу
