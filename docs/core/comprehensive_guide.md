# 📚 SpritePro v3.4.0 — Полная Документация

**Единое руководство по всей библиотеке**  
Версия: 3.4.0 | Последнее обновление: Март 2026

---

## 🎯 Быстрый старт (5 минут)

### Установка
```bash
pip install spritepro
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

s.run(scene=MainScene, size=(800, 600), title="Моя игра")
```

### Шаблон проекта
```bash
python -m spritePro.cli --create
```

---

## 📦 Структура библиотеки

SpritePro состоит из следующих основных модулей:

### 1. Ядро (Core)
- **Scene** — базовая сцена с lifecycle (`on_enter`, `update`, `on_exit`)
- **SceneManager** — управление сценами, переключение, перезапуск
- **SpriteProGame** — главный игровой класс
- **GameContext** — контекст игры (экран, камера, ввод)

### 2. Спрайты и UI
- **Sprite** — базовый спрайт с позицией, размером, цветом, анимациями
- **Button** — интерактивная кнопка с состояниями
- **ToggleButton** — переключатель ВКЛ/ВЫКЛ
- **TextInput** — текстовое поле ввода
- **Slider** — ползунок для значений
- **Bar** — полоса прогресса (HP, опыт)
- **TextSprite** — текстовый компонент
- **Layout** — автолейауты (flex, grid, circle, line)

### 3. Компоненты
- **Animation** — кадровая анимация
- **Tween** — плавные переходы с Fluent API
- **Timer** — таймеры и задержки
- **Health** — система здоровья
- **DraggableSprite** — перетаскиваемые объекты
- **MouseInteractor** — взаимодействие с мышью
- **Pages** — управление страницами UI

### 4. Физика (pymunk)
- **PhysicsWorld** — физический мир
- **PhysicsBody** — физические тела (DYNAMIC, STATIC, KINEMATIC)
- **PhysicsShape** — формы коллайдеров (BOX, CIRCLE, LINE, SEGMENT)

### 5. Частицы
- **ParticleEmitter** — эмиттер частиц
- **ParticleConfig** — конфигурация частиц
- **Шаблоны**: sparks, smoke, fire, snowfall, circular_burst, trail

### 6. Audio & Save/Load
- **AudioManager** — звук и музыка
- **PlayerPrefs** — сохранения в JSON
- **SaveLoadManager** — менеджер сохранений

### 7. Сеть и Мультиплеер
- **NetServer** — серверная часть
- **NetClient** — клиентская часть
- **multiplayer_ctx** — контекст мультиплеера

### 8. Mobile & Web
- **Kivy Host** — запуск в Kivy
- **Web Build** — сборка для WebAssembly

### 9. Editor & CLI
- **Sprite Editor** — визуальный редактор сцен
- **CLI Tools** — командная строка (создание, Android build)

### 10. Utils & Plugins
- **ObjectPool** — пулы объектов
- **AssetWatcher** — наблюдение за файлами
- **PluginManager** — система плагинов

---

## 🎨 Детальное описание модулей

### 1. Scene System

#### Базовая сцена
```python
import spritePro as s

class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("player.png", (50, 50), s.WH_C, scene=self)
    
    def update(self, dt):
        self.player.handle_keyboard_input()
    
    def on_enter(self, context):
        print("Сцена активирована")
    
    def on_exit(self):
        print("Сцена завершена")

# Запуск
s.run(scene=GameScene, size=(800, 600))
```

#### Переключение сцен
```python
# Перезапустить текущую сцену
s.restart_scene()

# Перейти к другой сцене
s.set_scene("next_scene")

# Сцена по имени
s.set_scene_by_name("menu", recreate=True)
```

### 2. Sprite Builder (Fluent API)

#### Создание спрайтов
```python
import spritePro as s

# Базовый спрайт
sprite = s.sprite("player.png").position(100, 200).size((50, 50)).build()

# С цветом и прозрачностью
sprite = s.sprite("enemy.png") \
    .position(300, 400) \
    .color(255, 100, 50) \
    .alpha(0.7) \
    .build()

# Масштабирование
sprite = s.sprite("boss.png") \
    .position(s.WH_C) \
    .scale(2.0) \
    .build()
```

