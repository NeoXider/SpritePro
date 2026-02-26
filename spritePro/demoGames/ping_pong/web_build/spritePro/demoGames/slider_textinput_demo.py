"""Демо Slider и TextInput на базе SpritePro."""

from __future__ import annotations

import spritePro as s


class SliderTextInputDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        W, H = s.WH.x, s.WH.y
        cx = W // 2

        self._slider_value = 0.5
        self._text_value = ""

        self.slider = s.Slider(
            size=(280, 16),
            pos=(cx, H // 2 - 60),
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            on_change=self._on_slider_change,
            scene=self,
            sorting_order=1000,
        )

        self.text_input = s.TextInput(
            size=(280, 36),
            pos=(cx, H // 2),
            placeholder="Введите текст...",
            value="",
            max_length=64,
            on_change=self._on_text_change,
            on_submit=self._on_text_submit,
            scene=self,
            sorting_order=1000,
        )

        self.label_slider = s.TextSprite(
            f"Slider: {self._slider_value:.2f}",
            font_size=18,
            color=(200, 200, 200),
            pos=(cx, H // 2 - 100),
            scene=self,
            sorting_order=1001,
        )

        self.label_text = s.TextSprite(
            "TextInput: —",
            font_size=18,
            color=(200, 200, 200),
            pos=(cx, H // 2 + 50),
            scene=self,
            sorting_order=1001,
        )

    def _on_slider_change(self, value: float) -> None:
        self._slider_value = value
        self.label_slider.set_text(f"Slider: {value:.2f}")

    def _on_text_change(self, value: str) -> None:
        self._text_value = value
        self.label_text.set_text(f"TextInput: {value or '—'}")

    def _on_text_submit(self, value: str) -> None:
        self.label_text.set_text(f"Submitted: {value}")


def run_demo() -> None:
    s.get_screen((600, 400), "Slider & TextInput Demo")
    s.set_scene(SliderTextInputDemoScene())
    while True:
        s.update(fill_color=(30, 30, 38))


if __name__ == "__main__":
    run_demo()
