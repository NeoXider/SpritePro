# Hybrid Kivy + SpritePro

Этот режим нужен, когда:

- меню, навигация, верхняя панель и системный UI хочется делать на `Kivy`
- сама игра должна жить внутри отдельной области или виджета
- над игрой нужны обычные `Kivy`-кнопки, например `Back`, `Pause`, `Settings`

Если hybrid не нужен, используйте обычный full-screen запуск:

```python
s.run(scene=MainScene, platform="kivy")
```

Это по-прежнему основной и самый простой путь.

---

## Что есть сейчас

В SpritePro теперь есть два сценария работы с `Kivy`:

1. **Full-screen Kivy host**
   Игра занимает всё окно приложения. Это текущий режим по умолчанию.

2. **Hybrid Kivy UI + SpritePro game widget**
   У вас есть обычный `Kivy`-интерфейс, а внутри layout живёт встроенная игровая область SpritePro.

---

## Вариант 1. Full-screen Kivy

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (90, 90), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

s.run(
    scene=MainScene,
    title="My Game",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

Когда выбирать этот вариант:

- вся игра целиком должна быть на экране без внешнего UI
- нужен самый короткий и понятный запуск
- вы делаете обычную mobile-игру без сложной `Kivy`-обвязки

---

## Вариант 2. Hybrid через `s.run_kivy_hybrid(...)`

Это самый удобный high-level способ для гибридного интерфейса.

Идея:

- SpritePro создаёт встроенный игровой виджет
- вы получаете его в `root_builder(game_widget)`
- собираете вокруг него любой `Kivy` layout

### Минимальный пример

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import spritePro as s


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (90, 90), s.WH_C, scene=self)
        self.player.set_rect_shape((90, 90), (90, 210, 255), border_radius=24)

    def update(self, dt):
        if s.input.is_mouse_pressed(1):
            self.player.set_position(s.input.mouse_pos)


def build_root(game_widget):
    root = BoxLayout(orientation="vertical", spacing=8, padding=8)

    header = BoxLayout(size_hint_y=None, height=56, spacing=8)
    back_button = Button(text="Back", size_hint_x=None, width=120)
    title = Label(text="Hybrid Kivy + SpritePro")

    def stop_app(*_args):
        app = App.get_running_app()
        if app is not None:
            app.stop()

    back_button.bind(on_release=stop_app)
    header.add_widget(back_button)
    header.add_widget(title)

    root.add_widget(header)
    root.add_widget(game_widget)
    return root


s.run_kivy_hybrid(
    scene=MainScene,
    root_builder=build_root,
    size=(1000, 700),
    title="Hybrid Demo",
    fill_color=(20, 20, 30),
)
```

Что здесь происходит:

- верхняя панель полностью сделана на `Kivy`
- кнопка `Back` тоже обычная `Kivy Button`
- сама игра рендерится в `game_widget`
- touch/mouse внутри `game_widget` попадает в `SpritePro`

---

## Вариант 3. Полностью свой Kivy App через `s.create_kivy_widget(...)`

Если вы хотите полностью контролировать `App`, `ScreenManager`, переходы экранов и свою архитектуру, создавайте игровой виджет вручную.

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager

import spritePro as s


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (100, 100), s.WH_C, scene=self)
        self.player.set_rect_shape((100, 100), (255, 180, 90), border_radius=24)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        button = Button(text="Start Game")
        button.bind(on_release=self._start_game)
        self.add_widget(button)

    def _start_game(self, *_args):
        self.manager.current = "game"


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")

        back_button = Button(text="Back", size_hint_y=None, height=56)
        back_button.bind(on_release=lambda *_: setattr(self.manager, "current", "menu"))

        game_widget = s.create_kivy_widget(
            scene=MainScene,
            fps=60,
            fill_color=(20, 20, 30),
        )

        root.add_widget(back_button)
        root.add_widget(game_widget)
        self.add_widget(root)


class HybridApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        return sm


HybridApp().run()
```

Этот вариант нужен, если:

- у вас много экранов на `Kivy`
- вы хотите свой `ScreenManager`
- логика приложения живёт в `Kivy`, а SpritePro отвечает только за игровую область

---

## Как работают `s.input` и `s.events`

В hybrid-режиме SpritePro получает события только из своей игровой области.

Это удобно и правильно:

- нажатия внутри `game_widget` попадают в `SpritePro`
- кнопки `Kivy`, расположенные снаружи игрового виджета, не мешают игре
- верхняя панель на `Kivy` остаётся полностью независимой

Что работает автоматически:

