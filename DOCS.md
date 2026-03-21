# 🎮 SpritePro v3.3.1 — Документация

**Высокоуровневый фреймворк для 2D-игр на Python (поверх Pygame)**  
🚀 Desktop • Web • Mobile • Editor • Physics • UI • Multiplayer

---

## 🎯 Быстрый старт (30 секунд)

### 1. Установка
```bash
pip install spritepro
# Для mobile/Kivy:
pip install "spritepro[kivy]"
```

### 2. Первая игра
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

### 3. Шаблон проекта
```bash
python -m spritePro.cli --create
```

**Вот и всё!** У вас есть окно, сцена, игровой цикл, рендер и управление. 🎮

---

## 📚 Полное содержание

| Раздел | Описание | Файл |
|--------|----------|------|
| **🚀 Старт** | Установка, первая игра, концепции | [GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| **🔧 API Reference** | Все классы, функции, параметры | [API_REFERENCE.md](docs/API_REFERENCE.md) |
| **💡 Best Practices** | Паттерны и оптимизация | [BEST_PRACTICES.md](docs/BEST_PRACTICES.md) |
| **📖 Руководства** | Пошаговые гайды по подсистемам | [guides/](docs/guides/) |
| **🎮 Демо-игры** | 64 примера с кодом | [DEMO_GAMES.md](docs/guides/demo_games.md) |

---

## 🛣️ Пути обучения

### Для новичков (5 шагов)
1. **[GETTING_STARTED.md](docs/GETTING_STARTED.md)** — установка и первая игра
2. **Sprite** — базовый спрайт, движение, коллизии
3. **UI компоненты** — кнопки, текст, слайдеры
4. **Твины** — плавные анимации
5. **Демо-игры** — изучите код примеров

### Для продвинутых
1. **[API_REFERENCE.md](docs/API_REFERENCE.md)** — полный справочник
2. **[physics_guide.md](docs/guides/physics_guide.md)** — физика pymunk + редактор
3. **[multiplayer_guide.md](docs/guides/multiplayer_guide.md)** — сетевая игра
4. **[mobile_web.md](docs/guides/mobile_web.md)** — mobile/Kivy, web build

### Для UI-разработчиков
1. **[ui_layouts.md](docs/guides/ui_layouts.md)** — лейауты и UI
2. **Button/ToggleButton/Slider** — интерактивные элементы
3. **Layout** — flex, grid, circle, line автолейауты

---

## 🔍 Поиск по функциям

| Что нужно | Где искать |
|-----------|------------|
| Создать спрайт | [sprite.md](docs/sprite.md), `s.sprite()` в API |
| Добавить физику | [physics_guide.md](docs/guides/physics_guide.md) |
| Анимация | [animation_tweens.md](docs/guides/animation_tweens.md) |
| UI кнопки | [button.md](docs/button.md), [ui_layouts.md](docs/guides/ui_layouts.md) |
| Текст | [text.md](docs/text.md) |
| Сохранения | [save_load.md](docs/save_load.md), `PlayerPrefs` |
| Звук | [audio.md](docs/audio.md), `AudioManager` |
| Сцены | [game_loop.md](docs/game_loop.md), `SceneManager` |
| Камера | API Reference, `set_camera_follow()` |
| Debug overlay | [debug.md](docs/debug.md) |

---

## 📖 Навигация по файлам

### Основные документы
- **[README.md](../README.md)** — главная страница проекта
- **[DOCS.md](DOCS.md)** — этот файл (главный индекс документации)
- **[OVERVIEW.md](docs/OVERVIEW.md)** — краткий обзор возможностей
- **[CHANGELOG.md](../CHANGELOG.md)** — история изменений

### Руководства (guides/)
- **physics_guide.md** — физика pymunk + редактор сцен
- **ui_layouts.md** — UI компоненты и лейауты
- **animation_tweens.md** — анимации, твины, Fluent API
- **mobile_web.md** — mobile/Kivy, web build, Android APK
- **multiplayer_guide.md** — сетевая игра, лобби, курс
- **editor_guide.md** — Sprite Editor (редактор сцен)
- **demo_games.md** — все 64 демо-игры

### Компоненты
- **sprite.md** — базовый спрайт
- **button.md** — кнопки
- **toggle_button.md** — переключатели
- **slider.md** — слайдеры
- **text_input.md** — поля ввода
- **text.md** — текст
- **bar.md**, **bar_background.md** — прогресс-бары
- **layout.md** — автолейауты
- **animation.md** — покадровая анимация
- **tween.md**, **tween_presets.md** — плавные переходы
- **timer.md** — таймеры
- **particles.md** — система частиц
- **health.md** — здоровье
- **pages.md** — страницы

### Утилиты
- **surface.md** — работа с поверхностями
- **color_effects.md** — цветовые эффекты
- **save_load.md** — сохранения
- **debug.md** — отладка
- **input.md** — ввод
- **events.md** — события (EventBus)
- **mouse_interactor.md** — мышь
- **draggable_sprite.md** — drag-and-drop

### Специальные
- **API_REFERENCE.md** — полная справка по API
- **BEST_PRACTICES.md** — лучшие практики
- **readySprites.md** — готовые спрайты
- **text_fps.md** — счётчик FPS
- **building.md** — сборка проекта
- **mobile.md** — mobile запуск
- **kivy_hybrid.md** — hybrid Kivy UI
- **networking.md** — мультиплеер
- **pygame_to_web.md** — pygame → web
- **PLUGINS_GUIDE.md** — плагины
- **VALIDATION_GUIDE.md** — валидация

### Специальные
- **sprite_editor.md** — редактор сцен
- **physics_issues.md** — нюансы физики

---

## 🎮 Демо-игры (64 штуки)

Все демо находятся в `spritePro/demoGames/`. Основные:

| Демо | Описание | Запуск |
|------|----------|--------|
| physics_demo.py | Гравитация, отскок, платформы | `python -m spritePro.demoGames.physics_demo` |
| hoop_bounce_demo.py | Шарик в обруче с отскоком | `python -m spritePro.demoGames.hoop_bounce_demo` |
| fluent_tween_demo.py | Fluent API: DoMove, SetEase, OnComplete | `python -m spritePro.demoGames.fluent_tween_demo` |
| builder_demo.py | Builder Fluent API для спрайтов и частиц | `python -m spritePro.demoGames.builder_demo` |
| layout_demo.py | Все типы лейаутов (flex, grid, circle, line) | `python -m spritePro.demoGames.layout_demo` |
| menu_shop_demo.py | Меню и инвентарь на Layout | `python -m spritePro.demoGames.menu_shop_demo` |
| local_multiplayer_demo.py | Сетевой мультиплеер (хост + клиенты) | `python -m spritePro.demoGames.local_multiplayer_demo` |
| scenes_demo.py | Сцены и переключение | `python -m spritePro.demoGames.scenes_demo` |
| editor_scene_runtime_demo.py | Сцена из редактора + логика в коде | `python -m spritePro.demoGames.editor_scene_runtime_demo` |
| ... | ... | ... |

Полный список: [DEMO_GAMES.md](docs/guides/demo_games.md)

---

## 📊 Сравнение с альтернативами

| Функция | pygame | arcade | **SpritePro** |
|---------|--------|--------|---------------|
| Автоматическая отрисовка | ❌ | ✅ | ✅ |
| Готовая камера | ❌ | ✅ | ✅ |
| Физика (pymunk) | ❌ | ✅ | ✅ |
| Layout (flex, сетка, круг) | ❌ | ❌ | ✅ |
| Редактор сцен (JSON) | ❌ | ❌ | ✅ |
| Мультиплеер (TCP, лобби) | ❌ | ❌ | ✅ |
| Система частиц | ❌ | ❌ | ✅ |
| AudioManager | ❌ | ❌ | ✅ |
| PlayerPrefs | ❌ | ❌ | ✅ |
| Якоря позиционирования | ❌ | ❌ | ✅ |

**SpritePro = pygame + физика, Layout, редактор сцен, мультиплеер и всё остальное для игры.**

---

## 🎯 Ключевые преимущества

### 🚀 Скорость разработки
- Создайте прототип игры за **минуты**, а не часы
- Меньше кода = меньше багов
- Больше времени на геймплей, меньше на инфраструктуру

### 🎨 Красота из коробки
- Автоматические анимации кнопок
- Плавные переходы (tweening)
- Готовые эффекты частиц
- Цветовые эффекты

### 🛠️ Мощность и гибкость
- Полный доступ к pygame под капотом
- Расширяемая архитектура
- Можно использовать как pygame, так и высокоуровневые функции

### 📚 Отличная документация
- Подробные примеры для каждого компонента
- Демо-игры с исходным кодом
- Понятные API

---

## 🔄 Обновления документации

**2026-03 (v3.3.1)**: Полностью переписана система документации — единый индекс, руководства, API reference, best practices.  
**2026-03 (v3.2.1)**: Sprite Editor обновлён (меню File/GameObject/Tools/View, Text-объекты, runtime).  
**2026-03 (v3.1.1)**: Android-документация уточнена, шаблон проекта улучшен.  
**2026-03 (v3.1.0)**: Virtual resolution `reference_size` добавлена.  
**2026-03 (v3.0.x)**: Mobile/Android build workflow обновлён.

---

## 📞 Обратная связь

Если вы не нашли нужную информацию или у вас есть предложения по улучшению документации:
- Создайте Issue на GitHub с тегом `documentation`
- Предложите улучшения через Pull Request
- Обсудите в GitHub Discussions

---

<div align="center">

**🎮 Начните создавать игры уже сегодня!**

[📖 GETTING_STARTED](docs/GETTING_STARTED.md) • [🔧 API Reference](docs/API_REFERENCE.md) • [💡 Best Practices](docs/BEST_PRACTICES.md) • [🎮 Демо](spritePro/demoGames/)

**Создано с ❤️ для разработчиков игр**

</div>
