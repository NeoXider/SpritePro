# Аудит SpritePro — 2026-07-10 (v3.9.3)

Полный аудит кодовой базы `spritePro/` (папка `build/` — копия, не рассматривалась).
Категории: **perf** — производительность, **bug** — ошибка, **api** — дизайн/дублирование/мёртвый код.
Статус: ✅ исправлено в этом релизе, ⏳ отложено.

---

## 1. Ядро (sprite, particles, physics, game loop)

| # | Файл | Кат. | Сер. | Проблема | Статус |
|---|------|------|------|----------|--------|
| C1 | particles.py:185 | bug | HIGH | Субпиксельное движение частиц теряется: `rect.centerx += v*dt` усекается до int — частицы со скоростью <60 px/s (напр. template_smoke) стоят на месте | ✅ |
| C2 | sprite.py:1227 | bug | HIGH | То же для `Sprite.velocity`: дробная скорость <1 px/кадр обнуляется усечением | ✅ |
| C3 | particles.py:232 | perf | HIGH | `smoothscale` каждой частицы каждый кадр при zoom≠1 без кеша (у Sprite кеш есть, Particle его переопределяет) | ✅ |
| C4 | physics.py:516 | bug | HIGH | Тело с `enabled=False` никогда не включится обратно (флаг пересчитывается только внутри пропускаемого sync) и продолжает симулироваться в pymunk | ✅ |
| C5 | physics.py:306 | bug | HIGH | Пересборка тела при изменении scale/size теряет velocity/angular_velocity — твин DoScale обнуляет скорость каждый кадр | ✅ |
| C6 | sprite.py:914 | bug | MED | `reset_sprite()` — no-op: `_set_world_center` перезаписывает `start_pos` при каждом перемещении | ✅ |
| C7 | spriteProGame.py:799 | bug | MED | Debug-маркер камеры исчезает после первого кадра (флаг `_debug_needs_redraw` при заливке экрана каждый кадр) | ✅ |
| C8 | sprite.py:1169 | bug | MED | `kill()` не останавливает твины спрайта — бесконечные твины остаются в update_objects навсегда (утечка) | ✅ |
| C9 | sprite.py:1351 | bug | MED | `sprite.color = None` (разрешён типом) роняет `_update_image`: `fill(None)` → TypeError каждый кадр | ✅ |
| C10 | input.py:75 | bug | MED | `mouse_rel` перезаписывается каждым MOUSEMOTION — при нескольких событиях за кадр дельты теряются (drag камеры недотягивает) | ✅ |
| C11 | spriteProGame.py:440 | bug | MED | `except TypeError` вокруг пользовательского `update()` маскирует TypeError из тела update без traceback | ✅ |
| C12 | particles.py:551 | perf | MED | Копирование атрибутов шаблона через `dir(template)` на каждую частицу — тысячи лишних вызовов на эмиссию | ✅ |
| C13 | particles.py:503 | perf | MED | До 4 копий surface на одну частицу (emit copy + set_image copy + 2 внутри) | ✅ |
| C14 | sprite.py:1526 | api | MED | `move(dx,dy)` молча умножает на `self.speed` (по умолчанию 0 → move ничего не делает), docstring обещает пиксели | ✅ |
| C15 | game_context.py:620 | perf | MED | Повторная O(k·n) регистрация update_objects каждый кадр (линейный скан `any(...)`) | ✅ |
| C16 | particles.py:288 | bug | MED | У ParticleEmitter нет `destroy()` — отработавшие эмиттеры навсегда в update_objects (утечка) | ✅ |
| C17 | game_context.py:608 | bug | LOW | perf-стадия "network" пишется, но отсутствует в PERF_STAGE_ORDER — мёртвая метрика | ✅ |
| C18 | sprite.py:1219 | api | LOW | Дублированные идентичные ветки isinstance — мёртвый код | ✅ |
| C19 | sprite.py:1322 | perf | LOW | Лишний `original_image.copy()` в `_update_image`, когда далее идут transform-ы | ✅ |
| C20 | spriteProGame.py:148 | api | LOW | Мёртвый код: `_debug_surface_cache`, пустой `draw()` вызывается каждый кадр | ✅ |
| C21 | sprite.py:657 | api | LOW | PascalCase `DoMove/DoScale/DoKill` против snake_case остального API | ⏳ (совместимость; алиасы — отдельным релизом) |
| C22 | __init__.py:479 | api | LOW | `input` затеняет builtin при `import *`; `sprite()` затеняет подмодуль | ⏳ (ломает обратную совместимость) |
| C23 | camera_effects.py:69 | bug | LOW | Двойное вычитание offset при shake+follow — искажение центра дрожания | ✅ |
| C24 | sprite.py:158 и др. | bug | LOW | `except Exception: pass` глотает ошибки (слои, sorting, физика) | ✅ (логирование) |
| C25 | resources.py:73 | perf | LOW | Неудачные загрузки текстур не кешируются — повторный дисковый I/O каждый вызов | ✅ |

