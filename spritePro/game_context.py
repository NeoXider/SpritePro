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
        return self._game.get_camera().copy()

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
        self.WH: Vector2 = Vector2()
        self.WH_C: Vector2 = Vector2()
        self.clock = pygame.time.Clock()
        self.dt: float = 0.0
        self.frame_count: int = 0
        self.time_since_start: float = 0.0
        self._start_time: float = time.perf_counter()
        self._startup_log_done = False
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
            pygame.init()
            pygame.font.init()
            pygame.mixer.init()
        except Exception:
            import spritePro

            spritePro.debug_log_warning("Error init pygame")

    def get_screen(
        self,
        size: Tuple[int, int] = (800, 600),
        title: str = "Игра",
        icon: str | None = None,
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
        self.screen = pygame.display.set_mode(size)
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption(title)
        if icon:
            icon_surface = resource_cache.load_texture(icon)
            if icon_surface is not None:
                pygame.display.set_icon(icon_surface)

        self.WH = Vector2(size)
        self.WH_C = Vector2(self.screen_rect.center)
        if not self._startup_log_done:
            self._startup_log_done = True
            self.game.debug_log_custom(
                prefix="[info]",
                text="Привет! SpritePro создан neoxider — https://github.com/NeoXider/SpritePro",
                color=(80, 220, 120),
            )
        return self.screen

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

        if fill_color is not None:
            self.screen.fill(fill_color)

        if self.game.debug_enabled:
            if not self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if not self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)

        self.events = pygame.event.get()
        try:
            import spritePro as _sp

            _sp.pygame_events = self.events
        except Exception:
            pass
        self.input.update(self.events)
        self.event_bus.send(GlobalEvents.TICK, dt=self.dt, frame_count=self.frame_count)
        if self.game.debug_enabled and self.game.debug_camera_drag_button is not None:
            if self.input.is_mouse_pressed(self.game.debug_camera_drag_button):
                rel = self.input.mouse_rel
                if rel != (0, 0):
                    self.game.move_camera(-rel[0], -rel[1])

        for event in self.events:
            if event.type == pygame.QUIT:
                self.event_bus.send(GlobalEvents.QUIT, event=event)
                raise SystemExit
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

        self.scene_manager.update(self.dt)
        self.game.update(self.screen, dt=self.dt, wh_c=self.WH_C)
        self.scene_manager.draw(self.screen)
        if self.game.debug_enabled:
            if self.game.debug_grid_on_top:
                self.game.draw_debug_grid(self.screen)
            if self.game.debug_hud_on_top:
                self.game.draw_debug_hud(self.screen)
            self.game.draw_debug_overlay(self.screen, self.WH_C, dt=self.dt)

        if update_display:
            pygame.display.update()

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Регистрирует спрайт в игровом контексте."""
        self.game.register_sprite(sprite)

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
