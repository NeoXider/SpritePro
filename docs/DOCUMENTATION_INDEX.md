# 📚 Документация SpritePro v3.4.0

**Полная навигационная карта всех разделов документации**

---

## 🎯 Быстрый старт (5 минут)

### 1. Установка
```bash
pip install spritepro
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

s.run(scene=MainScene, size=(800, 600), title="Моя игра")
```

### 3. Шаблон проекта
```bash
python -m spritePro.cli --create
```

---

## 📖 Структура документации

### 🔥 Ядро (Core) — `docs/core/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Быстрый старт** | Установка, первая игра, шаблон проекта | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Builder API** | Fluent API для спрайтов и частиц | [BUILDER_API.md](core/BUILDER_API.md) |
| **Tween система** | Плавные анимации и easing функции | [tween_system.md](core/tween_system.md) |
| **Tween Presets** | Готовые твины для позиции, масштаба, поворота, цвета | [tween_presets.md](core/tween_presets.md) |
| **Физика (pymunk)** | DYNAMIC/STATIC/KINEMATIC тела, коллизии | [physics_guide.md](core/physics_guide.md) |
| **Частицы** | ParticleEmitter, шаблоны, пулы | [particles_guide.md](core/particles_guide.md) |
| **Sprite** | Базовый класс спрайта с анимациями и эффектами | [sprite.md](core/sprite.md) |
| **Camera & Particles** | Камера и частицы вместе | [camera_and_particles.md](core/camera_and_particles.md) |
| **SpriteProGame** | Главный класс игры и жизненный цикл | [spriteProGame.md](core/spriteProGame.md) |
| **Exceptions** | Пользовательские исключения движка | [exceptions.md](core/exceptions.md) |
| **Resources** | Система кэширования и управления ресурсами | [resources.md](core/resources.md) |
| **Input Validation** | Валидация пользовательского ввода | [input_validation.md](core/input_validation.md) |

### 🎨 UI Components — `docs/ui/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Button** | Интерактивная кнопка с состояниями | [button.md](ui/button.md) |
| **Toggle Button** | Переключатель ВКЛ/ВЫКЛ | [toggle_button.md](ui/toggle_button.md) |
| **Slider** | Ползунок для значений | [slider.md](ui/slider.md) |
| **TextInput** | Текстовое поле ввода | [text_input.md](ui/text_input.md) |
| **Text Sprite** | Компонент текста с эффектами | [text.md](ui/text.md) |
| **Text FPS** | Отображение FPS в тексте | [text_fps.md](ui/text_fps.md) |
| **Bar & Background** | Полосы прогресса (HP, опыт) | [bar.md](ui/bar.md), [bar_background.md](ui/bar_background.md) |
| **Layout** | Автолейауты (flex, сетка, круг, линия) | [layout_ui.md](ui/layout_ui.md) |
| **Pages Manager** | Управление страницами UI | [pages_guide.md](ui/pages_guide.md) |
| **Mouse Interactor** | Взаимодействие с мышью | [mouse_interactor.md](ui/mouse_interactor.md) |
| **Draggable Sprite** | Drag-and-drop компонент | [draggable_sprite.md](ui/draggable_sprite.md) |

### 🎮 Systems — `docs/systems/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Game Loop** | Базовый цикл и сцены для разделения экранов | [game_loop.md](systems/game_loop.md) |
| **Event System** | EventBus для подписки на события | [events_system.md](systems/events_system.md) |
| **Input System** | InputState в стиле Unity | [input_system.md](systems/input_system.md) |
| **Networking** | Минимальные TCP-хелперы для мультиплеера | [networking_guide.md](systems/networking_guide.md) |
| **Health Component** | Система управления здоровьем | [health_component.md](systems/health_component.md) |
| **Timer Component** | Система таймеров и задержек | [timer_component.md](systems/timer_component.md) |
| **Multiplayer** | Полноценная система для сетевых игр | [multiplayer.md](systems/multiplayer.md) |