- `s.input.mouse_pos`
- `s.input.is_mouse_pressed(...)`
- `s.input.was_mouse_pressed(...)`
- `s.input.was_mouse_released(...)`
- `s.events` для мышиных/touch-событий внутри игровой области

Практически это означает, что touch внутри `Kivy` game-widget ведёт себя для SpritePro как мышь.

---

## Поведение размеров

Размер игровой области в hybrid-режиме зависит от размера самого `game_widget`.

То есть:

- `s.WH`
- `s.WH_C`
- привязка UI в screen space

будут соответствовать размеру встроенного игрового виджета, а не всему окну приложения.

Это именно то поведение, которое нужно для embedded-игры.

Важно понимать нюанс resize:

- при изменении размера `game_widget` значения `s.WH` и `s.WH_C` тоже обновляются
- но уже созданные объекты не перепозиционируются автоматически
- если вы один раз поставили спрайт в `__init__` через `s.WH_C`, он не "переедет" сам после следующего resize
- для truly adaptive layout пересчитывайте позиции/размеры от текущих `s.WH` и `s.WH_C`

---

## Что лучше использовать

### Используйте обычный `s.run(..., platform="kivy")`, если:

- нужен просто mobile launch
- игра занимает весь экран
- не нужен внешний `Kivy`-UI

### Используйте `s.run_kivy_hybrid(...)`, если:

- нужен `Kivy`-header, `Back`, `Pause`, системные кнопки
- хочется простой hybrid без собственного `App`
- нужен один игровой виджет внутри общего layout

### Используйте `s.create_kivy_widget(...)`, если:

- у вас уже есть своё `Kivy`-приложение
- вы строите `ScreenManager`, меню и навигацию сами
- SpritePro должен быть только частью интерфейса

---

## Ограничения и рекомендации

- В одном приложении предполагается **один активный SpritePro game widget**.
- `SpritePro` остаётся единым runtime, поэтому не стоит одновременно создавать несколько независимых игровых областей.
- Для мобильного управления лучше делать крупные hitbox и экранные кнопки.
- Если нужен сложный HUD поверх игры, сначала решите, где ему лучше жить:
  либо в самом SpritePro, либо в внешнем `Kivy` UI.

---

## Сборка APK для hybrid-режима

Для Android hybrid-режим собирается так же, как и обычный `Kivy` full-screen запуск. Отдельного special-case здесь нет: упаковщик смотрит только на ваш `main.py`.

Если в `main.py` используется:

- `s.run(..., platform="kivy")`
- `s.run_kivy_hybrid(...)`
- `s.create_kivy_widget(...)` внутри собственного `Kivy App`

то общий Android flow остаётся тем же.

### Быстро через CLI

```bash
python -m spritePro.cli --android .
python -m spritePro.cli --android . --android-mode release
python -m spritePro.cli --android . --android-permission INTERNET
```

### Напрямую через Buildozer

```bash
buildozer init
buildozer android debug
```

После `buildozer init` для `SpritePro`/`pygame` hybrid-приложения сразу проверьте `buildozer.spec` и выставьте проверенную конфигурацию:

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

Если hybrid-приложение использует локальные непубликованные фиксы `SpritePro`, проследите, чтобы в APK попал именно свежий код библиотеки:

- либо упаковывайте уже обновлённый локальный пакет
- либо явно синхронизируйте папку `spritePro/` в проект игры перед Android build

Если hybrid-приложение использует сеть, не забудьте добавить:

```ini
android.permissions = INTERNET
```

Если у вас в интерфейсе есть внешние `Kivy`-экраны и встроенный игровой виджет, перед сборкой особенно полезно проверить:

- что layout не ломается на portrait/landscape
- что `game_widget` получает ожидаемый размер
- что `s.WH` и `s.WH_C` внутри игровой области совпадают с ожиданиями
- что внешние `Kivy`-кнопки и внутриигровой touch не конфликтуют

Если после установки APK hybrid-приложение доходит только до splash screen или экрана ошибки, снимите `adb logcat` сразу после запуска. Для hybrid-режима это особенно полезно, потому что проблема может быть не в `Kivy` layout, а в обычном Python traceback внутри SpritePro runtime.

Подробный общий гайд по Android-сборке: [building.md](building.md)

---

## Готовый demo

В репозитории есть пример:

```bash
python spritePro/demoGames/kivy_hybrid_demo.py
```

Он показывает:

- верхнюю панель на `Kivy`
- кнопку `Back`
- встроенную игровую область `SpritePro`

---

## Связанные документы

- [mobile.md](mobile.md)
- [game_loop.md](game_loop.md)
- [building.md](building.md)
