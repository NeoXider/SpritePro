<div align="center">

# 🎮 [SpritePro](https://github.com/NeoXider/SpritePro)

### Создавайте 2D-игры на Python быстрее: editor, runtime, physics, UI, mobile и web в одном фреймворке

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-Open%20Source-yellow.svg)](LICENSE)

**SpritePro** помогает перейти от идеи к играбельному прототипу без тонны инфраструктурного кода.

**Меньше борьбы с циклом, камерой, UI, физикой и layout. Больше времени на саму игру.**

![Demo](https://github.com/user-attachments/assets/db56e1fd-0db5-4353-945d-c4a31c6b9d7f)

</div>

---

## Почему это интересно

SpritePro — это не просто обёртка над `pygame`. Это **высокоуровневый 2D game framework** с единым developer flow:

- **Desktop, web и mobile** из одной кодовой базы
- **Scene-based архитектура**, а не разрозненные скрипты
- **Встроенный Sprite Editor** с JSON-сценами и запуском игры прямо из editor
- **Камера, физика, частицы, UI, tween, audio, save/load, multiplayer** уже внутри
- **Reference resolution**, resize-aware runtime и путь к Android/Kivy без переписывания логики

Если коротко: `pygame` даёт низкий уровень. **SpritePro даёт темп разработки.**

---

## Что даёт SpritePro

### Быстрое прототипирование

Вместо ручной сборки игрового цикла, слоёв, камеры, UI и служебного кода:

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("player.png", (50, 50), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=MainScene, size=(800, 600), title="My Game", fill_color=(20, 20, 30))
```

Это уже полноценный рабочий старт: scene lifecycle, rendering, input, runtime loop и готовая точка расширения.

### Один фреймворк, а не набор разрозненных решений

| Что обычно приходится собирать вручную | Что уже есть в SpritePro |
| --- | --- |
| Рендер-цикл и обновление | `s.run(...)`, `Scene`, auto-render |
| Камера и слежение | Camera API, follow, zoom, shake |
| UI-слой | `Button`, `ToggleButton`, `TextSprite`, `Slider`, `TextInput`, `Layout` |
| Физика | `pymunk`-интеграция, типы тел, коллизии, сцены из editor |
| Частицы и эффекты | `ParticleEmitter`, presets, color/tween tools |
| Сохранения | `PlayerPrefs`, save/load helpers |
| Визуальная сборка уровней | Sprite Editor + `spawn_scene(...)` |
| Mobile/web flow | `platform="kivy"`, `pygbag`, build docs |

### Сильные стороны проекта

- **Scene-first подход**: удобно масштабировать игру, а не только прототип
- **Editor-first workflow**: сцены можно собирать визуально и поднимать в рантайм как объекты
- **Unity-like удобства**: PlayerPrefs, scene runtime, визуальный editor, tooling, callbacks
- **Не отрезает от pygame**: при необходимости можно спускаться на низкий уровень
- **Подходит и для solo-dev, и для команды**: editor settings и JSON-сцены удобно переносить между проектами и разработчиками

---

## Sprite Editor

В `SpritePro` встроен **визуальный редактор сцен**: можно собирать уровни мышью, сохранять в JSON и запускать игру прямо из editor.

<img width="800" alt="Sprite Editor" src="https://github.com/user-attachments/assets/01947bfe-d5e6-40cb-ba75-c03f2d4aeb9d" />

### Что уже умеет editor

- `File / GameObject / Tools / View` меню
- `Image`, `Text`, `Rectangle`, `Circle`, `Ellipse`
- Hierarchy с **мини-превью объектов**
- Inspector со свойствами объекта и text-полями
- gizmo с подписями угла, координат и размера
- запуск игры через `Run` или `F5`
- окно `Settings` с сохранением, импортом и экспортом editor-настроек

### Запуск editor

```bash
python -m spritePro.cli --editor
python -m spritePro.cli -e
```

### Что дальше

1. Собираете сцену визуально
2. Сохраняете её в JSON
3. Загружаете в игре через `spawn_scene("scene.json", scene=...)`
4. Получаете объекты по имени и навешиваете логику

Подробнее: [docs/sprite_editor.md](docs/sprite_editor.md)

---

## Быстрый старт

### Установка

```bash
pip install spritepro
```

Для mobile host-режима:

```bash
pip install "spritepro[kivy]"
```

### Первая игра

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=MainScene, size=(800, 600), title="My Game", fill_color=(20, 20, 30))
```

**Вот и всё.** У вас уже есть окно, сцена, игровой цикл, рендер и управление.

### Если нужен готовый шаблон проекта

```bash
python -m spritePro.cli --create
```

Команда создаёт структуру проекта с `main.py`, `config.py`, `assets/`, `scenes/` и стартовой scene-based архитектурой.

---

## Когда SpritePro особенно хорош

- когда вы хотите **быстро делать играбельные прототипы**
- когда вам нужен **визуальный editor**, а не только код
- когда хочется **pygame-экосистему**, но без постоянной рутины
- когда важен путь к **mobile/web**, а не только desktop
- когда хочется фреймворк, который можно начать просто, а потом масштабировать

---

## 🚀 Быстрый старт (30 секунд)

### Установка

#### Способ 1: Установка через pip (рекомендуемый)

Это самый простой и быстрый способ начать работу со SpritePro.

```bash
pip install spritepro
```
Все зависимости, включая `pygame`, будут установлены автоматически.

Для мобильного host-режима:

```bash
pip install "spritepro[kivy]"
```

#### Обновление

Чтобы обновить SpritePro до последней версии, используйте команду:
```bash
pip install --upgrade spritepro
```

#### Способ 2: Для разработчиков (из исходного кода)

Этот способ подходит, если вы хотите внести свой вклад в разработку или использовать самую последнюю, еще не опубликованную версию.

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/NeoXider/SpritePro.git
    ```

2.  **Перейдите в папку проекта:**
    ```bash
    cd SpritePro
    ```
3.  **(Опционально) Установите в режиме редактирования:**
    ```bash
    pip install -e .
    ```
    Это позволит вам изменять код библиотеки и сразу видеть изменения в своих проектах.

### Ваша первая игра

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=MainScene, size=(800, 600), title="My Game", fill_color=(20, 20, 30))
```

**Вот и всё!** У вас уже есть игра с управлением, отрисовкой и игровым циклом. Для mobile достаточно сменить `platform` на `"kivy"`. 🎮

Для файлов ассетов задавайте путь явно от текущего файла, а не от рабочей папки:

```python
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "images"

def asset_path(name: str) -> str:
    return str((ASSETS_DIR / name).resolve())
```

Такой способ одинаково корректно работает и в `pygame`, и в `kivy`. Подробности: [docs/mobile.md](docs/mobile.md).

### ⚡ Быстрый старт 2.0 (шаблон проекта)

```bash
python -m spritePro.cli --create
```

Создаст `main.py` в текущей папке и структуру `assets/audio`, `assets/images`, `scenes`.
Шаблон теперь сразу современный:

- `main.py` запускает игру через `s.run(...)`
- `config.py` — общие настройки игры и готовые пути `PROJECT_ROOT`, `ASSETS_DIR`, `AUDIO_DIR`, `IMAGES_DIR`, `SCENES_DIR`, `GAME_DIR`, `DOMAIN_DIR`, `SERVICES_DIR`
- `game_events.py` — базовый файл для `EventBus`: событие старта игры, подписка и лог
- `scenes/main_scene.py` — основная сцена, которая грузит `config.MAIN_LEVEL_PATH`
- `scenes/second_scene.py` — вторая почти пустая сцена-заготовка, чтобы было удобно расширять проект
- `scenes/main_level.json` — стартовый уровень в формате Sprite Editor
- `game/domain/game_state.py` — пример domain-модели
- `game/services/game_service.py` — пример сервиса для игровой логики

То есть новый проект после `--create` уже показывает нормальную scene-based структуру, а не только один файл с ручным циклом.

Если хотите создать проект в отдельной папке, укажите путь:
```bash
python -m spritePro.cli --create MyGame
```

## 📱 Mobile и Build

### Mobile игры

Теперь на SpritePro можно делать и мобильные 2D-игры. Идея простая:

```python
s.run(scene=MainScene, platform="pygame")
s.run(scene=MainScene, platform="kivy")
```

То есть логика игры остаётся той же, меняется только host-платформа.

Полезные ссылки:

- [Mobile guide](docs/mobile.md) — как устроен Kivy runtime и touch-ввод
- [Hybrid Kivy UI guide](docs/kivy_hybrid.md) — Kivy menu/layout + встроенная игровая область SpritePro
- [Build guide](docs/building.md) — как собирать library, web и mobile build, включая два Android-сценария: локальные правки `SpritePro` и проверка через `pip`

Быстрый preview разных экранов через CLI:

```bash
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen phone-tall
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --preview main.py --platform pygame --size 412x915
python -m spritePro.cli --list-screen-presets
```

Практически это нужно не только для mobile-layout, но и для обычной разработки на небольшом мониторе:

- не обязательно открывать огромное окно или нативное `4K`, чтобы проверить mobile-сцену
- удобнее тестировать через логические размеры окна вроде `360x640`, `412x915`, `640x360`, `1280x720`
- на реальном телефоне fullscreen-игра может визуально выглядеть мельче, чем в маленьком desktop-окне, поэтому layout лучше сверять на нескольких профилях, а не на одном размере
- если игра использует `s.WH` и `s.WH_C`, помните: при resize они обновляются, но уже созданные объекты не перестраиваются автоматически без вашего relayout-кода

Быстрая Android/APK-сборка через CLI:

```bash
python -m spritePro.cli --android .
python -m spritePro.cli --android . --android-mode release
python -m spritePro.cli --android . --android-mode spec
python -m spritePro.cli --android . --android-orientation portrait
python -m spritePro.cli --android . --android-orientation auto
```

По ориентации:

- `landscape` — режим по умолчанию
- `portrait` — принудительный портретный режим
- `auto` — автоповорот устройства

Для `pygame`-игр на Android используйте проверенную конфигурацию `Buildozer`:

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

И собирать проект лучше внутри `WSL/Linux home`, а не из `/mnt/c/...`.

Если вы проверяете не опубликованный `spritepro`, а локальные свежие правки библиотеки, не полагайтесь на старый пакет из окружения сборки:

- либо сначала соберите/установите актуальную локальную версию `SpritePro`
- либо явно включите папку `spritePro/` в проект игры перед Android build

После первой установки APK удобно сразу проверить запуск через `adb logcat`, чтобы быстро поймать Python traceback, если приложение не доходит до игрового экрана.

Полный рабочий flow: [docs/building.md](docs/building.md).

### Что уже работает

- desktop runtime через `pygame`
- web build через `pygbag`
- mobile host через `Kivy`
- hybrid-режим: `Kivy` UI + встроенный `SpritePro`-виджет
- demo, которые можно запускать через `--kivy`

### Отдельная инструкция по сборке

Подробный гайд вынесен в отдельный файл:

- [docs/building.md](docs/building.md)

---

## 💡 Примеры "Вау!" возможностей

### 🎨 Создайте игру за минуту

```python
import spritePro as s

class PlatformerScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("player.png", (50, 50), (100, 300), speed=5, scene=self)
        self.platforms = [
            s.Sprite("", (200, 20), (200, 400), scene=self),
            s.Sprite("", (200, 20), (500, 350), scene=self),
        ]
        self.emitter = s.ParticleEmitter(s.ParticleConfig(
            amount=10,
            speed_range=(50, 100),
            lifetime_range=(0.5, 1.0),
        ))

        self.player.set_collision_targets(self.platforms)
        s.set_camera_follow(self.player)

    def update(self, dt):
        self.player.handle_keyboard_input()
        if self.player.velocity.length() > 0:
            self.emitter.emit(self.player.rect.center)

s.run(scene=PlatformerScene, size=(800, 600), title="Platformer", fill_color=(135, 206, 235))
```

**Результат:** Полноценная платформер-игра с физикой, камерой и эффектами!

### 🎵 Звук и музыка - проще некуда

```python
# Получаем готовый AudioManager
audio = s.audio_manager

# Вариант 1: Загружаем и сохраняем для многократного использования
jump_sound = audio.load_sound("jump", "sounds/jump.mp3")
jump_sound.play()  # Автоматически применяются настройки громкости!

# Вариант 2: Прямое воспроизведение по пути (без загрузки!)
audio.play_sound("sounds/jump.mp3")  # Автоматически загрузит и воспроизведет!
audio.play_sound("sounds/coin.wav", volume=0.8)  # С кастомной громкостью

# Вариант 3: В одну строку для быстрого воспроизведения
audio.load_sound("explosion", "sounds/explosion.mp3").play()

# Музыка
audio.play_music("music/background.mp3", volume=0.5)  # Сразу с нужной громкостью!
# Или установить громкость отдельно
audio.set_music_volume(0.5)  # 50% громкости
```

**Никаких** `pygame.mixer.Sound()`, **никаких** ручных настроек - всё работает!

### 🎯 UI за секунды

```python
# Кнопка с автоматической анимацией
button = s.Button(
    "", (200, 50), (400, 300),
    "Начать игру",
    on_click=lambda: print("Игра началась!")
)

# Переключатель музыки
music_toggle = s.ToggleButton(
    "", (150, 40), (100, 50),
    text_on="Музыка: ВКЛ",
    text_off="Музыка: ВЫКЛ",
    on_toggle=lambda is_on: s.audio_manager.set_music_enabled(is_on)
)

# Текст с якорем (автоматическое позиционирование!)
score_text = s.TextSprite(
    "Score: 0", 36, (255, 255, 255),
    (s.WH.x - 10, 10),
    anchor=s.Anchor.TOP_RIGHT  # Прижмется к правому краю!
)
```

**Всё работает автоматически** - наведение, клики, анимации!

### ⌨️ Ввод и события (как в Unity)

```python
import pygame
import spritePro as s

class InputScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.events.on("quit", self.on_quit)

    def on_quit(self, event):
        print("Quit")

    def update(self, dt):
        if s.input.was_pressed(pygame.K_SPACE):
            print("Space pressed")

s.run(scene=InputScene, size=(800, 600), title="Input")
```

Если нужен доступ к сырым событиям pygame — используйте `s.pygame_events`.

### 🧩 Сцены без пересоздания и перезапуск

```python
import spritePro as s

class MainScene(s.Scene):
    def on_enter(self, context):
        pass

s.run(scene=MainScene, size=(800, 600), title="Scenes")

# Перезапуск сцены
s.restart_scene()         # текущая сцена
s.restart_scene("main")   # по имени
```

### 🎆 Частицы - это просто

```python
# Создаем эффект взрыва
explosion = s.ParticleEmitter(s.ParticleConfig(
    amount=50,
    speed_range=(100, 300),
    angle_range=(0, 360),
    lifetime_range=(0.5, 1.5),
    gravity=s.Vector2(0, 200)
))

# Взрыв при клике
explosion.emit(mouse_pos)  # Всё! 50 частиц летят во все стороны!
```

**3 строки кода** = красивый эффект взрыва!

### 💾 Сохранения как в Unity

```python
# Создаем PlayerPrefs
prefs = s.PlayerPrefs("save.json")

# Сохраняем что угодно
prefs.set_float("score", 1250.5)
prefs.set_int("level", 5)
prefs.set_string("player_name", "Hero")
prefs.set_vector2("player_pos", (400, 300))

# Загружаем
score = prefs.get_float("score", 0)
level = prefs.get_int("level", 1)
name = prefs.get_string("player_name", "Player")
pos = prefs.get_vector2("player_pos", (0, 0))

# Всё автоматически сохраняется в JSON!
```

**Никаких** ручных парсеров, **никаких** сложных форматов!

---

## 🎮 Что можно создать?

### ✅ Платформеры
- Автоматические столкновения
- Камера следует за игроком
- Готовые частицы для эффектов

### ✅ Аркады
- Система здоровья из коробки
- Таймеры для событий
- Готовые UI элементы

### ✅ RPG
- Система сохранений
- Инвентарь (через спрайты)
- Диалоги (через TextSprite)

### ✅ Пазлы
- Интерактивные элементы
- Анимации переходов
- Система состояний

### ✅ Tower Defense
- Пути для врагов (через move_towards)
- Система частиц для эффектов
- UI для интерфейса

### ✅ Мультиплеерные игры
- Встроенная сетевая подсистема (NetServer / NetClient, relay)
- Синхронизация позиций, состояний, событий (ready, start, счёт)
- Мини-курс в папке `multiplayer_course/`: уроки 1–10 с примерами, практикой и решениями

### ✅ Мобильные игры
- Запуск той же игры через `platform="kivy"`
- Экранные кнопки, touch-ввод, Kivy-host
- Основа для Android-сборок через Kivy/Buildozer

---

## 📊 Сравнение с альтернативами

| Функция | [pygame](https://www.pygame.org/) | [arcade](https://api.arcade.academy/) | [SpritePro](https://github.com/NeoXider/SpritePro) |
|---------|--------|--------|-----------|
| Автоматическая отрисовка | ❌ | ✅ | ✅ |
| Готовая камера | ❌ | ✅ | ✅ |
| **Физика (2D)** | ❌ | ✅ | ✅ pymunk, типы тел, коллизии |
| **Layout (flex, сетка, круг)** | ❌ | ❌ | ✅ |
| **Редактор сцен (JSON)** | ❌ | ❌ | ✅ |
| **Мультиплеер (TCP, лобби)** | ❌ | ❌ | ✅ |
| Система частиц | ❌ | ❌ | ✅ |
| AudioManager | ❌ | ❌ | ✅ |
| PlayerPrefs | ❌ | ❌ | ✅ |
| Якоря позиционирования | ❌ | ❌ | ✅ |
| Простота использования | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**SpritePro = pygame + физика, Layout, редактор сцен, мультиплеер и всё остальное для игры.**

---

## 🎯 Ключевые преимущества

### 🚀 **Скорость разработки**
- Создайте прототип игры за **минуты**, а не часы
- Меньше кода = меньше багов
- Больше времени на геймплей, меньше на инфраструктуру

### 🎨 **Красота из коробки**
- Автоматические анимации кнопок
- Плавные переходы (tweening)
- Готовые эффекты частиц
- Цветовые эффекты

### 🛠️ **Мощность и гибкость**
- Полный доступ к pygame под капотом
- Расширяемая архитектура
- Можно использовать как pygame, так и высокоуровневые функции

### 📚 **Отличная документация**
- Подробные примеры для каждого компонента
- Демо-игры с исходным кодом
- Понятные API

---

## 🎬 Демо-игры

Все с открытым исходным кодом. Полный список — [DOCUMENTATION_INDEX.md → Демо](DOCUMENTATION_INDEX.md#-демонстрационные-игры).

| Демо | Описание |
|------|----------|
| [Ping Pong](spritePro/demoGames/ping_pong.py) | Игра с меню, звуком, физикой |
| [Physics Demo](spritePro/demoGames/physics_demo.py) | Гравитация, отскок, платформы, статика/кинематика |
| [Mobile Orb Collector](spritePro/demoGames/mobile_orb_collector_demo.py) | Mobile-first demo: экранные кнопки, touch, Kivy |
| [Kivy Hybrid Demo](spritePro/demoGames/kivy_hybrid_demo.py) | Kivy UI + встроенная игровая область SpritePro |
| [demoGames/](demoGames/README.md) | **Сцена из редактора**: level.json, spawn_scene, get_physics, платформер. `python demoGames/main.py` |
| [Fireworks](spritePro/demoGames/fireworks_demo.py) | Частицы |
| [Tween](spritePro/demoGames/tweenDemo.py) | Плавные анимации |
| Мультиплеер | [local_multiplayer_demo](spritePro/demoGames/local_multiplayer_demo.py), курс [multiplayer_course](multiplayer_course/README.md) |

Запуск из корня репозитория: `python -m spritePro.demoGames.physics_demo` или `python demoGames/main.py`.

---

## 📦 Что внутри?

### 🎮 Основные компоненты
- **Sprite** — базовый класс с движением и визуальными эффектами
- **Button**, **ToggleButton** — кнопки и переключатели с анимациями
- **TextSprite** — текст с якорями
- **Bar** — полосы прогресса (HP, опыт)

### ⚙️ Физика
- **pymunk** — мир тел, типы DYNAMIC/STATIC/KINEMATIC, формы (PhysicsShape), гравитация, коллизии. Тело из сцены: `s.get_physics(sprite)`. [docs/physics.md](docs/physics.md)

### 📐 Layout и UI
- **Layout** — автолейаут: flex, сетка, круг, линия; контейнер — спрайт или rect. [docs/layout.md](docs/layout.md)
- **ScrollView** — скроллируемая область (колёсико, перетаскивание)
- Slider, TextInput, Pages — слайдеры, поля ввода, страницы

### 🎨 Игровые системы
- **Animation** — анимации по кадрам
- **Tween** — плавные переходы; Fluent API: `sprite.DoMove(...).SetEase(...)`. [docs/tween.md](docs/tween.md)
- **Timer**, **Health** — таймеры и здоровье
- **ParticleEmitter** — частицы (конфиг, emit)

### 🌐 Мультиплеер
- **NetServer / NetClient**, relay, контекст (send, poll, send_every)
- **Лобби** — экран с именем, хост/клиент, порт, «В игру». [docs/networking.md](docs/networking.md)
- Курс: [multiplayer_course/](multiplayer_course/README.md) — 10 уроков

### 📱 Mobile и build
- **Kivy host** — запуск game loop внутри mobile-оболочки
- **run(platform="kivy") / run_kivy(...)** — full-screen режим по умолчанию
- **run_kivy_hybrid(...) / create_kivy_widget(...)** — Kivy UI вокруг встроенной игровой области
- Подробно: [docs/mobile.md](docs/mobile.md), [docs/kivy_hybrid.md](docs/kivy_hybrid.md), [docs/building.md](docs/building.md)

### 🛠️ Утилиты
- **AudioManager** — звук и музыка
- **PlayerPrefs** — сохранения в JSON
- **Camera** — камера и слежение за объектом
- **Builder** — fluent API для спрайтов и частиц

### 🎨 Редактор сцен
- **Sprite Editor** — сцены в стиле Unity: `File` / `GameObject` / `Tools` / `View`, Hierarchy, Inspector, JSON, `Text`-объекты
- В игре: `spawn_scene("level.json", ...)`, объекты по имени, физика из сцены. [docs/sprite_editor.md](docs/sprite_editor.md)
- Запуск: `python -m spritePro.cli --editor` или `-e`

---

## 📖 Документация

**Главная карта** — [**DOCUMENTATION_INDEX.md**](DOCUMENTATION_INDEX.md): всё по полочкам (старт, основы, физика, редактор, UI, демо, порядок изучения).

| Раздел | Куда смотреть |
|--------|----------------|
| **Старт** | [Установка](#установка), [Первая игра](#ваша-первая-игра), [Шаблон проекта](#-быстрый-старт-20-шаблон-проекта) |
| **Обзор** | [docs/OVERVIEW.md](docs/OVERVIEW.md) — Layout, физика, Builder, мультиплеер кратко |
| **Физика** | [docs/physics.md](docs/physics.md) — pymunk, типы тел, PhysicsShape, сцена из редактора; [docs/physics_issues.md](docs/physics_issues.md) — нюансы |
| **Редактор сцен** | [docs/sprite_editor.md](docs/sprite_editor.md) — редактор, spawn_scene, get_physics из сцены |
| **Демо** | [DOCUMENTATION_INDEX.md → Демо](DOCUMENTATION_INDEX.md#-демонстрационные-игры); сцена из редактора: [demoGames/](demoGames/README.md) |
| **Сеть** | [docs/networking.md](docs/networking.md); курс: [multiplayer_course/](multiplayer_course/README.md) |
| **Mobile** | [docs/mobile.md](docs/mobile.md) — Kivy runtime, touch, mobile demo |
| **Hybrid Kivy UI** | [docs/kivy_hybrid.md](docs/kivy_hybrid.md) — меню/кнопки Kivy + встроенная игра SpritePro |
| **Build** | [docs/building.md](docs/building.md) — library wheel/sdist, web, Android, packaging |
| **Вся документация** | [docs/README.md](docs/README.md) — навигация по docs |

---

## 🎯 Примеры использования

### Игра с меню, звуком и сохранениями

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()

        audio = s.audio_manager
        audio.load_sound("click", "sounds/click.mp3")
        self.click_sound = audio.get_sound("click")
        audio.play_music("music/bg.mp3")

        self.prefs = s.PlayerPrefs("save.json")
        self.high_score = self.prefs.get_int("high_score", 0)
        self.score = 0

        self.start_button = s.Button(
            "", (200, 50), s.WH_C, "Начать игру",
            on_click=lambda: self.click_sound.play(),
            scene=self,
        )
        self.player = s.Sprite("player.png", (50, 50), (100, 300), speed=5, scene=self)
        s.set_camera_follow(self.player)

    def update(self, dt):
        self.player.handle_keyboard_input()
        if self.score > self.high_score:
            self.prefs.set_int("high_score", self.score)

s.run(scene=MainScene, size=(800, 600), title="My Game", fill_color=(20, 20, 30))
```

**Всё работает вместе из коробки!**

---

## 🆚 SpritePro vs Обычный pygame

### ❌ С pygame нужно писать:
```python
# 100+ строк для базовой игры
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
sprites = pygame.sprite.Group()
# ... обработка событий ...
# ... ручная отрисовка ...
# ... ручное управление камерой ...
# ... ручная система слоев ...
# ... и так далее ...
```

### ✅ С SpritePro:
```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("player.png", (50, 50), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=MainScene, size=(800, 600), title="Game")
```

**В 10 раз меньше кода!** 🚀

---

## 🎁 Бонусы

### ✨ Автоматические фичи
- **Автоматическая отрисовка** - создали спрайт? Он уже рисуется!
- **Автоматическое обновление** - Tween, Animation, Timer обновляются сами
- **Автоматическая камера** - слежение за объектами одной строкой
- **Автоматические столкновения** - физика из коробки

### 🎨 Готовые эффекты
- Пульсация, мерцание, волны для кнопок
- Плавные переходы (easing)
- Система частиц
- Цветовые эффекты

### 🛠️ Удобные утилиты
- Якоря позиционирования (как в Unity!)
- PlayerPrefs (как в Unity!)
- AudioManager (централизованное управление звуком)
- Готовые компоненты (Bar, TextSprite, Button)

---

## 🚀 Начните прямо сейчас!

```bash
pip install spritepro
```

Затем — [Ваша первая игра](#ваша-первая-игра) выше или шаблон: `python -m spritePro.cli --create`.

---

## 📊 Статистика

- ⚡ **В 10 раз меньше кода** чем с чистым pygame
- 🚀 **В 5 раз быстрее** разработка прототипов
- 🎯 **100% готовых компонентов** для типичных задач
- 📚 **Полная документация** с примерами
- 🎮 **30+ демо-игр** с исходным кодом

---

## 🤝 Сообщество

- 💬 Вопросы? Откройте [Issue](https://github.com/NeoXider/SpritePro/issues)
- 🐛 Нашли баг? [Сообщите](https://github.com/NeoXider/SpritePro/issues)
- 💡 Есть идея? [Предложите](https://github.com/NeoXider/SpritePro/issues)
- ⭐ Понравилось? Поставьте звезду!

---

## 📄 Лицензия

Открытый исходный код. Используйте свободно в своих проектах!

---

<div align="center">

## 🎮 Начните создавать игры уже сегодня!

**SpritePro - это не просто библиотека. Это ваш путь от идеи к игре!**

[📖 Документация](DOCUMENTATION_INDEX.md) • [🎮 Демо-игры](spritePro/demoGames/) • [💬 Вопросы](https://github.com/NeoXider/SpritePro/issues)

**Создано с ❤️ для разработчиков игр**

</div>
