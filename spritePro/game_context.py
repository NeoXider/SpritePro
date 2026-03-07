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
        self.WH: Vector2 = Vector2()
        self.WH_C: Vector2 = Vector2()
        self.clock = pygame.time.Clock()
        self.dt: float = 0.0
        self.frame_count: int = 0
        self.time_since_start: float = 0.0
        self._start_time: float = time.perf_counter()
        self._startup_log_done = False
        self._quit_requested = False
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
        scale = min(output_w / ref_w, output_h / ref_h)
        viewport_w = max(1, int(round(ref_w * scale)))
        viewport_h = max(1, int(round(ref_h * scale)))
        viewport_x = (output_w - viewport_w) // 2
        viewport_y = (output_h - viewport_h) // 2
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
            return

        self._viewport_rect = self._calculate_viewport_rect(
            self._output_surface.get_size(),
            self._reference_size,
        )

        if self._reference_size is None:
            self.screen = self._output_surface
            self.screen_rect = self.screen.get_rect()
        else:
            if self.screen is None or self.screen.get_size() != self._reference_size:
                self.screen = pygame.Surface(self._reference_size, pygame.SRCALPHA, 32)
            self.screen_rect = pygame.Rect((0, 0), self._reference_size)

        self.WH = Vector2(self.screen_rect.size)
        self.WH_C = Vector2(self.screen_rect.center)

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
            return list(events)

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

        self._output_surface.fill((0, 0, 0))
        viewport = self._viewport_rect
        if viewport.width <= 0 or viewport.height <= 0:
            return
        scaled = pygame.transform.smoothscale(self.screen, viewport.size)
        self._output_surface.blit(scaled, viewport.topleft)

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
        return self.screen

    def get_screen(
        self,
        size: Tuple[int, int] = (800, 600),
        title: str = "Игра",
        icon: str | None = None,
        reference_size: Tuple[int, int] | None = None,
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
        self.attach_surface(
            pygame.display.set_mode(size),
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
        update_display: bool,
        fill_color: Tuple[int, int, int] | None,
        update_objects: Tuple[object, ...],
        exit_on_quit: bool,
    ) -> None:
        if fill_color is not None:
            self.screen.fill(fill_color)

        if self.game.debug_enabled:
            if not self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if not self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)

        self.events = self._remap_input_events(list(events))
        try:
            import spritePro as _sp

            _sp.pygame_events = self.events
        except Exception:
            pass
        self.input.update(self.events)
        if not any(
            event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)
            for event in self.events
        ):
            self._sync_reference_mouse_state()
        self.event_bus.send(GlobalEvents.TICK, dt=self.dt, frame_count=self.frame_count)
        if self.game.debug_enabled and self.game.debug_camera_drag_button is not None:
            if self.input.is_mouse_pressed(self.game.debug_camera_drag_button):
                rel = self.input.mouse_rel
                if rel != (0, 0):
                    self.game.move_camera(-rel[0], -rel[1])

        for event in self.events:
            if event.type == pygame.QUIT:
                self._quit_requested = True
                self.event_bus.send(GlobalEvents.QUIT, event=event)
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

        for obj in update_objects:
            self.game.register_update_object(obj)

        get_plugin_manager().emit("game_update", dt=self.dt)
        self.scene_manager.update(self.dt)
        self.game.update(self.screen, dt=self.dt, wh_c=self.WH_C)
        self.game.draw(self.screen)
        self.scene_manager.draw(self.screen)
        if self.game.debug_enabled:
            if self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)
            self.game.draw_debug_overlay(self.screen, self.WH_C, dt=self.dt)

        self._present_frame()
        if update_display and pygame.display.get_surface() is not None:
            pygame.display.update()

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
        self.frame_count += 1
        self.time_since_start = time.perf_counter() - self._start_time
        self.game.debug_fps_value = self.clock.get_fps()

        if self.screen is None:
            return

        self._run_frame(
            events=pygame.event.get(),
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
        self.dt = self.clock.tick(self.fps) / 1000.0
        self.frame_count += 1
        self.time_since_start = time.perf_counter() - self._start_time
        self.game.debug_fps_value = self.clock.get_fps()

        if self.screen is None:
            return

        self._run_frame(
            events=list(events or []),
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
