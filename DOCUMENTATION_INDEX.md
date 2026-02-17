# Индекс документации SpritePro

Полный указатель всей документации проекта SpritePro.

## 📋 Основные документы проекта

### [README.md](README.md)
**Главная страница проекта**
- Обзор возможностей библиотеки
- Быстрый старт и установка
- Примеры использования
- Ссылки на всю документацию

### [docs/OVERVIEW.md](docs/OVERVIEW.md) 📋
**Краткий обзор SpritePro**
- Layout, мультиплеер, основные подсистемы
- Таблицы типов лейаутов, API
- Полезные пути и команды запуска демо

### [ROADMAP.md](ROADMAP.md) 🗺️
**План развития проекта**
- Краткосрочные цели (v1.1 - v1.3)
- Среднесрочные цели (v1.4 - v2.0)
- Долгосрочные цели (v2.1+)
- Временные рамки и приоритеты
- Новые игровые системы и компоненты

### [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md) 🔧
**Технические спецификации**
- Архитектурные принципы
- Детальные спецификации планируемых функций
- Примеры API и кода
- Требования к производительности
- Интеграция с существующими системами

### [CONTRIBUTING.md](CONTRIBUTING.md) 🤝
**Руководство по участию**
- Как внести вклад в проект
- Стандарты кодирования
- Процесс разработки
- Создание документации
- Система благодарностей

### [GAME_IDEAS.md](GAME_IDEAS.md) 🎮
**Идеи игр и примеров**
- Простые игры для начинающих
- Игры среднего уровня сложности
- Продвинутые проекты
- Демонстрационные примеры
- Образовательные проекты

### [PERFORMANCE.md](PERFORMANCE.md) ⚡
**Оптимизация производительности**
- Цели производительности
- Текущие оптимизации
- Планируемые улучшения
- Профилирование и мониторинг
- Бенчмарки и тесты

## 📚 Документация компонентов

### Основные компоненты

#### [docs/sprite.md](docs/sprite.md)
**Базовая система спрайтов**
- Создание и управление спрайтами
- Позиционирование и трансформации
- Цепочки вызовов (set_position, set_scale, set_alpha и др. возвращают self)
- Базовые методы отрисовки

#### [docs/sprite_editor.md](docs/sprite_editor.md)
**Редактор спрайтов (Sprite Editor)** — один документ покрывает и редактор, и использование сцен в своём проекте.
- **Редактор:** запуск (`python -m spritePro.cli --editor`), интерфейс (Viewport, Hierarchy, Inspector, Toolbar), инструменты (Select, Move, Rotate, Scale), типы спрайтов (Image, Rect/Circle/Ellipse), Drag & Drop, сохранение/загрузка JSON, координаты по центру объекта, Undo/Redo, камера.
- **Использование сцены в игре:** `spawn_scene("level.json", scene=...)`, получение по имени (`rt.first("player")`, `rt.exact("name")`, `rt.startswith("enemy")`), `placement()` (pos = центр), `to_button`, `to_text_sprite`, `to_toggle`, `.Sprite(**kwargs)`.
- **Экспорт сцены из кода в JSON:** `EditorScene.export_from_runtime(scene_instance_or_class, path)` — round-trip: код → JSON → правки в редакторе → загрузка в игре. Примеры: [editor_scene_runtime_demo.py](spritePro/demoGames/editor_scene_runtime_demo.py), [scenes_demo editor.py](spritePro/demoGames/scenes_demo editor.py).



### UI компоненты

#### [docs/button.md](docs/button.md)
**Интерактивные кнопки**
- Создание кнопок
- Обработка событий
- Стилизация и анимации

#### [docs/toggle_button.md](docs/toggle_button.md)
**Переключатели**
- Кнопки-переключатели
- Состояния вкл/выкл
- Группы переключателей

#### [docs/slider.md](docs/slider.md)
**Слайдер**
- Slider(Sprite), два режима: auto_register и ручная отрисовка
- handle_event(), draw(screen), on_change
- Примеры в сцене и вне игрового цикла

#### [docs/text_input.md](docs/text_input.md)
**Поле ввода текста**
- TextInput(Button), placeholder, value, max_length
- on_change, on_submit, Enter/Escape/TEXTINPUT
- activate/deactivate, handle_event

