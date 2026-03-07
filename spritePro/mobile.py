"""Инструменты для full-screen и hybrid запуска SpritePro в Kivy."""

from __future__ import annotations

import os
from typing import Any, Callable, List, Mapping, Sequence

import pygame

import spritePro as s


def _require_kivy():
    try:
        os.environ.setdefault("KIVY_NO_ARGS", "1")
        from kivy.app import App
        from kivy.clock import Clock
        from kivy.graphics import Rectangle
        from kivy.graphics.texture import Texture
        from kivy.uix.widget import Widget
    except ImportError as exc:
        raise ImportError(
            "Для мобильного режима нужен Kivy. Установите зависимость: pip install kivy"
        ) from exc
    return App, Clock, Rectangle, Texture, Widget


class KivySpriteProWidget:
    """Фабрика Kivy-виджета, который рендерит SpritePro в Texture."""

    @staticmethod
    def create_class():
        App, Clock, Rectangle, Texture, Widget = _require_kivy()

        class _KivySpriteProWidget(Widget):
            def __init__(
                self,
                bootstrap: Callable[[], None] | None = None,
                fps: int = 60,
                fill_color: tuple[int, int, int] = (20, 20, 30),
                **kwargs,
            ):
                super().__init__(**kwargs)
                pygame.init()
                self._bootstrap = bootstrap
                self._bootstrapped = False
                self._fps = fps
                self._fill_color = fill_color
                self._event_queue: List[pygame.event.Event] = []
                self._surface: pygame.Surface | None = None
                self._texture = None
                self._active_touch_id: str | None = None
                self._last_touch_pos: tuple[int, int] | None = None
                self._bootstrap_wait_frames = 0

                with self.canvas:
                    self._rect = Rectangle(pos=self.pos, size=self.size)

                self.bind(pos=self._update_rect, size=self._on_resize)
                Clock.schedule_interval(self._tick, 1.0 / max(1, fps))

            def _update_rect(self, *_args) -> None:
                self._rect.pos = self.pos
                self._rect.size = self.size

            def _on_resize(self, *_args) -> None:
                width = max(1, int(self.width))
                height = max(1, int(self.height))
                if self._surface is not None and self._surface.get_size() == (width, height):
                    self._update_rect()
                    return

                self._surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                s.attach_surface(self._surface)

                self._texture = Texture.create(size=(width, height), colorfmt="rgba")
                self._texture.flip_vertical()
                self._rect.texture = self._texture
                self._update_rect()

                if not self._bootstrapped:
                    # Kivy может прислать несколько resize подряд во время initial layout.
                    # Ждём пару кадров без смены размера, чтобы сцена создавалась уже
                    # с финальными s.WH / s.WH_C, как в pygame-режиме.
                    self._bootstrap_wait_frames = 2

            def _to_local_pos(self, touch) -> tuple[int, int]:
                local_x = int(touch.x - self.x)
                local_y = int(touch.y - self.y)
                clamped_x = max(0, min(int(self.width) - 1, local_x))
                clamped_y = max(0, min(int(self.height) - 1, local_y))
                return (clamped_x, max(0, int(self.height) - 1 - clamped_y))

            def _enqueue_mouse_motion(
                self,
                pos: tuple[int, int],
                rel: tuple[int, int],
                buttons: Sequence[int] = (0, 0, 0),
            ) -> None:
                self._event_queue.append(
                    pygame.event.Event(
                        pygame.MOUSEMOTION,
                        {
                            "pos": pos,
                            "rel": rel,
                            "buttons": tuple(buttons),
                        },
                    )
                )

            def on_touch_down(self, touch):
                if not self.collide_point(*touch.pos):
                    return super().on_touch_down(touch)
                if self._active_touch_id is not None:
                    return True

                pos = self._to_local_pos(touch)
                self._active_touch_id = str(touch.uid)
                self._last_touch_pos = pos
                self._enqueue_mouse_motion(pos, (0, 0), (1, 0, 0))
                self._event_queue.append(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {
                            "button": 1,
                            "pos": pos,
                        },
                    )
                )
                return True

            def on_touch_move(self, touch):
                if str(touch.uid) != self._active_touch_id:
                    return super().on_touch_move(touch)

                pos = self._to_local_pos(touch)
                prev = self._last_touch_pos or pos
                rel = (pos[0] - prev[0], pos[1] - prev[1])
                self._last_touch_pos = pos
                self._enqueue_mouse_motion(pos, rel, (1, 0, 0))
                return True

            def on_touch_up(self, touch):
                if str(touch.uid) != self._active_touch_id:
                    return super().on_touch_up(touch)

                pos = self._to_local_pos(touch)
                prev = self._last_touch_pos or pos
                rel = (pos[0] - prev[0], pos[1] - prev[1])
                self._enqueue_mouse_motion(pos, rel, (0, 0, 0))
                self._event_queue.append(
                    pygame.event.Event(
                        pygame.MOUSEBUTTONUP,
                        {
                            "button": 1,
                            "pos": pos,
                        },
                    )
                )
                self._active_touch_id = None
                self._last_touch_pos = None
                return True

            def _tick(self, _dt: float) -> None:
                if self._surface is None:
                    self._on_resize()
                if self._surface is None or self._texture is None:
                    return
                if not self._bootstrapped:
                    if self._bootstrap_wait_frames > 0:
                        self._bootstrap_wait_frames -= 1
                        return
                    self._bootstrapped = True
                    if self._bootstrap is not None:
                        self._bootstrap()
                    return

                events = self._event_queue
                self._event_queue = []
                s.update_embedded(self._fps, self._fill_color, events)

                buffer = pygame.image.tostring(self._surface, "RGBA")
                self._texture.blit_buffer(buffer, colorfmt="rgba", bufferfmt="ubyte")
                self.canvas.ask_update()

        return _KivySpriteProWidget, App

    @staticmethod
    def create_widget(
        *,
        bootstrap: Callable[[], None] | None = None,
        fps: int = 60,
        fill_color: tuple[int, int, int] = (20, 20, 30),
        **widget_kwargs: Any,
    ):
        """Создаёт экземпляр Kivy-виджета со встроенной игрой SpritePro."""
        widget_cls, _ = KivySpriteProWidget.create_class()
        return widget_cls(bootstrap=bootstrap, fps=fps, fill_color=fill_color, **widget_kwargs)


