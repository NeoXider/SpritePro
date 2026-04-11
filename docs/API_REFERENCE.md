# 📚 API Reference — SpritePro v3.8.0

**Полная справка по всем классам, функциям и методам библиотеки**

---

## 🎯 Обзор экспортируемых объектов

Из `import spritePro as s` доступны:

### Основные функции
- `s.run()` — запуск игры
- `s.sprite()` — Builder для спрайтов (Fluent API)
- `s.particles()` — Builder для частиц (Fluent API)
- `s.add_physics()`, `s.add_static_physics()`, `s.add_kinematic_physics()` — физика pymunk
- Камера: `set_camera_follow()`, `shake_camera()`, `zoom_camera()`
- Сцены: `restart_scene()`, `set_scene_by_name()`
- Debug: `enable_debug()`, `debug_log_info()`

### Классы и компоненты
- **Sprite** — базовый спрайт
- **Button**, **ToggleButton**, **Slider**, **TextInput** — UI компоненты
- **TextSprite** — текст с якорями
- **Bar**, **Layout** — прогресс-бары и автолейауты
- **Animation**, **Tween**, **Timer** — игровые системы
- **ParticleEmitter** — система частиц
- **SceneManager**, **EventBus**, **InputState** — подсистемы
- **ClipMask** — маска обрезки (клиппинг)
- **ScrollView** — скроллируемая область

### Утилиты
- **AudioManager** — звук и музыка
- **PlayerPrefs** — сохранения в JSON
- **PluginManager** — плагины и хуки
- **validate_*** — функции валидации параметров

---

## 📖 Полная документация по разделам

### 1. Основные функции `s.`

#### `s.run(scene, size=(800, 600), title="Game", ...)`
Запускает игровой цикл.

**Параметры:**
- `scene` (`Scene | type[Scene] | Callable`) — сцена для запуска
- `size` (`tuple[int, int]`, optional) — размер окна (по умолчанию 800x600)
- `title` (`str`, optional) — заголовок окна
- `fill_color` (`tuple[int, int, int]`, optional) — цвет фона (RGB 0-255)
- `platform` (`"pygame" | "kivy"`, optional) — платформа (pygame по умолчанию)
- `multiplayer` (`bool`, optional) — включить мультиплеерный контекст
- `use_lobby` (`bool`, optional) — использовать экран лобби

**Пример:**
```python
s.run(scene=MainScene, size=(800, 600), title="Моя игра")
s.run(scene=MainScene, platform="kivy")  # Mobile режим
```

#### `s.sprite(path: str = "") -> SpriteBuilder`
Builder Fluent API для создания спрайтов.

**Методы Builder:**
- `.position(x, y)` — установить позицию
- `.scale(value)` — масштаб (float или tuple)
- `.color(r, g, b)` — цвет (RGB 0-255)
- `.crop(left, top, width, height)` — обрезка изображения
- `.border_radius(radius)` — скругление углов
- `.mask()` — создать маску коллизий
- `.build()` — создать и вернуть Sprite

**Пример:**
```python
sprite = s.sprite("player.png").position(100, 200).scale(1.5).color(255, 0, 0).build()
```

#### `s.particles() -> ParticleBuilder`
Builder Fluent API для создания эмиттеров частиц.

**Методы Builder:**
- `.amount(n)` — количество частиц
- `.lifetime(sec)` — время жизни (секунды или мс)
- `.speed(min, max)` — скорость вылета
- `.gravity(x, y)` — гравитация
- `.position(x, y)` — позиция эмиссии
- `.auto_emit()` — автоэмиссия при создании
- `.build()` — создать и вернуть ParticleEmitter

**Пример:**
```python
emitter = s.particles().amount(50).lifetime(1.0).speed(100, 200).position(400, 300).build()
```

#### `s.add_physics(sprite, config=None, shape=PhysicsShape.AUTO, auto_add=True)`
Добавляет физическое тело к спрайту (pymunk).

**Параметры:**
- `sprite` — спрайт для физики
- `config` (`PhysicsConfig`, optional) — настройки тела
- `shape` (`PhysicsShape | str`) — форма коллайдера: AUTO, BOX, CIRCLE, LINE
- `auto_add` (`bool`) — автоматически добавить в мир (по умолчанию True)

**Возвращает:** `PhysicsBody`

