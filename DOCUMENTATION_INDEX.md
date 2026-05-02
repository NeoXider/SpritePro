# Индекс документации SpritePro

Полный указатель материалов репозитория. **Все ссылки на статьи в `docs/` ведут от корня репозитория** (как на GitHub при открытии файла в корне).

<a id="doc-toc"></a>

## Быстрая навигация

| Нужно | Куда |
|--------|------|
| Установка и первая сцена | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Справочник API | [docs/API_REFERENCE.md](docs/API_REFERENCE.md) |
| Обзор подсистем | [docs/core/overview.md](docs/core/overview.md) |
| Каталог демо (команды запуска) | [docs/demo_games/demo_games.md](docs/demo_games/demo_games.md) |
| Сеть и лобби | [docs/systems/networking_guide.md](docs/systems/networking_guide.md) |
| Редактор сцен | [docs/editor/sprite_editor.md](docs/editor/sprite_editor.md) |
| Web / mobile / сборки | [docs/builds/building_web.md](docs/builds/building_web.md), [docs/builds/mobile_kivy.md](docs/builds/mobile_kivy.md) |
| Папка `docs/` на GitHub | [docs/README.md](docs/README.md) |

---

## Проект и процессы

| Файл | Описание |
|------|----------|
| [README.md](README.md) | Обзор, установка, примеры |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Как вносить вклад |
| [ROADMAP.md](ROADMAP.md) | Планы развития |
| [CHANGELOG.md](CHANGELOG.md) | История версий и заметки по документации |

Идеи игр, техспеки и гайды по перфу, если появятся в репозитории, будут добавлены сюда; сейчас см. **ROADMAP** и **CHANGELOG**.

---

## Ядро (`docs/core/`)

| Документ | Тема |
|----------|------|
| [docs/core/overview.md](docs/core/overview.md) | Краткий обзор |
| [docs/core/comprehensive_guide.md](docs/core/comprehensive_guide.md) | Развёрнутое руководство |
| [docs/core/sprite.md](docs/core/sprite.md) | Класс Sprite |
| [docs/core/spriteProGame.md](docs/core/spriteProGame.md) | Игра и точка входа |
| [docs/core/animation.md](docs/core/animation.md) | Покадровая анимация |
| [docs/core/tween_system.md](docs/core/tween_system.md) | Твины и Fluent API |
| [docs/core/tween_presets.md](docs/core/tween_presets.md) | Пресеты твинов |
| [docs/core/physics_guide.md](docs/core/physics_guide.md) | Физика pymunk |
| [docs/core/camera_and_particles.md](docs/core/camera_and_particles.md) | Камера и частицы |
| [docs/core/particles_guide.md](docs/core/particles_guide.md) | Частицы подробно |
| [docs/core/resources.md](docs/core/resources.md) | Ресурсы |
| [docs/core/BUILDER_API.md](docs/core/BUILDER_API.md) | Fluent Builder |
| [docs/core/exceptions.md](docs/core/exceptions.md) | Исключения |
| [docs/core/input_validation.md](docs/core/input_validation.md) | Валидация ввода |
| [docs/core/VALIDATION_GUIDE.md](docs/core/VALIDATION_GUIDE.md) | Валидация в проекте |

---

## UI (`docs/ui/`)

| Документ | Тема |
|----------|------|
| [docs/ui/button.md](docs/ui/button.md) | Button |
| [docs/ui/toggle_button.md](docs/ui/toggle_button.md) | ToggleButton |
| [docs/ui/slider.md](docs/ui/slider.md) | Slider |
| [docs/ui/text.md](docs/ui/text.md) | TextSprite |
| [docs/ui/text_input.md](docs/ui/text_input.md) | TextInput |
| [docs/ui/text_fps.md](docs/ui/text_fps.md) | Счётчик FPS |
| [docs/ui/layout_ui.md](docs/ui/layout_ui.md) | Layout, ScrollView |
| [docs/ui/pages_guide.md](docs/ui/pages_guide.md) | Pages |
| [docs/ui/mouse_interactor.md](docs/ui/mouse_interactor.md) | MouseInteractor |
| [docs/ui/draggable_sprite.md](docs/ui/draggable_sprite.md) | Перетаскивание |
| [docs/ui/bar.md](docs/ui/bar.md) | Bar |
| [docs/ui/bar_background.md](docs/ui/bar_background.md) | Bar с фоном |
| [docs/ui/clip_mask.md](docs/ui/clip_mask.md) | ClipMask |

---

## Системы (`docs/systems/`)