#### Методы Builder API
- `.position(x, y)` — установить позицию
- `.center(pos)` — центрировать
- `.size(w, h)` — задать размер
- `.scale(s)` — масштаб (float или tuple)
- `.color(r, g, b)` — RGB цвет
- `.alpha(a)` — прозрачность (0.0-1.0)
- `.crop(left, top, w, h)` — обрезка изображения
- `.border_radius(radius)` — скругление углов
- `.mask()` — создать маску коллизии
- `.scene(scene)` — добавить в сцену
- `.parent(parent)` — установить родителя

### 3. Tween System

#### Базовые твины
```python
import spritePro as s

# Плавное перемещение
sprite.DoMove((100, 200), duration=1.0) \
    .SetEase(s.Ease.OutQuad) \
    .OnComplete(lambda: print("Пришло!"))

# Масштабирование
sprite.DoScale(2.0, duration=0.5) \
    .SetLoop()  # Бесконечный цикл

# Поворот
sprite.DoRotate(360, duration=2.0) \
    .SetEase(s.Ease.OutBounce)

# Цветовой эффект
sprite.DoColor((255, 0, 0), duration=1.0) \
    .SetAlpha(0.5)
```

#### Preset твины
```python
# Готовые функции
s.tween_position(sprite, (100, 200), duration=1.0)
s.tween_scale(sprite, 2.0, duration=0.5)
s.tween_rotate(sprite, 360, duration=2.0)
s.tween_color(sprite, (255, 0, 0), duration=1.0)
s.tween_alpha(sprite, 0.5, duration=1.0)
s.tween_size(sprite, (100, 50), duration=1.0)

# Эффекты тряски
s.tween_shake_position(sprite, strength=(10, 10), duration=0.3)
s.tween_shake_rotation(sprite, angle=15, duration=0.5)

# Fade эффекты
s.tween_fade_in(sprite, duration=1.0)
s.tween_fade_out(sprite, duration=1.0)
```

#### Easing функции
- `Linear` — линейная
- `Quad.In/Out` — квадратичная
- `Cubic.In/Out` — кубическая
- `Quart.In/Out` — четвертая степень
- `Quint.In/Out` — пятая степень
- `Sin.In/Out` — синусоидальная
- `Expo.In/Out` — экспоненциальная
- `Circ.In/Out` — круговая
- `Elastic.In/Out` — упругая
- `Back.In/Out` — обратная
- `Bounce.In/Out` — отскок

### 4. Physics (pymunk)

#### Создание тел
```python
import spritePro as s

# Динамическое тело (падает, отскакивает)
body = s.PhysicsBody(
    mass=10,
    shape=s.PhysicsShape.CIRCLE(radius=25),
    position=(100, 300)
)
s.physics.add(body)

# Статичное тело (стена, пол)
wall = s.PhysicsBody(
    shape=s.PhysicsShape.BOX(width=800, height=20),
    position=(400, 590)
)
s.physics.add_static(wall)

# Кинематическое тело (движется, но не реагирует на силы)
platform = s.PhysicsBody(
    body_type=s.BodyType.KINEMATIC,
    shape=s.PhysicsShape.BOX(width=200, height=20),
    position=(400, 300)
)
s.physics.add_kinematic(platform)

# Движение кинематического тела
platform.set_velocity((100, 0))  # Двигается вправо
```

#### Коллизии
```python
# Обработчик коллизий
def on_collision(body_a, body_b, event):
    print(f"Коллизия: {body_a} <-> {body_b}")
    return True  # Продолжить обработку

# Подписать на событие
s.physics.add_collision_handler(on_collision)

# Удалить обработчик
s.physics.remove_collision_handler(on_collision)
```

#### Гравитация и границы
```python
# Изменить гравитацию мира
s.physics.set_gravity((0, 300))  # Вниз

# Установить границы мира
s.physics.set_bounds((0, 0, 800, 600))
```

### 5. Particle System