#### [docs/text.md](docs/text.md)
**Система текста**
- Рендеринг текста
- Шрифты и стили
- Многострочный текст

#### [docs/mouse_interactor.md](docs/mouse_interactor.md)
**Взаимодействие с мышью**
- Обработка кликов
- Hover эффекты
- Drag & Drop

#### [docs/draggable_sprite.md](docs/draggable_sprite.md)
**Drag-and-drop спрайт**
- Перетаскивание объектов
- Колбэки начала/конца
- Возврат на место

#### [docs/pages.md](docs/pages.md)
**Pages**
- Страницы и менеджер страниц
- Автовключение/выключение спрайтов

#### [docs/layout.md](docs/layout.md)
**Layout**
- Автолейаут: flex, сетка, окружность, линия
- Контейнер — спрайт, rect или сам лейаут
- set_size((w, h)) при container=None — размер в пикселях, затем apply()
- Цепочки вызовов: add, add_children, remove, apply, refresh, set_size возвращают self

### Игровые системы

#### [docs/animation.md](docs/animation.md)
**Система анимации**
- Покадровая анимация
- Управление состояниями
- Циклы и переходы

#### [docs/tween.md](docs/tween.md)
**Плавные переходы**
- Easing функции (EasingType, Ease)
- Анимация свойств
- Цепочки анимаций

#### [docs/tween_presets.md](docs/tween_presets.md)
**Готовые твины и Fluent API**
- Позиция, масштаб, поворот, цвет, прозрачность
- **Fluent API** на Sprite: DoMove, DoScale, DoRotateBy, DoColor, DoFadeOut/In, SetEase, SetDelay, OnComplete, SetLoops, SetYoyo, Kill

#### [docs/networking.md](docs/networking.md)
**Networking**
- Минимальные TCP-хелперы, run(), MultiplayerContext
- Файловые логи в spritepro_logs, net_log_to_overlay
- Примеры мультиплеера

#### [docs/timer.md](docs/timer.md)
**Система времени**
- Таймеры и задержки
- Планирование событий
- Игровое время

#### [docs/game_loop.md](docs/game_loop.md)
**Игровой цикл и сцены**
- Базовый цикл
- Сцены и их жизненный цикл

#### [docs/input.md](docs/input.md)
**Ввод**
- InputState (was_pressed, is_pressed, оси, мышь)
- Сырые события pygame

#### [docs/events.md](docs/events.md)
**События (EventBus)**
- EventBus: connect, send, disconnect, get_event
- EventSignal: get_event(name).send(route="all", net=ctx, **payload) — тот же роутинг, что у events.send
- GlobalEvents: QUIT, KEY_DOWN, KEY_UP, MOUSE_DOWN, MOUSE_UP, TICK
- LocalEvent, роутинг и сеть (route, net)

#### [docs/debug.md](docs/debug.md)
**Debug Overlay**
- Сетка мира и координаты камеры
- Логи с тайм‑аутом

#### [docs/particles.md](docs/particles.md)
**Частицы**
- Время жизни (секунды или миллисекунды)
- Гравитация, скорость и углы
- Слои отрисовки (sorting_order)
- Частицы на основе изображений, поворот и масштаб

#### [docs/camera_and_particles.md](docs/camera_and_particles.md)
**Камера и частицы**
- Управление камерой и режим слежения
- Система частиц и их конфигурация
- Примеры использования

#### [docs/bar.md](docs/bar.md)
**Прогресс-бары**
- Unity-style fillAmount функциональность
- 4 направления заполнения (горизонтальные и вертикальные)
- Плавная анимация изменений
- Корректная работа с якорями

#### [docs/bar_background.md](docs/bar_background.md)
**Прогресс-бары с фоном**
- Отдельные изображения для фона и заполнения
- Фоновое изображение всегда видимо
- Заполнение обрезается по направлению
- Все функции базового Bar класса

#### [docs/health.md](docs/health.md)
**Система здоровья**
- Управление HP
- Урон и лечение
- Callbacks и события

### Утилиты

#### [docs/surface.md](docs/surface.md)
**Работа с поверхностями**
- Создание и модификация поверхностей
- Эффекты и фильтры
- Оптимизация рендеринга

