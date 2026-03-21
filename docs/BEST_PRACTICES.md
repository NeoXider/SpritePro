# 💡 Best Practices — SpritePro v3.4.0

**Лучшие практики и паттерны для эффективной разработки игр**

---

## 🏗 Архитектура проекта

### Рекомендуемая структура
```
MyGame/
├── main.py              # Точка входа, запуск игры
├── config.py            # Настройки и пути к ассетам
├── game_events.py       # События через EventBus
├── assets/
│   ├── audio/          # Звуки и музыка
│   └── images/         # Изображения спрайтов
├── scenes/
│   ├── __init__.py
│   ├── main_scene.py   # Главная сцена
│   └── second_scene.py # Вторая сцена (заготовка)
└── game/
    ├── domain/         # Domain-модели
    │   └── game_state.py
    └── services/       # Сервисы логики
        └── game_service.py
```

### config.py — центр настроек
```python
from pathlib import Path

# Пути к ассетам (относительно текущего файла)
PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"
IMAGES_DIR = ASSETS_DIR / "images"
SCENES_DIR = PROJECT_ROOT / "scenes"

# Пути к файлам игры
GAME_DIR = PROJECT_ROOT / "game"
DOMAIN_DIR = GAME_DIR / "domain"
SERVICES_DIR = GAME_DIR / "services"

# Путь к уровню из редактора
MAIN_LEVEL_PATH = SCENES_DIR / "main_level.json"
```

---

## 🎯 Пути к ассетам

### Правильный способ (работает везде)
```python
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

def asset_path(name: str) -> str:
    """Получить полный путь к ассету"""
    return str((ASSETS_DIR / name).resolve())

# Использование
player_sprite = s.Sprite(asset_path("images/player.png"), ...)
```

**Преимущества:**
- Работает в `pygame` и `kivy`
- Не зависит от рабочей папки
- Чистый код без `os.path`

---

## 🔄 Scene-based архитектура

### Паттерн сцен
```python
class MenuScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.start_button = s.Button(
            "", (200, 50), s.WH_C, "Начать игру",
            on_click=lambda: s.restart_scene("game")
        )

class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (50, 50), s.WH_C, scene=self)
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_ESCAPE):
            s.restart_scene("menu")

# Запуск
s.run(scene=MenuScene)

# Переключение
s.set_scene_by_name("game", recreate=True)
```

### Жизненный цикл сцены
```python
class MyScene(s.Scene):
    def on_enter(self, context):
        # Вызывается при входе в сцену
        print(f"Вход в {self.__class__.__name__}")
    
    def update(self, dt):
        # Вызывается каждый кадр
        pass
    
    def on_exit(self):
        # Вызывается при выходе из сцены
        print(f"Выход из {self.__class__.__name__}")
```

---

## ⚡ Оптимизация

### Object Pool (пул объектов)
```python
# Создаём пул снарядов
bullets = s.ObjectPool(
    factory=lambda: s.Sprite("bullet.png", scene=self),
    pool_size=20
)

# Получаем из пула
bullet = bullets.get()
bullet.set_position(player_pos)
bullet.visible = True

# Возвращаем в пул (скрываем)
bullet.visible = False
bullets.put(bullet)
```

### Resource Cache (кэш ресурсов)
```python
from spritePro.resources import resource_cache

# Загрузка с кэшированием
texture = s.load_texture("player.png")  # Кэшируется автоматически
sound = s.load_sound("jump", "sounds/jump.mp3")

# Очистка кэша при необходимости
resource_cache.clear()
```

### Hot Reload (горячая перезагрузка)
```python
from spritePro.asset_watcher import get_hot_reload_manager

manager = get_hot_reload_manager()
manager.watch("assets/images/")  # Следить за изменениями

# При изменении файла — спрайт автоматически обновится
```

---

## 🎨 Debugging

### Debug Overlay (отладочная сетка)
```python
s.enable_debug(True)              # Включить overlay
s.set_debug_grid_enabled(True)    # Показать сетку мира
s.debug_log_info("Test message")  # Логирование
```