#### Базовый эмиттер
```python
import spritePro as s

# Простой взрыв
explosion = s.particles() \
    .amount(100) \
    .lifetime_range(0.5, 1.5) \
    .speed_range(200, 400) \
    .angle_range(0, 360) \
    .gravity((0, 200)) \
    .position(s.WH_C) \
    .build()

# Эмитировать частицы
explosion.emit()

# Остановить
explosion.stop()

# Перезапустить
explosion.restart(amount=150, lifetime=2.0)
```

#### Шаблоны частиц
```python
from spritePro.particles import (
    template_sparks,
    template_smoke,
    template_fire,
    template_snowfall,
    template_circular_burst,
    template_trail
)

# Искры
sparks = s.particles(template_sparks).position(s.WH_C).build()

# Дым
smoke = s.particles(template_smoke).position(400, 300).build()

# Огонь
fire = s.particles(template_fire).position(s.WH_C).auto_emit().build()

# Снег
snow = s.particles(template_snowfall).position(s.WH_C).build()

# След (trail) за объектом
trail = s.particles(template_trail).lifetime(0.5).auto_emit().build()
```

#### Кастомизация шаблонов
```python
# Изменить параметры шаблона
custom_fire = s.particles(template_fire) \
    .amount(200) \
    .lifetime_range(0.3, 1.5) \
    .speed_range(100, 300) \
    .color(255, 150, 50) \
    .position(s.WH_C) \
    .build()
```

### 6. UI Components

#### Button
```python
import spritePro as s

button = s.Button(
    "", (200, 50), s.WH_C, "Начать игру",
    on_click=lambda: print("Игра началась!"),
    scene=scene
)

# Состояния кнопки
button.set_normal_color((100, 100, 100))
button.set_hover_color((150, 150, 150))
button.set_press_color((200, 200, 200))

# Анимация нажатия
button.animate_press()
```

#### TextInput
```python
text_input = s.TextInput(
    "", (100, 100), (300, 50),
    placeholder="Введите текст",
    scene=scene
)

# Получить текст
value = text_input.get_text()

# Установить текст
text_input.set_text("Новый текст")

# Очистить
text_input.clear()
```

#### Slider
```python
slider = s.Slider(
    "", (100, 200), (300, 30),
    min_value=0, max_value=100,
    value=50,
    scene=scene
)

# Получить значение
value = slider.get_value()

# Установить значение
slider.set_value(75)

# Изменить диапазон
slider.set_range(0, 200)
```

#### Layout
```python
# Flex layout (горизонтальный/вертикальный)
layout = s.Layout(
    "", (0, 0), s.WH_C,
    layout_type=s.LayoutType.FLEX,
    direction=s.Direction.HORIZONTAL,
    spacing=10,
    scene=scene
)

# Grid layout (сетка)
grid = s.Layout(
    "", (0, 0), s.WH_C,
    layout_type=s.LayoutType.GRID,
    columns=4,
    rows=3,
    cell_size=(100, 100),
    spacing=5,
    scene=scene
)

# Add children to layout
layout.add_child(child_sprite)
layout.remove_child(child_sprite)
```

### 7. Audio System

#### AudioManager
```python
import spritePro as s

audio = s.audio_manager

# Загрузить звук
jump_sound = audio.load_sound("jump", "sounds/jump.mp3")

# Воспроизвести
jump_sound.play()

# Громкость
audio.set_sound_volume("jump", 0.8)

# Музыка
audio.play_music("music/background.mp3", volume=0.5)
audio.set_music_volume(0.7)
audio.toggle_music()  # Вкл/Выкл
```

#### Быстрое воспроизведение
```python
# Прямое воспроизведение без загрузки
audio.play_sound("sounds/jump.mp3")
audio.play_sound("sounds/coin.wav", volume=0.8)

# Загрузить и воспроизвести в одну строку
audio.load_sound("explosion", "sounds/explosion.mp3").play()
```

### 8. Save/Load System

#### PlayerPrefs
```python
import spritePro as s

prefs = s.PlayerPrefs("save.json")

# Сохранение данных
prefs.set_int("score", 1250)
prefs.set_float("high_score", 1250.5)
prefs.set_string("player_name", "Hero")
prefs.set_vector2("position", (400, 300))
prefs.set_bool("music_enabled", True)

# Загрузка с дефолтными значениями
score = prefs.get_int("score", 0)
high_score = prefs.get_float("high_score", 0)
player_name = prefs.get_string("player_name", "Player")
position = prefs.get_vector2("position", (0, 0))
music_enabled = prefs.get_bool("music_enabled", False)

# Автоматическое сохранение в JSON!
```