**Пример:**
```python
body = s.add_physics(sprite, shape=s.PhysicsShape.BOX)
body.set_bounce(0.8)  # Настройка отскока
```

#### `s.add_static_physics(sprite, config=None, shape=PhysicsShape.AUTO)`
Добавляет статическое тело (стена/пол).

**Возвращает:** `PhysicsBody`

#### `s.add_kinematic_physics(sprite, config=None, shape=PhysicsShape.AUTO)`
Добавляет кинематическое тело (движется, но не под действием сил).

**Возвращает:** `PhysicsBody`

#### Камера
```python
s.set_camera_follow(target_sprite)  # Камера следит за спрайтом
s.shake_camera(strength=(12, 12), duration=0.35)  # Тряска экрана
s.zoom_camera(factor=1.5)  # Зум камеры
```

#### Сцены
```python
s.restart_scene()              # Перезапуск текущей сцены
s.set_scene_by_name("menu")    # Переключение на сцену по имени
s.get_current_scene()          # Получить текущую сцену
```

#### Debug
```python
s.enable_debug(True)           # Включить debug overlay
s.debug_log_info("Message")    # Логирование сообщения
s.set_debug_grid_enabled(True) # Показать сетку мира
```

---

### 2. Классы и компоненты

#### **Sprite** (sprite.py)
Базовый визуальный объект с движением и эффектами.

**Основные методы:**
- `set_position(x, y)` — установить позицию (обновляет дочерние спрайты)
- `get_world_position()` — получить мировую позицию
- `set_world_position(x, y)` — установить мировую позицию
- `handle_keyboard_input()` — обработка WASD/стрелок
- `move_towards(target, speed)` — движение к цели
- `collides_with(other, use_mask=True)` — проверка коллизии
- `set_collision_targets(targets)` — установить цели для коллизий
- `set_parent(parent, keep_world_position=True)` — назначить родителя

**Свойства:**
- `rect` — прямоугольник спрайта
- `size` — размер (ширина, высота)
- `angle` — угол поворота
- `alpha` — прозрачность (0-255, где 255 = непрозрачный)
- `active` — видимость и обновление спрайта
- `children` — список дочерних спрайтов
- `parent` — родительский спрайт

> **Важно:** `set_position()` автоматически обновляет позиции всех дочерних
> спрайтов через `_update_children_world_positions()`. Это гарантирует
> корректную работу иерархий (Layout, ScrollView, ChatUI).

#### **Button** (button.py)
Интерактивная кнопка с анимациями.

**Параметры:**
- `path` (`str`) — путь к изображению (пустая строка = прямоугольник)
- `size` (`tuple[int, int]`) — размер кнопки
- `position` (`tuple[float, float]`) — позиция
- `text` (`str`, optional) — текст на кнопке
- `on_click` (`Callable`, optional) — callback при клике

**Свойства:**
- `is_hovered` — True если мышь над кнопкой
- `is_pressed` — True если нажата

#### **ToggleButton** (toggle_button.py)
Переключатель с состояниями ON/OFF.

**Параметры:**
- `text_on` (`str`) — текст в состоянии ON
- `text_off` (`str`) — текст в состоянии OFF
- `on_toggle` (`Callable[bool]`, optional) — callback при переключении

#### **Slider** (slider.py)
Слайдер для выбора числового значения.

**Параметры:**
- `min_val` / `max_val` — диапазон значений
- `on_change` (`Callable[float]`, optional) — callback при изменении

#### **TextInput** (text_input.py)
Поле ввода текста с валидацией.

**Параметры:**
- `input_type` (`"text" | "int" | "float"`) — тип поля
- `min_val` / `max_val` — диапазон для int/float
- `on_change`, `on_submit` — callbacks

#### **TextSprite** (components/text.py)
Текст с якорями позиционирования.

**Параметры:**
- `text` (`str`) — текст для отображения (поддерживает `\n`)
- `anchor` (`Anchor`) — якорь (TOP_LEFT, CENTER, BOTTOM_RIGHT и др.)
- `color` (`tuple[int, int, int]`) — цвет текста

#### **Bar** (bar.py) / **BarBackground** (bar_background.md)
Прогресс-бары для HP/опыта.

**Параметры:**
- `fill_amount` (`float`) — значение заполнения (0-1)
- `direction` (`HORIZONTAL` | `VERTICAL`) — направление заполнения
- `use_image` (`bool`) — использовать изображение или цвет