| Документ | Тема |
|----------|------|
| [docs/systems/game_loop.md](docs/systems/game_loop.md) | Цикл, сцены, `reference_size` |
| [docs/systems/input_system.md](docs/systems/input_system.md) | Ввод |
| [docs/systems/events_system.md](docs/systems/events_system.md) | EventBus |
| [docs/systems/timer_component.md](docs/systems/timer_component.md) | Таймеры |
| [docs/systems/health_component.md](docs/systems/health_component.md) | Здоровье |
| [docs/systems/networking_guide.md](docs/systems/networking_guide.md) | Сеть, лобби, декораторы |
| [docs/systems/multiplayer.md](docs/systems/multiplayer.md) | Мультиплеер (обзор) |

---

## Утилиты (`docs/utils/`)

| Документ | Тема |
|----------|------|
| [docs/utils/save_load.md](docs/utils/save_load.md) | Сохранения |
| [docs/utils/surface.md](docs/utils/surface.md) | Поверхности |
| [docs/utils/audio.md](docs/utils/audio.md) | Аудио |
| [docs/utils/debug_overlay.md](docs/utils/debug_overlay.md) | Отладочный оверлей |
| [docs/utils/color_effects.md](docs/utils/color_effects.md) | Цветовые эффекты |
| [docs/utils/camera_effects.md](docs/utils/camera_effects.md) | Эффекты камеры |
| [docs/utils/scroll.md](docs/utils/scroll.md) | ScrollController / ScrollArea |
| [docs/utils/grid_renderer.md](docs/utils/grid_renderer.md) | Сетка |
| [docs/utils/resource_watcher.md](docs/utils/resource_watcher.md) | Hot reload |
| [docs/utils/angle_utils.md](docs/utils/angle_utils.md) | Углы |

---

## Редактор и сборки

| Документ | Тема |
|----------|------|
| [docs/editor/sprite_editor.md](docs/editor/sprite_editor.md) | Sprite Editor, `spawn_scene`, экспорт |
| [docs/editor/physics_issues.md](docs/editor/physics_issues.md) | Физика в редакторе |
| [docs/builds/building_web.md](docs/builds/building_web.md) | Web, wheel, pygbag |
| [docs/builds/web_build.md](docs/builds/web_build.md) | Web-сборка |
| [docs/builds/pygame_to_web.md](docs/builds/pygame_to_web.md) | pygame → web |
| [docs/builds/mobile_kivy.md](docs/builds/mobile_kivy.md) | Kivy / mobile |
| [docs/builds/kivy_hybrid.md](docs/builds/kivy_hybrid.md) | Kivy + игровая область |

---

## Демо и примеры

| Материал | Описание |
|----------|----------|
| [docs/demo_games/demo_games.md](docs/demo_games/demo_games.md) | Полный список демо и команд |
| [docs/demo_games/readySprites.md](docs/demo_games/readySprites.md) | Готовые сцены и компоненты |
| [demoGames/README.md](demoGames/README.md) | Демо в корне с `level.json` |
| [multiplayer_course/README.md](multiplayer_course/README.md) | Курс по сетевой игре |
| [multiplayer_course/tictactoe_example/README.md](multiplayer_course/tictactoe_example/README.md) | Крестики-нолики |

Исходники демо: каталог `spritePro/demoGames/` (запуск через `python -m spritePro.demoGames.<имя>`).

---

## CLI и плагины

| Документ | Тема |
|----------|------|
| [docs/cli_tools/PLUGINS_GUIDE.md](docs/cli_tools/PLUGINS_GUIDE.md) | Плагины |

---

## Прочее в `docs/`

| Документ | Тема |
|----------|------|
| [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | Практики разработки |

---

## Порядок изучения

**Новичок:** [README.md](README.md) → [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) → [docs/core/sprite.md](docs/core/sprite.md) → [docs/ui/button.md](docs/ui/button.md) → [docs/demo_games/demo_games.md](docs/demo_games/demo_games.md).

**Игра с уровнями:** [docs/editor/sprite_editor.md](docs/editor/sprite_editor.md) → [docs/core/physics_guide.md](docs/core/physics_guide.md) → демо `editor_scene_runtime_demo`, `physics_demo`.

**Сеть:** [docs/systems/networking_guide.md](docs/systems/networking_guide.md) → [multiplayer_course/README.md](multiplayer_course/README.md).

---

## Обновления документации

Актуальная история изменений библиотеки и сопутствующих правок в доках — в [CHANGELOG.md](CHANGELOG.md). Этот индекс поддерживается вместе с кодом: при добавлении нового `.md` в `docs/` строка должна появиться в соответствующей таблице выше.

---

## Обратная связь

Вопросы и предложения по документации — [Issues](https://github.com/NeoXider/SpritePro/issues) с тегом `documentation` или pull request.

**Совет:** в начале страницы — [быстрая навигация](#doc-toc). Внутри папки `docs/` удобнее открыть [docs/README.md](docs/README.md).