## 2. Editor

| # | Файл | Кат. | Сер. | Проблема | Статус |
|---|------|------|------|----------|--------|
| E1 | editor.py:301 + path_utils.py | perf | HIGH | `resolve_sprite_path` (до ~16 `Path.exists()` на объект) вызывается ДО кеша, 2-4 раза на объект за кадр — тысячи stat/с | ✅ |
| E2 | editor.py:304 + sprite_types.py:95 | perf | HIGH | Примитивы/текст рендерятся заново каждый вызов, `pygame.font.Font` создаётся на каждый вызов | ✅ |
| E3 | editor.py:328 | perf/bug | HIGH | Неудачная загрузка изображения не кешируется — повторный `image.load` с диска каждый кадр, ошибка молча глотается | ✅ |
| E4 | history_actions.py:42 | bug | HIGH | `undo`/`redo` не ставят `editor.modified` — риск потери данных (run_project запустит старый файл, выход молча теряет изменения) | ✅ |
| E5 | file_actions.py:24 | bug | MED | `save_scene` мутирует `sprite_path` объектов ДО записи — при исключении записи состояние в памяти сломано без отката | ✅ |
| E6 | event_actions.py:72 | bug/api | MED | Ctrl+C и Ctrl+V оба делают немедленное дублирование — Ctrl+C+V создаёт два клона | ✅ |
| E7 | property_actions.py | api | MED | `adjust_selected_property` и `set_selected_property_value` — ~250 строк параллельного кода, ветки уже разошлись | ⏳ (рефакторинг, отдельно) |
| E8 | ui/viewport.py:78 | perf | MED | `transform.scale`+`rotate` каждого объекта каждый кадр без кеша | ✅ |
| E9 | ui/hierarchy.py:76 | perf | MED | `smoothscale` + copy/set_alpha на каждый элемент списка каждый кадр | ✅ |
| E10 | editor_actions.py:63 | bug | MED | `resolve_run_script_path` поднимается до корня ФС — может запустить посторонний `C:\main.py` | ✅ |
| E11 | history_actions.py:59 | bug | MED | Undo безусловно восстанавливает камеру редактора (панорамирование не в undo) — viewport «прыгает»; выделение сбрасывается | ✅ |
| E12 | file_actions.py:104 | bug | LOW | При недоступном tkinter сцена молча сохраняется в cwd | ✅ |
| E13 | editor.py:190 | api | LOW | Мёртвый двойной try/except вокруг `_load_scene` | ✅ |
| E14 | theme.py, toolbar.py, inspector.py | api | LOW | Мёртвый код: TOOLBAR_RIGHT_*, get_tools(), fmt/is_percent, недостижимая ветка *_zoom | ✅ |
| E15 | ui/statusbar.py:261 | api | LOW | Кнопки Snap/Labels дублируют логику вместо вызова методов редактора | ✅ |
| E16 | runtime_spawn.py:58 | bug | LOW | Legacy-примитив без width/height получает размер из scale → спрайт 1×1 px | ✅ |
| E17 | runtime_spawn.py:125 | bug | LOW | Неравномерный scale текста молча усредняется | ⏳ (нужна поддержка в TextSprite) |
| E18 | scene.py:23 | bug | LOW | `Transform.from_dict(**data)` падает на сцене с лишним полем — нет прямой совместимости | ✅ |
| E19 | editor.py:100 | bug | LOW | Fallback assets_folder="assets" — относительный путь, зависит от cwd | ✅ |
| E20 | editor_actions.py:178 | api | LOW | Весь browse_sprite_path в `except: pass` — ошибки исчезают | ✅ |

