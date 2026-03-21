# 🎮 Demo Games — 54 демонстрационные игры SpritePro v3.4.0

**Все демо-игры с описанием и командами запуска**

---

## 📋 Таблица всех демо

| № | Демо | Описание | Запуск |
|---|------|----------|--------|
| 1 | [amongus.py](#1-amonguspy) | Клон Among Us с движением | `python -m spritePro.demoGames.amongus` |
| 2 | [animationDemo.py](#2-animationdemopy) | Покадровая анимация | `python -m spritePro.demoGames.animationDemo` |
| 3 | [bar_demo.py](#3-bar_demopy) | Прогресс-бары (разные направления) | `python -m spritePro.demoGames.bar_demo` |
| 4 | [bar_hp_demo.py](#4-bar_hp_demopy) | HP бар с анимацией | `python -m spritePro.demoGames.bar_hp_demo` |
| 5 | [bar_simple_demo.py](#5-bar_simple_demopy) | Простой прогресс-бар | `python -m spritePro.demoGames.bar_simple_demo` |
| 6 | [builder_demo.py](#6-builder_demopy) | Builder Fluent API (спрайты + частицы) | `python -m spritePro.demoGames.builder_demo` |
| 7 | [child_movement_demo.py](#7-child_movement_demopy) | Движение дочерних спрайтов | `python -m spritePro.demoGames.child_movement_demo` |
| 8 | [color_text_demo.py](#8-color_text_demopy) | Цветной текст с эффектами | `python -m spritePro.demoGames.color_text_demo` |
| 9 | [debug_overlay_demo.py](#9-debug_overlay_demopy) | Debug сетка и логи | `python -m spritePro.demoGames.debug_overlay_demo` |
| 10 | [demo_pymunk.py](#10-demo_pymunkpy) | Базовая физика pymunk | `python -m spritePro.demoGames.demo_pymunk` |
| 11 | [drag_drop_demo.py](#11-drag_drop_demopy) | Drag-and-drop спрайт | `python -m spritePro.demoGames.drag_drop_demo` |
| 12 | [easy_clicker.py](#12-easy_clickerpy) | Кликер с улучшениями | `python -m spritePro.demoGames.easy_clicker` |
| 13 | [editor_scene_runtime_demo.py](#13-editor_scene_runtime_demopy) | Сцена из редактора + логика в коде | `python -m spritePro.demoGames.editor_scene_runtime_demo` |
| 14 | [event_bus_demo.py](#14-event_bus_demopy) | EventBus события | `python -m spritePro.demoGames.event_bus_demo` |
| 15 | [events_rps_demo.py](#15-events_rps_demopy) | Камень-ножницы-бумага через события | `python -m spritePro.demoGames.events_rps_demo` |
| 16 | [fireworks_demo.py](#16-fireworks_demopy) | Эффект фейерверка | `python -m spritePro.demoGames.fireworks_demo` |
| 17 | [fluent_tween_demo.py](#17-fluent_tween_demopy) | Fluent Tween API (DoMove, SetEase, OnComplete) | `python -m spritePro.demoGames.fluent_tween_demo` |
| 18 | [frame_tween_demo.py](#18-frame_tween_demopy) | Твины по кадрам | `python -m spritePro.demoGames.frame_tween_demo` |
| 19 | [hero_vs_enemy.py](#19-hero_vs_enemypy) | Бой герой vs враг | `python -m spritePro.demoGames.hero_vs_enemy` |
| 20 | [hoop_bounce_demo.py](#20-hoop_bounce_demopy) | Шарик в обруче с отскоком | `python -m spritePro.demoGames.hoop_bounce_demo` |
| 21 | [hot_reload_demo.py](#21-hot_reload_demopy) | Hot reload ассетов | `python -m spritePro.demoGames.hot_reload_demo` |
| 22 | [input_events_demo.py](#22-input_events_demopy) | Ввод + события | `python -m spritePro.demoGames.input_events_demo` |
| 23 | [kivy_hybrid_demo.py](#23-kivy_hybrid_demopy) | Kivy UI + игровая область | `python -m spritePro.demoGames.kivy_hybrid_demo` |
| 24 | [layout_demo.py](#24-layout_demopy) | Все типы лейаутов (flex, grid, circle, line) | `python -m spritePro.demoGames.layout_demo` |
| 25 | [local_multiplayer_demo.py](#25-local_multiplayer_demopy) | Сетевой мультиплеер (хост + клиенты) | `python -m spritePro.demoGames.local_multiplayer_demo --quick` |
| 26 | [menu_shop_demo.py](#26-menu_shop_demopy) | Меню и инвентарь на Layout | `python -m spritePro.demoGames.menu_shop_demo` |
| 27 | [mobile_orb_collector_demo.py](#27-mobile_orb_collector_demopy) | Mobile-first demo (touch, экранные кнопки) | `python -m spritePro.demoGames.mobile_orb_collector_demo --kivy` |
| 28 | [object_pool_demo.py](#28-object_pool_demopy) | Пул объектов для переиспользования | `python -m spritePro.demoGames.object_pool_demo` |
| 29 | [pages_demo.py](#29-pages_demopy) | Система страниц (PageManager) | `python -m spritePro.demoPages.pages_demo` |
| 30 | [particle_demo.py](#30-particle_demopy) | Базовая система частиц | `python -m spritePro.demoGames.particle_demo` |
| 31 | [particle_pool_demo.py](#31-particle_pool_demopy) | Пул частиц (ParticleEmitter с use_pool=True) | `python -m spritePro.demoGames.particle_pool_demo` |
| 32 | [particle_template_test.py](#32-particle_template_testpy) | Тест шаблонов частиц | `python -m spritePro.demoGames.particle_template_test` |
| 33 | [particles_auto_demo.py](#33-particles_auto_demopy) | Авто-эмиссия частиц | `python -m spritePro.demoGames.particles_auto_demo` |
| 34 | [particles_images_demo.py](#34-particles_images_demopy) | Частицы из изображений (c.png, platforma.png) | `python -m spritePro.demoGames.particles_images_demo` |
| 35 | [particles_stress_demo.py](#35-particles_stress_demopy) | Stress-тест частиц | `python -m spritePro.demoGames.particles_stress_demo` |
| 36 | [particles_templates_demo.py](#36-particles_templates_demopy) | Готовые шаблоны (Sparks, Smoke, Fire) | `python -m spritePro.demoGames.particles_templates_demo` |
| 37 | [physics_demo.py](#37-physics_demopy) | Физика: гравитация, отскок, платформы, статика/кинематика | `python -m spritePro.demoGames.physics_demo` |
| 38 | [ping_pong.py](#38-ping_pongly) | Пинг-понг с физикой мяча | `python -m spritePro.demoGames.ping_pong` |
| 39 | [platformer_demo.py](#39-platformer_demopy) | Платформер с камерой | `python -m spritePro.demoGames.platformer_demo` |
| 40 | [plugin_demo.py](#40-plugin_demopy) | Система плагинов и хуков | `python -m spritePro.demoGames.plugin_demo` |
| 41 | [primitives_demo.py](#41-primitives_demopy) | Базовые примитивы (rect, circle, ellipse) | `python -m spritePro.demoGames.primitives_demo` |
| 42 | [resource_cache_demo.py](#42-resource_cache_demopy) | Кэш ресурсов | `python -m spritePro.demoGames.resource_cache_demo` |
| 43 | [save_load_demo.py](#43-save_load_demopy) | Система сохранений (PlayerPrefs) | `python -m spritePro.demoGames.save_load_demo` |
| 44 | [scenes_demo editor.py](#44-scenes_demo-editorpy) | Сцены из редактора + экспорт в JSON | `python -m spritePro.demoGames.scenes_demo\ editor` |
| 45 | [scenes_demo.py](#45-scenes_demopy) | Переключение сцен (меню, игра, пауза) | `python -m spritePro.demoGames.scenes_demo` |
| 46 | [slider_textinput_demo.py](#46-slider_textinput_demopy) | Слайдер + поле ввода текста | `python -m spritePro.demoGames.slider_textinput_demo` |
| 47 | [sorting_order_demo.py](#47-sorting_order_demopy) | Порядок отрисовки (слои) | `python -m spritePro.demoGames.sorting_order_demo` |
| 48 | [test_horror.py](#48-test_horrorpy) | Хоррор-демо с атмосферой | `python -m spritePro.demoGames.test_horror` |
| 49 | [text_fps_demo.py](#49-text_fps_demopy) | Счётчик FPS | `python -m spritePro.demoGames.text_fps_demo` |
| 50 | [three_clients_move_demo.py](#50-three_clients_move_demopy) | Три клиента + синхронизация | `python -m spritePro.demoGames.three_clients_move_demo --quick` |
| 51 | [toggle_demo.py](#51-toggle_demopy) | ToggleButton переключатели | `python -m spritePro.demoGames.toggle_demo` |
| 52 | [tween_presets_demo.py](#52-tween_presets_demopy) | Готовые пресеты твинов | `python -m spritePro.demoGames.tween_presets_demo` |
| 53 | [tweenDemo.py](#53-tweenDemopy) | Базовые твины (позиция, масштаб, цвет) | `python -m spritePro.demoGames.tweenDemo` |
| 54 | [visibility_culling_demo.py](#54-visibility_culling_demopy) | Culling невидимых объектов | `python -m spritePro.demoGames.visibility_culling_demo` |

---

## 🎯 Категории демо

### 🏗 Базовые компоненты
| Демо | Описание |
|------|----------|
| [primitives_demo.py](#41-primitives_demopy) | Rect, circle, ellipse примитивы |
| [color_text_demo.py](#8-color_text_demopy) | Текст с цветами и эффектами |
| [text_fps_demo.py](#49-text_fps_demopy) | Счётчик FPS |

### 🎨 UI & Layout
| Демо | Описание |
|------|----------|
| [layout_demo.py](#24-layout_demopy) | Flex, grid, circle, line лейауты |
| [menu_shop_demo.py](#26-menu_shop_demopy) | Меню и инвентарь на Layout |
| [slider_textinput_demo.py](#46-slider_textinput_demopy) | Слайдер + TextInput |
| [toggle_demo.py](#51-toggle_demopy) | ToggleButton переключатели |

### 🎬 Анимация & Эффекты
| Демо | Описание |
|------|----------|
| [animationDemo.py](#2-animationdemopy) | Покадровая анимация |
| [tweenDemo.py](#53-tweenDemopy) | Базовые твины |
| [fluent_tween_demo.py](#17-fluent_tween_demopy) | Fluent API DoMove, SetEase |
| [frame_tween_demo.py](#18-frame_tween_demopy) | Твины по кадрам |
| [tween_presets_demo.py](#52-tween_presets_demopy) | Готовые пресеты |
| [fireworks_demo.py](#16-fireworks_demopy) | Фейерверк частиц |

### ⚙️ Физика & Редактор
| Демо | Описание |
|------|----------|
| [demo_pymunk.py](#10-demo_pymunkpy) | Базовая физика pymunk |
| [physics_demo.py](#37-physics_demopy) | Гравитация, отскок, платформы |
| [hoop_bounce_demo.py](#20-hoop_bounce_demopy) | Шарик в обруче с отскоком |
| [ping_pong.py](#38-ping_pongly) | Пинг-понг с физикой мяча |
| [platformer_demo.py](#39-platformer_demopy) | Платформер с камерой |
| [editor_scene_runtime_demo.py](#13-editor_scene_runtime_demopy) | Сцена из редактора + код |

### 🎮 Игровая логика
| Демо | Описание |
|------|----------|
| [easy_clicker.py](#12-easy_clickerpy) | Кликер с улучшениями |
| [hero_vs_enemy.py](#19-hero_vs_enemypy) | Бой герой vs враг |
| [amongus.py](#1-amonguspy) | Among Us клон |

### 🌐 Сеть & Мультиплеер
| Демо | Описание |
|------|----------|
| [local_multiplayer_demo.py](#25-local_multiplayer_demopy) | Хост + клиенты (TCP) |
| [three_clients_move_demo.py](#50-three_clients_move_demopy) | Три клиента синхронизация |
| [events_rps_demo.py](#15-events_rps_demopy) | Камень-ножницы-бумага |

### 💾 Утилиты & Оптимизация
| Демо | Описание |
|------|----------|
| [save_load_demo.py](#43-save_load_demopy) | PlayerPrefs сохранения |
| [object_pool_demo.py](#28-object_pool_demopy) | Пул объектов |
| [resource_cache_demo.py](#42-resource_cache_demopy) | Кэш ресурсов |
| [hot_reload_demo.py](#21-hot_reload_demopy) | Hot reload ассетов |

### 🎭 Сцены & Страницы
| Демо | Описание |
|------|----------|
| [scenes_demo.py](#45-scenes_demopy) | Переключение сцен (меню/игра/пауза) |
| [pages_demo.py](#29-pages_demopy) | PageManager страницы |

### 🔧 Debug & Tools
| Демо | Описание |
|------|----------|
| [debug_overlay_demo.py](#9-debug_overlay_demopy) | Сетка мира + логи |
| [plugin_demo.py](#40-plugin_demopy) | Плагины и хуки |
| [event_bus_demo.py](#14-event_bus_demopy) | EventBus события |

### 📱 Mobile & Kivy
| Демо | Описание |
|------|----------|
| [mobile_orb_collector_demo.py](#27-mobile_orb_collector_demopy) | Mobile-first (touch, экранные кнопки) |
| [kivy_hybrid_demo.py](#23-kivy_hybrid_demopy) | Kivy UI + игровая область |

### 🎆 Частицы
| Демо | Описание |
|------|----------|
| [particle_demo.py](#30-particle_demopy) | Базовая система частиц |
| [particles_templates_demo.py](#36-particles_templates_demopy) | Шаблоны (Sparks, Smoke, Fire) |
| [particles_images_demo.py](#34-particles_images_demopy) | Частицы из изображений |
| [particle_pool_demo.py](#31-particle_pool_demopy) | Пул частиц |

### 🎨 Прочее
| Демо | Описание |
|------|----------|
| [bar_demo.py](#3-bar_demopy) | Прогресс-бары (разные направления) |
| [drag_drop_demo.py](#11-drag_drop_demopy) | Drag-and-drop |
| [child_movement_demo.py](#7-child_movement_demopy) | Движение дочерних спрайтов |
| [input_events_demo.py](#22-input_events_demopy) | Ввод + события |
| [sorting_order_demo.py](#47-sorting_order_demopy) | Порядок отрисовки (слои) |
| [visibility_culling_demo.py](#54-visibility_culling_demopy) | Culling невидимых объектов |

---

## 🚀 Быстрый запуск

### Запустить одно демо:
```bash
python -m spritePro.demoGames.physics_demo
python -m spritePro.demoGames.fluent_tween_demo
python -m spritePro.demoGames.layout_demo
```

### Запустить мультиплеер (хост + клиенты):
```bash
python -m spritePro.demoGames.local_multiplayer_demo --quick
python -m spritePro.demoGames.three_clients_move_demo --quick
```

### Mobile/Kivy демо:
```bash
python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
python -m spritePro.demoGames.kivy_hybrid_demo --kivy
```

---

## 📖 Где найти код?

Все демо-игры находятся в папке `spritePro/demoGames/`.  
Структура:
```
SpritePro/
├── spritePro/
│   └── demoGames/
│       ├── physics_demo.py
│       ├── fluent_tween_demo.py
│       ├── layout_demo.py
│       └── ... (54 файла)
└── docs/
    └── guides/
        └── demo_games.md  ← этот файл
```

---

## 🎯 Рекомендации по изучению

### Для новичков:
1. [easy_clicker.py](#12-easy_clickerpy) — простая логика
2. [tweenDemo.py](#53-tweenDemopy) — базовые анимации
3. [bar_simple_demo.py](#5-bar_simple_demopy) — UI компоненты
4. [text_fps_demo.py](#49-text_fps_demopy) — счётчик FPS

### Для продвинутых:
1. [physics_demo.py](#37-physics_demopy) + [hoop_bounce_demo.py](#20-hoop_bounce_demopy) — физика pymunk
2. [local_multiplayer_demo.py](#25-local_multiplayer_demopy) — сетевая игра
3. [editor_scene_runtime_demo.py](#13-editor_scene_runtime_demopy) — редактор + код
4. [fluent_tween_demo.py](#17-fluent_tween_demopy) — Fluent API

### Для UI-разработчиков:
1. [layout_demo.py](#24-layout_demopy) — все типы лейаутов
2. [menu_shop_demo.py](#26-menu_shop_demopy) — меню и инвентарь
3. [slider_textinput_demo.py](#46-slider_textinput_demopy) — ввод данных

---

<div align="center">

**🎮 Готовы к практике?**  
Запустите первое демо: `python -m spritePro.demoGames.physics_demo`

Или изучите [полный API Reference](../API_REFERENCE.md)!

</div>