### 9. Debug System

#### Debug Overlay
```python
import spritePro as s

# Включить отладку
s.enable_debug()

# Настроить сетку
s.set_debug_grid(
    enabled=True,
    spacing=50,
    color=(200, 200, 200),
    anchor=s.Anchor.TOP_LEFT
)

# Настроить логи
s.set_debug_logs_enabled(True)
s.set_debug_log_anchor(s.Anchor.BOTTOM_LEFT)
s.set_debug_log_style(font_size=12, color=(255, 255, 255))

# Профилирование FPS
s.set_debug_perf_enabled(True)
snapshot = s.get_perf_snapshot()
print(f"FPS: {snapshot.fps}, Objects: {sprite_count}")
```

### 10. Event System

#### EventBus
```python
import spritePro as s

# Подписаться на событие
def on_quit(event):
    print("Quit event")

s.events.on("quit", on_quit)

# Отправить событие
s.events.emit("quit", {"reason": "user_close"})

# Удалить подписку
s.events.off("quit", on_quit)
```

#### Global Events
```python
import pygame
import spritePro as s

class InputScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.events.on("key_pressed", self.on_key)
    
    def on_key(self, event):
        if event.key == pygame.K_SPACE:
            print("Space pressed!")
    
    def update(self, dt):
        if s.input.was_pressed(pygame.K_SPACE):
            print("Space was pressed")

s.run(scene=InputScene, size=(800, 600))
```

### 11. Camera System

#### Управление камерой
```python
import spritePro as s

# Позиция камеры
s.set_camera_position(400, 300)
s.move_camera(50, -30)  # Сдвиг
position = s.get_camera_position()  # (x, y)

# Зум
s.set_camera_zoom(1.5)
s.zoom_camera(0.1)  # +10%
zoom = s.get_camera_zoom()  # Текущий зум

# Следование за объектом
player = s.Sprite("", (50, 50), s.WH_C, scene=scene)
s.set_camera_follow(player, offset=(50, 0))

# Очистить слежение
s.clear_camera_follow()

# Тряска камеры
s.shake_camera(strength=(12, 12), duration=0.35)
```

### 12. Object Pooling

#### Пул спрайтов
```python
import spritePro as s
from spritePro.utils.pool import ObjectPool

class OptimizedScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Создать пул эмиттеров
        self.emitter_pool = ObjectPool(
            factory=lambda: s.particles() \
                .amount(50) \
                .lifetime_range(0.5, 1.5) \
                .build(),
            pool_size=20
        )
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            # Получить из пула
            emitter = self.emitter_pool.get()
            emitter.emit()
            
            # Вернуть после завершения
            emitter.on_complete(lambda: self.emitter_pool.put(emitter))

s.run(scene=OptimizedScene, size=(800, 600))
```

### 13. Plugins System

#### Регистрация плагина
```python
import spritePro as s

class MyPlugin(s.Plugin):
    def __init__(self):
        super().__init__("MyPlugin", "1.0")
    
    def on_scene_enter(self, scene):
        print(f"Plugin {self.name} loaded in scene")
    
    def on_update(self, dt):
        # Логика плагина
        pass

# Зарегистрировать плагин
plugin = MyPlugin()
s.register_plugin(plugin)
```

#### Хуки (Hooks)
```python
# Доступные хуки:
# - HOOKS_LIFECYCLE: lifecycle events
# - HOOKS_SPRITE: sprite events
# - HOOKS_SCENE: scene events
# - HOOKS_INPUT: input events

@plugin.hook(s.HOOKS_SCENE)
def on_scene_change(old_scene, new_scene):
    print(f"Scene changed: {old_scene} -> {new_scene}")
```

### 14. Hot Reload

#### Автоматическое обновление ассетов
```python
import spritePro as s

# Включить hot reload
s.enable_hot_reload()

# Настроить наблюдение
s.set_asset_watcher(
    watch_paths=["assets/images", "scenes"],
    auto_reload=True,
    debounce=0.5  # задержка в секундах
)

# Ручная перезагрузка
s.reload_assets()
```