#### [docs/color_effects.md](docs/color_effects.md)
**Цветовые эффекты**
- Динамические цвета
- Градиенты и переходы
- Анимированные эффекты

#### [docs/save_load.md](docs/save_load.md) ✨
**Система сохранения/загрузки**
- Сохранение игровых данных
- Поддержка различных форматов
- Автоматические резервные копии
- Сериализация пользовательских классов

### Готовые компоненты

#### [docs/readySprites.md](docs/readySprites.md)
**Обзор готовых компонентов**
- Предварительно настроенные спрайты
- Готовые к использованию элементы
- Примеры интеграции

#### [docs/text_fps.md](docs/text_fps.md)
**Счетчик FPS**
- Автоматическое отображение FPS
- Настройка внешнего вида
- Мониторинг производительности

## 🎮 Демонстрационные игры

- [Layout Demo](spritePro/demoGames/layout_demo.py) - Все типы лейаутов (flex, grid, circle, line)
- [Menu/Shop Demo](spritePro/demoGames/menu_shop_demo.py) - Меню и инвентарь на Layout
- [Fluent Tween Demo](spritePro/demoGames/fluent_tween_demo.py) - Fluent API: DoMove, DoScale, SetEase, SetLoops, OnComplete, Kill
- [Tween Demo](spritePro/demoGames/tweenDemo.py) - Базовые твины
- [Tween Presets Demo](spritePro/demoGames/tween_presets_demo.py) - Готовые пресеты твинов
- [FPS Camera Demo](spritePro/demoGames/fps_camera_demo/fps_camera_demo.py) - Камера и FPS
- [Local Multiplayer Demo](spritePro/demoGames/local_multiplayer_demo.py) - Сетевой мультиплеер
- [TicTacToe Multiplayer](multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py) - Крестики-нолики по сети
- [Save/Load Demo](spritePro/demoGames/save_load_demo.py) - Система сохранений
- [Sorting Order Demo](spritePro/demoGames/sorting_order_demo.py) - Порядок отрисовки (слои)
- [Particles Images Demo](spritePro/demoGames/particles_images_demo.py) - Частицы из изображений (c.png, platforma.png)
- [Particles Templates Demo](spritePro/demoGames/particles_templates_demo.py) - Готовые шаблоны (Sparks, Smoke, Fire)
- [Bar Demo](spritePro/demoGames/bar_demo.py) - Прогресс-бары с разными направлениями заполнения
- [Bar Background Demo](spritePro/demoGames/bar_background_demo.py) - Прогресс-бары с отдельными фоновыми и заполняющими изображениями
- [Input + EventBus Demo](spritePro/demoGames/input_events_demo.py) - Ввод и события
- [Scenes Demo](spritePro/demoGames/scenes_demo.py) - Сцены
- [Scenes Demo (editor)](spritePro/demoGames/scenes_demo editor.py) - Сцены с загрузкой из JSON редактора; экспорт сцены из кода в JSON (round-trip)
- [Resource Cache Demo](spritePro/demoGames/resource_cache_demo.py) - Кэш ресурсов
- [Drag & Drop Demo](spritePro/demoGames/drag_drop_demo.py) - Перетаскивание
- [Debug Overlay Demo](spritePro/demoGames/debug_overlay_demo.py) - Отладочная сетка и логи

## 🔍 Навигация по типам документации

### По уровню сложности

#### 🟢 Начинающий уровень
- [README.md](README.md) - Начало работы
- [docs/sprite.md](docs/sprite.md) - Основы спрайтов
- [docs/button.md](docs/button.md) - Простые кнопки
- [docs/text.md](docs/text.md) - Отображение текста



### По категориям функций

#### 🎨 Графика и рендеринг
- [docs/sprite.md](docs/sprite.md)
- [docs/surface.md](docs/surface.md)
- [docs/color_effects.md](docs/color_effects.md)
- [docs/animation.md](docs/animation.md)
- [docs/tween.md](docs/tween.md) — плавные переходы, Fluent API (DoMove, DoScale, ...)



#### 🖱️ Пользовательский интерфейс
- [docs/button.md](docs/button.md)
- [docs/toggle_button.md](docs/toggle_button.md)
- [docs/slider.md](docs/slider.md)
- [docs/text_input.md](docs/text_input.md)
- [docs/text.md](docs/text.md)
- [docs/layout.md](docs/layout.md)
- [docs/mouse_interactor.md](docs/mouse_interactor.md)
- [docs/draggable_sprite.md](docs/draggable_sprite.md)

