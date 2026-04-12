from __future__ import annotations

from typing import List, Tuple
import os
import time

import pygame
from pygame.math import Vector2

from .spriteProGame import SpriteProGame
from .input import InputState
from .event_bus import EventBus, GlobalEvents
from .resources import resource_cache
from .scenes import SceneManager
from .plugins import get_plugin_manager


DEFAULT_CAMERA_KEYS = {
    "left": (pygame.K_LEFT,),
    "right": (pygame.K_RIGHT,),
    "up": (pygame.K_UP,),
    "down": (pygame.K_DOWN,),
}

WINDOW_RESIZE_EVENT_TYPES = tuple(
    event_type
    for event_type in (
        getattr(pygame, "VIDEORESIZE", None),
        getattr(pygame, "WINDOWRESIZED", None),
        getattr(pygame, "WINDOWSIZECHANGED", None),
    )
    if event_type is not None
)


class CameraController:
    """Управление камерой и следованием."""

    def __init__(self, game: SpriteProGame) -> None:
        """Инициализирует контроллер камеры."""
        self._game = game

    def set_position(self, x: float, y: float) -> None:
        """Устанавливает позицию камеры."""
        self._game.set_camera((x, y))

    def move(self, dx: float, dy: float) -> None:
        """Смещает камеру на заданный вектор."""
        self._game.move_camera(dx, dy)

    def get_position(self) -> Vector2:
        """Возвращает текущую позицию камеры."""
        camera = self._game.get_camera()
        return Vector2(camera.x, camera.y)

    def follow(self, target, offset: Vector2 | Tuple[float, float] = (0.0, 0.0)) -> None:
        """Включает слежение камеры за целью."""
        self._game.set_camera_follow(target, offset)

    def clear_follow(self) -> None:
        """Отключает слежение камеры за целью."""
        self._game.clear_camera_follow()

    @staticmethod
    def _normalize_camera_keys(custom: dict | None) -> dict[str, Tuple[int, ...]]:
        """Нормализует словарь клавиш управления камерой."""
        mapping: dict[str, Tuple[int, ...]] = {
            direction: tuple(keys) for direction, keys in DEFAULT_CAMERA_KEYS.items()
        }
        if not custom:
            return mapping
        for direction, value in custom.items():
            if direction not in mapping:
                continue
            if value is None:
                mapping[direction] = ()
                continue
            if isinstance(value, int):
                mapping[direction] = (value,)
                continue
            try:
                filtered = tuple(key for key in value if isinstance(key, int))
            except TypeError:
                continue
            else:
                mapping[direction] = filtered
        return mapping

    def process_input(
        self,
        input_state: InputState,
        dt: float,
        speed: float = 250.0,
        keys: dict | None = None,
        mouse_drag: bool = True,
        mouse_button: int = 1,
    ) -> Vector2:
        """Обрабатывает ввод и перемещает камеру."""
        mapping = self._normalize_camera_keys(keys)
        move = Vector2()

        def handle(direction: str, offset: Vector2) -> None:
            """Обрабатывает движение камеры по одной оси."""
            for key in mapping.get(direction, ()):
                if input_state.is_pressed(key):
                    move.x += offset.x
                    move.y += offset.y
                    break

        handle("left", Vector2(-1, 0))
        handle("right", Vector2(1, 0))
        handle("up", Vector2(0, -1))
        handle("down", Vector2(0, 1))

        if move.length_squared() > 0:
            move = move.normalize() * speed * dt
            self.move(move.x, move.y)

        if mouse_drag and input_state.is_mouse_pressed(mouse_button):
            rel = input_state.mouse_rel
            if rel != (0, 0):
                self.move(-rel[0], -rel[1])

        return self.get_position()