---

## 🎮 Demo Games (54 файла)

Все демо-игры находятся в `spritePro/demoGames/`. Запуск: `python -m spritePro.demoGames.<имя>`

### Категории демо:

#### 🏗 Базовые компоненты
- [physics_demo.py](demoGames/physics_demo.py) — физика pymunk
- [tween_presets_demo.py](demoGames/tween_presets_demo.py) — твины
- [particle_demo.py](demoGames/particle_demo.py) — частицы
- [debug_overlay_demo.py](demoGames/debug_overlay_demo.py) — debug tools

#### 🎨 UI & Layout
- [layout_demo.py](demoGames/layout_demo.py) — автолейауты
- [menu_shop_demo.py](demoGames/menu_shop_demo.py) — меню и инвентарь
- [slider_textinput_demo.py](demoGames/slider_textinput_demo.py) — слайдер + ввод

#### 🎬 Анимация & Эффекты
- [fluent_tween_demo.py](demoGames/fluent_tween_demo.py) — Fluent API
- [fireworks_demo.py](demoGames/fireworks_demo.py) — фейерверк
- [color_text_demo.py](demoGames/color_text_demo.py) — текст с эффектами

#### 🎮 Игровая логика
- [easy_clicker.py](demoGames/easy_clicker.py) — кликер с улучшениями
- [hero_vs_enemy.py](demoGames/hero_vs_enemy.py) — бой герой vs враг
- [ping_pong.py](demoGames/ping_pong.py) — пинг-понг

#### 🌐 Сеть & Мультиплеер
- [local_multiplayer_demo.py](demoGames/local_multiplayer_demo.py) — хост + клиенты
- [three_clients_move_demo.py](demoGames/three_clients_move_demo.py) — 3 клиента синхронизация

#### 💾 Утилиты & Оптимизация
- [save_load_demo.py](demoGames/save_load_demo.py) — PlayerPrefs
- [object_pool_demo.py](demoGames/object_pool_demo.py) — пул объектов
- [hot_reload_demo.py](demoGames/hot_reload_demo.py) — горячая перезагрузка

#### 📱 Mobile & Kivy
- [mobile_orb_collector_demo.py](demoGames/mobile_orb_collector_demo.py) — mobile-first
- [kivy_hybrid_demo.py](demoGames/kivy_hybrid_demo.py) — Kivy UI + игра

---

## 🔍 Поиск по документации

### Найти фичу:
1. Используйте **Ctrl+F** в этом документе
2. Ищите по ключевым словам: `sprite`, `button`, `physics`, `tween`, `particle`

### Найти пример:
1. Перейдите к разделу [Demo Games](#demo-games-54-файла)
2. Найдите нужную категорию демо
3. Запустите через CLI: `python -m spritePro.demoGames.<имя>`

---

## 📊 Сравнение с альтернативами

| Функция | pygame | arcade | **SpritePro** |
|---------|--------|--------|---------------|
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
- Плавные переходы (easing)
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

### 📱 Mobile и build
- **Kivy host** — запуск game loop внутри mobile-оболочки
- **run(platform="kivy") / run_kivy(...)** — full-screen режим по умолчанию
- **run_kivy_hybrid(...) / create_kivy_widget(...)** — Kivy UI вокруг встроенной игровой области

### 🛠️ Утилиты
- **AudioManager** — звук и музыка
- **PlayerPrefs** — сохранения в JSON
- **Camera** — камера и слежение за объектом
- **Builder** — fluent API для спрайтов и частиц

### 🎨 Редактор сцен
- **Sprite Editor** — сцены в стиле Unity: `File` / `GameObject` / `Tools` / `View`, Hierarchy, Inspector, JSON, `Text`-объекты
- В игре: `spawn_scene("level.json", ...)`, объекты по имени, физика из сцены. [docs/sprite_editor.md](docs/sprite_editor.md)

---

<div align="center">

**🎮 Готовы к практике?**  
Начните с [Быстрый старт](#быстрый-старт-5-минут) или запустите [демо-игры](#demo-games-54-файла)!

</div>