#### **Layout** (layout.py)
Автолейаут для групп спрайтов. Наследует `Sprite` — можно перемещать и масштабировать.

**Типы (LayoutDirection):**
- `FLEX_ROW`, `FLEX_COLUMN` — гибкая раскладка с переносом
- `HORIZONTAL`, `VERTICAL` — ряд/колонка
- `GRID` — сетка (rows × cols)
- `CIRCLE` — элементы по окружности
- `LINE` — элементы вдоль ломаной

**Параметры:**
- `container` — Sprite, tuple `(x, y, w, h)` или `None` (Layout сам контейнер)
- `gap` / `padding` — отступы
- `align_main` / `align_cross` — выравнивание
- `auto_apply` (`bool`) — авто-обновление при add/remove (по умолчанию True)
- `size` / `pos` / `scene` — при `container=None`

**Удобные функции:**
```python
layout = s.layout_vertical(None, [sprite1, sprite2], gap=10, pos=(400, 300), size=(200, 400))
layout = s.layout_flex_row(None, items, gap=8, padding=12)
layout = s.layout_grid(None, items, cols=4, gap=5)
layout = s.layout_circle(None, items, radius=100)
```

**Методы:** `add()`, `add_children()`, `remove()`, `apply()`, `refresh()`, `set_size()`

> **Заметка:** При `container=None`, Layout создаёт прозрачный спрайт-контейнер
> (`alpha=0`). Дочерние спрайты привязываются через `set_parent()`.

#### **ClipMask** (clip_mask.py)
Маска обрезки для ограничения видимости спрайтов прямоугольной областью.

**Параметры:**
- `pos` (`tuple[float, float]`) — позиция маски (левый верхний угол)
- `size` (`tuple[float, float]`) — размер маски
- `bg_color` — цвет фона (`None` — прозрачный, фон от основного цикла)
- `border_color` / `border_width` / `border_radius` — рамка
- `hide_content` (`bool`) — скрыть спрайты из основной отрисовки

**Режимы:**

| Режим | `hide_content` | Описание |
|-------|---------------|----------|
| Ручной | `False` | Спрайты рисуются основным циклом + маска перерисовывает с обрезкой |
| Автоматический | `True` | `active=False` на спрайтах; рисуются **только** через `mask.draw()` |

**Методы:**
```python
mask = s.ClipMask(pos=(50, 50), size=(300, 200), hide_content=True)
mask.add(sprite1, sprite2)       # Добавить спрайты (рекурсивно с children)
mask.remove(sprite1)             # Удалить (восстановит active=True)
mask.clear()                     # Очистить все
mask.draw(screen)                # Отрисовка с обрезкой
mask.draw(screen, cam_x, cam_y)  # С учётом камеры
mask.contains(x, y)              # Точка внутри маски?
mask.set_position((100, 100))    # Переместить маску
mask.set_size((400, 300))        # Изменить размер
```

> **Как работает `hide_content=True`:**
> 1. `mask.add(sprite)` ставит `sprite.active = False` — основной цикл не рисует его
> 2. `mask.draw()` собирает спрайты через BFS по `Sprite.children` (иерархически)
> 3. Перед blitting вызывается `_update_image()` для применения dirty-флагов (alpha, color)
> 4. Спрайты с `alpha=0` (контейнеры Layout) пропускаются
> 5. `pygame.Surface.set_clip()` обрезает отрисовку по rect маски

Подробнее: [ClipMask](ui/clip_mask.md)

#### **ScrollView** (scroll.py)
Скроллируемая область для длинного контента.

**Параметры:**
- `pos` (`tuple[float, float]`) — позиция viewport
- `size` (`tuple[float, float]`) — размер viewport

**Методы:**
```python
scroll = s.ScrollView(pos=(50, 100), size=(300, 400))
scroll.set_content(layout)            # Установить контент (Layout)
scroll.update_from_input(s.input)     # Обновить скролл из ввода (колёсико + drag)
scroll.apply_scroll()                 # Применить текущий скролл к контенту
scroll.scroll_to_bottom()             # Прокрутить к концу
```

#### **Animation** (components/animation.py)
Покадровая анимация.

