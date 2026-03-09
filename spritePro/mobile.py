"""Инструменты для full-screen и hybrid запуска SpritePro в Kivy."""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Any, Callable, List, Mapping, Sequence

import pygame

import spritePro as s

_MAX_MOBILE_RENDER_LONGEST_SIDE = 1920
_MAX_MOBILE_REFERENCE_RENDER_LONGEST_SIDE = 1920


def _write_mobile_crash_log(text: str) -> None:
    candidates = [
        Path.cwd() / "debug.log",
        Path.cwd() / "spritepro_mobile_crash.log",
        Path.cwd() / "android_error.log",
    ]
    for path in candidates:
        try:
            path.write_text(text, encoding="utf-8")
            break
        except OSError:
            continue


def _format_mobile_exception(exc: BaseException) -> str:
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).strip()


def _is_android_runtime() -> bool:
    return bool(os.environ.get("ANDROID_ARGUMENT") or os.environ.get("P4A_BOOTSTRAP"))


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
            'Для мобильного режима нужен Kivy. Установите зависимость: pip install "spritepro[kivy]"'
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
                reference_size: tuple[int, int] | None = None,
                fps: int = 60,
                fill_color: tuple[int, int, int] = (20, 20, 30),
                **kwargs,
            ):
                super().__init__(**kwargs)
                try:
                    if not pygame.font.get_init():
                        pygame.font.init()
                except Exception:
                    pass
                self._bootstrap = bootstrap
                self._reference_size = reference_size
                self._bootstrapped = False
                self._fps = fps
                self._fill_color = fill_color
                self._event_queue: List[pygame.event.Event] = []
                self._dispatch_event_queue: List[pygame.event.Event] = []
                self._surface: pygame.Surface | None = None
                self._texture = None
                self._active_touch_id: str | None = None
                self._last_touch_pos: tuple[int, int] | None = None
                self._bootstrap_wait_frames = 0
                self._keyboard = None
                self._fatal_error: str | None = None

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
                surface_size = self._calculate_surface_size(width, height)
                if self._surface is not None and self._surface.get_size() == surface_size:
                    self._update_rect()
                    return

                self._surface = pygame.Surface(surface_size, 0, 24)
                s.attach_surface(self._surface, reference_size=self._reference_size)

                self._texture = Texture.create(size=surface_size, colorfmt="rgb")
                self._texture.flip_vertical()
                self._rect.texture = self._texture
                self._update_rect()

                if not self._bootstrapped:
                    # Kivy может прислать несколько resize подряд во время initial layout.
                    # Ждём пару кадров без смены размера, чтобы сцена создавалась уже
                    # с финальными s.WH / s.WH_C, как в pygame-режиме.
                    self._bootstrap_wait_frames = 2

            def _calculate_surface_size(self, width: int, height: int) -> tuple[int, int]:
                limit = (
                    _MAX_MOBILE_REFERENCE_RENDER_LONGEST_SIDE
                    if self._reference_size is not None
                    else _MAX_MOBILE_RENDER_LONGEST_SIDE
                )
                longest_side = max(width, height)
                if longest_side <= limit:
                    return (width, height)
                scale = limit / float(longest_side)
                return (
                    max(1, int(round(width * scale))),
                    max(1, int(round(height * scale))),
                )

            def _to_local_pos(self, touch) -> tuple[int, int]:
                surface_w = max(1, self._surface.get_width() if self._surface is not None else int(self.width))
                surface_h = max(1, self._surface.get_height() if self._surface is not None else int(self.height))
                widget_w = max(1, int(self.width))
                widget_h = max(1, int(self.height))
                local_x = int(touch.x - self.x)
                local_y = int(touch.y - self.y)
                mapped_x = int(round(local_x * surface_w / widget_w))
                mapped_y = int(round(local_y * surface_h / widget_h))
                clamped_x = max(0, min(surface_w - 1, mapped_x))
                clamped_y = max(0, min(surface_h - 1, mapped_y))
                return (clamped_x, max(0, surface_h - 1 - clamped_y))

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

            def _present_surface(self) -> None:
                if self._surface is None or self._texture is None:
                    return
                buffer = pygame.image.tostring(self._surface, "RGB")
                self._texture.blit_buffer(buffer, colorfmt="rgb", bufferfmt="ubyte")
                self.canvas.ask_update()

            def _set_fatal_error(self, exc: BaseException) -> None:
                self._fatal_error = _format_mobile_exception(exc)
                _write_mobile_crash_log(self._fatal_error)
                print(self._fatal_error, flush=True)

            def _draw_fatal_error(self) -> None:
                if self._surface is None:
                    return
                self._surface.fill((12, 12, 18))
                try:
                    if not pygame.font.get_init():
                        pygame.font.init()
                    title_font = pygame.font.Font(None, 36)
                    text_font = pygame.font.Font(None, 22)
                except Exception:
                    self._present_surface()
                    return

                y = 18
                title = title_font.render("SpritePro mobile error", True, (255, 120, 120))
                self._surface.blit(title, (18, y))
                y += 42

                hint = text_font.render(
                    "Logs saved to debug.log / spritepro_mobile_crash.log", True, (220, 220, 220)
                )
                self._surface.blit(hint, (18, y))
                y += 32

                for line in (self._fatal_error or "").splitlines()[:14]:
                    rendered = text_font.render(line[:110], True, (235, 235, 235))
                    self._surface.blit(rendered, (18, y))
                    y += 22

                self._present_surface()

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

            def _map_kivy_key_to_pygame(self, keycode, modifiers) -> tuple[int, int]:
                key_value, key_name = keycode
                name = (key_name or "").lower()
                mapping = {
                    "enter": pygame.K_RETURN,
                    "return": pygame.K_RETURN,
                    "kp_enter": pygame.K_RETURN,
                    "backspace": pygame.K_BACKSPACE,
                    "escape": pygame.K_ESCAPE,
                    "esc": pygame.K_ESCAPE,
                    "space": pygame.K_SPACE,
                    "spacebar": pygame.K_SPACE,
                }
                if name in mapping:
                    pg_key = mapping[name]
                elif len(name) == 1:
                    attr_name = f"K_{name}"
                    pg_key = getattr(pygame, attr_name, key_value)
                else:
                    pg_key = key_value

                mod = 0
                if "shift" in modifiers:
                    mod |= pygame.KMOD_SHIFT
                if "ctrl" in modifiers or "control" in modifiers:
                    mod |= pygame.KMOD_CTRL
                if "alt" in modifiers:
                    mod |= pygame.KMOD_ALT
                if "meta" in modifiers or "cmd" in modifiers or "super" in modifiers:
                    mod |= pygame.KMOD_META
                return pg_key, mod

            def _open_soft_keyboard(self) -> None:
                if self._keyboard is not None:
                    return
                try:
                    from kivy.core.window import Window
                except Exception:
                    return
                keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
                if keyboard is None:
                    return
                self._keyboard = keyboard
                try:
                    self._keyboard.bind(
                        on_key_down=self._on_key_down,
                        on_textinput=self._on_textinput,
                    )
                except Exception:
                    self._keyboard = None

            def _close_soft_keyboard(self) -> None:
                kb = self._keyboard
                if kb is None:
                    return
                try:
                    kb.unbind(on_key_down=self._on_key_down, on_textinput=self._on_textinput)
                except Exception:
                    pass
                try:
                    kb.release()
                except Exception:
                    pass
                self._keyboard = None

            def _on_keyboard_closed(self, *_args) -> None:
                self._keyboard = None

            def _on_key_down(self, keyboard, keycode, text, modifiers):
                pg_key, pg_mod = self._map_kivy_key_to_pygame(keycode, modifiers or [])
                event = pygame.event.Event(
                    pygame.KEYDOWN,
                    {
                        "key": pg_key,
                        "mod": pg_mod,
                        "unicode": text or "",
                    },
                )
                self._event_queue.append(event)
                return True

            def _on_textinput(self, keyboard, text: str):
                if not text:
                    return False
                event = pygame.event.Event(
                    pygame.TEXTINPUT,
                    {
                        "text": text,
                    },
                )
                self._event_queue.append(event)
                return True

            def _sync_soft_keyboard_state(self) -> None:
                try:
                    active_inputs = [
                        ti
                        for ti in s.get_sprites_by_class(s.TextInput, active_only=True)
                        if getattr(ti, "is_active", False)
                    ]
                except Exception:
                    active_inputs = []

                if active_inputs and self._keyboard is None:
                    self._open_soft_keyboard()
                elif not active_inputs and self._keyboard is not None:
                    self._close_soft_keyboard()

            def _tick(self, _dt: float) -> None:
                if self._surface is None:
                    self._on_resize()
                if self._surface is None or self._texture is None:
                    return
                if self._fatal_error is not None:
                    self._draw_fatal_error()
                    return
                if not self._bootstrapped:
                    if self._bootstrap_wait_frames > 0:
                        self._bootstrap_wait_frames -= 1
                        return
                    self._bootstrapped = True
                    if self._bootstrap is not None:
                        try:
                            self._bootstrap()
                        except Exception as exc:
                            self._set_fatal_error(exc)
                            self._draw_fatal_error()
                    return

                events = self._event_queue
                self._event_queue = self._dispatch_event_queue
                self._event_queue.clear()
                self._dispatch_event_queue = events
                try:
                    s.update_embedded(self._fps, self._fill_color, events)
                except Exception as exc:
                    self._set_fatal_error(exc)
                    self._draw_fatal_error()
                    return

                self._sync_soft_keyboard_state()

                self._present_surface()

        return _KivySpriteProWidget, App

    @staticmethod
    def create_widget(
        *,
        bootstrap: Callable[[], None] | None = None,
        reference_size: tuple[int, int] | None = None,
        fps: int = 60,
        fill_color: tuple[int, int, int] = (20, 20, 30),
        **widget_kwargs: Any,
    ):
        """Создаёт экземпляр Kivy-виджета со встроенной игрой SpritePro."""
        widget_cls, _ = KivySpriteProWidget.create_class()
        return widget_cls(
            bootstrap=bootstrap,
            reference_size=reference_size,
            fps=fps,
            fill_color=fill_color,
            **widget_kwargs,
        )


