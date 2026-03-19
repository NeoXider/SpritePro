"""Демо hybrid-режима: Kivy UI + встроенная область игры SpritePro.

Запуск:
    python spritePro/demoGames/kivy_hybrid_demo.py

Нужно:
    pip install kivy
"""

from __future__ import annotations

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

from kivy.app import App  # noqa: E402
from kivy.uix.boxlayout import BoxLayout  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.uix.label import Label  # noqa: E402

import spritePro as s  # noqa: E402


class HybridDemoScene(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.player = s.Sprite("", (90, 90), s.WH_C, speed=6, scene=self)
        self.player.set_rect_shape((90, 90), (90, 210, 255), border_radius=24)
        self.info = s.TextSprite(
            "Touch or hold mouse inside game area",
            20,
            (230, 230, 230),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def update(self, dt: float) -> None:
        if s.input.is_mouse_pressed(1):
            self.player.set_position(s.input.mouse_pos)
        self.player.color = s.utils.ColorEffects.rainbow()


def build_root(game_widget):
    root = BoxLayout(orientation="vertical", spacing=8, padding=8)

    header = BoxLayout(size_hint_y=None, height=56, spacing=8)
    back_button = Button(text="Back", size_hint_x=None, width=120)
    title = Label(text="Hybrid Kivy UI + SpritePro Game")

    def stop_app(*_args) -> None:
        app = App.get_running_app()
        if app is not None:
            app.stop()

    back_button.bind(on_release=stop_app)
    header.add_widget(back_button)
    header.add_widget(title)

    root.add_widget(header)
    root.add_widget(game_widget)
    return root


def main() -> None:
    s.run_kivy_hybrid(
        scene=HybridDemoScene,
        root_builder=build_root,
        size=(1000, 700),
        title="SpritePro Hybrid Demo",
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    main()