**Методы:**
- `play(state)` — запустить анимацию состояния
- `pause()` / `resume()` — пауза/продолжение
- `set_frame(frame_index)` — установить кадр вручную

#### **Tween** (components/tween.py)
Плавные переходы с easing функциями.

**Fluent API на Sprite:**
```python
sprite.DoMove((100, 200)).SetDuration(1.0).SetEase(Ease.OUT_CUBIC).OnComplete(callback).Start()
sprite.DoScale(1.5).SetLoops(3).SetYoyo(True).Start()
sprite.DoRotateBy(360).SetDuration(2.0).Start()
sprite.DoFadeOut().SetDuration(1.0).OnComplete(callback).Start()
sprite.DoKill(complete=True)  # Остановить все твины спрайта
```

**Easing функции:** `Ease.LINEAR`, `Ease.IN_QUAD`, `Ease.OUT_CUBIC`, `Ease.OUT_ELASTIC`, ...

#### **Timer** (components/timer.py)
Таймеры и задержки.

**Методы:**
- `set_delay(sec)` — установить задержку
- `set_repeat(interval)` — повторяющийся таймер
- `on_complete(callback)` — callback при завершении

#### **ParticleEmitter** (particles.py)
Система частиц с эффектами.

**Конфигурация:**
```python
config = s.ParticleConfig(
    amount=50,           # Количество частиц
    speed_range=(100, 200),  # Скорость
    lifetime_range=(0.5, 1.5),  # Время жизни (сек)
    angle_range=(0, 360),  # Угол вылета
    gravity=s.Vector2(0, 200)  # Гравитация
)
emitter = s.ParticleEmitter(config).auto_emit().build()
```

**Готовые шаблоны:** `template_sparks`, `template_smoke`, `template_fire`, `template_snowfall`

#### **SceneManager** (scenes.py)
Управление сценами.

**Методы:**
- `add_scene(name, scene_factory)` — добавить сцену
- `set_scene_by_name(name, recreate=False)` — переключить сцену
- `restart_scene()` — перезапустить текущую

#### **EventBus** (event_bus.py)
Система событий.

**Методы:**
```python
s.events.connect("quit", callback)  # Подписка
s.events.send("custom_event", data)  # Отправка события
s.events.disconnect("quit", callback)  # Отписка
```

#### **InputState** (input.py)
Состояние ввода в стиле Unity.

**Методы:**
- `was_pressed(key)` — True если нажато в этом кадре
- `is_pressed(key)` — True если нажато сейчас
- `get_axis(name)` — получить ось (например, "Horizontal")

#### **AudioManager** (audio.py)
Централизованное управление звуком.

**Методы:**
```python
audio = s.audio_manager
sound = audio.load_sound("jump", "sounds/jump.mp3")  # Загрузка
sound.play()  # Воспроизведение
audio.play_music("music/bg.mp3")  # Фоновая музыка
audio.set_music_volume(0.5)  # Громкость музыки
```

#### **PlayerPrefs** (utils/save_load.py)
Сохранения в JSON.

**Методы:**
```python
prefs = s.PlayerPrefs("save.json")
prefs.set_int("score", 100)
prefs.set_float("health", 75.5)
prefs.set_string("player_name", "Hero")
prefs.set_vector2("position", (400, 300))

# Чтение
score = prefs.get_int("score", 0)  # 0 — значение по умолчанию
```

#### **PluginManager** (plugins.py)
Система плагинов.

**Декораторы:**
```python
from spritePro.plugins import register_plugin, hook

@register_plugin("my_plugin", "1.0.0", "Author")
def my_plugin_init():
    pass

@hook("game_update")
def on_game_update(dt):
    s.debug_log_info(f"Update: {dt}")
```

**Предопределённые хуки:** `HOOKS_LIFECYCLE`, `HOOKS_SPRITE`, `HOOKS_SCENE`, `HOOKS_INPUT`

---

### 3. Валидация параметров (utils/validation.py)

```python
from spritePro.utils.validation import (
    validate_color,      # RGB кортеж/список
    validate_vector2,    # Vector2 или tuple(x, y)
    validate_float,      # Число с min/max
    validate_string,     # Строка с длиной
    validate_enum,       # Значение Enum
    validate_list,       # Список элементов
    validate_dict        # Словарь с ключами
)

# Пример
validate_color((255, 0, 0), "background")
validate_vector2((100, 200), "position")
validate_float(0.5, "zoom", min_val=0.1, max_val=5.0)
```