#### 🔧 Утилиты и инструменты
- [docs/save_load.md](docs/save_load.md)
- [docs/tween.md](docs/tween.md) — Tween, TweenManager, Fluent API
- [docs/text_fps.md](docs/text_fps.md)
- [docs/game_loop.md](docs/game_loop.md)
- [docs/input.md](docs/input.md)
- [docs/events.md](docs/events.md)
- [docs/debug.md](docs/debug.md)
- [docs/pages.md](docs/pages.md)

#### 📋 Планирование и разработка
- [ROADMAP.md](ROADMAP.md)
- [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GAME_IDEAS.md](GAME_IDEAS.md)

## 📖 Рекомендуемый порядок изучения

### Для новичков в SpritePro
1. [README.md](README.md) - Общий обзор
2. [docs/sprite.md](docs/sprite.md) - Основы спрайтов
3. [docs/text.md](docs/text.md) - Отображение текста
4. [docs/button.md](docs/button.md) - Интерактивность
5. [Простые демо](spritePro/demoGames/) - Практические примеры

### Для разработки игр
1. [docs/sprite.md](docs/sprite.md) - Спрайты и игровые объекты
2. [docs/animation.md](docs/animation.md) - Анимации
3. [docs/tween.md](docs/tween.md) - Плавные переходы (в т.ч. Fluent API)
4. [docs/timer.md](docs/timer.md) - Игровое время
5. [docs/health.md](docs/health.md) - Игровые системы
6. [docs/save_load.md](docs/save_load.md) - Сохранения

### Для продвинутых разработчиков
1. [docs/layout.md](docs/layout.md) - Автолейауты
2. [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md) - Архитектура
3. [PERFORMANCE.md](PERFORMANCE.md) - Оптимизация
4. [CONTRIBUTING.md](CONTRIBUTING.md) - Участие в разработке

### Для планирования проектов
1. [GAME_IDEAS.md](GAME_IDEAS.md) - Идеи игр
2. [ROADMAP.md](ROADMAP.md) - Планы развития
3. [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md) - Технические возможности

## 🔄 Обновления документации

### Последние обновления
- **2026-02**: Редактор сцен: экспорт из кода в JSON (`Scene.export_from_runtime`), координаты по центру объекта; runtime: `placement()` возвращает центр, `to_button`/`to_text_sprite`/`to_toggle`, `.Sprite(**kwargs)`, `exact(name)`. Демо [scenes_demo editor.py](spritePro/demoGames/scenes_demo editor.py) — загрузка сцены из JSON, логика в коде. Документация: sprite_editor.md (разделы «Координаты в редакторе», «Экспорт сцены из кода в JSON», обновлённая интеграция).
- **2026-02**: Общий модуль `grid_renderer` для сетки и подписей (игра + редактор); зум-адаптивная плотность подписей. Редактор: переключатель Labels (статусбар и Settings → Scene). Button и TextSprite по умолчанию `screen_space=True`. Документация: debug.md, sprite_editor.md, button.md, text.md.
- **2026-02**: Slider(Sprite), TextInput(Button), auto_register у Sprite; документация slider.md, text_input.md, events.md
- **2026-02**: Fluent Tween API (DoMove, DoScale, SetEase, SetLoops, OnComplete, Kill) — демо fluent_tween_demo.py
- **2026-02**: Layout, мультиплеер, крестики-нолики — обзор в docs/OVERVIEW.md
- **2025-06**: Добавлена система сохранения/загрузки
- **2025-06**: Создан roadmap и технические спецификации

### Планируемые обновления
- Документация по системе инвентаря
- Руководство по системе диалогов
- Документация по системе частиц
- Туториалы для начинающих

## 📞 Обратная связь

Если вы не нашли нужную информацию или у вас есть предложения по улучшению документации:

- Создайте Issue на GitHub с тегом `documentation`
- Предложите улучшения через Pull Request
- Обсудите в GitHub Discussions

---

**Совет**: Используйте поиск по файлам (Ctrl+F) для быстрого поиска нужной информации в документации! 🔍

