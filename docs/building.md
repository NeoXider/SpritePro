# Сборка и билд SpritePro

Этот документ про два сценария:

1. Как собрать саму библиотеку `SpritePro` в `wheel`/`sdist`
2. Как собирать игры на `SpritePro` для `desktop`, `web` и `mobile`

Если нужен только mobile runtime и запуск на телефоне, сначала посмотрите [mobile.md](mobile.md).

---

## Что выбрать

| Цель | Инструмент | Когда использовать |
|------|------------|--------------------|
| Проверить игру локально на ПК | `python main.py` или `python -m ...` | Обычный dev-цикл |
| Собрать библиотеку | `python -m build` | Публикация пакета / проверка wheel |
| Сделать web build | `pygbag` / `spritepro --webgl` | HTML5 / браузер |
| Сделать Android build | `Kivy` + `Buildozer` | APK/AAB для Android |
| Сделать desktop `.exe` | `PyInstaller` или аналог | Распространяемый desktop build |

---

## 1. Сборка библиотеки

### Подготовка

```bash
pip install --upgrade build
```

### Сборка wheel и sdist

Из корня репозитория:

```bash
python -m build
```

Результат появится в папке `dist/`:

- `*.whl` — wheel-пакет
- `*.tar.gz` — source distribution

### Проверка локальной установки wheel

```bash
pip install dist/<имя-файла>.whl
```

Если вы тестируете текущий исходный код без пересборки:

```bash
pip install -e .
```

---

## 2. Запуск и сборка игры на desktop

### Обычный запуск

```bash
python main.py
```

или:

```bash
python -m my_game.main
```

### Рекомендуемый стиль запуска

Для новых игр используйте `s.run(...)` и `Scene`:

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=MainScene, size=(800, 600), title="My Game")
```

Для desktop отдельно указывать платформу не нужно, но можно явно:

```python
s.run(scene=MainScene, platform="pygame")
```

### Сборка `.exe`

SpritePro не привязан к одному packager, но для Windows чаще всего подходит `PyInstaller`.

Установка:

```bash
pip install pyinstaller
```

Базовая сборка:

```bash
pyinstaller --onefile --windowed main.py
```

Если у игры есть ассеты, обычно удобнее собирать не в один файл, а в папку:

```bash
pyinstaller --windowed main.py
```

Потом проверьте:

- корректные пути к `assets/`
- что изображения, звуки и JSON-сцены попали в билд
- что рабочая директория не ломает загрузку файлов

Практически всегда лучше использовать относительные пути от папки проекта или отдельную функцию-резолвер пути.

---

## 3. Web build

Для web-версии в SpritePro уже есть отдельная документация:

- [pygame_to_web.md](pygame_to_web.md)

Ниже короткий рабочий сценарий.

### Установка

```bash
pip install pygbag
```

### Прямая сборка через pygbag

```bash
python -m pygbag .
```

или только сборка:

```bash
python -m pygbag . --build
```

### Через инструменты SpritePro

Если в проекте уже используется CLI/обвязка SpritePro для web:

```bash
spritepro --webgl . --archive
```

Это удобно, если вам нужен готовый архив для публикации.

### Что проверить перед web build

- пути к ассетам без жёсткой привязки к локальным папкам
- отсутствие desktop-only зависимостей
- обработку паузы/возврата во вкладку
- ввод мышью и touch, если игра должна работать на mobile browser

---

## 4. Mobile build через Kivy

### Как это работает

Теперь `SpritePro` может запускать игру внутри `Kivy` host:

```python
s.run(scene=MainScene, platform="kivy")
```

Это тот же игровой код, но с другим host-приложением и touch-вводом.

### Локальная проверка mobile-режима на ПК

Установите `Kivy`:

```bash
pip install kivy
```

Запустите игру:

```python
s.run(scene=MainScene, size=(800, 600), title="My Mobile Game", platform="kivy")
```

Или используйте готовые demo:

```bash
python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
python -m spritePro.demoGames.builder_demo --kivy
```

### Android: рекомендуемый путь

Для Android-сборки обычно используется `Buildozer`.

Важно:

- `Buildozer` официально удобнее всего запускать на Linux
- на Windows обычно используют `WSL` или отдельную Linux-машину
- на Android нужно заранее продумать ассеты, ориентацию экрана и touch-управление

### Минимальный сценарий сборки Android

1. Подготовьте проект игры с точкой входа `main.py`
2. Убедитесь, что игра запускается через `platform="kivy"`
3. Установите `buildozer`
4. Сгенерируйте `buildozer.spec`
5. Пропишите зависимости
6. Соберите `apk` или `aab`

### Пример `main.py`

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (80, 80), s.WH_C, speed=6, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(
    scene=MainScene,
    size=(1280, 720),
    title="SpritePro Mobile",
    fill_color=(18, 18, 28),
    platform="kivy",
)
```

### Buildozer

Установка:

```bash
pip install buildozer
```

Инициализация:

```bash
buildozer init
```

В `buildozer.spec` обычно нужно проверить как минимум:

```ini
title = My SpritePro Game
package.name = myspriteprogame
package.domain = org.example
source.include_exts = py,png,jpg,jpeg,wav,mp3,json,ttf,atlas
requirements = python3,kivy,pygame,spritepro
orientation = landscape
fullscreen = 1
```

Если игра использует сеть по Wi-Fi:

```ini
android.permissions = INTERNET
```

Сборка debug APK:

```bash
buildozer android debug
```

Сборка release:

```bash
buildozer android release
```

### Что важно для mobile

- не рассчитывайте только на клавиатуру
- делайте UI и hitbox крупнее, чем на desktop
- проверяйте производительность на реальном устройстве
- избегайте слишком тяжёлых текстур и большого количества частиц
- для локального мультиплеера по Wi-Fi проверьте права сети и доступность IP хоста

### iOS

iOS-сборка возможна через стек `kivy-ios`, но это отдельный более сложный сценарий с `Xcode` и `macOS`. В текущей документации основным поддерживаемым путём считается Android через `Kivy + Buildozer`.

---

## 5. Что проверить перед любым билдом

- игра стартует без ошибок из чистого окружения
- все пути к ассетам корректные
- шрифты, изображения, JSON и аудио включены в билд
- нет лишних dev-зависимостей
- demo-режимы и debug-флаги отключены
- размеры окна, ориентация и управление подходят под целевую платформу

---

## 6. Полезные документы

- [mobile.md](mobile.md)
- [pygame_to_web.md](pygame_to_web.md)
- [game_loop.md](game_loop.md)
- [networking.md](networking.md)

Если нужен краткий старт без деталей, вернитесь в [README.md](../README.md).