class GameContext:
    """Контекст игры, который инкапсулирует глобальное состояние."""

    _instance: "GameContext | None" = None

    def __init__(self) -> None:
        """Инициализирует контекст игры и подсистемы."""
        if GameContext._instance is not None:
            return
        self.game = SpriteProGame.get()
        self.camera = CameraController(self.game)
        self.input = InputState()
        self.event_bus = EventBus()
        self.resources = resource_cache
        self.scene_manager = SceneManager()

        self.fps: int = 60
        self.events: List[pygame.event.Event] = []
        self.screen: pygame.Surface | None = None
        self.screen_rect: pygame.Rect | None = None
        self._output_surface: pygame.Surface | None = None
        self._reference_size: Tuple[int, int] | None = None
        self._viewport_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.visible_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.safe_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._present_scale_surface: pygame.Surface | None = None
        self._last_resize_signature: tuple | None = None
        self.WH: Vector2 = Vector2()
        self.WH_C: Vector2 = Vector2()
        self.clock = pygame.time.Clock()
        self.dt: float = 0.0
        self.frame_count: int = 0
        self.time_since_start: float = 0.0
        self._start_time: float = time.perf_counter()
        self._startup_log_done = False
        self._quit_requested = False
        self._window_flags: int = 0
        self._window_resizable: bool = False
        GameContext._instance = self

    @classmethod
    def get(cls) -> "GameContext":
        """Возвращает единственный экземпляр контекста игры."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init_pygame(self) -> None:
        """Инициализирует модули pygame."""
        try:
            is_android_runtime = bool(
                os.environ.get("ANDROID_ARGUMENT") or os.environ.get("P4A_BOOTSTRAP")
            )

            if is_android_runtime:
                if not pygame.font.get_init():
                    pygame.font.init()
                return

            if not pygame.get_init():
                pygame.init()
            if not pygame.font.get_init():
                pygame.font.init()
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except Exception:
            import spritePro

            spritePro.debug_log_warning("Error init pygame")

    @staticmethod
    def _normalize_reference_size(
        reference_size: Tuple[int, int] | None,
    ) -> Tuple[int, int] | None:
        if reference_size is None:
            return None
        width = max(1, int(reference_size[0]))
        height = max(1, int(reference_size[1]))
        return (width, height)

    @staticmethod
    def _calculate_viewport_rect(
        output_size: Tuple[int, int],
        reference_size: Tuple[int, int] | None,
    ) -> pygame.Rect:
        output_w = max(1, int(output_size[0]))
        output_h = max(1, int(output_size[1]))
        if reference_size is None:
            return pygame.Rect(0, 0, output_w, output_h)
        ref_w = max(1, int(reference_size[0]))
        ref_h = max(1, int(reference_size[1]))
        scale = max(output_w / ref_w, output_h / ref_h)
        viewport_w = max(1, int(round(ref_w * scale)))
        viewport_h = max(1, int(round(ref_h * scale)))
        viewport_x = int(round((output_w - viewport_w) / 2))
        viewport_y = int(round((output_h - viewport_h) / 2))
        return pygame.Rect(viewport_x, viewport_y, viewport_w, viewport_h)

    def _uses_reference_resolution(self) -> bool:
        return (
            self._reference_size is not None
            and self._output_surface is not None
            and self.screen is not None
            and self.screen is not self._output_surface
        )

    def _rebuild_render_targets(self) -> None:
        if self._output_surface is None:
            self.screen = None
            self.screen_rect = None
            self.WH = Vector2()
            self.WH_C = Vector2()
            self._viewport_rect = pygame.Rect(0, 0, 0, 0)
            self.visible_rect = pygame.Rect(0, 0, 0, 0)
            self.safe_rect = pygame.Rect(0, 0, 0, 0)
            self._present_scale_surface = None
            return

        self._viewport_rect = self._calculate_viewport_rect(
            self._output_surface.get_size(),
            self._reference_size,
        )

        if self._reference_size is None:
            self.screen = self._output_surface
            self.screen_rect = self.screen.get_rect()
        else:
            output_alpha = bool(self._output_surface.get_flags() & pygame.SRCALPHA)
            output_depth = max(24, int(self._output_surface.get_bitsize() or 24))
            expected_flags = pygame.SRCALPHA if output_alpha else 0
            if (
                self.screen is None
                or self.screen.get_size() != self._reference_size
                or self.screen.get_bitsize() != output_depth
                or bool(self.screen.get_flags() & pygame.SRCALPHA) != output_alpha
            ):
                self.screen = pygame.Surface(self._reference_size, expected_flags, output_depth)
            self.screen_rect = pygame.Rect((0, 0), self._reference_size)

        self.WH = Vector2(self.screen_rect.size)
        self.WH_C = Vector2(self.screen_rect.center)
        self.visible_rect = self._calculate_visible_rect()
        self.safe_rect = self._calculate_safe_rect()
        self._present_scale_surface = None

    def _calculate_visible_rect(self) -> pygame.Rect:
        if self.screen_rect is None:
            return pygame.Rect(0, 0, 0, 0)
        if not self._uses_reference_resolution() or self._output_surface is None:
            return self.screen_rect.copy()

        output_w, output_h = self._output_surface.get_size()
        top_left = self._map_output_pos_to_screen((0, 0))
        bottom_right = self._map_output_pos_to_screen((output_w, output_h))
        left = max(0, min(self.screen_rect.width, min(top_left[0], bottom_right[0])))
        top = max(0, min(self.screen_rect.height, min(top_left[1], bottom_right[1])))
        right = max(0, min(self.screen_rect.width, max(top_left[0], bottom_right[0])))
        bottom = max(0, min(self.screen_rect.height, max(top_left[1], bottom_right[1])))
        return pygame.Rect(left, top, max(1, right - left), max(1, bottom - top))

    def _calculate_safe_rect(self) -> pygame.Rect:
        visible = self.visible_rect.copy()
        if visible.width <= 0 or visible.height <= 0:
            return visible
        is_android_runtime = bool(
            os.environ.get("ANDROID_ARGUMENT") or os.environ.get("P4A_BOOTSTRAP")
        )
        if not is_android_runtime or self._output_surface is None:
            return visible

        margin = max(18, int(round(min(visible.width, visible.height) * 0.03)))
        return pygame.Rect(
            visible.left + margin,
            visible.top + margin,
            max(1, visible.width - margin * 2),
            max(1, visible.height - margin * 2),
        )

    def dispatch_resize_event(self, force: bool = False) -> None:
        if self.screen_rect is None or self._output_surface is None:
            return
        signature = (
            tuple(self.screen_rect.size),
            tuple(self._output_surface.get_size()),
            tuple(self.visible_rect),
            tuple(self.safe_rect),
            tuple(self._viewport_rect),
            self._reference_size,
        )
        if not force and signature == self._last_resize_signature:
            return
        self._last_resize_signature = signature
        self.event_bus.send(
            GlobalEvents.RESIZE,
            size=self.screen_rect.size,
            center=self.screen_rect.center,
            output_size=self._output_surface.get_size(),
            reference_size=self._reference_size,
            viewport_rect=self._viewport_rect.copy(),
            visible_rect=self.visible_rect.copy(),
            visible_size=self.visible_rect.size,
            visible_center=self.visible_rect.center,
            safe_rect=self.safe_rect.copy(),
            safe_size=self.safe_rect.size,
            safe_center=self.safe_rect.center,
        )

    def _map_output_pos_to_screen(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        if not self._uses_reference_resolution() or self.screen_rect is None:
            return (int(pos[0]), int(pos[1]))

        viewport = self._viewport_rect
        if viewport.width <= 0 or viewport.height <= 0:
            return (int(pos[0]), int(pos[1]))

        mapped_x = (pos[0] - viewport.x) * self.screen_rect.width / viewport.width
        mapped_y = (pos[1] - viewport.y) * self.screen_rect.height / viewport.height
        return (int(round(mapped_x)), int(round(mapped_y)))

    def _map_output_rel_to_screen(self, rel: Tuple[int, int]) -> Tuple[int, int]:
        if not self._uses_reference_resolution() or self.screen_rect is None:
            return (int(rel[0]), int(rel[1]))

        viewport = self._viewport_rect
        if viewport.width <= 0 or viewport.height <= 0:
            return (int(rel[0]), int(rel[1]))

        mapped_x = rel[0] * self.screen_rect.width / viewport.width
        mapped_y = rel[1] * self.screen_rect.height / viewport.height
        return (int(round(mapped_x)), int(round(mapped_y)))

    def _remap_input_events(
        self,
        events: List[pygame.event.Event],
    ) -> List[pygame.event.Event]:
        if not self._uses_reference_resolution():
            return events

        remapped_events: List[pygame.event.Event] = []
        for event in events:
            if event.type not in (
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ):
                remapped_events.append(event)
                continue

            payload = dict(event.dict)
            if "pos" in payload:
                payload["pos"] = self._map_output_pos_to_screen(payload["pos"])
            if "rel" in payload:
                payload["rel"] = self._map_output_rel_to_screen(payload["rel"])
            remapped_events.append(pygame.event.Event(event.type, payload))
        return remapped_events

    def _sync_reference_mouse_state(self) -> None:
        if not self._uses_reference_resolution():
            return
        if self.screen_rect is None:
            return
        try:
            current_mouse_pos = pygame.mouse.get_pos()
        except pygame.error:
            return

        mapped = self._map_output_pos_to_screen(current_mouse_pos)
        last = getattr(self.input, "_last_mouse_pos", mapped)
        self.input.mouse_pos = mapped
        self.input.mouse_rel = (mapped[0] - last[0], mapped[1] - last[1])

    def _present_frame(self) -> None:
        if self.screen is None or self._output_surface is None:
            return
        if self.screen is self._output_surface:
            return

        viewport = self._viewport_rect
        if viewport.width <= 0 or viewport.height <= 0:
            return
        if viewport.size == self.screen.get_size():
            self._output_surface.blit(self.screen, viewport.topleft)
            return
        if (
            self._present_scale_surface is None
            or self._present_scale_surface.get_size() != viewport.size
        ):
            scale_flags = pygame.SRCALPHA if self._output_surface.get_flags() & pygame.SRCALPHA else 0
            self._present_scale_surface = pygame.Surface(
                viewport.size,
                scale_flags,
                max(24, int(self._output_surface.get_bitsize() or 24)),
            )
        pygame.transform.scale(self.screen, viewport.size, self._present_scale_surface)
        self._output_surface.blit(self._present_scale_surface, viewport.topleft)

    def attach_surface(
        self,
        surface: pygame.Surface,
        reference_size: Tuple[int, int] | None = None,
    ) -> pygame.Surface:
        """Подключает внешнюю поверхность рендера вместо окна pygame."""
        self._output_surface = surface
        self._reference_size = self._normalize_reference_size(reference_size)
        self._rebuild_render_targets()
        self._quit_requested = False
        self.dispatch_resize_event(force=True)
        return self.screen

    def _resize_desktop_window(self, size: Tuple[int, int]) -> None:
        if not self._window_resizable:
            return
        width = max(1, int(size[0]))
        height = max(1, int(size[1]))
        current_surface = pygame.display.get_surface()
        if current_surface is not None and current_surface.get_size() == (width, height):
            return
        self._output_surface = pygame.display.set_mode((width, height), self._window_flags)
        self._rebuild_render_targets()
        self._quit_requested = False
        self.dispatch_resize_event(force=False)

    def get_screen(
        self,
        size: Tuple[int, int] = (800, 600),
        title: str = "Игра",
        icon: str | None = None,
        reference_size: Tuple[int, int] | None = None,
        resizable: bool = False,
    ) -> pygame.Surface:
        """Создает окно и сохраняет параметры экрана."""
        net_tag = os.environ.get("SPRITEPRO_NET_LOG_TAG")
        if net_tag:
            log_dir = os.environ.get("SPRITEPRO_LOG_DIR", "spritepro_logs")
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError:
                pass
            self.game.set_debug_log_file(path=os.path.join(log_dir, f"debug_{net_tag}.log"))
        pos = os.environ.get("SPRITEPRO_WINDOW_POS")
        if pos and pos.lower() != "center":
            try:
                x_str, y_str = pos.split(",", 1)
                x = int(x_str.strip())
                y = int(y_str.strip())
                os.environ["SDL_VIDEO_WINDOW_POS"] = f"{x},{y}"
            except ValueError:
                pass
        self._window_resizable = bool(resizable)
        self._window_flags = pygame.RESIZABLE if self._window_resizable else 0
        self.attach_surface(
            pygame.display.set_mode(size, self._window_flags),
            reference_size=reference_size,
        )
        pygame.display.set_caption(title)
        if icon:
            icon_surface = resource_cache.load_texture(icon)
            if icon_surface is not None:
                pygame.display.set_icon(icon_surface)

        get_plugin_manager().emit("game_init")
        pm = get_plugin_manager()
        enabled_plugins = [
            n for n in pm.list_plugins() if pm.get_plugin(n) and pm.get_plugin(n).enabled
        ]
        if enabled_plugins:
            self.game.debug_log_info(f"Плагины: {', '.join(enabled_plugins)}")
        if not self._startup_log_done:
            self._startup_log_done = True
            self.game.debug_log_custom(
                prefix="[info]",
                text="Привет! SpritePro создан neoxider — https://github.com/NeoXider/SpritePro",
                color=(80, 220, 120),
            )
        return self.screen

    def _run_frame(
        self,
        *,
        events: List[pygame.event.Event],
        cpu_started_ns: int,
        dt_ms: float,
        update_display: bool,
        fill_color: Tuple[int, int, int] | None,
        update_objects: Tuple[object, ...],
        exit_on_quit: bool,
    ) -> None:
        perf_enabled = self.game.debug_perf_enabled
        perf_stages = None
        if perf_enabled:
            perf_stages = {
                "input": 0.0,
                "events": 0.0,
                "plugins": 0.0,
                "scenes": 0.0,
                "sprites": 0.0,
                "debug": 0.0,
                "present": 0.0,
            }

        stage_started_ns = time.perf_counter_ns()
        if fill_color is not None:
            self.screen.fill(fill_color)

        if self.game.debug_enabled:
            if not self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if not self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)
        if perf_enabled and perf_stages is not None:
            perf_stages["debug"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        self.events = self._remap_input_events(events)
        try:
            import spritePro as _sp

            _sp.pygame_events = self.events
        except Exception:
            pass
        is_android_runtime = bool(
            os.environ.get("ANDROID_ARGUMENT") or os.environ.get("P4A_BOOTSTRAP")
        )
        self.input.update(self.events, poll_hardware=not is_android_runtime)
        if not any(
            event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)
            for event in self.events
        ):
            self._sync_reference_mouse_state()
        if self.game.debug_enabled and self.game.debug_camera_drag_button is not None:
            if self.input.is_mouse_pressed(self.game.debug_camera_drag_button):
                rel = self.input.mouse_rel
                if rel != (0, 0):
                    self.game.move_camera(-rel[0], -rel[1])
        if perf_enabled and perf_stages is not None:
            perf_stages["input"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        for event in self.events:
            if event.type == pygame.QUIT:
                self._quit_requested = True
                self.event_bus.send(GlobalEvents.QUIT, event=event)
            elif event.type in WINDOW_RESIZE_EVENT_TYPES:
                new_size = getattr(event, "size", None)
                if new_size is None:
                    event_x = getattr(event, "x", 0)
                    event_y = getattr(event, "y", 0)
                    new_size = (event_x, event_y)
                self._resize_desktop_window(new_size)
            elif event.type == pygame.MOUSEWHEEL:
                if self.game.debug_enabled and getattr(self.game, "debug_wheel_zoom_enabled", True):
                    factor = 1.15 if event.y > 0 else 1 / 1.15
                    self.game.zoom_camera(factor)
            elif event.type == pygame.KEYDOWN:
                self.event_bus.send(GlobalEvents.KEY_DOWN, key=event.key, event=event)
            elif event.type == pygame.KEYUP:
                self.event_bus.send(GlobalEvents.KEY_UP, key=event.key, event=event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.event_bus.send(
                    GlobalEvents.MOUSE_DOWN,
                    button=event.button,
                    pos=event.pos,
                    event=event,
                )
            elif event.type == pygame.MOUSEBUTTONUP:
                self.event_bus.send(
                    GlobalEvents.MOUSE_UP,
                    button=event.button,
                    pos=event.pos,
                    event=event,
                )

        self.event_bus.send(
            GlobalEvents.TICK,
            dt=self.dt,
            frame_count=self.frame_count,
            time_since_start=self.time_since_start,
        )
        if perf_enabled and perf_stages is not None:
            perf_stages["events"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        try:
            import spritePro as s
            if getattr(s, "multiplayer_ctx", None):
                s.multiplayer_ctx.update_frame()
            from .net_decorators import dispatch_net_events
            dispatch_net_events()
        except ImportError:
            pass
        if perf_enabled and perf_stages is not None:
            perf_stages["network"] = (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        for obj in update_objects:
            self.game.register_update_object(obj)

        get_plugin_manager().emit("game_update", dt=self.dt)
        if perf_enabled and perf_stages is not None:
            perf_stages["plugins"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        self.scene_manager.update(self.dt)
        if perf_enabled and perf_stages is not None:
            perf_stages["scenes"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        self.game.update(self.screen, dt=self.dt, wh_c=self.WH_C)
        self.game.draw(self.screen)
        self.scene_manager.draw(self.screen)
        if perf_enabled and perf_stages is not None:
            perf_stages["sprites"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        if self.game.debug_enabled:
            if self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)
            self.game.draw_debug_overlay(self.screen, self.WH_C, dt=self.dt)
        if perf_enabled and perf_stages is not None:
            perf_stages["debug"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0

        stage_started_ns = time.perf_counter_ns()
        self._present_frame()
        if update_display and pygame.display.get_surface() is not None:
            pygame.display.update()
        if perf_enabled and perf_stages is not None:
            perf_stages["present"] += (time.perf_counter_ns() - stage_started_ns) / 1_000_000.0
            cpu_frame_ms = (time.perf_counter_ns() - cpu_started_ns) / 1_000_000.0
            physics_world = getattr(self.game, "physics_world", None)
            body_count = (
                len(getattr(physics_world, "_all_bodies", ()))
                if physics_world is not None
                else 0
            )
            self.game.record_perf_frame(
                frame_ms=dt_ms,
                cpu_ms=cpu_frame_ms,
                dt_ms=dt_ms,
                fps=float(self.game.debug_fps_value),
                event_count=len(self.events),
                sprite_count=len(self.game.all_sprites),
                body_count=body_count,
                stages=perf_stages,
            )

        if self._quit_requested and exit_on_quit:
            import sys

            if sys.platform != "emscripten":
                sys.exit(0)

    def update(
        self,
        fps: int = 60,
        fill_color: Tuple[int, int, int] | None = None,
        update_display: bool = True,
        *update_objects,
    ) -> None:
        """Обновляет ввод, сцены, спрайты и debug overlay.

        Args:
            fps (int, optional): Целевой FPS. По умолчанию 60.
            fill_color (tuple[int, int, int] | None, optional): Цвет заливки экрана.
                Если None, заливка не выполняется.
            update_display (bool, optional): Вызывать ли обновление окна.
            *update_objects: Объекты, которые нужно обновлять каждый кадр.
        """
        if fps >= 0 and fps != self.fps:
            self.fps = fps
        self.dt = self.clock.tick(self.fps) / 1000.0
        cpu_started_ns = time.perf_counter_ns()
        dt_ms = self.dt * 1000.0
        self.frame_count += 1
        self.time_since_start = time.perf_counter() - self._start_time
        self.game.debug_fps_value = self.clock.get_fps()

        if self.screen is None:
            return

        self._run_frame(
            events=pygame.event.get(),
            cpu_started_ns=cpu_started_ns,
            dt_ms=dt_ms,
            update_display=update_display,
            fill_color=fill_color,
            update_objects=update_objects,
            exit_on_quit=True,
        )

    def update_embedded(
        self,
        fps: int = 60,
        fill_color: Tuple[int, int, int] | None = None,
        events: List[pygame.event.Event] | None = None,
        *update_objects,
    ) -> None:
        """Обновляет игру на внешней поверхности без собственного окна pygame."""
        if fps >= 0 and fps != self.fps:
            self.fps = fps
        self.dt = self.clock.tick(0) / 1000.0
        cpu_started_ns = time.perf_counter_ns()
        self.frame_count += 1
        self.time_since_start = time.perf_counter() - self._start_time
        self.game.debug_fps_value = self.clock.get_fps()

        if self.screen is None:
            return

        self._run_frame(
            events=events if isinstance(events, list) else list(events or []),
            cpu_started_ns=cpu_started_ns,
            dt_ms=self.dt * 1000.0,
            update_display=False,
            fill_color=fill_color,
            update_objects=update_objects,
            exit_on_quit=False,
        )

    def quit_requested(self) -> bool:
        """Возвращает True, если было событие выхода (закрытие окна)."""
        return self._quit_requested

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Регистрирует спрайт в игровом контексте."""
        self.game.register_sprite(sprite)
        get_plugin_manager().emit("sprite_created", sprite=sprite)

    def unregister_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Удаляет спрайт из игрового контекста."""
        self.game.unregister_sprite(sprite)

    def enable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Включает спрайт в игровом контексте."""
        self.game.enable_sprite(sprite)

    def disable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отключает спрайт в игровом контексте."""
        self.game.disable_sprite(sprite)

    def register_update_object(self, obj) -> None:
        """Регистрирует объект для автоматического обновления."""
        self.game.register_update_object(obj)

    def unregister_update_object(self, obj) -> None:
        """Отменяет регистрацию объекта обновления."""
        self.game.unregister_update_object(obj)

    def get_sprites_by_class(self, sprite_class: type, active_only: bool = True):
        """Возвращает список спрайтов указанного класса."""
        return self.game.get_sprites_by_class(sprite_class, active_only)