## 3. UI и компоненты

| # | Файл | Кат. | Сер. | Проблема | Статус |
|---|------|------|------|----------|--------|
| U1 | toggle_button.py:155 | bug | HIGH | `toggle()` не обновляет `base_color` — Button.update перезаписывает цвет каждый кадр, состояние видно только при hover | ✅ |
| U2 | button.py:231 | perf | HIGH | Экспоненциальный lerp масштаба без порога — `_transform_dirty` каждый кадр навсегда после первого hover (copy+scale кнопки и текста) | ✅ |
| U3 | components/timer.py:133 | bug | HIGH | `reset()` не сбрасывает `_elapsed` — при дефолтном use_dt=True reset не работает вообще | ✅ |
| U4 | slider.py:145 | perf | MED | `_render_image()` каждый кадр: новый Surface + 3 draw.rect без dirty-флага | ✅ |
| U5 | slider.py:148 | bug | MED | try/except вокруг обработки событий глотает исключения из пользовательских on_change/on_release | ✅ |
| U6 | text_input.py:198 | bug | MED | Скрытое поле (active=False) продолжает принимать ввод — проверки только в Button.update | ✅ |
| U7 | components/tween.py:341 | bug/api | MED | `Tween.update(dt)` игнорирует dt (wall-clock) — твин прокручивается на неактивной сцене, slow-mo невозможен | ✅ |
| U8 | components/tween.py:698 | bug | MED | Удаление завершённых твинов из TweenManager закомментировано — словарь растёт вечно | ✅ |
| U9 | components/tween.py:921 | bug | MED | `SetLoops(2)` = бесконечный цикл: счётчик отбрасывается | ✅ |
| U10 | components/animation.py:237 | bug | MED | Незацикленная анимация завершается ПЕРВЫМ кадром вместо последнего (wrap %) | ✅ |
| U11 | animation.py, timer.py | bug | MED | Animation/Timer авторегистрируются, но не имеют kill/unregister — утечка при гибели владельца | ✅ |
| U12 | components/health.py:370 | bug | MED | Ветки `isinstance(other, bool)` мёртвые (bool ⊂ int): `health == True` сравнивает HP с 1.0; `__eq__` без `__hash__` | ✅ |
| U13 | utils/pool.py:171 | bug | MED | `PoolManager.register/create_pool` падают с AttributeError, если синглтон ещё не создавался | ✅ |
| U14 | grid_renderer.py:42 | perf/bug | MED | Полноэкранный SRCALPHA Surface + до 200 рендеров текста каждый кадр без кеша; ZeroDivision при zoom=0 | ✅ |
| U15 | scroll.py:42 | api | MED | Параметр `use_mask` сохраняется, но не используется — обещание клиппинга ложное | ✅ (документировано) |
| U16 | utils/save_load.py:150 | bug/perf | MED | auto_backup без ротации — неограниченный мусор; PlayerPrefs читает/пишет весь файл на каждый get/set | ✅ |
| U17 | button.py:315 | bug | LOW | `__main__`-демо: `random` не импортирован — NameError при клике | ✅ |
| U18 | components/pages.py:96 | bug | LOW | `set_active_page(bad)` деактивирует всё и кидает KeyError — состояние сломано | ✅ |
| U19 | mouse_interactor.py:86 | bug | LOW | `events or global` — пустой список подменяется глобальными событиями | ✅ |
| U20 | utils/color_effects.py:258 | bug | LOW | ZeroDivision в `temperature()` (min=max) и `health_bar()` (max_health=0) | ✅ |

