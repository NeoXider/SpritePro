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

Практический смысл такого preview:

- не нужно тестировать mobile-layout только через большое fullscreen-окно на ПК
- на небольшом мониторе удобнее гонять логические профили `360x640`, `412x915`, `640x360`, `1280x720`
- это позволяет быстро заметить, что UI или игровая сцена становятся визуально слишком мелкими на больших экранах
- сначала удобно отладить поведение в компактных окнах, а потом уже сверить результат на реальном телефоне

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
- если fullscreen на телефоне визуально делает игру "слишком мелкой", проверьте сцену в нескольких portrait/landscape профилях, а не только в одном desktop-окне

### Android: рекомендуемый путь

Для Android-сборки обычно используется `Buildozer`.

Важно:

- `Buildozer` официально удобнее всего запускать на Linux
- на Windows обычно используют `WSL` или отдельную Linux-машину
- собирать проект лучше внутри Linux filesystem/WSL home, а не из Windows-диска
- на Android нужно заранее продумать ассеты, ориентацию экрана и touch-управление
- для `pygame`-приложений на `SpritePro` надёжнее использовать проверенную связку `python-for-android` с `Python 3.10.12`, а не `Python 3.11`

### Проверенная конфигурация для `pygame`/`SpritePro`

На практике рабочая Android-сборка для `SpritePro` + `pygame` сейчас выглядит так:

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

Почему именно так:

- старый `pygame` recipe в `python-for-android` конфликтует с `Python 3.11` и часто падает на C API ошибках
- `Python 3.10.12` для этой связки заметно стабильнее
- `arm64-v8a` упрощает сборку и убирает лишние ABI
- если используете `Buildozer` локально, полезно зафиксировать `Cython 0.29.33`

Что дополнительно было проверено на реальном устройстве:

- APK не только собирается, но и запускается с этим стеком
- для mobile-host на Android важно не использовать устаревший bundle `SpritePro`, если вы тестируете свежие локальные фиксы
- при проблемах старта быстрее всего сразу смотреть `adb logcat`, а не гадать по splash screen

### Быстрый путь через `spritePro.cli`

Если проект уже имеет `main.py`, самый удобный путь теперь такой:

```bash
python -m spritePro.cli --android .
```

Что делает команда:

- находит `main.py` в проекте
- создаёт `buildozer.spec`, если его ещё нет
- подставляет базовые настройки для Android build
- включает типичные расширения файлов из проекта: код, `assets/images`, `assets/audio`, `scenes`, JSON, шрифты и другие файлы по расширению
- на Linux/WSL сразу запускает `buildozer android debug`

После генерации `buildozer.spec` для `pygame`-игры на `SpritePro` обязательно проверьте и при необходимости замените `requirements` на проверенную конфигурацию:

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

Если нужен только `buildozer.spec`, без запуска сборки:

```bash
python -m spritePro.cli --android . --android-mode spec
```

Если хотите перегенерировать `buildozer.spec` под значения SpritePro:

```bash
python -m spritePro.cli --android . --android-mode spec --android-refresh-spec
```

Release APK:

```bash
python -m spritePro.cli --android . --android-mode release
```

AAB для Google Play:

```bash
python -m spritePro.cli --android . --android-mode aab
```

Часто полезные override-параметры:

```bash
python -m spritePro.cli --android . --android-title "My Game" --android-package-name mygame --android-package-domain com.example --android-orientation landscape
python -m spritePro.cli --android . --android-orientation portrait
python -m spritePro.cli --android . --android-orientation auto
python -m spritePro.cli --android . --android-permission INTERNET
```

Ориентация APK:

- `landscape` — режим по умолчанию
- `portrait` — фиксированный portrait
- `auto` — автоповорот устройства

Для `auto` в итоговом Android-конфиге используется `orientation = all`.

Что стоит проверить в `buildozer.spec` после генерации:

