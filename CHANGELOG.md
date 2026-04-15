# Changelog

Все значимые изменения в проекте SpritePro будут документированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.9.2]

### Fixed
- 🐛 **Физика: утечка тел при перезапуске сцены** — `Sprite.kill()` теперь удаляет все привязанные `PhysicsBody` из `PhysicsWorld` и `pymunk.Space`. Раньше при перезапуске сцены спрайты удалялись, но их физические тела оставались в мире, вызывая призрачные коллизии и ошибки обращения к мёртвым спрайтам.

### Changed
- 🔧 **Версия библиотеки** — релиз обновлён до `3.9.2`.

---

## [3.9.0]

### Fixed
- 🐛 **BUG-1: NetServer relay** — сервер пересылал сырой TCP-chunk вместо разобранного сообщения. Теперь ретрансляция строит корректный `line.encode("utf-8") + b"\n"`.
- 🐛 **BUG-2: ParticleConfig** — `angular_velocity_range` и `scale_velocity_range` имели default `(None,)` вместо `None`, что вызывало `TypeError` при распаковке.
- 🐛 **BUG-5: EventSignal.send()** — ошибки в обработчиках подписчиков теперь логируются через `traceback.print_exc()` вместо молчаливого `pass`.
- 🐛 **BUG-6: save_load_demo** — вызовы `s.debug_log_info()` без аргумента заменены на `s.debug_log_info("")`.

### Changed
- 🔧 **ARCH-1: Удалён `sys.path.append()`** из 8 модулей: `button.py`, `toggle_button.py`, `text.py`, `animation.py`, `mouse_interactor.py`, `pages.py`, `text_fps.py`, `bar.py`. Все импорты переведены на относительные.
- 🔧 **ARCH-2: Python ≥ 3.10** — `requires-python` обновлён с `>=3.7` до `>=3.10`; удалены классификаторы для Python 3.7–3.9; `ruff target-version` обновлён до `py310`.
- 🔧 **ARCH-4**: Удалён неиспользуемый `import random` из `button.py`.
- 🔧 **ARCH-8: logging.basicConfig** — удалён из `save_load.py`, `networking.py`, `utils/logger.py`. Библиотечный код не должен конфигурировать logging.

### Improved
- ⚡ **OPT-3+OPT-4: Сетевой буфер** — `recv(1024)` → `recv(4096)`, строковая конкатенация → `bytearray.extend()` (O(1) вместо O(n²)) для `NetServer` и `NetClient`.

### Security
- 🔒 **ARCH-7**: Добавлено предупреждение в docstring `_load_pickle()` о риске произвольного выполнения кода через `pickle.load()`.

---

## [3.8.0]

### Added
- 🎭 **ClipMask: проверка alpha** — `_blit_one` проверяет `sprite._alpha` перед blitting; спрайты с `alpha=0` (контейнеры Layout) полностью пропускаются, не оставляя чёрных прямоугольников.
- 🎭 **ClipMask: _update_image для скрытых спрайтов** — при `hide_content=True` вызов `_update_image()` перед blit гарантирует, что dirty-флаги (alpha, color, transform) применяются к surface, даже если sprite.active=False и обычный `update()` не вызывается.
- 🎭 **ClipMask: BFS-сбор спрайтов** — `_collect_sprites` использует BFS для рекурсивного обхода иерархии `Sprite.children`, гарантируя правильный порядок отрисовки (от родителя к потомкам) и исключая дубликаты через `seen`-множество.
- 🔄 **ClipMask: синхронизация позиций** — перед отрисовкой вызываются `_apply_parent_transform()` и `_update_children_world_positions()` для каждого спрайта, обеспечивая корректные позиции без лишних draw-вызовов.

### Changed
- 📐 **Sprite.set_position()** — добавлен вызов `_update_children_world_positions()`. Теперь при изменении позиции родителя дочерние спрайты корректно синхронизируют свои мировые координаты (аналогично `set_world_position()`). Критично для `ScrollView.apply_scroll()`.
- 🎭 **ClipMask.draw()** — bg_color теперь опционален. Для ChatUI фон предоставляется отдельным `panel_bg` спрайтом со скруглёнными углами, а ClipMask только обрезает сообщения.

### Fixed
- 🐛 **Layout._apply_debug_style**: порядок `set_alpha(0)` / `set_rect_shape()` был инвертирован — `set_rect_shape` создавал новую surface и затирал ранее установленную alpha. Теперь alpha применяется **после** создания surface.
- 🐛 **ChatUI: регистрация пузырей в маске** — восстановлен `_clip_mask.add(bubble)` для каждого нового сообщения и `_clip_mask.remove(bubble)` при перестройке. Без этого пузыри рисовались основным циклом без клиппинга.
- 🐛 **ClipMask: сортировка с None** — `sorting_order=None` больше не вызывает `TypeError` при сортировке; используется `getattr(s, "sorting_order", 0) or 0`.

---

## [3.7.0]

### Added
- 🌐 **Мультиплеер: ChatScene** — готовая сцена мультиплеерного чата с ClipMask, ScrollView, Layout, полем ввода и кнопкой отправки.
- 📜 **ScrollView** — компонент прокрутки контента с поддержкой колёсика мыши и перетаскивания.
- 🎭 **ClipMask** — маска обрезки (`hide_content=True/False`) для ограничения видимости спрайтов прямоугольной областью.

---

## [3.3.1]

### Added
- 🌐 MultiplayerContext: автозаполнение `ctx.players` / `ctx.get_player_ids()` из `roster`, включая имя игрока из лобби.
- 🏷️ Встроенное лобби: имя из поля «Имя» отправляется в `join` и отображается в списке игроков.

---

## [3.3.0]

### Added
- ✨ **Мобильный ввод: экранная клавиатура для TextInput** — в Kivy‑режиме SpritePro автоматически запрашивает системную софт‑клавиатуру, когда любое поле `s.TextInput` становится активным. События `on_key_down` и `on_textinput` из Kivy транслируются в `pygame.KEYDOWN` и `pygame.TEXTINPUT`, поэтому `TextInput` обрабатывает ввод на Android так же, как на desktop.

### Changed
- 🔧 **Kivy mobile host** — `_KivySpriteProWidget` отслеживает активные `s.TextInput` и открывает/закрывает экранную клавиатуру через `Window.request_keyboard(...)`. Закрытие клавиатуры происходит автоматически при деактивации всех полей ввода (по Enter или при тапе вне поля).
- 🔧 **Версия библиотеки** — релиз обновлён до `3.3.0`.

---

## [3.2.0]

### Added
- **Project template paths** — `spritePro.cli --create` теперь создаёт `config.py` с готовыми путями `PROJECT_ROOT`, `ASSETS_DIR`, `AUDIO_DIR`, `IMAGES_DIR`, `SCENES_DIR` и `MAIN_LEVEL_PATH`, чтобы в новых проектах не нужно было каждый раз вручную собирать `Path(__file__).resolve()...`.
- **Project template events file** — в шаблон добавлен `game_events.py` с базовым событием `game_started`, подпиской через `s.events.connect(...)`, отправкой через `s.events.get_event(...).send(...)` и логом через `s.debug_log_info(...)`.

