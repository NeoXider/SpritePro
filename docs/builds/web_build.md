# Web Build (Веб-сборка)

Игры на Pygame компилируются в WebAssembly через pygbag.

## Установка

```bash
pip install pygbag
```

## Сборка

```bash
python -m pygbag .
# Открыть http://localhost:8000
```

### Через SpritePro CLI

```bash
pip install "spritepro[web]"
spritepro --webgl . --archive
```

## Подготовка кода

### 1. Главный файл — main.py

```python
import asyncio

async def main():
    import spritePro as s

    class MainScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.player = s.Sprite("", (50, 50), s.WH_C, scene=self)

        def update(self, dt):
            self.player.handle_keyboard_input()

    s.run(scene=MainScene, size=(800, 600), title="My Game")


asyncio.run(main())
```

### 2. Важные моменты

- Точка входа должна быть `main.py`
- Игровой цикл в `async def main()` с `await asyncio.sleep(0)`
- Только OGG для звука (MP3/WAV не поддерживаются)
- Пути только с прямыми слэшами `/`

## Сборка для публикации

```bash
pygbag my_game --build          # Только билд
pygbag my_game --archive       # ZIP для Яндекс.Игры, itch.io
```

## Площадки

### Яндекс Игры

- Требуется Yandex Games SDK
- ZIP-архив: `index.html` в корне + файлы билда
- Звук должен приглушаться при сворачивании

### CrazyGames

- До 50 MB до первого кадра (мобильная версия — 20 MB)
- Требуется SDK (событие "Gameplay start")
- Относительные пути к файлам

## Ограничения

| Что | Ограничение |
|-----|-------------|
| Аудио | Только OGG |
| Сеть | Нет TCP-сокетов (для мультиплеера — WebSocket) |
| Файлы | Только внутри проекта |

## Демо

```bash
python -m spritePro.demoGames.particle_demo
```