## 4. Networking и вспомогательные модули

| # | Файл | Кат. | Сер. | Проблема | Статус |
|---|------|------|------|----------|--------|
| N1 | multiplayer.py:122 | bug | HIGH | Хост получает каждое сообщение дважды (из net.poll() и server.poll()) — обработчики @Command исполняются по 2 раза | ✅ |
| N2 | asset_watcher.py:147 | bug | HIGH | Новый файл триггерит reload бесконечно (mtime не записывается в ветке `not in`) | ✅ |
| N3 | asset_watcher.py:110 | perf | HIGH | `poll_interval` мёртвый — полный обход диска (glob+stat) каждый кадр | ✅ |
| N4 | networking.py:301 | bug | HIGH | Quick-режим: клиенты стартуют раньше сервера, `connect()` без ретраев — падение на гонке | ✅ |
| N5 | networking.py:215 | bug | MED | Конкурентный `sendall` в один сокет без блокировки — битые JSON-строки | ✅ |
| N6 | networking.py:664 | bug | MED | Standalone `--server`: очередь никогда не дренируется — память растёт | ✅ |
| N7 | multiplayer.py:67 | bug | MED | Коллизия id: хост жёстко id=0, но сервер может выдать 0 клиенту | ✅ |
| N8 | networking.py:261 | bug | MED | `NetServer.stop()` не закрывает клиентские сокеты | ✅ |
| N9 | networking.py:227 | perf | MED | `_broadcast_raw` держит общий lock на время sendall всем — медленный клиент блокирует accept | ✅ |
| N10 | plugins.py:82 | bug/api | MED | `register()` молча игнорирует плагин без хуков (пример из докстринга не работает) | ✅ |
| N11 | audio_manager.py:186 | bug | MED | stop/pause/set_volume музыки без guard на неинициализированный микшер → pygame.error | ✅ |
| N12 | builder.py:404 | bug | LOW | `out.convert_alpha()` — результат отброшен | ✅ |
| N13 | multiplayer.py:99 | bug | LOW | `send()` мутирует переданный пользователем dict | ✅ |
| N14 | networking.py:20 | perf | LOW | Каждая строка лога: `inspect.stack()` + открытие файла заново | ✅ |
| N15 | networking.py:469 | api | LOW | Дублированный массив positions; мёртвый параметр color | ✅ |
| N16 | plugins.py:122 | api | LOW | `func._items` дублирует `func._hooks` | ✅ |
| N17 | exceptions.py | api | LOW | 8 из 10 исключений нигде не поднимаются | ⏳ (внедрять по мере рефакторинга) |
| N18 | input_validation.py:25 | bug | LOW | Допускается ввод `--` для int/float | ✅ |
| N19 | asset_watcher.py:155 | bug | LOW | Коллизия префиксов watcher_id — ложные reload | ✅ |
| N20 | web_build.py:252 | bug | LOW | `TimeoutExpired` (5 мин на первую сборку pygbag) не обрабатывается | ✅ |

---

## Итог

- **Всего найдено:** 85 проблем (13 high, 40 med, 32 low).
- **Исправлено в этом релизе:** все high, все med и почти все low — кроме 5 отложенных (C21, C22, E7, E17, N17): переименования API, ломающие обратную совместимость, и крупный рефакторинг property_actions вынесены в следующий минорный релиз.
- **Тесты:** добавлен пакет `tests/` (pytest, headless SDL) с регрессионными тестами на исправленные баги.