### Changed
- **Project template structure** — шаблон `--create` по умолчанию создаёт `main.py`, `config.py`, `game_events.py`, `scenes/main_scene.py`, `scenes/second_scene.py` и `scenes/main_level.json`. Вторая сцена остаётся почти пустой заготовкой для меню, паузы, магазина или другого уровня.
- **Multiplayer entrypoint** — рекомендации, demoGames и `multiplayer_course` обновлены под единый app-level запуск через `s.run(..., multiplayer=True)`, а `s.networking.run(...)` оставлен как low-level runner.
- **Версия библиотеки** — релиз обновлён до `3.2.0`.

### Fixed
- **Editor runtime image sizing** — runtime-сцены, созданные в редакторе, снова корректно подхватывают размер image-объектов в embedded/Kivy-сценариях вместо fallback-белого прямоугольника.

---

## [3.2.1]

### Added
- **Редактор: Text object** — в Sprite Editor появился тип объекта `Text`: его можно создать через `GameObject -> New Text`, редактировать текст, `Font Size` и цвет в Inspector, а `spawn_scene(...)` автоматически поднимает такие объекты как `TextSprite`.
- **Редактор: dropdown menu bar** — верхняя панель собрана в расширяемые меню `File`, `GameObject`, `Tools`, `View` с видимыми hotkey-подсказками рядом с действиями.

### Changed
- **Редактор: модульность** — часть крупной логики вынесена из `spritePro/editor/editor.py` в `spritePro/editor/file_actions.py` и `spritePro/editor/object_actions.py`, чтобы редактор было проще расширять дальше.
- **Редактор: hierarchy UX** — контекстное меню в иерархии локализовано (`Дублировать` / `Удалить`), показывает hotkeys и визуально выделяет удаление.
- **Версия библиотеки** — релиз обновлён до `3.2.1`.

### Fixed
- **Редактор: статусные сообщения** — `Saved`, `Loaded`, `Invalid input` и ошибки больше не теряются в нижней панели: теперь они показываются заметной toast-плашкой поверх viewport.

---

## [3.1.0]

### Added
- **Reference resolution** — в `s.run(...)`, `s.get_screen(...)`, `s.attach_surface(...)`, `s.run_kivy(...)`, `s.run_kivy_hybrid(...)` и `s.create_kivy_widget(...)` добавлен параметр `reference_size`, который позволяет держать игровую логику, `s.WH`, `s.WH_C`, screen-space UI и camera math в виртуальном разрешении, независимо от реального размера окна или Kivy-host.

### Changed
- **Масштабирование кадра** — SpritePro теперь умеет рендерить сцену во внутреннюю виртуальную поверхность и затем масштабировать итоговый кадр в фактическое окно с сохранением пропорций.
- **Input remap** — `input.mouse_pos`, `mouse_rel` и `event.pos`/`event.rel` автоматически пересчитываются из реального окна в координаты `reference_size`, чтобы клики, drag и hover оставались корректными.
- **Документация по game loop** — в README и `docs/game_loop.md` добавлены примеры использования `reference_size` для desktop-preview и mobile-layout сценариев.
- **Версия библиотеки** — релиз обновлён до `3.1.0`.

---

## [3.0.3]

### Added
- **Android orientation modes** — в `spritePro.cli --android` добавлены удобные режимы ориентации `landscape` (по умолчанию), `portrait` и `auto` для генерации `buildozer.spec`.

### Changed
- **Mobile preview docs** — README и mobile/building docs уточнены под реальный workflow тестирования на разных размерах окна без огромных fullscreen-preview на desktop.
- **Документация по ориентации** — в docs добавлены примеры, как переключать `portrait`, `landscape` и `auto` для Android APK.
- **Версия библиотеки** — релиз обновлён до `3.0.3`.

### Fixed
- **Android/Kivy fullscreen** — mobile host надёжнее растягивает игру на весь экран Android-устройства вместо маленькой игровой области.
- **Физика после лаг-кадров** — шаг физики ограничен безопасным `dt`, чтобы уменьшить скачки скорости и провалы объектов при нестабильном FPS на mobile.
- **Restart сцены с физикой** — runtime-сцены теперь корректно очищают заспавненные физические тела и спрайты при выходе/перезапуске сцены.

---

## [3.0.2]

### Changed
- **Android/Kivy runtime** — инициализация `pygame` в mobile-host сделана безопаснее для `python-for-android`: на Android ранний import `SpritePro` больше не поднимает агрессивный `pygame.init()` / `pygame.mixer.init()` до запуска `Kivy` host.
- **Совместимость с Android stack** — убраны места, где код опирался на `pygame.math.Vector2.copy()`, потому что в реально используемом Android-стеке с `pygame 2.1.0` этот метод может отсутствовать. Это исправляет падения при создании текста, tween-значений, camera offset и drag/update-сценариев.
- **Аннотации импорта** — в `spritePro.__init__` включены postponed annotations, чтобы импорт библиотеки не падал на Python 3.10 внутри Android bootstrap.
- **Документация по APK build** — README и Android-docs обновлены под реально проверенный flow: `WSL/Linux home`, стек `python3==3.10.12`, `hostpython3==3.10.12`, `kivy==2.3.0`, `pyjnius==1.5.0`, `pygame,pymunk,spritepro`, проверка запуска через `adb logcat`, а для непубликованных локальных фиксов — явное включение свежего `spritePro` в проект сборки.
- **Версия библиотеки** — релиз обновлён до `3.0.2`.

---

## [3.0.1]

### Added
- **Редактор: Save As** — в тулбаре появилась отдельная кнопка `Save As`, а также горячая клавиша `Ctrl+Shift+S` для сохранения сцены в новый JSON-файл.

### Changed
- **Редактор: пути к изображениям** — при сохранении сцены `sprite_path` теперь автоматически нормализуется относительно JSON-файла, чтобы сцены оставались переносимыми между машинами и каталогами.
- **Runtime round-trip** — `RuntimeScene.save(...)` теперь тоже пересчитывает пути к изображениям относительно нового JSON, а runtime использует ту же общую логику поиска ассетов, что и редактор.
- **Версия библиотеки** — релиз обновлён до `3.0.1`.

---

## [3.0.0]

### Added
- **Mobile runtime через Kivy** — одну и ту же игру теперь можно запускать через `s.run(..., platform="pygame")` и `s.run(..., platform="kivy")`. Добавлены low-level API для embedded-рендера и mobile host, touch-события прокидываются в игровой ввод.
- **Новый mobile demo** — добавлен `spritePro/demoGames/mobile_orb_collector_demo.py` как пример игры с экранными кнопками и запуском в Kivy.
- **Документация по мобильному запуску и сборке** — добавлены и обновлены материалы по mobile flow, Kivy runtime, web/mobile build и запуску demo.

### Changed
- **Основной игровой запуск** — рекомендованный путь теперь через `s.run(...)`, `Scene` и `SceneManager`, вместо ручного `while True: s.update(...)` в каждом примере.
- **Демо-игры** — демо переведены на новый Scene-based запуск; часть примеров теперь умеет запускаться и в `Kivy`.
- **CLI `--create`** — шаблон нового проекта теперь создаёт современный scene-based старт: `main.py` на `s.run(...)`, основную сцену с `main_level.json` и вторую сцену-заготовку для расширения проекта.
- **README и docs** — главный README обновлён под SpritePro 3.x: desktop/web/mobile позиционирование, ссылки на mobile/build guide, актуализированные примеры запуска.
- **Версия библиотеки** — релиз обновлён до `3.0.0`.

