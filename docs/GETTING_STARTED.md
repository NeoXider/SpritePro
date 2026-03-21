# 🚀 Getting Started — SpritePro v3.4.0

**Быстрый старт для новичков: установка, первая игра, базовые концепции**

---

## 1️⃣ Установка (2 минуты)

### Способ 1: Через pip (рекомендуемый)
```bash
pip install spritepro
```

Для mobile/Kivy-режима:
```bash
pip install "spritepro[kivy]"
```

### Способ 2: Из исходного кода (для разработчиков)
```bash
git clone https://github.com/NeoXider/SpritePro.git
cd SpritePro
pip install -e .
```

---

## 2️⃣ Первая игра за 5 минут

Создайте файл `my_game.py`:

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        # Создаём спрайт игрока в центре экрана
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)
    
    def update(self, dt):
        # Обработка ввода (WASD/стрелки)
        self.player.handle_keyboard_input()

# Запуск игры
s.run(scene=MainScene, size=(800, 600), title="Моя первая игра")
```

Запустите:
```bash
python my_game.py
```

**Готово!** У вас есть окно, сцена, игровой цикл и управление. 🎮

---

## 3️⃣ Шаблон проекта (CLI)

Для быстрого старта с правильной структурой:

```bash
python -m spritePro.cli --create
```

Или в отдельную папку:
```bash
python -m spritePro.cli --create MyGame
```

**Что создаст:**
- `main.py` — точка входа
- `config.py` — настройки и пути к ассетам
- `game_events.py` — базовые события через EventBus
- `scenes/main_scene.py` — главная сцена
- `scenes/second_scene.py` — вторая сцена (заготовка)
- `scenes/main_level.json` — стартовый уровень из редактора
- `assets/audio/`, `assets/images/` — папки для ассетов

---

## 4️⃣ Базовые концепции

### Сцена (Scene)
**Сцена** — изолированный игровой мир с собственным циклом обновления. Каждая сцена имеет:
- `__init__()` — инициализация объектов
- `update(dt)` — вызывается каждый кадр
- `on_enter(context)` — вызывается при входе в сцену
- `on_exit()` — вызывается при выходе из сцены

**Переключение между сценами:**
```python
s.restart_scene()           # Перезапуск текущей сцены
s.set_scene_by_name("menu") # Переключение на сцену "menu"
```

### Спрайт (Sprite)
**Спрайт** — базовый визуальный объект. Основные возможности:
- Позиционирование: `set_position(x, y)`
- Трансформации: `set_scale()`, `set_rotation()`, `set_color()`
- Движение: `handle_keyboard_input()`, `move_towards()`
- Коллизии: `collides_with()`, `collide_mask()`

**Создание спрайта:**
```python
# Пустой прямоугольник
sprite = s.Sprite("", (100, 100), (50, 30), scene=scene)

# С изображением
sprite = s.Sprite("player.png", (100, 100), (50, 30), scene=scene)

# С физикой
s.add_physics(sprite, shape=s.PhysicsShape.BOX)
```

### Игровой цикл
SpritePro автоматически управляет игровым циклом:
- `update(dt)` — вызывается ~60 раз в секунду (dt = delta time в секундах)
- `draw(screen)` — отрисовка спрайтов
- Обработка событий (keyboard, mouse)

**Ваш код:**
```python
def update(self, dt):
    # Логика игры (вызывается каждый кадр)
    self.player.handle_keyboard_input()
    
    if s.input.was_pressed(s.pygame.K_SPACE):
        print("Прыжок!")
```

---

## 5️⃣ 5-минутный туториал

### Шаг 1: Создаём игрока
```python
class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        # Игрок в центре экрана, размер 50x30, скорость 5
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)
```

### Шаг 2: Добавляем управление
```python
def update(self, dt):
    # WASD / стрелки
    self.player.handle_keyboard_input()
```

### Шаг 3: Добавляем камеру
```python
def __init__(self):
    super().__init__()
    self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)
    
    # Камера следит за игроком
    s.set_camera_follow(self.player)