- `requirements = python3,kivy,pygame,pymunk,spritepro`
- для стабильной Android-сборки `pygame`-игры замените строку выше на `python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro`
- `source.dir = .`
- `source.include_exts` включает картинки, аудио, JSON, шрифты, `.kv`, `.atlas`
- `source.exclude_dirs` убирает `.git`, `.venv`, `build`, `dist` и другие служебные папки
- `android.archs = arm64-v8a` полезно задать явно

Это удобно для проектов, созданных через `spritePro.cli --create`, потому что их структура уже соответствует ожидаемому шаблону:

- `main.py`
- `assets/images`
- `assets/audio`
- `scenes`

Если у вас hybrid-режим через `s.run_kivy_hybrid(...)` или `s.create_kivy_widget(...)`, команда та же самая. Для упаковки Android это обычное `Kivy`-приложение с вашим `main.py`.

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

### Напрямую через Buildozer

`Buildozer` ставится и запускается внутри Linux/WSL-окружения.

Установка:

```bash
python3 -m pip install buildozer "cython==0.29.33"
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
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
orientation = landscape
fullscreen = 1
android.archs = arm64-v8a
```

Если нужен автоповорот, замените:

```ini
orientation = all
```

Эта ручная схема нужна, если:

- вы не хотите использовать `spritePro.cli --android`
- у вас уже есть свой настроенный `buildozer.spec`
- вы хотите тонко контролировать Android-конфиг вручную

Если вы тестируете не опубликованный `spritepro`, а локально модифицированную версию, заранее проверьте, как именно библиотека попадёт в Android build:

- либо используйте опубликованный пакет `spritepro`
- либо собирайте/подключайте свою локальную версию отдельно и проверяйте это до финальной сборки
- либо явно копируйте актуальную папку `spritePro/` в сам проект игры перед `buildozer android debug`, чтобы APK точно упаковал свежий код, а не старую зависимость из окружения

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

### Проверенный сценарий для Windows + WSL

Если вы собираете из Windows, самый надёжный flow такой:

1. Установить `WSL2` и `Ubuntu`.
1. Скопировать проект игры в Linux home, например в `~/MyGame`, а не собирать из `/mnt/c/...`.
1. Если нужен локальный исходный `SpritePro`, тоже скопировать репозиторий в Linux home и установить его там.
1. Сгенерировать `buildozer.spec` через `spritePro.cli` или вручную.
1. Зафиксировать в `buildozer.spec`:

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

1. Запустить `buildozer android debug`.

Именно такой сценарий уже был проверен на реальной сборке `SpritePro`-игры в `apk`.

Если игра собирается на локальных непубликованных фикcах `SpritePro`, добавьте ещё один шаг между копированием проекта и сборкой:

1. Синхронизировать свежую папку `spritePro/` в каталог игры или убедиться, что Android build берёт именно ваш локальный пакет, а не старую версию из Python environment.

### Проверка после установки APK

Если APK установился, но игра не открывается как ожидается, сначала не пересобирайте вслепую, а снимите лог:

```bash
adb logcat -c
adb shell monkey -p org.example.mygame -c android.intent.category.LAUNCHER 1
adb logcat -d
```

Что искать в выводе:

- `Traceback` — обычная Python-ошибка внутри игры или библиотеки
- `Py_Exit` / `Process ... has died` — приложение закрылось слишком рано, часто ещё на bootstrap-этапе
- путь к `main.py`, `spritePro/...` и тип ошибки (`AttributeError`, `TypeError`, `ImportError`) — это обычно уже даёт точное место фикса

Если у приложения уже есть экран ошибки от SpritePro mobile-host, дополнительно проверьте файлы `debug.log` и `spritepro_mobile_crash.log` внутри sandbox приложения.

### Что важно для mobile

- не рассчитывайте только на клавиатуру
- делайте UI и hitbox крупнее, чем на desktop
- проверяйте производительность на реальном устройстве
- избегайте слишком тяжёлых текстур и большого количества частиц
- для локального мультиплеера по Wi-Fi проверьте права сети и доступность IP хоста
- если используете hybrid `Kivy` UI, проверьте отдельно и размеры внешнего layout, и размеры встроенной игровой области

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