### Fixed
- **Ввод в mobile host** — обработка `mouse_pos`, нажатий, отпусканий и перемещения мыши/тача теперь работает корректнее в embedded/Kivy-режиме.
- **UI взаимодействие** — `MouseInteractor` использует обобщённый input state, поэтому hover/click работают стабильнее в desktop и mobile host.

---

## [2.2.3]

### Added
- **Редактор: типизированные поля ввода** — каждое текстовое поле в Inspector и Statusbar имеет тип **text**, **int** или **float**. Для int допускаются только цифры и минус в начале; для float — одна десятичная точка. Некорректные символы не вводятся и отфильтровываются при вставке. Парсинг и ограничения (min/max) выполняются при применении значения.
- **Редактор: Ctrl+V / Ctrl+C в полях ввода** — при фокусе в текстовом поле Ctrl+V вставляет текст из буфера обмена (с фильтрацией по типу поля), Ctrl+C копирует содержимое поля в буфер.

### Changed
- Версия 2.2.3. В [docs/sprite_editor.md](docs/sprite_editor.md) обновлены разделы про поля ввода, горячие клавиши и ограничения.

### Fixed
- **Редактор: применение значений из полей** — значения Mass, Friction, Bounce (и остальные свойства) из Inspector теперь корректно записываются в объект при нажатии Enter или клике вне поля (раньше для physics_* применялись только кнопки +/-).
- **Редактор: применение по Enter и при потере фокуса** — одно и то же поведение для всех текстовых полей: Enter или клик в другое место применяет введённое значение.

---

## [2.2.2]