def create_kivy_widget(
    bootstrap: Callable[[], None] | None = None,
    *,
    reference_size: tuple[int, int] | None = None,
    fps: int = 60,
    fill_color: tuple[int, int, int] = (20, 20, 30),
    **widget_kwargs: Any,
):
    """Публичный helper для создания SpritePro-виджета внутри Kivy layout."""
    return KivySpriteProWidget.create_widget(
        bootstrap=bootstrap,
        reference_size=reference_size,
        fps=fps,
        fill_color=fill_color,
        **widget_kwargs,
    )


def run_kivy_app(
    bootstrap: Callable[[], None],
    *,
    title: str = "SpritePro Mobile",
    reference_size: tuple[int, int] | None = None,
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
    from kivy.core.window import Window

    if _is_android_runtime():
        try:
            Window.fullscreen = "auto"
        except Exception:
            pass
    elif window_size is not None:
        Window.size = tuple(int(v) for v in window_size)

    class _SpriteProMobileApp(App):
        def build(self):
            self.title = title
            resolved_widget_kwargs = dict(widget_kwargs or {})
            resolved_widget_kwargs.setdefault("size_hint", (1, 1))
            game_widget = create_kivy_widget(
                bootstrap,
                reference_size=reference_size,
                fps=fps,
                fill_color=fill_color,
                **resolved_widget_kwargs,
            )
            if root_builder is None:
                return game_widget
            return root_builder(game_widget)

    _SpriteProMobileApp().run()
