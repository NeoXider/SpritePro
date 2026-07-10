# Sprite Editor (Редактор сцен)

Визуальный редактор игровых сцен в стиле Unity. Поддерживает модульные окна, drag-and-drop, Inspector, настройку камеры/сетки.

## Запуск

```bash
python -m spritePro.cli --editor
python -m spritePro.cli -e
python -m spritePro.editor
```

## Интерфейс

```
┌──────────────────────────────────────────────────────────────┐
│  File  GameObject  Tools  View                    Scene *   │
├────────┬───────────────────────────────┬────────────────────┤
│Objects │                               │ Properties          │
│  ● Player│       Viewport              │ Name: Player       │
│  ● Ground│   ┌──────────┐              │ Position X: [100] │
│  ○ Label │   │  Sprite  │              │ Scale X: [1.0]   │
│          │   └──────────┘              │ Sprite: player.png│
├────────┴───────────────────────────────┴────────────────────┤
│  X: 100  Y: 200  │  Zoom: 100%  │  Grid: 10px  │  Snap: ON │
└──────────────────────────────────────────────────────────────┘
```

### Основные области

| Область | Описание |
|---------|----------|
| **Toolbar** | File, GameObject, Tools, View, Run (F5) |
| **Hierarchy** | Список объектов (● активен, ○ скрыт) |
| **Inspector** | Свойства выделенного объекта |
| **Viewport** | Область редактирования с сеткой |
| **Statusbar** | Координаты мыши, Zoom, Grid, Snap |

## Инструменты

Панель инструментов (как в Unity) — постоянно видна в левом верхнем углу viewport: Select / Move / Rotate / Scale, активный подсвечен. Горячие клавиши работают всегда:

| Клавиша | Инструмент | Описание |
|---------|-----------|----------|
| V | Select | Выделение объектов |
| G | Move | Перемещение |
| R | Rotate | Вращение (шаг 15°) |
| T | Scale | Масштабирование |

## Создание объектов

- Кнопка **«+»** в заголовке панели иерархии — меню создания (Image, Rectangle, Circle, Ellipse, Text, Button); объект появляется в центре видимой области.
- **Правый клик по пустому месту viewport** — то же меню, объект создаётся в точке клика.
- Меню **GameObject** — дублирует создание.

## Управление

| Действие | Управление |
|----------|-----------|
| Zoom | Колесо мыши |
| Pan | Средняя кнопка мыши |
| Выделить | Левый клик |
| Добавить к выделению | Shift + клик |
| Удалить | Delete / Backspace |
| Отменить | Ctrl + Z |
| Повторить | Ctrl + Y |
| Сохранить | Ctrl + S |
| Запустить игру | F5 |

## Типы спрайтов

- **Image** — изображение из файла
- **Rectangle** — прямоугольник (кнопка Rect)
- **Circle** — круг (кнопка Circle)
- **Ellipse** — эллипс (кнопка Ellipse)
- **Button** — кнопка (GameObject → New Button или Ctrl+Shift+B). Как в Unity, создаётся с **дочерним Text-объектом** — надпись живёт в нём (текст/шрифт/цвет редактируются на ребёнке, позицию надписи можно сдвигать). Удалите ребёнка — кнопка будет без текста (для икон-кнопок). При загрузке через `spawn_scene` создаётся настоящий `spritePro.Button`, дочерний Text становится его надписью (`btn.text_sprite`) и отдельным объектом не спавнится.

## Иерархия (вложенность объектов)

Как в Unity: объекты можно класть внутрь других объектов.

- Перетащите элемент в панели иерархии **на другой элемент** — он станет ребёнком (дети рисуются с отступом под родителем).
- Перетащите на пустое место панели — объект освобождается от родителя.
- Перемещение родителя (инструмент Move или правка X/Y в инспекторе) двигает всех потомков.
- При удалении родителя дети остаются в сцене и освобождаются от него.
- В JSON у ребёнка хранится ссылка `parent` (id родителя), координаты — мировые. Старые сцены без поля работают как раньше.
- В рантайме `spawn_scene` автоматически вызывает `set_parent(..., keep_world_position=True)`.