def create_kivy_widget(
    bootstrap: Callable[[], None] | None = None,
    *,
    fps: int = 60,
    fill_color: tuple[int, int, int] = (20, 20, 30),
    **widget_kwargs: Any,
):
    """Публичный helper для создания SpritePro-виджета внутри Kivy layout."""
    return KivySpriteProWidget.create_widget(
        bootstrap=bootstrap,
        fps=fps,
        fill_color=fill_color,
        **widget_kwargs,
    )


def run_kivy_app(
    bootstrap: Callable[[], None],
    *,
    title: str = "SpritePro Mobile",
    fps: int = 60,
    fill_color: tuple[int, int, int] = (20, 20, 30),
    window_size: tuple[int, int] | None = None,
    root_builder: Callable[[object], object] | None = None,
    widget_kwargs: Mapping[str, Any] | None = None,
):
    """Запускает SpritePro внутри Kivy-приложения.

    По умолчанию весь root приложения — это игровая область SpritePro.
    Для hybrid-режима можно передать `root_builder(game_widget)`, который
    построит ваш Kivy-интерфейс вокруг встроенного игрового виджета.
    """
    _, App = KivySpriteProWidget.create_class()
    if window_size is not None:
        from kivy.core.window import Window

        Window.size = tuple(int(v) for v in window_size)

    class _SpriteProMobileApp(App):
        def build(self):
            self.title = title
            game_widget = create_kivy_widget(
                bootstrap,
                fps=fps,
                fill_color=fill_color,
                **dict(widget_kwargs or {}),
            )
            if root_builder is None:
                return game_widget
            return root_builder(game_widget)

    _SpriteProMobileApp().run()
