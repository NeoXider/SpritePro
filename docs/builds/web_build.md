# Web Build (Веб-сборка)

Модуль `web_build.py` предоставляет инструменты для создания веб-версий игр на базе SpritePro.

## Обзор

Веб-сборка позволяет:
- Конвертировать игры в формат для браузера
- Настраивать веб-плеер
- Оптимизировать ассеты для веба
- Управлять разрешениями

## WebBuilder

```python
from spritePro.web_build import WebBuilder

builder = WebBuilder(game_source="my_game.py")
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `game_source` | str | Путь к исходному файлу игры |
| `output_dir` | str | Папка для веб-сборки |
| `title` | str | Название игры в браузере |

### Методы

#### `build()`

Создание веб-сборки.

```python
builder.build()
```

#### `set_canvas_size(width, height)`

Настройка размера canvas.

```python
builder.set_canvas_size(800, 600)
```

#### `enable_touch(enabled=True)`

Включение/выключение поддержки тачскрина.

```python
builder.enable_touch(True)
```

#### `set_background_color(color)`

Установка цвета фона.

```python
builder.set_background_color((0, 0, 0))
```

## WebPlayer

```python
from spritePro.web_build import WebPlayer

player = WebPlayer()
```

### Методы

#### `load_game(url)`

Загрузка игры по URL.

```python
player.load_game("https://example.com/game.html")
```

#### `pause()`

Пауза игры.

#### `resume()`

Возобновление игры.

#### `get_canvas()`

Получение HTML5 Canvas.

```python
canvas = player.get_canvas()
```

## Конфигурация

### Файл конфигурации

```json
{
    "title": "Моя Игра",
    "width": 800,
    "height": 600,
    "background_color": "#000000",
    "touch_enabled": true,
    "fps": 60
}
```

### Python API

```python
config = WebConfig()
config.title = "Моя Игра"
config.width = 800
config.height = 600
config.background_color = (0, 0, 0)
config.fps = 60
config.assets_path = "assets/"
config.main_module = "main"
```

## Сборка проекта

### Шаг 1: Подготовка

```bash
spritepro-web init my_game
cd my_game
```

### Шаг 2: Конфигурация

Отредактируйте `web_config.json`:

```json
{
    "title": "Моя Игра",
    "width": 800,
    "height": 600
}
```

### Шаг 3: Сборка

```bash
spritepro-web build
```

### Шаг 4: Публикация

```bash
spritepro-web serve  # Локальный сервер
# или
spritepro-web deploy # Публикация
```

## Оптимизация для веба

### Сжатие ассетов

```python
builder.optimize_assets(quality=80)
```

### Lazy Loading

```python
builder.enable_lazy_loading(True)
```

### Кэширование

```python
builder.configure_cache(max_age=3600)
```

## HTML-шаблон

```html
<!DOCTYPE html>
<html>
<head>
    <title>Моя Игра</title>
    <script src="spritepro.js"></script>
</head>
<body>
    <canvas id="game"></canvas>
    <script>
        var game = new SpriteProGame('game', {
            width: 800,
            height: 600
        });
        game.start();
    </script>
</body>
</html>
```

## Обработка событий браузера

```python
def on_visibility_change(self, is_visible):
    if not is_visible:
        self.pause()
        
def on_resize(self, width, height):
    self.set_canvas_size(width, height)
```

## Отладка

### Режим отладки

```python
builder.enable_debug(True)
```

### Логирование

```python
builder.set_log_level('debug')
```

## Поддержка браузеров

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Ограничения

- Нет доступа к файловой системе напрямую
- Ограниченный объем памяти
- Нет поддержки некоторых модулей (multiprocessing)

## Лучшие практики

1. **Оптимизируйте ассеты** — сжимайте изображения и звуки
2. **Используйте атласы** — объединяйте спрайты
3. **Ограничьте FPS** — 30-60 FPS достаточно
4. **Тестируйте на мобильных** — проверяйте на реальных устройствах
5. **Предоставьте fallback** — для старых браузеров