### Added
- **Документация: физика из сцены редактора** — в [docs/physics.md](docs/physics.md) добавлен раздел «Получение и настройка физики из сцены редактора»: `s.get_physics(sprite)`, `set_bounce(0)`, задание скорости, удаление тела и создание своего, границы мира. Пример кода и ссылка на demoGames.
- **demoGames/** в корне репозитория — пример сцены из редактора (level.json) с получением и настройкой физики в коде (платформер); README с инструкцией запуска и описанием.

### Changed
- Версия 2.2.2. В [docs/sprite_editor.md](docs/sprite_editor.md) и [docs/OVERVIEW.md](docs/OVERVIEW.md) добавлены упоминания `get_physics` и донастройки физики из кода. В разделе «Демо и примеры» [docs/physics.md](docs/physics.md) добавлен пункт про demoGames.

---

## [2.2.0]

### Added
- **Физика на pymunk** — реализация модуля физики переведена на библиотеку pymunk (2D-движок Chipmunk). Формы коллайдеров: прямоугольник по `sprite.rect`, круг, линия (segment); задаются через **PhysicsShape** (AUTO, BOX, CIRCLE, LINE) или строки.
- **PhysicsConfig**: опциональные поля `collision_category` и `collision_mask` для фильтра коллизий; по умолчанию тело сталкивается со всеми.
- **Редактор сцен**: для объектов с типом физики (Static/Kinematic/Dynamic) в Inspector доступны Mass, Friction, Bounce и при необходимости Category/Mask; значения сохраняются в JSON и подставляются в PhysicsConfig при загрузке сцены.

### Changed
- Версия библиотеки 2.2.0. Обратная совместимость API сохранена: `add_physics`, `add_static_physics`, `add_kinematic_physics`, `PhysicsConfig`, `PhysicsBody` (velocity, position, grounded, apply_impulse, set_velocity, set_bounds, add_constraint и т.д.) работают как раньше.
- Синхронизация спрайт↔тело: при любом изменении позиции спрайта привязанное тело сразу телепортируется; для static позиция берётся из спрайта каждый кадр, для dynamic/kinematic спрайт следует за телом после шага физики. **Поворот с физикой не синхронизируется** — в спрайт записывается только позиция (`rect.center`), угол из тела в спрайт не переносится (избегается рост rect при повороте).
- Документация: [docs/physics.md](docs/physics.md) переписана под pymunk (PhysicsShape, формы, отсутствие синхронизации поворота); [docs/physics_issues.md](docs/physics_issues.md), [docs/sprite_editor.md](docs/sprite_editor.md) и [docs/OVERVIEW.md](docs/OVERVIEW.md) обновлены.

### Dependencies
- Добавлена зависимость `pymunk>=6.0.0` (поддерживаются pymunk 6 и 7).

---

## [2.0.0]

### Added
- **Sprite Editor** — визуальный редактор спрайтов в стиле Unity
  - **Viewport** — центральная область редактирования с сеткой
  - **Инструменты**: Select (V), Move (G), Rotate (R), Scale (T)
  - **UI панели**: Hierarchy (слева), Inspector (справа), Toolbar (сверху), Statusbar (снизу)
  - **Drag & Drop** — перетаскивание изображений из проводника
  - **Undo/Redo** — Ctrl+Z / Ctrl+Y
  - **Копирование/Вставка** — Ctrl+C / Ctrl+V
  - **Камера**: zoom колесом мыши, pan средней кнопкой
  - **Сетка**: настраиваемый размер, привязка к сетке
  - **Сохранение/Загрузка**: JSON формат
- **CLI команда** — запуск редактора: `python -m spritePro.cli --editor` или `-e`
- **Модуль scene** — классы Scene, SceneObject, Transform для работы со сценами
- **Документация**: [docs/sprite_editor.md](docs/sprite_editor.md)

### Changed
- Версия библиотеки 2.0.0 (мажорный релиз — новый редактор)
- Обновлена документация: добавлен раздел о редакторе в README
- Улучшена структура проекта: редактор вынесен в tools/sprite_editor

### Fixed
- Добавлена поддержка Python 3.13

---

## [2.0.3]

### Fixed
- **Редактор: числовые поля в Inspector** — при вводе цифр символы больше не дублируются (11, 00, 22). Ввод обрабатывается только через TEXTINPUT; в KEYDOWN оставлены Enter/Escape/Backspace и fallback для keypad.

---

## [2.0.6]

### Added
- **Лобби мультиплеера (готовый экран)** — сцена `MultiplayerLobbyScene(s.Scene)` с полной очисткой спрайтов в `on_exit()`. При нажатии «В игру» хост рассылает событие `start_game`, игра запускается у обоих (хост и клиент). Экспорт: `EVENT_START_GAME`, `MultiplayerLobbyScene`, `run_multiplayer_lobby` из `spritePro.readyScenes`.
- **Кнопка «Готов» для клиента в лобби** — переключатель с визуальной подсветкой (активное состояние «Готов ✓»), отправка события `ready` с полем `value` (True/False) для опциональной логики на хосте.
- **TextSprite: поддержка переносов строк** — символ `\n` в тексте отображается как многострочный блок (рендер по строкам, отступ между строками). Удобно для списков игроков, подсказок, логов.

### Changed
- **Лобби** — все UI-элементы (включая `text_sprite` кнопок и полей ввода) снимаются с регистрации при переходе в игру; список игроков (roster) отображается с переносами строк.

### Документация
- Подробная инструкция по лобби в [docs/networking.md](docs/networking.md) (запуск, сценарий для игрока и разработчика).
- Обновлены [docs/text.md](docs/text.md) (многострочный текст), [docs/readySprites.md](docs/readySprites.md) (лобби), [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md).

---

## [2.0.8]

### Changed
- **Лобби мультиплеера** — убрана кнопка «Готов». В лобби у хоста: кнопки «Назад» и «В игру»; у клиента: кнопка «Назад». «Назад» отключает соединение (сервер/клиент) и возвращает к экрану настройки (имя, хост/клиент, порт, IP).

### Fixed
- **Лобби (режим хоста):** при входе в игру из лобби выставляется файл debug-лога по роли (`debug_host.log` / `debug_client.log` в `SPRITEPRO_LOG_DIR`), лог хоста пишется корректно.

---

## [2.1.0] — 2025-02-27

### Added
- **Физика: подсказки и докстринги для `s.physics`** — у прокси глобального мира явно объявлены методы `add`, `add_static`, `add_kinematic`, `remove`, `set_gravity`, `set_bounds`, `add_constraint`, `remove_constraint` с типами и докстрингами для IDE.
- **Физика: авто-добавление тел в мир** — у `add_physics`, `add_static_physics`, `add_kinematic_physics` параметр `auto_add=True` по умолчанию: тело сразу попадает в глобальный мир, вызывать `s.physics.add(body)` вручную не нужно. Для ручного контроля можно передать `auto_add=False`.
- **Редактор сцен: физика из сцены** — при загрузке сцены через `spawn_scene()` объекты с выставленным в редакторе типом физики (Static / Kinematic / Dynamic) автоматически получают тело и добавляются в глобальный мир `s.physics`; отдельный мир для сцены больше не создаётся.
- **Builder: типизированный возврат `build()`** — `s.sprite(path).build()` возвращает `Sprite` (явная типизация в коде и публичном API для корректных подсказок в IDE).

### Changed
- **Физика** — демо `physics_demo`, `hoop_bounce_demo`, ping_pong переведены на `auto_add=True` и импорт `import spritePro as s`; ручные вызовы `s.physics.add(...)` убраны. Остальные демо (visibility_culling, hot_reload, frame_tween, builder, particle_pool) и их копии в web_build переведены на `s`; в web_build синхронизированы physics_demo, hoop_bounce_demo, object_pool_demo и ping_pong (убраны лишние `physics.add`).
- **Документация** — [docs/physics.md](docs/physics.md): добавление тел через `s.add_physics`, `s.PhysicsConfig` и т.д., запуск демо из корня репозитория. [docs/sprite.md](docs/sprite.md): раздел «Столкновения по маске» (ensure_mask, collide_mask, collides_with). [docs/builder.md](docs/builder.md): ссылка на проверку столкновений по маске. [docs/OVERVIEW.md](docs/OVERVIEW.md), [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md): физика через `s.`, Sprite mask collision.

---

## [Unreleased]

### Added
- **Sprite: столкновения по маске** — методы `ensure_mask()`, `collide_mask(other)`, `collides_with(other, use_mask=True)` для пиксельно-точных столкновений при включённом `update_mask` (в Builder: `.mask(True)`). Документация: [docs/sprite.md](docs/sprite.md#столкновения-по-маске-пиксельная-точность).
- **Физика: глобальный мир** — один мир создаётся с игрой и доступен через `s.physics` или `s.get_physics_world()`. Гравитация: `s.physics.set_gravity(980)`. Ограничения с методом `update(dt)`: `s.physics.add_constraint(constraint)` — мир сам вызывает их после шага физики. Создавать `PhysicsWorld` и вызывать `register_update_object(world)` не нужно.
- **Ping Pong (демо)** — мяч на физическом движке (динамическое тело), ракетки и стены — статика. При ударе о ракетку задаётся направление по месту касания (offset по вертикали), константа `PADDLE_AIM_STRENGTH`. Подача с минимальной вертикальной составляющей (мяч не летит строго по прямой).
- **EventSignal и мультиплеер** — у объекта из `s.events.get_event(name)` метод `send(route="all", net=ctx, **payload)` рассылает событие локально и в сеть (как `s.events.send(...)`). Удобно хранить ссылку на событие: `start_game = s.events.get_event("start_game"); start_game.send(route="all", net=ctx)`.
- **CLI `--create` (архитектура шаблона):** новый проект теперь включает `scenes/level.json` (уровень редактора) и сцену, которая загружает его через `spawn_scene(...)`. Игрок берётся по имени `player` из JSON (`rt.exact("player").Sprite(speed=5)`), при отсутствии/ошибке JSON включается безопасный fallback без падения.
- **Экспорт сцены из кода в JSON** — `Scene.from_runtime(scene_instance)` и `Scene.export_from_runtime(scene_or_class, filepath)` в `spritePro.editor.scene`. Имена объектов = атрибуты сцены, позиция = центр спрайта; round-trip: код → JSON → правки в редакторе → загрузка в игре. Демо: `scenes_demo editor.py`.
- **Runtime сцен из редактора:** `placement()` возвращает **pos как центр** (rect.centerx, centery); `to_button`, `to_text_sprite`, `to_toggle` используют его по умолчанию. `exact(name)` — поиск по точному имени. Демо SceneA загружает сцену из `scene_a.json` через `spawn_scene`, вешает логику через `rt.exact("mover").Sprite(speed=1)`, `to_button`, `to_toggle` и т.д.
- **Типы спрайтов в редакторе** — примитивы Rectangle, Circle, Ellipse (по аналогии с Unity: GameObject → 2D → Square). Модуль `spritePro.editor.sprite_types`. В тулбаре кнопки Rect, Circle, Ellipse; в Inspector выпадающий список Sprite Type (Image / Rectangle / Circle / Ellipse) и для примитивов — Color R/G/B и размер (Size X/Y). В сцене: `sprite_shape`, `sprite_color`, для примитивов размер в `custom_data` (width, height). Runtime создаёт соответствующие спрайты при загрузке сцены.
- **Общий модуль отрисовки сетки** — `spritePro.grid_renderer`: единая функция `draw_world_grid()` для игры и редактора. Сетка (шаг 10/50/500) и подписи координат с плотностью, зависящей от зума (чем меньше зум — реже подписи, без «мельтешения» текста).
- **Редактор: подписи координат на сетке** — переключатель «Labels ON/OFF» в статусбаре и в Settings → Scene (Grid Labels). Подписи используют ту же зум-адаптивную логику, что и в игре.

### Changed
- **Физика** — демо `physics_demo`, `hoop_bounce_demo` переведены на глобальный мир `s.physics` (без своего `PhysicsWorld` и без `register_update_object`). Документация [docs/physics.md](docs/physics.md): раздел «Глобальный мир физики», `set_gravity`, `add_constraint`/`remove_constraint`, примеры без создания мира.
- **Hoop Bounce (демо)** — обруч рисуется одним кольцом (заливка внешнего круга + вырез внутреннего), без двойного контура от `pygame.draw.circle(..., width=...)`.
- **Редактор:** позиция объекта в JSON и в viewport — **центр** спрайта (transform.x, transform.y). Экспорт из runtime записывает rect.center.
- **Sprite (примитивы):** при `set_rect_shape`/`set_circle_shape`/`set_ellipse_shape` сохраняются цвет и флаг `_shape_fill_color`, чтобы цвет не терялся при перезапуске сцены и не применялся двойной тинт.
- **Button и TextSprite** — по умолчанию `screen_space=True`: позиция и размер не зависят от камеры и зума. Для кнопки/текста в мировых координатах (например над объектом) можно вызвать `.set_screen_space(False)`.
- **Debug-сетка** — подписи координат рисуются через `grid_renderer` с адаптивным шагом (min_label_px, «удобные» шаги 1/2/5/10/25/50). Редактор рисует сетку и подписи тем же модулем.

### Fixed
- **CLI `--create` шаблон сцены:** исправлена загрузка `player` из `level.json` — больше нет `None.Sprite(...)`, fallback-игрок не создаётся поверх успешно загруженного уровня.

### Планируется
- Продвинутые UI компоненты

## [1.4.9]

### Added
- **Tween.completion_value** — при **SetYoyo(True)** запоминается исходная стартовая позиция; при **Kill(complete=True)** применяется она (логический конец анимации), а не конец текущего полуцикла. Можно вызывать DoKill(True) и сразу новый DoMoveBy без ручного set_position.

### Changed
- **Документация**: [docs/tween.md](docs/tween.md), докстринг DoKill — уточнено поведение Kill(complete=True) при yoyo.

## [1.4.8]

### Fixed
- **SetLoops(count)** — исправлена логика циклов: раньше при любом `count != 0` твин шёл бесконечно. Теперь `SetLoops(1)` = один проход и завершение, `SetLoops(2)` = два прохода, `SetLoops(-1)` = бесконечно. В Tween добавлены `loop_count` и счётчик `_loops_done`.

### Changed
- **Документация**: [docs/tween.md](docs/tween.md) — уточнено описание SetLoops (0/1/2+/−1).

## [1.4.7]

### Added
- **Sprite.DoKill(complete=False)** — останавливает все твины этого спрайта (DoMove, DoScale и т.д.). Без хранения хэндлов: `sprite.DoKill(complete=False)` или `DoKill(complete=True)` (применить конец и on_complete). Возвращает `self`.
- **TweenHandle.Restart(apply_end=False)** — сброс твина в начало и повторный запуск. Работает и после `Kill()` (твин снова регистрируется и возвращается в список спрайта для DoKill).
- Do*-методы регистрируют твины у спрайта; при завершении или при `handle.Kill()` твин удаляется из списка. `handle.Kill()` также убирает твин из списка спрайта.

### Changed
- **DoMove и остальные Do*** возвращают **твин** (TweenHandle), не спрайт. Хэндл можно сохранить и удалить/перезапустить только его: `h = sprite.DoMove(...); h.Kill()` или `h.Restart()`.
- **Документация**: [docs/tween.md](docs/tween.md) — уточнено, что Do* возвращают TweenHandle; добавлены примеры сохранения хэндла, Kill одного твина, Restart; метод DoKill и Restart в таблицах.

## [1.4.6]

### Added
- **Готовые сцены (readyScenes)** — модуль `spritePro.readyScenes` для подключения готовых сцен в играх. **ChatScene** — мультиплеерный чат с историей, полем имени, сообщениями (время ЧЧ:ММ:СС), скроллом (колёсико и перетаскивание мышью по области), маской обрезки по viewport. **ChatStyle** — класс стиля (цвета, шрифты, отступы); можно переопределить перед использованием. Подключение: `from spritePro.readyScenes import ChatScene, ChatStyle`; после инициализации мультиплеера — `s.scene.add_scene("chat", ChatScene)` и `s.scene.set_scene_by_name("chat", recreate=True)`.
- **ScrollView**: параметр **use_mask=True** (по умолчанию) — контент за границами viewport не отображается (клиппинг); опциональный аргумент **mouse_drag_delta_y** в **update_from_input()** для скролла перетаскиванием мыши по области.
- **TextSprite**: свойство **input_active** — при `True` и пустом тексте отображается курсор «|»; при первом вводе символ курсора исчезает. Для сцен с полем ввода выставляйте `input_active` у активного поля перед вызовом `input()`.

### Changed
- Чат перенесён в библиотеку: сцена и стиль в `spritePro.readyScenes.chat`; пример запуска — `multiplayer_course/Chat/example_chat.py` (импорт ChatScene, ChatStyle из readyScenes).
- **Документация**: [docs/layout.md](docs/layout.md) — раздел «Скролл (ScrollView)» дополнен: use_mask, скролл мышью; [docs/README.md](docs/README.md) — добавлен раздел «Готовые сцены (readyScenes)»; [README.md](README.md) — упоминание готовых сцен в «Что внутри».
- Версия библиотеки 1.4.6 (патч).

## [1.4.5]

### Added
- **Layout: вставка и перестановка детей** — `add(child, index=None)`: при указании **index** вставка в произвольное место (0 — в начало). `add_at_start(child)` — в начало. `add_children(*children, index=None)` — при **index** вставка с указанной позиции. `move(child, index)` — перенос уже добавленного ребёнка на новую позицию в списке (меняет порядок расстановки).
- **Документация**: [docs/layout.md](docs/layout.md) — раздел «Добавление в начало/по индексу и move».
- Версия библиотеки 1.4.5 (патч).

## [1.4.4]

### Added
- **Удобные функции лейаута (size, pos, scene)** — во все функции `layout_flex_row`, `layout_flex_column`, `layout_horizontal`, `layout_vertical`, `layout_grid`, `layout_circle`, `layout_line` добавлены опциональные аргументы **size**, **pos**, **scene**. При `container=None` их можно передать сразу в вызов, без цепочки `.set_position().set_size()`: `s.layout_flex_column(None, [text, button], gap=20, pos=s.WH_C, size=(400, 300))`.
- **Ручной режим лейаута (auto_apply)** — у **Layout** и у всех удобных функций добавлен параметр **auto_apply=True**. При **auto_apply=False** методы `add`, `add_children`, `remove`, `remove_children`, `set_size` не вызывают `apply()`; расстановка обновляется только при явном вызове `refresh()` или `apply()`. Свойство `layout.auto_apply` можно менять в runtime.
- **Документация**: [docs/layout.md](docs/layout.md) — разделы «Удобные функции: size, pos, scene», «Ручной режим (auto_apply=False)», пример в одну строку.
- Версия библиотеки 1.4.4 (патч).

### Changed
- **Sprite.set_scene(scene)** — при передаче **None** спрайт снимается с регистрации (перестаёт обновляться и рисоваться). При передаче сцены спрайт при необходимости снова регистрируется. Раньше присваивался только атрибут `scene`, спрайт оставался в группе отрисовки.
- **Sprite.set_scene(scene, unregister_when_none=True)** — добавлен параметр **unregister_when_none**: при `scene=None` и `unregister_when_none=False` только обнуляется привязка к сцене, регистрация не снимается (спрайт остаётся в игре и рисуется).

## [1.4.3]

### Added
- **Sprite.set_size(size)** — установка ширины и высоты в пикселях (не scale). Возвращает `self`. Аргумент: `(width, height)` или Vector2.
- **Layout.set_size(size)** — переопределение: меняет размер контейнера, при `container=None` сохраняет стиль и вызывает `apply()` для перерасчёта детей. Возвращает `self`.
- **Примитивы с опциональными size и color**: у `set_rect_shape`, `set_circle_shape`, `set_ellipse_shape`, `set_polygon_shape`, `set_polyline` параметры `size` и/или `color` можно не указывать (`None`): берётся текущий размер и текущий цвет спрайта (для цвета при отсутствии tint — белый). Вспомогательный метод `_shape_color(color)`.
- **Документация**: [docs/sprite.md](docs/sprite.md) — добавлены `set_size` в список цепочек, раздел «Размер и примитивы»; [docs/layout.md](docs/layout.md) — раздел «Изменение размера (set_size)».
- Версия библиотеки 1.4.3 (патч).

## [1.4.2]

### Changed
- **Цепочки вызовов (продолжение)** — возврат `self` добавлен для методов движения, коллизий и UI:
  - **Sprite**: `limit_movement`, `reset_sprite`, `move`, `move_towards`, `move_up`, `move_down`, `move_left`, `move_right`, `stop`, `rotate_by`, `fade_by`, `scale_by`, `handle_keyboard_input`, `remove_collision_target`, `remove_collision_targets`, `clear_collision_targets`.
  - **Button**: `on_click`, `on_hover`.
  - **ToggleButton**: `toggle`.
- **Документация**: [docs/sprite.md](docs/sprite.md) — раздел «Цепочки вызовов» дополнен списком методов движения и примером с `handle_keyboard_input().limit_movement()`.
- Версия библиотеки 1.4.2 (патч).

## [1.4.1]

### Changed
- **Цепочки вызовов (fluent setters)** — методы установки возвращают `self` для цепочек:
  - **Sprite**: `set_position`, `set_scale`, `set_angle`, `rotate_to`, `set_alpha`, `set_color`, `set_sorting_order`, `look_at`, `set_screen_space`, `set_parent`, `set_world_position`, `set_image`, `set_rect_shape`, `set_circle_shape`, `set_ellipse_shape`, `set_polygon_shape`, `set_polyline`, `set_native_size`, `set_flip`, `set_active`, `set_scene`, `set_velocity`, `set_state`, `set_collision_targets`, `add_collision_target`, `add_collision_targets`.
  - **TextSprite**: `set_text`, `set_color`, `set_font`.
  - **Button**: `set_base_color`, `set_all_colors`, `set_all_scales`, `set_scale`, `set_sorting_order`.
  - **ToggleButton**: `set_state`, `set_colors`, `set_texts`.
  - **Bar**: `set_fill_amount`, `set_fill_direction`, `set_animate_duration`, `set_fill_type`, `set_image`, `set_fill_image`, `set_fill_color`, `set_background_image`, `set_background_size`, `set_fill_size`, `set_both_sizes`.
  - **Layout**: `add`, `add_children`, `remove`, `remove_children`, `apply`, `refresh`.
  - Обратная совместимость сохранена.
- **Демо**: в `fluent_tween_demo`, `layout_demo`, `primitives_demo`, `tween_presets_demo`, `bar_demo` использованы цепочки вызовов.
- **Документация**: [docs/sprite.md](docs/sprite.md) — раздел «Цепочки вызовов» расширен; [docs/layout.md](docs/layout.md) — добавлено про цепочки `add`/`apply`/`refresh`.
- Версия библиотеки 1.4.1 (патч).

## [1.4.0]

### Added
- **Fluent Tween API (Do-твины)**: удобный цепочечный API в стиле DOTween.
  - Методы на **Sprite**: `DoMove`, `DoMoveBy`, `DoScale`, `DoScaleBy`, `DoRotate`, `DoRotateBy`, `DoColor`, `DoAlpha`, `DoFadeIn`, `DoFadeOut`, `DoSize`, `DoPunchScale`, `DoShakePosition`, `DoShakeRotation`, `DoBezier` — по умолчанию `Ease.OutQuad`, автоудаление по завершении.
  - **TweenHandle**: цепочка `SetEase`, `SetDelay`, `OnComplete`, `SetLoops`, `SetYoyo`, `Kill(complete=False|True)`.
  - **Ease**: enum с именами In/Out/InOut по кривым (OutQuad, InCubic, InOutSine и др.), альтернатива `EasingType`.
  - Зацикливание: режим reset по умолчанию, `SetYoyo(True)` для движения туда-обратно; при завершении (если не loop) твин сам снимается с обновления.
- **Tween**: параметр `auto_remove_on_complete`; `stop(apply_end, call_on_complete)` для `Kill(complete=True)`; `set_easing()`; в пресетах — параметр `auto_remove_on_complete`.
- **Демо**: `spritePro/demoGames/fluent_tween_demo.py` — примеры Do*, цепочки, циклы 8/9/0, Kill.
- **Документация**: раздел «Fluent API (Do-твины)» в [docs/tween.md](docs/tween.md), таблицы методов Do* и TweenHandle, обновлены README и docs/README.md.
- **Крестики-нолики (мультиплеер)**: анимации на Fluent Tween — появление символа в ячейке (DoPunchScale), пульс по выигрышной линии, отдача кнопки «Новая игра».

### Changed
- Версия библиотеки 1.4.0 (минор).

## [1.3.4]

### Added
- **Модуль layout** (`spritePro.layout`): автолейаут для дочерних спрайтов.
  - **Layout** наследует **Sprite**: лейаут можно перемещать; при `container=None` лейаут сам является контейнером (параметры size, pos, scene), дети при add/remove привязываются через set_parent.
  - **LayoutDirection**: FLEX_ROW, FLEX_COLUMN, HORIZONTAL, VERTICAL, GRID, CIRCLE, LINE.
  - **LayoutAlignMain** / **LayoutAlignCross**: выравнивание (START, CENTER, END, SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY).
  - **GridFlow**: ROW, COLUMN для сетки.
  - Контейнер: Sprite, (x, y, w, h) или None (лейаут-спрайт как контейнер). Список расставляемых детей — **arranged_children**.
  - Удобные функции: layout_flex_row, layout_flex_column, layout_horizontal, layout_vertical, layout_grid, layout_circle, layout_line.
  - Авто-обновление при add/remove детей; ручной refresh/apply при смене параметров или типа.
  - Для CIRCLE: rotate_children и offset_angle. gap и padding как число или кортеж.
- **docs/layout.md**: описание API, Layout как Sprite, container=None, arranged_children, use_local, пример «лейаут как перемещаемый блок».
- **spritePro/demoGames/layout_demo.py**: демо всех типов лейаута (FLEX_ROW, FLEX_COLUMN, GRID, HORIZONTAL, VERTICAL, CIRCLE, LINE).

### Changed
- Версия библиотеки 1.3.4 (минор).

## [1.3.3]

### Added
- **docs/networking.md**: раздел «Лучшие практики» — примитивы JSON (что можно отправлять), позиция списком `list(pos)` и приём через `data.get("pos", ...)`, значения по умолчанию, троттлинг.
- **docs/networking.md**: таблица полей контекста, «Кто такой этот процесс», «Отображаемое имя», «Как отличить своего игрока от чужих».

### Changed
- **Позиция по сети**: во всех примерах и курсе — отправка `{"pos": list(pos)}`, приём `remote_pos[:] = data.get("pos", ...)`; убраны лишние `float()` и поля `x`/`y`.
- **Лобби (урок 4)**: при отправке `join` добавляем себя в `players` локально (`players.add(name)`), чтобы хост и все клиенты видели полный список (реле не отдаёт сообщение отправителю).
- **Демо и курс**: упрощена обработка `sender_id` (без лишних try/except и int()), компактное получение `other_id = data.get("sender_id")` где уместно.
- Версия библиотеки 1.3.3 (патч).

## [1.3.2]

### Added
- **Сетевые логи**: запись в файл `spritepro_logs/debug_net_<tag>.log` (каталог рядом со скриптом); тег процесса — `host`, `client_0`, `client_1` и т.д.; в строках лога выводится callsite; вывод в debug overlay через `net_log_to_overlay()`.
- **Критические ошибки**: при FATAL traceback пишется в сетевой лог и в `s.debug_log_error`.
- **Оверлей-логи в мультиплеере**: при переменной окружения `SPRITEPRO_NET_LOG_TAG` лог-файл оверлея — `spritepro_logs/debug_<tag>.log` (отдельный на каждый процесс).

### Changed
- Версия библиотеки 1.3.2 (патч).

### Fixed
- **NetClient.connect()**: при ошибке подключения — явное сообщение в лог и подсказка (--quick / --server).

## [1.3.1]

### Fixed
- GitHub Actions: отступы в `publish-to-pypi.yml` (корректный YAML для steps).

### Changed
- Версия библиотеки 1.3.1 (патч).

## [1.3.0]

### Added
- 📚 **EventBus.send**: подробный Google-докстринг с вариантами route (local/server/clients/all/net), net, include_local и **payload; примечание про проброс входящих без route.
- 📝 **Курс**: в примерах (урок 3, урок 10) добавлены комментарии о вариантах отправки и ссылка на докстринг.

### Changed
- Версия библиотеки 1.3.0 (минор).

## [1.2.22]

### Added
- 🌐 **MultiplayerContext**: глобальный контекст для мультиплеера (role/id, send/poll/send_every)
- 🧭 **send_every**: лимитер частоты отправки сетевых событий
- 📚 **Курс по мультиплееру**: 9 уроков с примерами/практикой/решениями
- 🧭 **EventBus routing**: отправка событий локально и в сеть (local/server/clients/all)
- 🎮 **Demo**: `events_rps_demo.py` (камень/ножницы/бумага) на Events + Multiplayer

### Changed
- 🧪 **Демо мультиплеера**: переход на MultiplayerContext и лимитер отправки
- 📝 **Документация**: обновлен `docs/networking.md` и README курса
- 🔁 **Networking run()**: тикрейт сервера по умолчанию 30 и флаг `--tick_rate`
- 🎯 **MultiplayerContext**: `is_host`, цвет вынесен из контекста

### Fixed
- 🗺️ **Amongus demo**: исправлены пути к спрайтам

## [1.2.21]

### Added
- 🌐 **Sprite.set_world_position()**: публичная установка мировой позиции
- 📚 **Документация**: добавлено описание world position и мультиплеера

## [1.2.20]

### Added
- 🌐 **Networking**: NetServer/NetClient для простого мультиплеера
- 📚 **Документация**: добавлен `docs/networking.md`

## [1.2.19]

### Fixed
- 🖱️ **Button**: не обрабатывает клики, когда сцена не активна

## [1.2.16]

### Fixed
- 🧷 **Screen-space**: `set_screen_space()` теперь применяется ко всем дочерним спрайтам

## [1.2.14]

### Added
- 🧩 **Scene-aware компоненты**: Button/ToggleButton/TextSprite/Timer/Tween/Animation поддерживают `scene` в конструкторе
- ⏱️ **Scene updates**: Timer/Tween/TweenManager/Animation автоматически приостанавливаются, если сцена не активна

## [1.2.12]

### Added
- 🎬 **Scene API**: удобный доступ через `s.scene` и авто‑создание сцен из фабрик
- 📷 **Camera shake**: встроенный эффект с перезапуском (`s.shake_camera`)
- 🧭 **Sprite.local_position**: локальная позиция относительно родителя

### Changed
- 🧩 **Tween API**: stop/reset/remove поддерживают apply_end
- 📚 **Документация**: обновлены разделы по сценам/камере/твинам

## [1.2.11]

### Added
- 🎞️ **Tween presets**: готовые твины для позиции, масштаба, поворота, цвета, прозрачности и размера
- 📚 **Документация**: обновлён `docs/tween.md` и добавлен `docs/tween_presets.md`
- ✨ **Новые твины**: punch/ shake/ fade/ flash/ bezier
- 🎯 **Sprite.look_at**: поворот к цели с оффсетом
- 🎮 **Demo**: tween_presets_demo.py с подсказками

## [1.2.10]

### Added
- ⏱️ **TICK**: глобальное событие каждого кадра (dt, frame_count, time_since_start)
- 🧮 **Счётчики времени**: frame_count и time_since_start в GameContext и глобальных

### Changed
- 🧩 **EventBus**: общий базовый сигнал для локальных и именованных событий
- 🎮 **EventBus demo**: таймерный tick вынесен в отдельное событие
- 📚 **Документация**: обновлены события и параметры контекста
- 📝 **Докстринги**: обновлены описания ввода, сцен, кэша и событий

## [1.2.9]

### Added
- 🧷 **GlobalEvents**: список глобальных событий без строковых литералов
- 🔔 **LocalEvent**: локальные события в переменных

### Changed
- 🎮 **EventBus demo**: показ `LocalEvent` и `s.globalEvents`

## [1.2.1]

### Added
- 🧭 **Debug HUD**: FPS и координаты камеры
- 🧾 **Логи**: уровни (info/warning/error/custom), источник вызова, запись в файл
- 🖱️ **Debug camera input**: управление камерой кнопкой мыши (или None)
- ⚓ **Sprite.anchor**: смена якоря без смещения позиции
- 📄 **Pages API**: страницы умеют управлять спрайтами
- 🎮 **EventBus Demo**: показ подписки на события и таймеры
- 📣 **Стартовый лог**: приветственное сообщение с ссылкой на репозиторий

### Changed
- 🧩 **Debug overlay**: сетка и HUD могут рисоваться поверх или под сценой
- 🧭 **Сетка**: шаг 100 по умолчанию, подписи во всех ячейках
- 🛠️ **Шаблон проекта**: debug включён по умолчанию, стартовый лог
- 🔧 **Anchor/FillDirection**: переведены на Enum без поломки старого API
- 🧩 **Pages demo**: сцены и страницы с авто-спрайтами
- 📚 **README**: полный список ссылок на всю документацию
- 🧪 **Reactive example**: добавлен пример с Blinker

### Fixed
- 🏓 **Ping Pong**: очки начисляются корректной стороне
- 🖼️ **Sprite.set_image**: пустая строка не вызывает предупреждение

## [1.2.0]

### Added
- 🖱️ **DraggableSprite** — drag-and-drop компонент на базе Sprite
- 🎮 **Новая демо-сцена**: drag_drop_demo.py
- 📚 **Документация**: `docs/draggable_sprite.md` + обновлены индексы
- 🧭 **Debug Overlay** — сетка мира, координаты камеры и логи
- 🎮 **Новая демо-сцена**: debug_overlay_demo.py
- 📚 **Документация**: `docs/debug.md`

### Changed
- 🧩 **Button**: текст синхронизируется по активности и sorting_order

## [1.1.0]

### Added
- ⌨️ **InputState** в стиле Unity: `is_pressed`, `was_pressed`, `was_released`, `get_axis`, состояние мыши
- 📣 **EventBus** для подписки на события (`quit`, `key_down`, `key_up`, `mouse_down`, `mouse_up`)
- 🧩 **Scene/SceneManager** для управления экранами (меню/игра/пауза)
- 📦 **ResourceCache** (LRU) для текстур и звуков + `load_texture` / `load_sound`
- 🧪 **Новые демо**: ввод/события, сцены, кэш ресурсов

### Changed
- 🔧 **Рефакторинг ядра**: камера и контекст вынесены из `__init__.py` в отдельные классы
- 🔄 **API событий**: список событий pygame доступен как `s.pygame_events`
- 📚 **Документация**: добавлены `docs/input.md`, `docs/game_loop.md`, обновлены индексы и README

## [1.0.3]

### Changed
- 🔧 **Версия пакета обновлена до 1.0.3**

## [1.0.1]

### Добавлено
- ✨ **Система сохранения/загрузки** - Профессиональная система для сохранения игровых данных
  - Поддержка JSON, Pickle, Text, Binary форматов
  - Автоматическое определение формата по расширению
  - Сжатие данных (gzip)
  - Автоматические резервные копии
  - Thread-safe операции
  - Сериализация пользовательских классов
  - Обработка ошибок и логирование
  - Интеграция с существующими SpritePro объектами

### Документация
- 📚 **Полная документация системы сохранения/загрузки** ([docs/save_load.md](docs/save_load.md))
- 🗺️ **Roadmap проекта** ([ROADMAP.md](ROADMAP.md)) — планы развития
- 🔧 **Технические спецификации** ([TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)) - детальные спецификации планируемых функций
- 🤝 **Руководство по участию** ([CONTRIBUTING.md](CONTRIBUTING.md)) - как внести вклад в проект
- 🎮 **Идеи игр и примеров** ([GAME_IDEAS.md](GAME_IDEAS.md)) - коллекция идей для демо игр
- ⚡ **Руководство по производительности** ([PERFORMANCE.md](PERFORMANCE.md)) - стратегии оптимизации
- 📖 **Индекс документации** ([DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)) - полный указатель документации

### Примеры и демо
- 🎯 **Простой пример использования** ([save_load_example.py](save_load_example.py))
- 🎮 **Комплексная демонстрация** ([spritePro/demoGames/save_load_demo.py](spritePro/demoGames/save_load_demo.py))

### Улучшения
- 📦 **Обновлен utils/__init__.py** - экспорт новых функций сохранения/загрузки
- 📝 **Обновлен README.md** - добавлены ссылки на новую документацию

### Техническое
- 🔒 **Thread-safe операции** - безопасность при многопоточном доступе
- 📊 **Логирование** - подробное логирование всех операций
- 🛡️ **Обработка ошибок** - корректная обработка всех возможных ошибок
- 🗜️ **Сжатие данных** - опциональное сжатие для экономии места

## [1.0.0]

### Добавлено
- 🎮 **Базовая система спрайтов** - Основа для всех игровых объектов
- 🎯 **GameSprite** - Расширенные спрайты с игровой логикой
- ⚡ **PhysicSprite** - Спрайты с физическим моделированием
- 🖱️ **Система кнопок** - Интерактивные UI элементы
- 🔄 **ToggleButton** - Переключатели и чекбоксы
- 📝 **Система текста** - Рендеринг и управление текстом
- 🎬 **Система анимации** - Покадровая анимация и состояния
- 🌊 **Tweening система** - Плавные переходы и easing
- ⏰ **Система таймеров** - Управление временем и событиями
- ❤️ **Система здоровья** - HP, урон, лечение
- 🖱️ **Mouse Interactor** - Обработка мыши и hover эффектов
- 🎨 **Surface утилиты** - Работа с поверхностями
- 🌈 **Цветовые эффекты** - Динамические цвета и анимации
- 📊 **Text FPS** - Готовый счетчик FPS

### Демонстрационные игры
- 🎯 **Basic Demo** - Основы работы со спрайтами
- 🔘 **Button Demo** - Интерактивные кнопки
- 📝 **Text Demo** - Работа с текстом
- 🎬 **Animation Demo** - Система анимации
- 🌊 **Tween Demo** - Плавные переходы
- ⚡ **Physics Demo** - Физическое моделирование
- 🔄 **Toggle Demo** - Переключатели
- 🌈 **Color Effects Demo** - Цветовые эффекты
- 📊 **FPS Camera Demo** - Камера и FPS счетчик

### Документация
- 📚 **Полная документация** всех компонентов в папке `docs/`
- 🎯 **Примеры использования** для каждого компонента
- 🎮 **Демо игры** с исходным кодом

## Типы изменений

- `Added` - новые функции
- `Changed` - изменения в существующей функциональности
- `Deprecated` - функции, которые будут удалены в будущих версиях
- `Removed` - удаленные функции
- `Fixed` - исправления ошибок
- `Security` - исправления уязвимостей

## Планы на будущие версии

## [Unreleased]

- ✨ Улучшенное Kivy-лобби (`use_lobby=True`, `platform="kivy"`) с поддержкой мобильного режима и удобным десктопным тестированием.
- ✨ Автозапуск нескольких Kivy-процессов с лобби при `multiplayer_clients>1` — каждый процесс = отдельный игрок, для локального теста мультиплеера.
- 🎨 Перевод лобби на flex-лейауты SpritePro (`layout_flex_column` / `layout_flex_row`) для аккуратного расположения полей, кнопок и статуса.
- 📚 Обновления документации по `use_lobby=True`, Kivy-режиму и демо `three_clients_move_demo`.

### v1.1.0 - Система инвентаря
- Полноценная система управления предметами
- Drag & Drop интерфейс
- Категории и фильтрация предметов

### v1.2.0 - Продвинутый UI
- Слайдеры и прогресс-бары
- Выпадающие списки
- Модальные окна
- Система тем

### v1.3.0 - Система частиц
- Эмиттеры частиц
- Готовые эффекты (огонь, дым, взрывы)
- Физика частиц
- Оптимизация производительности

### v1.4.0 - Система диалогов
- Ветвящиеся диалоги
- Портреты персонажей
- Анимированный текст
- Интеграция с системой квестов

### v2.0.0 - Мультиплеер
- Клиент-серверная архитектура
- Синхронизация состояний
- P2P соединения
- Онлайн сервисы

---

**Примечание**: Даты в формате YYYY-MM-DD. Версии следуют [Semantic Versioning](https://semver.org/).

**Легенда эмодзи**:
- ✨ Новые функции
- 🐛 Исправления ошибок
- 📚 Документация
- 🎮 Игры и примеры
- ⚡ Производительность
- 🔒 Безопасность
- 🎨 UI/UX
- 🔧 Техническое