---

### 4. Физика pymunk (physics.py)

#### **PhysicsWorld**
Глобальный мир физики `s.physics`.

**Методы:**
- `set_gravity(x, y)` — установить гравитацию
- `set_bounds(rect)` — границы мира с отскоком
- `add(body)` / `remove(body)` — добавить/удалить тело

#### **PhysicsBody**
Физическое тело.

**Свойства:**
- `velocity` — вектор скорости
- `position` — позиция
- `grounded` — True если на земле
- `on_collision(callback)` — callback при коллизии

**Методы:**
- `set_bounce(value)` — установить отскок (0-1)
- `set_friction(value)` — установить трение

#### **PhysicsConfig**
Конфигурация тела.

**Параметры:**
- `mass` — масса (для DYNAMIC тел)
- `friction` — трение (0-1)
- `bounce` — отскок (0-1)
- `collision_category` / `collision_mask` — маски коллизий

#### **PhysicsShape**
Форма коллайдера.

**Значения:**
- `AUTO` — автоматически определить из спрайта
- `BOX` — прямоугольник
- `CIRCLE` — круг
- `LINE` — линия/платформа

---

### 5. Сеть (networking.py)

#### **NetServer**
TCP сервер для мультиплеера.

#### **NetClient**
TCP клиент.

#### **s.run(..., multiplayer=True)**
Единая точка входа для сетевой игры.

**Сценарий лобби:**
```python
# Хост
s.run(scene=MainScene, multiplayer=True, use_lobby=True)
# Клиент
s.run(scene=MainScene, multiplayer=True, host="127.0.0.1", port=5050)
```

**MultiplayerContext:**
```python
ctx = s.multiplayer_ctx
ctx.send("event_name", {"data": "value"})  # Отправка
for msg in ctx.poll():  # Очередь входящих
    if msg.get("event") == "pos":
        remote_pos = msg.get("data", {}).get("pos")
```

#### **Готовые сцены (readyScenes)**

**ChatScene** — мультиплеерный чат с полем ввода, скроллом и маской обрезки:
```python
from spritePro.readyScenes import ChatScene, ChatStyle

# Кастомизация стиля
ChatStyle.color_bg = (18, 20, 28)
ChatStyle.color_panel = (28, 32, 44)
ChatStyle.font_size = 16

s.run(scene=ChatScene, multiplayer=True, use_lobby=True)
```

---

### 6. Вспомогательные функции

#### **Anchor** (constants.py)
Якоря позиционирования:
- `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`
- `MIDDLE_LEFT`, `MIDDLE_CENTER`, `MIDDLE_RIGHT`
- `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`

#### **LayoutDirection** (layout.py)
Направления лейаутов:
- `FLEX_ROW`, `FLEX_COLUMN`
- `HORIZONTAL`, `VERTICAL`
- `GRID`, `CIRCLE`, `LINE`

#### **EasingType** (tween.py)
Типы easing функций:
- `LINEAR`, `QUAD`, `CUBIC`, `QUART`, `QUINT`
- `IN_*`, `OUT_*`, `IN_OUT_*`
- `ELASTIC`, `BACK`, `BOUNCE`

---

## 📚 Ссылки на полные руководства

| Раздел | Файл |
|--------|------|
| Быстрый старт | [GETTING_STARTED.md](GETTING_STARTED.md) |
| Физика | [core/physics_guide.md](core/physics_guide.md) |
| UI & Layouts | [ui/layout_ui.md](ui/layout_ui.md) |
| Маска обрезки | [ui/clip_mask.md](ui/clip_mask.md) |
| Анимации | [core/tween_system.md](core/tween_system.md) |
| Mobile/Web | [builds/mobile_kivy.md](builds/mobile_kivy.md) |
| Мультиплеер | [systems/networking_guide.md](systems/networking_guide.md) |
| Редактор | [editor/sprite_editor.md](editor/sprite_editor.md) |
| Демо-игры | [demo_games/demo_games.md](demo_games/demo_games.md) |

---

<div align="center">

**🎮 Готовы к практике?**  
Изучите [GETTING_STARTED](GETTING_STARTED.md) или запустите [демо-игры](demo_games/demo_games.md)!

</div>
