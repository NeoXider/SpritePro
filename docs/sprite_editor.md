# Sprite Editor

Встроенный редактор спрайтов в стиле Unity для визуального создания игровых сцен.
Редактор поддерживает модульные окна/страницы, интерактивный Inspector, настройку камеры/сетки через слайдеры и рамку предпросмотра камеры в viewport.

**Что описано в этом документе:** 1) сам редактор — запуск, интерфейс, инструменты, сохранение/загрузка; 2) **использование созданных в редакторе сцен в своей игре** — загрузка JSON, `spawn_scene`, получение объектов по имени (см. [Интеграция с SpritePro](#интеграция-с-spritepro)).

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Запуск](#запуск)
- [Интерфейс](#интерфейс)
- [Инструменты](#инструменты)
- [Управление](#управление)
- [Сохранение и загрузка](#сохранение-и-загрузка)
- [Формат JSON](#формат-json)
- [Координаты в редакторе](#координаты-в-редакторе)
- [Горячие клавиши](#горячие-клавиши)
- [Интеграция с SpritePro](#интеграция-с-spritepro) — использование сцены в своей игре
- [Экспорт сцены из кода в JSON](#экспорт-сцены-из-кода-в-json) — round-trip: код → JSON → редактор → игра

---

## Быстрый старт

### Установка

Редактор входит в состав SpritePro 2.0. Убедитесь, что у вас установлена последняя версия:

```bash
pip install spritepro
```

### Запуск

```bash
# Через CLI
python -m spritePro.cli --editor

# Или короткий вариант
python -m spritePro.cli -e

# Как отдельный модуль editor
python -m spritePro.editor

# Напрямую
python -m spritePro.editor
```

### Первая сцена

1. Запустите редактор
2. Перетащите изображения (PNG, JPG, BMP) из проводника на сцену
3. Спрайты появятся в центре viewport
4. Перетаскивайте спрайты для расстановки
5. Настройте Zoom/Grid слайдерами или текстовыми полями в нижней панели
6. Сохраните сцену (Ctrl+S или кнопка Save)

---

## Запуск

### Способы запуска

| Способ | Команда |
|--------|---------|
| CLI | `python -m spritePro.cli --editor` |
| CLI (короткий) | `python -m spritePro.cli -e` |
| Editor module | `python -m spritePro.editor` |
| Напрямую | `python -m spritePro.editor` |
| Из Python | `import spritePro as s; s.editor.launch_editor()` |

### Параметры при запуске

Можно передать размер окна:

```python
import spritePro as s
from spritePro.editor.editor import SpriteEditor

# Вариант 1: простой запуск
s.editor.launch_editor()

# Вариант 2: если нужен кастомный размер окна
editor = SpriteEditor(size=(1280, 720))
editor.run()
```

---

## Интерфейс

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Select (V)  Move (G)  Rotate (R)  Scale (T)    New Scene   *        │
├────────┬────────────────────────────────────────────┬────────────────────┤
│Objects │                                            │ Properties          │
│        │                                            │                     │
│  👁 Player    │         Viewport                    │ Name: Player       │
│  👁 Ground    │         (область редактирования)    │                    │
│  👁 Enemy     │                                    │ Position           │
│        │     ┌──────────┐                          │ X: [100] Y: [200]  │
│        │     │  Sprite  │                          │ Rotation: [0]      │
│        │     └──────────┘                          │ Scale X: [1.0]    │
│        │                                            │ Scale Y: [1.0]    │
│        │                                            │                    │
│        │                                            │ Sprite: player.png │
│        │                                            │ Sorting Order: 0   │
├────────┴────────────────────────────────────────────┴────────────────────┤
│  X: 100  Y: 200  │  Zoom: 100%  │  Grid: 10px  │  Snap: ON            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Основные области

#### Toolbar (Верхняя панель)

- **Инструменты**: Select, Move, Rotate, Scale
- **Кнопки**: Add (изображение), Rect, Circle, Ellipse (примитивы), Load, Save, New, Grid, Settings
- **Название сцены**: отображается в центре
- **Индикатор изменений**: `*` означает несохранённые изменения

#### Hierarchy (Левая панель)

Список всех объектов сцены:
- 👁 - объект видим
- ○ - объект скрыт
- Клик - выделить объект

#### Inspector (Правая панель)

Свойства выделенного объекта:
- **Name** - имя объекта
- **Position X/Y** - позиция в мировых координатах (редактируется кнопками +/-)
- **Rotation** - угол поворота в градусах (редактируется)
- **Scale X/Y** - масштаб по осям (редактируется раздельно)
- **Image Size** - реальный размер исходного файла в пикселях
- **Size X/Y** - фактический размер объекта на сцене (редактируется раздельно)
- **Sprite** - путь к файлу изображения
- **Sprite Type** — выпадающий список: Image (картинка по пути), Rectangle, Circle, Ellipse. При выборе примитива размер задаётся в Size X / Size Y (пиксели), цвет — в Color R, G, B (0–255).
- **Sprite** — путь к изображению (только для типа Image).
- **Color R / G / B** — цвет примитива (только для Rectangle / Circle / Ellipse).
- **Sorting Order** — слой отрисовки (редактируется).
- **Screen Space** — переключатель ON/OFF: при включении объект в игре не зависит от камеры и зума (фиксирован к экрану).
- **Visible / Locked** — флаги объекта (переключатели ON/OFF).

#### Viewport (Центральная область)

Область редактирования с:
- Сеткой (включается/выключается кнопкой Grid в тулбаре)
- Подписями координат на сетке (включаются/выключаются кнопкой Labels в статусбаре или в Settings → Scene). Плотность подписей зависит от зума: при отдалении камеры подписи реже.
- Спрайтами
- Gizmo выделения
- Рамкой предпросмотра камеры `800x600` (что увидит игрок при стандартном запуске)

#### Statusbar (Нижняя панель)

- **X, Y** - координаты мыши в мировых координатах
- **Zoom** - текущий масштаб
- **Grid** - размер клетки сетки
- **Snap** - включена ли привязка к сетке
- **Labels** - показывать ли подписи координат на сетке (зум-адаптивная плотность)
- **Слайдеры** - прямое управление Zoom и Grid
- **Поля ввода** - точный ввод Zoom (%) и Grid (px)

---

## Инструменты

### Select (V)

Выделение объектов.

**Использование:**
- Клик по спрайту - выделить один объект
- Shift + клик - добавить к выделению
- Клик по пустому пространству - снять выделение

### Move (G)

Перемещение объектов.

**Использование:**
1. Выберите инструмент Move (G)
2. Перетаскивайте выделенные объекты мышью

**Особенности:**
- Работает с несколькими выделенными объектами
- Поддерживается привязка к сетке

### Rotate (R)

Вращение объектов.

**Использование:**
1. Выберите инструмент Rotate (R)
2. Перетаскивайте мышь влево/вправо для вращения

**Особенности:**
- Положительное значение - вращение по часовой стрелке
- Отрицательное значение - вращение против часовой
- Shift - привязка угла к шагу 15°

### Scale (T)

Масштабирование объектов.

**Использование:**
1. Выберите инструмент Scale (T)
2. Перетаскивайте мышь для изменения масштаба

**Особенности:**
- По умолчанию изменяет `Scale X` и `Scale Y` раздельно
- Shift - пропорциональное масштабирование
- Минимальный масштаб: 0.05

---

## Управление

### Работа с камерой

| Действие | Управление |
|----------|-----------|
| Zoom (приближение/отдаление) | Колесо мыши |
| Pan (перемещение вида) | Средняя кнопка мыши (зажать и тянуть) |
| Точный Zoom | Слайдер или ввод значения в `%` (от `1` до `1000`) |
| Размер сетки | Слайдер или ввод значения в `px` |

### Работа с объектами

| Действие | Управление |
|----------|-----------|
| Выделить объект | Левый клик по спрайту |
| Добавить к выделению | Shift + левый клик |
| Снять выделение | Клик по пустому пространству |
| Переместить | Drag мышью (инструмент Move) |
| Удалить | Delete или Backspace |
| Копировать | Ctrl + C |
| Вставить | Ctrl + V |
| Отменить | Ctrl + Z |
| Повторить | Ctrl + Y |

### Drag & Drop

Перетаскивание файлов из проводника:

1. Найдите изображение в проводнике (PNG, JPG, JPEG, BMP, GIF)
2. Перетащите файл в viewport редактора
3. Спрайт автоматически добавится на сцену в позицию курсора

---

## Сохранение и загрузка

### Сохранение сцены

```python
# В редакторе нажмите Ctrl+S
# Сцена сохранится в файл scene_name.json
```

### Загрузка сцены

```python
from spritePro.editor.scene import Scene

# Загрузка из файла
scene = Scene.load("my_scene.json")

# Создание редактора с загруженной сценой
import spritePro as s
s.editor.launch_editor()
```

### Программное создание сцены

```python
from spritePro.editor.scene import Scene, SceneObject, Transform

# Создание сцены
scene = Scene(name="My Game")
scene.grid_size = 10
scene.snap_to_grid = True

# Добавление объектов
player = SceneObject(
    name="Player",
    sprite_path="assets/player.png",
    transform=Transform(x=100, y=200),
    z_index=10
)
scene.add_object(player)

# Сохранение
scene.save("level1.json")
```

---

## Формат JSON

Сохранённая сцена имеет следующую структуру:

```json
{
    "version": "1.0",
    "name": "My Scene",
    "camera": {
        "x": 0,
        "y": 0,
        "zoom": 1.0
    },
    "objects": [
        {
            "id": "abc12345",
            "name": "Player",
            "sprite_path": "assets/player.png",
            "transform": {
                "x": 100.0,
                "y": 200.0,
                "rotation": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0
            },
            "z_index": 10,
            "visible": true,
            "locked": false,
            "custom_data": {}
        }
    ],
    "grid_size": 10,
    "grid_visible": true,
    "snap_to_grid": true
}
```

### Поля объекта

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | str | Уникальный идентификатор |
| `name` | str | Отображаемое имя |
| `sprite_path` | str | Путь к файлу изображения |
| `transform.x` | float | Центр объекта по X |
| `transform.y` | float | Центр объекта по Y |
| `transform.rotation` | float | Угол поворота в градусах |
| `transform.scale_x` | float | Масштаб по X |
| `transform.scale_y` | float | Масштаб по Y |
| `z_index` | int | Слой отрисовки |
| `visible` | bool | Видимость объекта |
| `locked` | bool | Защита от редактирования |
| `custom_data` | dict | Пользовательские данные |

---

## Координаты в редакторе

В редакторе **позиция объекта** (`transform.x`, `transform.y`) хранится как **центр** спрайта. При отрисовке и при перетаскивании используется центр; при экспорте из игры в JSON также записывается центр. Это согласовано с якорем CENTER по умолчанию у Sprite/Button/TextSprite в SpritePro.

---

## Горячие клавиши

### Инструменты

| Клавиша | Действие |
|---------|----------|
| V | Инструмент Select (выделение) |
| G | Инструмент Move (перемещение) |
| R | Инструмент Rotate (вращение) |
| T | Инструмент Scale (масштаб) |

### Редактирование

| Клавиша | Действие |
|---------|----------|
| Delete | Удалить выделенные объекты |
| Backspace | Удалить выделенные объекты |
| Ctrl + Z | Отменить действие (Undo) |
| Ctrl + Y | Повторить действие (Redo) |
| Ctrl + C | Копировать выделенные объекты |
| Ctrl + V | Вставить скопированные объекты |
| Ctrl + S | Сохранить сцену |
| Escape | Снять выделение |
| F1 | Открыть/скрыть окно Settings |

### Навигация

| Клавиша | Действие |
|---------|----------|
| Колесо мыши | Zoom (приближение/отдаление) |
| Средняя кнопка | Pan (перемещение камеры) |

---

## Интеграция с SpritePro

### Загрузка сцены в игру

```python
import spritePro as s
from spritePro.editor.scene import Scene

# Загружаем сцену
scene = Scene.load("level1.json")

# Создаём игровые спрайты
s.get_screen((800, 600), "My Game")

sprites_map = {}  # id -> s.Sprite

for obj in scene.objects:
    if not obj.visible:
        continue

    image = s.pygame.image.load(obj.sprite_path).convert_alpha()
    native_w, native_h = image.get_size()
    final_size = (
        max(1, int(native_w * obj.transform.scale_x)),
        max(1, int(native_h * obj.transform.scale_y)),
    )
    
    sprite = s.Sprite(
        obj.sprite_path,
        final_size,
        (obj.transform.x, obj.transform.y),
        scene=s.get_current_scene()
    )
    
    # Применяем трансформации
    if obj.transform.rotation:
        sprite.angle = obj.transform.rotation
    
    # Z-index через sorting_order
    sprite.sorting_order = obj.z_index
    
    sprites_map[obj.id] = sprite

# Запускаем игру
while True:
    s.update(fill_color=(20, 20, 30))
```

### Короткий путь (рекомендуется): spawn_scene и RuntimeScene

```python
import spritePro as s
from spritePro.editor.runtime import spawn_scene

s.get_screen((800, 600), "My Game")
rt = spawn_scene("level1.json", scene=s.get_current_scene(), apply_camera=True)

# По имени (без учёта регистра) или точное имя
player = rt.first("player")      # первый с именем "player"
obj = rt.exact("Player")         # точное совпадение имени
enemies = rt.startswith("enemy") # все, чьё имя начинается с "enemy"
```

**Размещение из сцены:** `placement()` возвращает данные из сцены: **pos (центр)**, size, angle, sorting_order, screen_space, scene. Этим пользуются хелперы ниже; позиция — центр объекта (как в редакторе).

**Превращение заготовки в кнопку/текст/переключатель:**

```python
# Спрайт из сцены — только применить доп. параметры (speed, цвет уже из JSON)
mover = rt.exact("mover").Sprite(speed=1)

# Прямоугольник из сцены → кнопка (размер/позиция из сцены, в коде — текст и колбэк)
btn = rt.exact("button").to_button(text="Click me", on_click=my_callback)

# → текстовый спрайт
label = rt.exact("label").to_text_sprite(text="Hello", font_size=32, color=(255,255,255))

# → переключатель
toggle = rt.exact("toggle").to_toggle(text_on="ON", text_off="OFF", on_toggle=my_toggle)
```

Алиасы: `to_button` = `Button()`, `to_text_sprite` = `TextSprite()`, `to_toggle` = `Toggle()`.

**Физика:** если в Inspector у объекта выставлен тип физики (Physics: None / Static / Kinematic / Dynamic), при загрузке сцены через `spawn_scene` таким объектам автоматически создаётся тело и они добавляются в глобальный мир `s.physics`. Отдельно вызывать `s.physics.add(...)` не нужно. Подробнее: [physics.md](physics.md).

Полные примеры: `spritePro/demoGames/editor_scene_runtime_demo.py`, **Scenes Demo (editor)** — `spritePro/demoGames/scenes_demo editor.py` (сцена загружается из JSON, логика вешается в коде).

### Создание редактора внутри игры

```python
# Можно запустить редактор как отдельное окно
# и затем загрузить результат в игру
import spritePro as s
from spritePro.editor.scene import Scene

# Редактирование
s.editor.launch_editor()

# После выхода - редактор сохранит сцену в scene.name.json
# Загружаем в игру
game_scene = Scene.load("Level 1.json")
```

---

## Экспорт сцены из кода в JSON

Чтобы править в редакторе сцену, изначально собранную в коде, её можно один раз экспортировать в JSON. Дальше: правки в редакторе → сохранение → загрузка в игре из JSON.

**API:**

```python
from spritePro.editor.scene import Scene as EditorScene

# Вариант 1: из экземпляра сцены (после set_scene_by_name)
EditorScene.export_from_runtime(s.scene.current_scene, "scene_a.json")

# Вариант 2: передать класс сцены (создаётся временный экземпляр для экспорта)
EditorScene.export_from_runtime(SceneA, "scene_a.json")
```

**Что попадает в JSON:** имена объектов = имена атрибутов сцены (например `mover`, `button`, `label`). Позиция — центр спрайта; размер, цвет, путь к картинке — из самих спрайтов. Учитываются только корневые спрайты (без parent). После экспорта можно открыть файл в редакторе, изменить layout и сохранить; в игре загружать сцену через `spawn_scene("scene_a.json", scene=self)` и вешать логику через `rt.exact("mover").Sprite(speed=1)`, `rt.exact("button").to_button(...)` и т.д.

Пример полного цикла (код → JSON → редактор → загрузка из JSON в игре): `spritePro/demoGames/scenes_demo editor.py`.

---

## Окна и страницы

Редактор использует модульную систему окон (`spritePro/editor/ui/windows.py`):

- `Settings` - отдельное окно с вкладками `Scene` и `View`. На вкладке Scene: Grid Visible, Grid Labels (подписи координат на сетке), Snap To Grid.
- вкладки расширяются в отдельном модуле без правок основного цикла редактора
- кнопка `Settings` и горячая клавиша `F1` открывают/закрывают окно

### Добавление новой страницы в Settings

1. Откройте `spritePro/editor/ui/windows.py`
2. Добавьте имя вкладки в `SettingsWindow(... page_titles=[...])`
3. Добавьте рендер новой страницы в `SettingsWindow.render(...)`
4. Вынесите логику страницы в `_render_<page>_page(...)`

---

## Переезд редактора в пакет

Начиная с текущей версии, основной код редактора находится внутри пакета `spritePro`:

- `spritePro/editor/editor.py` — основной цикл и инструменты редактора
- `spritePro/editor/ui/windows.py` — модуль окон/вкладок (`Settings`)
- `spritePro/editor/scene.py` — модель данных сцены
- `spritePro/editor/runtime.py` — запуск сцены в рантайме (`spawn_scene`)

Папка `tools/sprite_editor` оставлена только для обратной совместимости (тонкие реэкспорты).

---

## Ограничения и известные проблемы

### Текущие ограничения

1. **Нет редактирования имени через Inspector** - Name пока read-only
2. **Нет выделения рамкой** - только клик/Shift+клик
3. **Нет слоёв/папок** - все объекты в одном списке
4. **Ограниченные форматы изображений** - PNG, JPG, BMP, GIF

### Планируемые функции

- [ ] Создание/удаление объектов из UI
- [ ] Множественное выделение (рамкой)
- [ ] Слои/папки для организации
- [ ] Preview (запуск игры)
- [ ] Экспорт в код SpritePro

---

## Примеры использования

### Типы спрайтов (Sprite Type)

В редакторе объект может быть:

- **Image** — отображается картинка по пути `sprite_path` (добавление через Add или перетаскивание файла).
- **Rectangle** — примитив «прямоугольник». Размер в Inspector: Size X, Size Y (пиксели). Цвет: Color R, G, B (0–255). В тулбаре: кнопка **Rect**.
- **Circle** — примитив «круг». Размер и цвет так же в Inspector. В тулбаре: кнопка **Circle**.
- **Ellipse** — примитив «эллипс». В тулбаре: кнопка **Ellipse**.

В Inspector выпадающий список **Sprite Type** переключает тип (Image → Rectangle → Circle → Ellipse → Image). Для примитивов размер хранится в `custom_data` (width, height), цвет — в `sprite_color`. В игре при загрузке сцены через `spawn_scene` примитивы создаются как спрайты с соответствующими формами.

### Создание платформера

Уровень можно собрать в редакторе: кнопки **Rect** / **Circle** для платформ и игрока, задать имена (например `Player`, `Platform`), размеры и цвета в Inspector, сохранить в JSON. Запуск демо:

```bash
python -m spritePro.demoGames.platformer_demo
```

Программное создание сцены с примитивами:

```python
from spritePro.editor.scene import Scene, SceneObject, Transform

scene = Scene(name="platformer_level1")

# Платформа как примитив (rectangle)
obj = SceneObject(
    name="Platform",
    sprite_path="",
    sprite_shape="rectangle",
    sprite_color=(70, 200, 70),
    transform=Transform(x=400, y=580),
    custom_data={"width": 800, "height": 20},
)
scene.add_object(obj)

# Игрок — примитив
player = SceneObject(
    name="Player",
    sprite_path="",
    sprite_shape="rectangle",
    sprite_color=(255, 80, 80),
    transform=Transform(x=400, y=200),
    custom_data={"width": 40, "height": 60},
    z_index=10,
)
scene.add_object(player)

scene.save("level1.json")
```

---

## Технические детали

### Требования

- Python 3.7+
- Pygame 2.0+

### Структура проекта

```
spritePro/editor/
├── __init__.py          # launch_editor, spawn_scene и экспорт API
├── __main__.py          # запуск: python -m spritePro.editor
├── editor.py            # главный цикл/инструменты редактора
├── scene.py             # модель Scene/SceneObject/Transform/Camera
├── sprite_types.py      # типы спрайтов: Image, Rectangle, Circle, Ellipse (примитивы)
├── runtime.py           # spawn_scene(...) для рантайма
└── ui/
    ├── __init__.py
    └── windows.py       # модуль окон/страниц редактора

tools/sprite_editor/
├── __init__.py          # совместимость со старыми импортами
├── editor.py            # совместимость (реэкспорт из spritePro.editor.editor)
├── scene.py             # совместимость (реэкспорт из spritePro.editor.scene)
└── ui/
    ├── __init__.py      # совместимость
    └── windows.py       # совместимость
```

### Архитектура

- **Scene** - контейнер объектов, камеры, настроек сетки
- **SceneObject** — объект с трансформацией, путём к спрайту (Image), типом примитива (sprite_shape: rectangle/circle/ellipse) и цветом (sprite_color)
- **Transform** - позиция, вращение, масштаб
- **SpriteEditor** - главный класс с игровым циклом и обработкой событий
- **ToolType** - перечисление инструментов (Select, Move, Rotate, Scale)
