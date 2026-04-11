# SpritePro

Высокоуровневый 2D game framework на Python (поверх pygame). Desktop, web и mobile из одной кодовой базы.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Open%20Source-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.8.0-green.svg)](CHANGELOG.md)

![Demo](https://github.com/user-attachments/assets/db56e1fd-0db5-4353-945d-c4a31c6b9d7f)

---

## Установка

```bash
pip install spritepro
```

Для mobile: `pip install "spritepro[kivy]"`

Шаблон проекта: `python -m spritePro.cli --create`

### Обновление

```bash
pip install --upgrade spritepro
```

---

## Почему SpritePro

| Обычно приходится | В SpritePro |
|-------------------|-------------|
| Ручной игровой цикл | `s.run(scene=...)` — сцена + auto-render |
| Своя камера | Camera API, follow, zoom, shake |
| UI с нуля | `Button`, `ToggleButton`, `TextSprite`, `Slider`, `TextInput`, `Layout` |
| Физика отдельно | `pymunk`-интеграция, типы тел, коллизии |
| Визуальный editor | Sprite Editor → JSON → `spawn_scene(...)` |
| Сохранения парсить | `PlayerPrefs` → JSON |
| Мультиплеер с нуля | TCP, лобби, ChatScene, синхронизация |
| Mobile отдельно | `platform="kivy"` — та же логика |
| Скроллируемый UI | `ScrollView` + `ClipMask` — готовый клиппинг |

**SpritePro = pygame + физика, Layout, ScrollView, ClipMask, редактор сцен, мультиплеер, UI.**

---

## Быстрый старт

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

Всё: окно, сцена, игровой цикл, управление.

---

## Что внутри

- **Sprite** — базовый класс с движением, эффектами, иерархией parent-child
- **UI**: Button, ToggleButton, Slider, TextInput, TextSprite, Layout (flex/grid/circle/line)
- **ClipMask** — маска обрезки для viewport, инвентарей, чатов
- **ScrollView** — скроллируемый контент с колёсиком и drag-and-drop
- **Физика**: pymunk, DYNAMIC/STATIC/KINEMATIC тела, коллизии
- **Анимации**: Tween, Fluent API (`DoMove`, `DoScale`, `SetEase`...)
- **Частицы**: ParticleEmitter, шаблоны, пулы
- **Мультиплеер**: TCP, лобби, ChatScene, синхронизация
- **Audio**: звук и музыка
- **Save/Load**: PlayerPrefs в JSON
- **Sprite Editor**: визуальная сборка сцен → JSON

---

## Sprite Editor

Визуальный редактор сцен с иерархией, инспектором, gizmo.

<img width="800" alt="Sprite Editor" src="https://github.com/user-attachments/assets/01947bfe-d5e6-40cb-ba75-c03f2d4aeb9d" />

```
python -m spritePro.cli --editor
```

Собираете сцену → сохраняете в JSON → загружаете в игре:

```python
rt = spawn_scene("level.json", scene=self)
player = rt.exact("player").Sprite(speed=5)
```

---

## Мультиплеерный чат

Готовая сцена чата с маской обрезки и скроллом:

```python
from spritePro.readyScenes import ChatScene, ChatStyle
import spritePro as s

s.run(scene=ChatScene, multiplayer=True, use_lobby=True, title="Chat")
```

---

## Сравнение

| Функция | pygame | arcade | SpritePro |
|---------|--------|--------|-----------|
| Авто-рендер | ❌ | ✅ | ✅ |
| Готовая камера | ❌ | ✅ | ✅ |
| Физика (pymunk) | ❌ | ✅ | ✅ |
| Layout (flex/grid) | ❌ | ❌ | ✅ |
| Редактор сцен (JSON) | ❌ | ❌ | ✅ |
| Маска обрезки / ScrollView | ❌ | ❌ | ✅ |
| Мультиплеер (TCP) | ❌ | ❌ | ✅ |
| PlayerPrefs | ❌ | ❌ | ✅ |

---

## Что создать

- Платформеры, аркады, RPG
- Пазлы, tower defense
- Мультиплеерные игры
- Мобильные игры (`platform="kivy"`)

---

## Демо-игры

```bash
python -m spritePro.demoGames.physics_demo       # физика
python -m spritePro.demoGames.fluent_tween_demo   # твины
python -m spritePro.demoGames.layout_demo         # лейауты
python -m spritePro.demoGames.local_multiplayer_demo --quick
```

[Все 54 демо](docs/demo_games/demo_games.md)

---

## Mobile и Web

```python
s.run(scene=MainScene, platform="kivy")  # Android/iOS
```

```bash
python -m spritePro.cli --android . --android-orientation portrait
```

Web: [docs/builds/building_web.md](docs/builds/building_web.md)

---

## Документация

| Что | Где |
|-----|-----|
| Полный индекс | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| API Reference | [docs/API_REFERENCE.md](docs/API_REFERENCE.md) |
| Для новичков | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Физика | [docs/core/physics_guide.md](docs/core/physics_guide.md) |
| UI/Layout | [docs/ui/layout_ui.md](docs/ui/layout_ui.md) |
| ClipMask | [docs/ui/clip_mask.md](docs/ui/clip_mask.md) |
| Мультиплеер | [docs/systems/networking_guide.md](docs/systems/networking_guide.md) |
| Sprite Editor | [docs/editor/sprite_editor.md](docs/editor/sprite_editor.md) |
| Mobile | [docs/builds/mobile_kivy.md](docs/builds/mobile_kivy.md) |

---

## Вклад

- [CONTRIBUTING.md](CONTRIBUTING.md) — как внести вклад
- [ROADMAP.md](ROADMAP.md) — планы развития
- [CHANGELOG.md](CHANGELOG.md) — история изменений

---

[📖 Документация](DOCUMENTATION_INDEX.md) · [💬 GitHub Issues](https://github.com/NeoXider/SpritePro/issues)