```

### Шаг 4: Добавляем платформы
```python
def __init__(self):
    super().__init__()
    self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)
    
    # Платформы (статическая физика)
    self.platform1 = s.Sprite("", (200, 20), (200, 400), scene=self)
    self.platform2 = s.Sprite("", (200, 20), (500, 350), scene=self)
    
    # Добавляем физику
    s.add_static_physics(self.platform1)
    s.add_static_physics(self.platform2)
    
    # Камера следит за игроком
    s.set_camera_follow(self.player)
```

### Шаг 5: Запускаем!
```python
s.run(scene=MainScene, size=(800, 600), title="Platformer", fill_color=(135, 206, 235))
```

**Полный код:**
```python
import spritePro as s

class PlatformerScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (50, 50), s.WH_C, speed=5, scene=self)
        
        # Платформы
        self.platforms = [
            s.Sprite("", (200, 20), (200, 400), scene=self),
            s.Sprite("", (200, 20), (500, 350), scene=self),
        ]
        
        # Физика платформ
        for p in self.platforms:
            s.add_static_physics(p)
        
        # Камера
        s.set_camera_follow(self.player)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(scene=PlatformerScene, size=(800, 600), title="Platformer", fill_color=(135, 206, 235))
```

---

## 6️⃣ Полезные команды

### Запуск демо-игр
```bash
# Физика
python -m spritePro.demoGames.physics_demo

# Твины (анимации)
python -m spritePro.demoGames.fluent_tween_demo

# Лейауты
python -m spritePro.demoGames.layout_demo

# Мультиплеер
python -m spritePro.demoGames.local_multiplayer_demo --quick
```

### Mobile preview
```bash
# Preview разных экранов
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --list-screen-presets
```

### Android build
```bash
# Сборка APK
python -m spritePro.cli --android .
python -m spritePro.cli --android . --android-mode release
python -m spritePro.cli --android . --android-orientation portrait
```

---

## 7️⃣ Следующие шаги

### Изучите документацию
1. **[API Reference](docs/API_REFERENCE.md)** — полный справочник всех классов и функций
2. **[Physics Guide](docs/guides/physics_guide.md)** — физика pymunk + редактор сцен
3. **[UI & Layouts](docs/guides/ui_layouts.md)** — UI компоненты и автолейауты
4. **[Animation & Tweens](docs/guides/animation_tweens.md)** — анимации и плавные переходы

### Практикуйтесь
- Изучите код демо-игр в `spritePro/demoGames/`
- Попробуйте изменить параметры в туториале
- Создайте свой проект через `python -m spritePro.cli --create`

### Сообщество
- [GitHub Issues](https://github.com/NeoXider/SpritePro/issues) — вопросы и баги
- [GitHub Discussions](https://github.com/NeoXider/SpritePro/discussions) — обсуждения
- [multiplayer_course](multiplayer_course/README.md) — курс по сетевой игре

---

## 🎯 Частые вопросы

**Q: Как загрузить изображение?**  
A: `s.Sprite("path/to/image.png", ...)` или через Builder: `s.sprite("image.png").build()`

**Q: Как добавить физику?**  
A: `s.add_physics(sprite, shape=s.PhysicsShape.BOX)` для динамического тела  
   `s.add_static_physics(sprite)` для статической (стена/пол)

**Q: Как сделать анимацию?**  
A: Используйте твины: `sprite.DoMove((100, 200)).SetDuration(1.0).Start()`

**Q: Как сохранить данные?**  
A: `prefs = s.PlayerPrefs("save.json")` → `prefs.set_int("score", 100)`

**Q: Как запустить mobile-версию?**  
A: `s.run(scene=MainScene, platform="kivy")`

---

<div align="center">

**🎮 Готовы к следующему шагу?**  
Перейдите к [API Reference](docs/API_REFERENCE.md) или изучите [демо-игры](docs/guides/demo_games.md)!

</div>
