# Kivy Hybrid

Гибридный режим: Kivy UI (меню, кнопки) + SpritePro игровая область.

## Вариант 1: Full-screen

```python
s.run(scene=MainScene, platform="kivy")
```

## Вариант 2: Hybrid с header

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
    
    header = BoxLayout(size_hint_y=None, height=56)
    back_button = Button(text="Back", size_hint_x=None, width=120)
    title = Label(text="Hybrid Kivy + SpritePro")
    
    def stop_app(*_args):
        App.get_running_app().stop()
    
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
)
```

## Вариант 3: Свой Kivy App

```python
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

import spritePro as s


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (100, 100), s.WH_C, scene=self)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn = Button(text="Start Game")
        btn.bind(on_release=lambda *_: setattr(self.manager, "current", "game"))
        self.add_widget(btn)


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        back_btn = Button(text="Back", size_hint_y=None, height=56)
        back_btn.bind(on_release=lambda *_: setattr(self.manager, "current", "menu"))
        
        game_widget = s.create_kivy_widget(scene=MainScene, fill_color=(20, 20, 30))
        
        root.add_widget(back_btn)
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

## Что использовать

| Сценарий | Функция |
|----------|---------|
| Простой mobile | `s.run(..., platform="kivy")` |
| Kivy header + игра | `s.run_kivy_hybrid(...)` |
| Свой Kivy App | `s.create_kivy_widget(...)` |

## Поведение размеров

В hybrid-режиме `s.WH` и `s.WH_C` соответствуют размеру игрового виджета, не всего окна.

При resize `s.WH`/`s.WH_C` обновляются, но уже созданные объекты не перепозиционируются автоматически.

## Сборка APK

```bash
python -m spritePro.cli --android .
```

## Демо

```bash
python spritePro/demoGames/kivy_hybrid_demo.py
```
