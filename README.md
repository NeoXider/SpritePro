<div align="center">

# 🎮 [SpritePro](https://github.com/NeoXider/SpritePro)

### **Создавайте игры на Python БЫСТРО и ПРОСТО!**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-Open%20Source-yellow.svg)](LICENSE)

**Мощный игровой фреймворк, который превращает создание 2D игр из сложной задачи в удовольствие!**

![Demo](https://github.com/user-attachments/assets/db56e1fd-0db5-4353-945d-c4a31c6b9d7f)

</div>

---

## 🎨 Sprite Editor — визуальный редактор сцен

В SpritePro появился **встроенный редактор спрайтов** в стиле Unity: создавайте сцены визуально, расставляйте объекты мышью и сохраняйте в JSON для использования в игре.

<img width="800" alt="Sprite Editor" src="https://github.com/user-attachments/assets/01947bfe-d5e6-40cb-ba75-c03f2d4aeb9d" />

### Запуск через терминал

```bash
python -m spritePro.cli --editor
```

или коротко:

```bash
python -m spritePro.cli -e
```

### Что делать в редакторе

1. **Добавлять объекты** — кнопки Rect, Circle, Ellipse для примитивов; Add или перетаскивание файлов для изображений.
2. **Редактировать** — инструменты Move (G), Rotate (R), Scale (T); перемещение, вращение, масштаб мышью.
3. **Настраивать** — Inspector справа: имя, позиция, размер, цвет, слой (Sorting Order).
4. **Сохранять** — Ctrl+S или кнопка Save; сцена сохраняется в JSON.
5. **Загружать в игру** — `spawn_scene("scene.json", scene=...)` и получение объектов по имени: `rt.exact("player").Sprite(speed=5)`, `rt.exact("button").to_button(...)`.

Подробнее: [документация редактора](docs/sprite_editor.md).

---

**SpritePro** — это высокоуровневая библиотека для создания 2D игр на Python, построенная на базе Pygame, которая автоматизирует рутинные задачи разработки и предоставляет готовые инструменты для быстрого создания игр.

---

## 📑 Содержание

- [⚡ Почему SpritePro?](#-почему-spritepro)
- [🌟 Что делает SpritePro особенным?](#-что-делает-spritepro-особенным)
- [🚀 Быстрый старт](#-быстрый-старт-30-секунд)
  - [Установка](#установка)
  - [Ваша первая игра](#ваша-первая-игра-5-строк)
- [💡 Примеры "Вау!" возможностей](#-примеры-вау-возможностей)
- [🎮 Что можно создать?](#-что-можно-создать)
- [📊 Сравнение с альтернативами](#-сравнение-с-альтернативами)
- [🎯 Ключевые преимущества](#-ключевые-преимущества)
- [🎬 Демо-игры](#-демо-игры)
- [📦 Что внутри?](#-что-внутри)
- [📖 Документация](#-документация)
- [🎯 Примеры использования](#-примеры-использования)
- [🆚 SpritePro vs Обычный pygame](#-spritepro-vs-обычный-pygame)
- [🎁 Бонусы](#-бонусы)
- [🚀 Начните прямо сейчас!](#-начните-прямо-сейчас)
- [📊 Статистика](#-статистика)
- [🤝 Сообщество](#-сообщество)
- [📄 Лицензия](#-лицензия)

---

## ⚡ Почему SpritePro?

### 🚀 **Вместо этого:**
```python
# С pygame нужно писать ВСЁ самому:
import pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
sprite = pygame.sprite.Sprite()
# ... 50+ строк кода для базовой игры ...
```

### ✨ **С SpritePro:**
```python
# Всё работает из коробки!
import spritePro as s

s.get_screen((800, 600), "My Awesome Game")

player = s.Sprite("player.png", (50, 50), s.WH_C, speed=5)

while True:
    s.update(fill_color=(20, 20, 30))
    player.handle_keyboard_input()  # Готово! Движение работает!
```

**Это всё!** Игра готова за 5 строк кода! 🎉

---

## 🌟 Что делает SpritePro особенным?

### 💎 **Автоматизация всего, что раздражает**

| Обычный pygame | SpritePro |
|----------------|-----------|
| ❌ Ручная отрисовка каждого спрайта | ✅ Автоматическая отрисовка всех спрайтов |
| ❌ Ручное управление камерой | ✅ Камера работает автоматически |
| ❌ Ручная обработка событий | ✅ Встроенная обработка ввода |
| ❌ Ручное управление слоями | ✅ Автоматическая система слоев |
| ❌ Ручное управление звуком | ✅ Готовый AudioManager |
| ❌ Ручная система сохранений | ✅ PlayerPrefs из коробки |
| ❌ Ручная система частиц | ✅ Простой ParticleEmitter |

### 🎯 **Всё, что нужно для игры - уже внутри:**

- ✅ **Автоматическая отрисовка** - просто создайте спрайт, он сам отрисуется
- ✅ **Умная камера** - слежение за объектами одной строкой
- ✅ **Простая физика** - столкновения, гравитация, движение из коробки
- ✅ **Система частиц** - красивые эффекты за 3 строки кода
- ✅ **UI компоненты** - кнопки, переключатели, текст готовы к использованию
- ✅ **Анимации и твининг** - плавные переходы без головной боли
- ✅ **Аудио менеджер** - управление звуком и музыкой централизованно
- ✅ **Система сохранений** - PlayerPrefs как в Unity!
- ✅ **Якоря позиционирования** - размещайте объекты точно где нужно
- ✅ **Автолейаут (Layout)** - flex, сетка, круг, линия для автоматического размещения дочерних спрайтов ([документация](docs/layout.md))
- ✅ **ScrollView** — скроллируемая область для контента (лейаут), колёсико и перетаскивание мышью, опциональная маска (клиппинг по viewport)
- ✅ **Готовые сцены (readyScenes)** — подключаемые сцены: **ChatScene** (мультиплеерный чат с историей, скроллом и маской) и **ChatStyle** для настройки оформления
- ✅ **Мультиплеер** - можно делать сетевые игры: встроенный TCP relay, контекст (send/poll/send_every), EventBus для событий; быстрый старт через `s.networking.run()`. В репозитории есть **мини-курс по мультиплеерным играм** (папка `multiplayer_course/`) — 10 уроков от обмена сообщениями до готовой мини-игры с меню и результатами.

---

## 🚀 Быстрый старт (30 секунд)

### Установка

#### Способ 1: Установка через pip (рекомендуемый)

Это самый простой и быстрый способ начать работу со SpritePro.

```bash
pip install spritepro
```
Все зависимости, включая `pygame`, будут установлены автоматически.

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

### Ваша первая игра (5 строк!)

```python
import spritePro as s

s.get_screen((800, 600), "My Game")

player = s.Sprite("", (50, 50), s.WH_C, speed=5)

while True:
    s.update(fill_color=(20, 20, 30))
    player.handle_keyboard_input()  # Готово! Игра работает!
```

**Вот и всё!** У вас уже есть игра с управлением, отрисовкой и игровым циклом! 🎮

### ⚡ Быстрый старт 2.0 (шаблон проекта)

```bash
python -m spritePro.cli --create
```

Создаст `main.py` в текущей папке и структуру `assets/audio`, `assets/images`, `scenes`.
Также создаст `scenes/level.json` (формат Sprite Editor): сцена по умолчанию загрузит уровень из JSON и возьмёт `player` по имени.

Если хотите создать проект в отдельной папке, укажите путь:
```bash
python -m spritePro.cli --create MyGame
```

---

## 💡 Примеры "Вау!" возможностей

### 🎨 Создайте игру за минуту

```python
import spritePro as s

screen = s.get_screen((800, 600), "Platformer")

# Игрок с автоматическим движением
player = s.Sprite("player.png", (50, 50), (100, 300), speed=5)

# Платформы
platforms = [
    s.Sprite("", (200, 20), (200, 400)),
    s.Sprite("", (200, 20), (500, 350)),
]

# Камера следует за игроком
s.set_camera_follow(player)

# Частицы при движении
emitter = s.ParticleEmitter(s.ParticleConfig(
    amount=10,
    speed_range=(50, 100),
    lifetime_range=(0.5, 1.0)
))

# Настраиваем столкновения один раз (не в цикле!)
player.set_collision_targets(platforms)

while True:
    s.update(fill_color=(135, 206, 235))  # Небо
    
    player.handle_keyboard_input()  # Столкновения обрабатываются автоматически!
    
    # Частицы
    if player.velocity.length() > 0:
        emitter.emit(player.rect.center)
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

s.get_screen((800, 600), "Input")

def on_quit(event):
    print("Quit")

s.events.on("quit", on_quit)

while True:
    s.update()

    if s.input.was_pressed(pygame.K_SPACE):
        print("Space pressed")
```

Если нужен доступ к сырым событиям pygame — используйте `s.pygame_events`.

### 🧩 Сцены без пересоздания и перезапуск

```python
import spritePro as s

class MainScene(s.Scene):
    def on_enter(self, context):
        pass

s.get_screen((800, 600), "Scenes")
manager = s.get_context().scene_manager
manager.add_scene("main", MainScene())
s.register_scene_factory("main", MainScene)
s.set_scene_by_name("main")

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

---

## 📊 Сравнение с альтернативами

| Функция | [pygame](https://www.pygame.org/) | [arcade](https://api.arcade.academy/) | [SpritePro](https://github.com/NeoXider/SpritePro) |
|---------|--------|--------|-----------|
| Автоматическая отрисовка | ❌ | ✅ | ✅ |
| Готовая камера | ❌ | ✅ | ✅ |
| Система частиц | ❌ | ❌ | ✅ |
| AudioManager | ❌ | ❌ | ✅ |
| PlayerPrefs | ❌ | ❌ | ✅ |
| Якоря позиционирования | ❌ | ❌ | ✅ |
| Автоматические столкновения | ❌ | ❌ | ✅ |
| Простота использования | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**SpritePro = pygame + всё необходимое для игры!**

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

**Увидьте SpritePro в действии!** Все демо с открытым исходным кодом:

- 🏓 **[Ping Pong](spritePro/demoGames/ping_pong.py)** - Полноценная игра с меню, звуком и UI
- 🎆 **[Fireworks](spritePro/demoGames/fireworks_demo.py)** - Красивые эффекты частиц
- 🎨 **[Tween Demo](spritePro/demoGames/tweenDemo.py)** - Плавные анимации
- 🎮 **[Among Us Demo](spritePro/demoGames/amongus.py)** - Платформер с взаимодействиями
- 💥 **[Particle Template Test](spritePro/demoGames/particle_template_test.py)** - Интерактивные частицы
- 🌐 **Мультиплеер** - [local_multiplayer_demo](spritePro/demoGames/local_multiplayer_demo.py), [камень/ножницы/бумага](spritePro/demoGames/events_rps_demo.py); полный курс — [multiplayer_course](multiplayer_course/README.md)

**Запустите любую демо-игру и увидьте возможности!**

```bash
python spritePro/demoGames/ping_pong.py
```

---

## 📦 Что внутри?

### 🎮 Основные компоненты
- **Sprite** - Базовый класс с физикой, движением и визуальными эффектами
- **Button** - Готовые кнопки с анимациями
- **ToggleButton** - Переключатели
- **TextSprite** - Текст с якорями позиционирования
- **Bar** - Полосы прогресса (HP, опыт и т.д.)

### 🎨 Игровые системы
- **Animation** - Система анимаций
- **Tween** - Плавные переходы (easing); **Fluent API**: `sprite.DoMove(...).SetEase(Ease.OutQuad)` — см. [Tween](docs/tween.md#fluent-api-do-твины) и [Fluent Tween Demo](spritePro/demoGames/fluent_tween_demo.py)
- **Timer** - Таймеры для событий
- **Health** - Система здоровья
- **ParticleEmitter** - Генератор частиц

### 🛠️ Утилиты
- **AudioManager** - Управление звуком и музыкой
- **PlayerPrefs** - Система сохранений
- **Camera** - Умная камера с автоматическим слежением
- **Color Effects** - Динамические цветовые эффекты

### 🎨 Редактор
- **Sprite Editor** - Визуальный редактор спрайтов в стиле Unity
  - Инструменты: Select, Move, Rotate, Scale
  - Drag & Drop изображений
  - UI панели: Hierarchy, Inspector, Toolbar
  - Сохранение/Загрузка в JSON
  - Undo/Redo, копирование/вставка
- Запуск: `python -m spritePro.cli --editor` или `-e`
- [Документация редактора](docs/sprite_editor.md)

---

## 📖 Документация

### 🚀 Быстрый старт
- [Установка и настройка](#-быстрый-старт-30-секунд)
- [Базовый пример](#ваша-первая-игра-5-строк)
- [Быстрый старт 2.0](#-быстрый-старт-20-шаблон-проекта)

### 📚 Индексы
- [📖 Индекс документации](DOCUMENTATION_INDEX.md) - Полный список модулей
- [📘 Документация папки docs](docs/README.md) - Навигация по разделам
- [🌐 Сетевой мультиплеер](docs/networking.md) - Запуск и базовые примеры
- [🎓 Мини-курс по мультиплеерным играм](multiplayer_course/README.md) - 10 уроков: от обмена сообщениями до готовой сетевой мини-игры

### 🧩 Полный список документации
- Основы: [Game Loop](docs/game_loop.md) • [Input](docs/input.md) • [Debug](docs/debug.md) • [Camera & Particles](docs/camera_and_particles.md)
- Спрайты и графика: [Sprite](docs/sprite.md) • [Surface](docs/surface.md) • [Text](docs/text.md) • [Text FPS](docs/text_fps.md) • [Color Effects](docs/color_effects.md) • [ReadySprites](docs/readySprites.md)
- UI: [Button](docs/button.md) • [Toggle Button](docs/toggle_button.md) • [Bar](docs/bar.md) • [Bar Background](docs/bar_background.md) • [Pages](docs/pages.md) • [Layout](docs/layout.md) • ScrollView (в [layout.md](docs/layout.md)) • [Готовые сцены](docs/README.md#готовые-сцены-readyscenes) (ChatScene)
- Компоненты: [Animation](docs/animation.md) • [Tween](docs/tween.md) • [Tween Presets](docs/tween_presets.md) • [Timer](docs/timer.md) • [Health](docs/health.md) • [Mouse Interactor](docs/mouse_interactor.md) • [Draggable Sprite](docs/draggable_sprite.md)
- Эффекты и частицы: [Particles](docs/particles.md)
- Аудио: [Audio](docs/audio.md)
- Сохранения и утилиты: [Save/Load](docs/save_load.md)

---

## 🎯 Примеры использования

### Игра с меню, звуком и сохранениями

```python
import spritePro as s

screen = s.get_screen((800, 600), "My Game")

# Аудио
audio = s.audio_manager
audio.load_sound("click", "sounds/click.mp3")
click_sound = audio.get_sound("click")
audio.play_music("music/bg.mp3")

# Сохранения
prefs = s.PlayerPrefs("save.json")
high_score = prefs.get_int("high_score", 0)

# UI
start_button = s.Button(
    "", (200, 50), s.WH_C,
    "Начать игру",
    on_click=lambda: click_sound.play()
)

# Игрок
player = s.Sprite("player.png", (50, 50), (100, 300), speed=5)

# Камера
s.set_camera_follow(player)

while True:
    s.update(fill_color=(20, 20, 30))
    player.handle_keyboard_input()
    
    # Сохраняем рекорд
    if score > high_score:
        prefs.set_int("high_score", score)
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
# 10 строк для той же игры!
import spritePro as s

s.get_screen((800, 600), "Game")
player = s.Sprite("player.png", (50, 50), s.WH_C, speed=5)

while True:
    s.update()
    player.handle_keyboard_input()
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

### 1. Установите
```bash
pip install pygame
git clone https://github.com/NeoXider/SpritePro.git
```

### 2. Скопируйте папку `spritePro` в ваш проект

### 3. Создайте игру!
```python
import spritePro as s

s.get_screen((800, 600), "My Game")
player = s.Sprite("", (50, 50), s.WH_C, speed=5)

while True:
    s.update()
    player.handle_keyboard_input()
```

**Готово!** У вас уже есть игра! 🎉

---

## 📊 Статистика

- ⚡ **В 10 раз меньше кода** чем с чистым pygame
- 🚀 **В 5 раз быстрее** разработка прототипов
- 🎯 **100% готовых компонентов** для типичных задач
- 📚 **Полная документация** с примерами
- 🎮 **15+ демо-игр** с исходным кодом

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