## Drag & Drop

Перетащите PNG/JPG/BMP/GIF из проводника в viewport — спрайт добавится в позицию курсора.

## Сохранение и загрузка

```python
# Сохранение: Ctrl+S в редакторе → scene_name.json
# Загрузка в игру
from spritePro.editor.scene import Scene
scene = Scene.load("level1.json")
```

## Интеграция с игрой

### Рекомендуемый способ: spawn_scene

```python
import spritePro as s
from spritePro.editor.runtime import spawn_scene

class LevelScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.rt = spawn_scene("level1.json", scene=self, apply_camera=True)
        
        self.player = self.rt.first("player")
        self.enemies = self.rt.startswith("enemy")


s.run(scene=LevelScene, size=(800, 600))
```

### Два пайплайна доступа к объектам

Путь к сцене резолвится как у картинок: можно передать голое имя (расширение `.json` необязательно) — файл ищется рядом со скриптом, в `scenes/` и `assets/`, затем от рабочей папки. При неудаче — `FileNotFoundError` со списком проверенных путей.

```python
rt = s.spawn_scene("main_level", scene=self)   # найдёт scenes/main_level.json
rt = s.spawn_scene("scene.json", scene=self)   # топ-левел алиас

# 1) Как есть — параметры из редактора не переопределяются
btn = rt.get("play_btn")            # объект или None
btn = rt["play_btn"]                # то же, но KeyError с подсказкой имён
label = rt.TextSprite("label")      # текст/шрифт/цвет — из редактора

# 2) С переопределением — меняется ТОЛЬКО явно переданное
btn = rt.Button("play_btn", on_click=start)      # текст/цвета из редактора
rt.on_click("play_btn", start)                   # шорткат для кнопок
label = rt.TextSprite("label", text="Changed")   # font_size/color из редактора
spr = rt.Sprite("panel", speed=5)

# Обход и проверка
"play_btn" in rt        # True
rt.names()              # список имён объектов сцены
for spawned in rt: ...  # итерация по объектам
```

### Превращение в UI-компоненты (legacy)

```python
# Спрайт → кнопка
btn = rt.exact("button").to_button(text="Click", on_click=callback)

# Спрайт → текст
label = rt.exact("label").to_text_sprite(text="Hello", font_size=32)

# Спрайт → переключатель
toggle = rt.exact("toggle").to_toggle(text_on="ON", text_off="OFF")
```

### Физика из редактора

Если в Inspector у объекта выставлен тип Physics (Static/Kinematic/Dynamic), при загрузке через `spawn_scene` тело создаётся автоматически. Настройки: Mass, Friction, Bounce.

## Экспорт сцены из кода

```python
from spritePro.editor.scene import Scene as EditorScene

# Экспорт: код → JSON → редактор
EditorScene.export_from_runtime(MyScene, "scene_a.json")
```

Полный цикл: `spritePro/demoGames/scenes_demo editor.py`

## Формат JSON

```json
{
    "version": "1.0",
    "name": "My Scene",
    "objects": [
        {
            "id": "abc12345",
            "name": "Player",
            "sprite_path": "assets/player.png",
            "sprite_shape": "image",
            "transform": {"x": 100.0, "y": 200.0, "rotation": 0.0, "scale_x": 1.0, "scale_y": 1.0},
            "z_index": 10,
            "active": true,
            "parent": null,
            "custom_data": {}
        }
    ]
}
```

## Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| V | Select |
| G | Move |
| R | Rotate |
| T | Scale |
| F1 | Settings |
| Ctrl+Z | Отменить |
| Ctrl+Y | Повторить |
| Ctrl+S | Сохранить |
| Ctrl+C / Ctrl+V | Копировать / вставить (со смещением) |
| Ctrl+D | Дублировать |
| Ctrl+Shift+B | Новая кнопка |
| F5 | Запустить игру |

## Демо

```bash
python -m spritePro.demoGames.platformer_demo
python -m spritePro.demoGames.editor_scene_runtime_demo
```
