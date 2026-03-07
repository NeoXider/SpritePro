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

Установите mobile-зависимости:

```bash
pip install "spritepro[kivy]"
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

Если вы работаете из исходников SpritePro, а не из опубликованного пакета:

```bash
pip install -e ".[kivy]"
```

### Тестирование на разных экранах до Android build

Перед реальной сборкой полезно прогнать одну и ту же игру на нескольких размерах окна в desktop-preview через `platform="kivy"`.

Самый быстрый способ теперь через CLI:

```bash
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen phone-tall
python -m spritePro.cli --preview main.py --platform kivy --screen phone-landscape
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --preview main.py --platform pygame --size 412x915
python -m spritePro.cli --list-screen-presets
```

Команда `--preview`:

- принимает путь к `main.py` или к папке проекта
- временно подменяет размер окна
- для scene-based игр на `s.run(...)` может быстро переключать `pygame` / `kivy`
- помогает быстро увидеть расхождения layout до Android build

Пример:

```python
import spritePro as s


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (96, 96), s.WH_C, scene=self)
        self.player.set_rect_shape((96, 96), (90, 210, 255), border_radius=24)


s.run(
    scene=MainScene,
    size=(360, 640),
    title="Phone Portrait Preview",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

Что стоит проверить хотя бы в нескольких профилях:

- `size=(360, 640)` — компактный phone portrait
- `size=(412, 915)` — современный высокий phone portrait
- `size=(640, 360)` — compact landscape
- `size=(1280, 720)` — tablet / desktop-preview landscape

На что смотреть:

- не уезжает ли UI за края
- хватает ли размеров hitbox и кнопок под touch
- корректно ли выглядят `screen_space`-элементы
- не завязана ли логика на один фиксированный `s.WH`
- одинаково ли ведут себя `pygame` и `kivy`
- помните, что в `Kivy` при resize `s.WH` и `s.WH_C` обновляются, но уже созданные объекты не relayout'ятся автоматически

### Android: рекомендуемый путь

Для Android-сборки обычно используется `Buildozer`.

Важно:

- `Buildozer` официально удобнее всего запускать на Linux
- на Windows обычно используют `WSL` или отдельную Linux-машину
- собирать проект лучше внутри Linux filesystem/WSL home, а не из Windows-диска
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

`Buildozer` ставится и запускается внутри Linux/WSL-окружения.

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

Если вы тестируете не опубликованный `spritepro`, а локально модифицированную версию, заранее проверьте, как именно библиотека попадёт в Android build:

- либо используйте опубликованный пакет `spritepro`
- либо собирайте/подключайте свою локальную версию отдельно и проверяйте это до финальной сборки

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