### 🛠️ Utils — `docs/utils/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Audio Manager** | Звук и музыка | [audio.md](utils/audio.md) |
| **Save/Load** | PlayerPrefs, JSON сохранения | [save_load.md](utils/save_load.md) |
| **Debug Overlay** | Отладка, сетка, профилирование | [debug_overlay.md](utils/debug_overlay.md) |
| **Surface Utils** | Утилиты для работы с поверхностями Pygame | [surface.md](utils/surface.md) |
| **Color Effects** | Динамические цветовые эффекты и анимации | [color_effects.md](utils/color_effects.md) |
| **Angle Utils** | Утилиты для работы с углами и вращением | [angle_utils.md](utils/angle_utils.md) |
| **Resource Watcher** | Hot reload для ассетов | [resource_watcher.md](utils/resource_watcher.md) |
| **Camera Effects** | Shake, zoom, fade, flash для камеры | [camera_effects.md](utils/camera_effects.md) |
| **Grid Renderer** | Отрисовка сеток и тайловых карт | [grid_renderer.md](utils/grid_renderer.md) |
| **Scroll System** | Прокрутка контента с инерцией | [scroll.md](utils/scroll.md) |

### 📱 Builds — `docs/builds/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Mobile/Kivy** | Запуск через Kivy, touch-ввод | [mobile_kivy.md](builds/mobile_kivy.md) |
| **Kivy Hybrid** | Kivy UI + встроенная игровая область SpritePro | [kivy_hybrid.md](builds/kivy_hybrid.md) |
| **Web Build** | Сборка для WebAssembly | [building_web.md](builds/building_web.md), [web_build.md](builds/web_build.md) |
| **Pygame to Web** | Конвертация pygame в веб-приложение | [pygame_to_web.md](builds/pygame_to_web.md) |

### 🎨 Editor — `docs/editor/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Sprite Editor** | Визуальный редактор сцен, JSON экспорт | [sprite_editor.md](editor/sprite_editor.md) |
| **Physics Issues** | Известные проблемы физики pymunk | [physics_issues.md](editor/physics_issues.md) |

### 🚀 CLI Tools — `docs/cli_tools/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **CLI Guide** | Командная строка, создание проектов | [PLUGINS_GUIDE.md](cli_tools/PLUGINS_GUIDE.md) |

### 📚 Справочники — `docs/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **API Reference** | Полный справочник всех классов и функций | [API_REFERENCE.md](API_REFERENCE.md) |
| **Best Practices** | Паттерны и лучшие практики разработки | [BEST_PRACTICES.md](BEST_PRACTICES.md) |
| **Overview** | Краткий обзор всех модулей | [OVERVIEW.md](core/overview.md) |

### 🎮 Demo Games — `docs/demo_games/`

| Раздел | Описание | Ссылка |
|--------|----------|--------|
| **Demo Games** | 54 демонстрационные игры с описанием | [demo_games.md](demo_games/demo_games.md) |
| **Ready Sprites** | Готовые спрайты для немедленного использования | [readySprites.md](demo_games/readySprites.md) |

---

## 🎯 Порядок изучения

### Для новичков:
1. ✅ [GETTING_STARTED.md](GETTING_STARTED.md) - базовый старт
2. ✅ [BUILDER_API.md](core/BUILDER_API.md) - создание спрайтов
3. ✅ [tween_system.md](core/tween_system.md) - анимации
4. ✅ [button.md](ui/button.md), [slider.md](ui/slider.md) - UI элементы

### Для продвинутых:
1. ✅ [physics_guide.md](core/physics_guide.md) - физика pymunk
2. ✅ [particles_guide.md](core/particles_guide.md) - частицы
3. ✅ [game_loop.md](systems/game_loop.md) - сцены и циклы
4. ✅ [audio.md](utils/audio.md) - звук

### Для экспертов:
1. ✅ [sprite_editor.md](editor/sprite_editor.md) - редактор сцен
2. ✅ [networking_guide.md](systems/networking_guide.md) - мультиплеер
3. ✅ [PLUGINS_GUIDE.md](cli_tools/PLUGINS_GUIDE.md) - плагины и CLI
4. ✅ [save_load.md](utils/save_load.md) - сохранения

---

## 🎮 Демо-игры (54 файла)

Все демо-игры находятся в `spritePro/demoGames/`. Запуск: `python -m spritePro.demoGames.<имя>`

### Категории демо:

#### 🏗 Базовые компоненты
- [physics_demo.py](demoGames/physics_demo.py) - физика pymunk
- [tween_presets_demo.py](demoGames/tween_presets_demo.py) - твины
- [particle_demo.py](demoGames/particle_demo.py) - частицы
- [debug_overlay_demo.py](demoGames/debug_overlay_demo.py) - debug tools

#### 🎨 UI & Layout
- [layout_demo.py](demoGames/layout_demo.py) - автолейауты
- [menu_shop_demo.py](demoGames/menu_shop_demo.py) - меню и инвентарь
- [slider_textinput_demo.py](demoGames/slider_textinput_demo.py) - слайдер + ввод