### Perf Snapshot (мониторинг FPS)
```python
# Включение производительности
s.set_debug_perf_enabled(True)

# Получение snapshot
snapshot = s.get_perf_snapshot()
print(f"FPS: {snapshot['fps']:.1f}")
print(f"Memory: {snapshot['memory_mb']:.1f} MB")
```

### Debug Log Styles
```python
# Настройка стилей логов
s.set_debug_log_style("info", color=(0, 255, 0))  # Зелёный для info
s.set_debug_log_style("warning", color=(255, 255, 0))  # Жёлтый
s.set_debug_log_style("error", color=(255, 0, 0))  # Красный

# Включение стека вызовов
s.set_debug_log_stack_enabled(True)
```

---

## 💾 Сохранения (PlayerPrefs)

### Паттерн сохранений
```python
class SaveSystem:
    def __init__(self):
        self.prefs = s.PlayerPrefs("save.json")
    
    def save_score(self, score: int):
        self.prefs.set_int("score", score)
        # Автосохранение в JSON
    
    def load_high_score(self) -> int:
        return self.prefs.get_int("high_score", 0)
    
    def reset(self):
        self.prefs.clear()
```

### Типы данных
```python
prefs = s.PlayerPrefs("save.json")

# Числа
prefs.set_int("score", 100)
score = prefs.get_int("score", 0)  # 0 — значение по умолчанию

prefs.set_float("health", 75.5)
health = prefs.get_float("health", 100.0)

# Строки
prefs.set_string("player_name", "Hero")
name = prefs.get_string("player_name", "Player")

# Векторы (позиция)
prefs.set_vector2("position", (400, 300))
pos = prefs.get_vector2("position", (0, 0))
```

---

## 🌐 Сетевая синхронизация

### Паттерн синхронизации позиции
```python
class MultiplayerScene(s.Scene):
    def __init__(self, net, role):
        super().__init__()
        s.multiplayer.init_context(net, role)
        self.ctx = s.multiplayer_ctx
        
        self.me = s.Sprite("", (50, 50), (200, 300), scene=self)
        self.other = s.Sprite("", (600, 300), (200, 300), scene=self)
        self.remote_pos = [600.0, 300.0]
    
    def update(self, dt):
        # Отправляем позицию каждые 16ms (~60 FPS)
        pos = self.me.get_world_position()
        self.ctx.send_every("pos", {"pos": list(pos)}, 0.016)
        
        # Обрабатываем входящие сообщения
        for msg in self.ctx.poll():
            if msg.get("event") == "pos":
                data = msg.get("data", {})
                self.remote_pos[:] = data.get("pos", [0, 0])
        
        # Обновляем удалённый спрайт
        self.other.set_position(self.remote_pos)
```

### Лобби мультиплеера
```python
# Хост
s.run(scene=MainScene, multiplayer=True, use_lobby=True)

# Клиент
s.run(
    scene=MainScene, 
    multiplayer=True, 
    host="127.0.0.1", 
    port=5050,
    use_lobby=True
)
```

---

## 🎬 Анимации и твины

### Fluent API паттерн
```python
# Плавное движение с easing
sprite.DoMove((200, 300)) \
    .SetDuration(1.0) \
    .SetEase(s.Ease.OUT_CUBIC) \
    .OnComplete(lambda: print("Пришло!")) \
    .Start()

# Циклическая анимация
sprite.DoScale(1.5) \
    .SetLoops(-1)  # -1 = бесконечно
    .SetYoyo(True) \
    .SetDuration(0.5) \
    .Start()

# Вращение
sprite.DoRotateBy(360) \
    .SetDuration(2.0) \
    .Start()
```

### Animation State Machine
```python
class Player(s.Sprite):
    def __init__(self, path, position, scene):
        super().__init__(path, (50, 50), position, scene=scene)
        
        # Создаём анимации
        self.animation = s.Animation()
        self.animation.add_state("idle", ["frame1.png", "frame2.png"])
        self.animation.add_state("walk", ["walk1.png", "walk2.png", ...])
        self.animation.add_state("jump", ["jump.png"])
        
        self.current_state = "idle"
    
    def update(self, dt):
        if s.input.is_pressed(s.pygame.K_SPACE):
            self.animation.play("jump")
        elif s.input.is_pressed(s.pygame.K_w):
            self.animation.play("walk")
        else:
            self.animation.play("idle")
```