#### 🎬 Анимация & Эффекты
- [fluent_tween_demo.py](demoGames/fluent_tween_demo.py) - Fluent API
- [fireworks_demo.py](demoGames/fireworks_demo.py) - фейерверк
- [color_text_demo.py](demoGames/color_text_demo.py) - текст с эффектами

#### 🎮 Игровая логика
- [easy_clicker.py](demoGames/easy_clicker.py) - кликер с улучшениями
- [hero_vs_enemy.py](demoGames/hero_vs_enemy.py) - бой герой vs враг
- [ping_pong.py](demoGames/ping_pong.py) - пинг-понг

#### 🌐 Сеть & Мультиплеер
- [local_multiplayer_demo.py](demoGames/local_multiplayer_demo.py) - хост + клиенты
- [three_clients_move_demo.py](demoGames/three_clients_move_demo.py) - 3 клиента синхронизация

#### 💾 Утилиты & Оптимизация
- [save_load_demo.py](demoGames/save_load_demo.py) - PlayerPrefs
- [object_pool_demo.py](demoGames/object_pool_demo.py) - пул объектов
- [hot_reload_demo.py](demoGames/hot_reload_demo.py) - горячая перезагрузка

#### 📱 Mobile & Kivy
- [mobile_orb_collector_demo.py](demoGames/mobile_orb_collector_demo.py) - mobile-first
- [kivy_hybrid_demo.py](demoGames/kivy_hybrid_demo.py) - Kivy UI + игра

---

## 🔍 Поиск по документации

### Найти фичу:
1. Откройте [API_REFERENCE.md](API_REFERENCE.md) для полного списка API
2. Используйте поиск в файле (Ctrl+F) по ключевым словам: `sprite`, `button`, `physics`, `tween`, `particle`

### Найти пример:
1. Перейдите к [DEMO_GAMES.md](demo_games/demo_games.md)
2. Найдите нужную категорию демо
3. Запустите через CLI: `python -m spritePro.demoGames.<имя>`

---

## 📝 Обновления в v3.4.0

### Новые возможности:
- ✅ **Editor-first workflow** - визуальный редактор сцен + JSON экспорт
- ✅ **Builder Pattern** - Fluent API для спрайтов и частиц
- ✅ **Mobile/Kivy support** - запуск на Android через Kivy
- ✅ **Hot Reload** - автоматическое обновление ассетов при изменении
- ✅ **Object Pooling** - оптимизация производительности
- ✅ **Plugin System** - расширяемые плагины и хуки
- ✅ **Новая документация** - полная документация всех модулей на русском языке:
  - Camera Effects (shake, zoom, fade)
  - Grid Renderer (сетки и тайловые карты)
  - Scroll System (прокрутка с инерцией)
  - Multiplayer System (полноценный сетевой движок)
  - Resource Watcher (мониторинг ассетов)
  - Angle Utils (работа с углами)
  - Exceptions (система исключений)
  - Resources (кэширование ресурсов)
  - Input Validation (валидация ввода)

### Улучшения:
- ✅ Полная документация по всем модулям
- ✅ 54 демонстрационные игры с примерами
- ✅ CLI инструменты для автоматизации
- ✅ Web Build через WebAssembly
- ✅ Debug Overlay с профилированием FPS

---

## 🎯 Рекомендации

### Для быстрого старта:
1. Прочитайте [GETTING_STARTED.md](GETTING_STARTED.md)
2. Запустите [physics_demo.py](demoGames/physics_demo.py)
3. Изучите [BUILDER_API.md](core/BUILDER_API.md) для создания спрайтов

### Для продвинутой разработки:
1. Изучите [physics_guide.md](core/physics_guide.md) - физика pymunk
2. Прочитайте [tween_system.md](core/tween_system.md) - анимации
3. Ознакомьтесь с [sprite_editor.md](editor/sprite_editor.md) - редактор сцен

### Для продакшена:
1. Изучите [object_pooling.md](utils/object_pooling.md) - оптимизация
2. Прочитайте [debug_overlay.md](utils/debug_overlay.md) - отладка
3. Используйте [save_load.md](utils/save_load.md) - сохранения

---

<div align="center">

**🎮 Готовы к практике?**  
Начните с [GETTING_STARTED](GETTING_STARTED.md) или запустите [демо-игры](demo_games/demo_games.md)!

</div>