---

## 🎮 UI паттерны

### Меню с кнопками
```python
class MenuScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Layout для меню
        menu_layout = s.Layout(
            container=s.WH_C,
            direction=s.LayoutDirection.FLEX_COLUMN,
            gap=20,
            padding=(50, 50)
        )
        
        # Кнопки
        self.start_btn = s.Button("", (200, 50), s.WH_C, "Начать")
        self.settings_btn = s.Button("", (200, 50), s.WH_C, "Настройки")
        self.exit_btn = s.Button("", (200, 50), s.WH_C, "Выход")
        
        # Добавляем в лейаут
        menu_layout.add(self.start_btn)
        menu_layout.add(self.settings_btn)
        menu_layout.add(self.exit_btn)
        
        # Привязываем события
        self.start_btn.on_click = lambda: s.restart_scene("game")
        self.exit_btn.on_click = lambda: s.quit()
```

### Инвентарь на Grid Layout
```python
class InventoryScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Сетка 4x4 для слотов
        grid = s.layout_grid(
            rows=4, 
            cols=4, 
            gap=10, 
            padding=(20, 20),
            container=s.WH_C
        )
        
        # Добавляем слоты
        for i in range(16):
            slot = s.Sprite("", (50, 50), scene=self)
            grid.add(slot)
```

---

## 📊 Производительность

### Culling невидимых объектов
```python
def update(self, dt):
    camera_rect = s.get_camera_position(), s.get_screen().get_size()
    
    for sprite in self.sprites:
        if not sprite.rect.colliderect(camera_rect):
            sprite.visible = False  # Скрываем за камерой
        else:
            sprite.visible = True   # Показываем если в кадре
```

### Оптимизация частиц
```python
# Используем пул для частиц
emitter = s.ParticleEmitter(config).use_pool(True).build()

# Ограничиваем количество активных частиц
config.max_active_particles = 100
```

---

## 🎨 Цветовые эффекты

### Pulse (пульсация)
```python
def update(self, dt):
    import math
    pulse = 0.5 + 0.5 * math.sin(s.get_time() * 2)
    self.set_alpha(pulse)
```

### Rainbow (радуга)
```python
def update(self, dt):
    import colorsys
    hue = (s.get_time() * 0.1) % 1
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    self.set_color(int(r*255), int(g*255), int(b*255))
```

### Color Flash (вспышка цвета)
```python
# Через tween
sprite.DoColorFlash((255, 255, 0), duration=0.3) \
    .SetEase(s.Ease.OUT_QUAD) \
    .Start()
```

---

## 🔄 Hot Reload (горячая перезагрузка)

### Автоматическое обновление ассетов
```python
from spritePro.asset_watcher import get_hot_reload_manager

manager = get_hot_reload_manager()
manager.watch("assets/images/")  # Следить за папкой

# При изменении файла — спрайт автоматически обновится при next update()
```

---

## 📝 Чек-лист перед релизом

### Проверка
- [ ] Все ассеты загружаются корректно
- [ ] Debug overlay отключён в production
- [ ] Perf snapshot показывает стабильный FPS (>30)
- [ ] Сохранения работают (создание/загрузка)
- [ ] Сцены переключаются без ошибок
- [ ] Звук воспроизводится на всех устройствах
- [ ] Mobile версия работает на разных экранах
- [ ] Мультиплеер синхронизирует позиции

### Оптимизация
- [ ] Удалены неиспользуемые спрайты из кэша
- [ ] Частицы используют пул объектов
- [ ] Невидимые объекты culling'уются
- [ ] Твины имеют конечную длительность

---

<div align="center">

**🎮 Готовы к продакшену?**  
Следуйте этим практикам для создания стабильных и производительных игр!

</div>
