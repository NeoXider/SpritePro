from typing import List, Tuple, Optional
import time
import sys
import inspect
from dataclasses import dataclass
import pygame
from pygame.math import Vector2


class SpriteProGame:
    """Одиночный игровой контекст с общей группой спрайтов и камерой.

    Управляет всеми спрайтами игры, камерой и их взаимодействием.
    Использует паттерн Singleton для обеспечения единственного экземпляра.

    Attributes:
        all_sprites (pygame.sprite.LayeredUpdates): Группа всех спрайтов с поддержкой слоев.
        camera (Vector2): Позиция камеры.
        camera_target (pygame.sprite.Sprite | None): Целевой спрайт для следования камеры.
        camera_offset (Vector2): Смещение камеры относительно цели.
        _instance (SpriteProGame | None): Единственный экземпляр класса.
    """

    _instance: "SpriteProGame | None" = None

    def __init__(self) -> None:
        """Инициализирует SpriteProGame.

        Создает группу спрайтов, инициализирует камеру и устанавливает экземпляр как единственный.
        """
        if SpriteProGame._instance is not None:
            return
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.camera = Vector2()
        self.camera_target: pygame.sprite.Sprite | None = None
        self.camera_offset = Vector2()
        self.update_objects: list = []  # Объекты для автоматического обновления

        # Debug overlay settings
        self.debug_enabled = False
        self.debug_logs_enabled = True
        self.debug_grid_enabled = True
        self.debug_log_anchor = "bottom_left"
        self.debug_log_padding = 8
        self.debug_log_line_height = 18
        self.debug_log_font_size = 16
        self.debug_log_max = 12
        self.debug_log_ttl = 4.0
        self.debug_log_file_enabled = True
        self.debug_log_file_path = "debug.log"
        self._debug_log_file_initialized = False
        self.debug_log_stack_enabled = True
        self.console_log_enabled = True
        self.console_log_color_enabled = True
        self.debug_start_time = time.monotonic()
        self.debug_grid_size = 100
        self.debug_grid_color = (80, 80, 80)
        self.debug_grid_alpha = 120
        self.debug_grid_label_color = (130, 130, 130)
        self.debug_grid_label_every = 1
        self.debug_grid_label_limit = 10000
        self.debug_grid_labels_enabled = True
        self.debug_grid_label_font_size = 12
        self.debug_grid_on_top = False
        self.debug_camera_color = (255, 80, 80)
        self.debug_camera_font_size = 16
        self.debug_camera_drag_button: int | None = 3
        self.debug_hud_anchor = "top_left"
        self.debug_hud_padding = 8
        self.debug_hud_color = (170, 220, 255)
        self.debug_hud_font_size = 16
        self.debug_show_fps = True
        self.debug_show_camera_coords = True
        self.debug_hud_on_top = True
        self.debug_fps_value = 0.0
        self.debug_log_prefixes = {
            "info": "[log]",
            "warning": "[warning]",
            "error": "[error]",
        }
        self.debug_log_colors = {
            "info": (170, 220, 255),
            "warning": (255, 200, 80),
            "error": (255, 90, 90),
        }
        self._debug_logs: list[_DebugLogEntry] = []
        self._debug_font: pygame.font.Font | None = None
        self._debug_grid_font: pygame.font.Font | None = None
        self._debug_camera_font: pygame.font.Font | None = None
        self._debug_hud_font: pygame.font.Font | None = None

        SpriteProGame._instance = self

    @classmethod
    def get(cls) -> "SpriteProGame":
        """Получает единственный экземпляр SpriteProGame.

        Returns:
            SpriteProGame: Единственный экземпляр игрового контекста.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Регистрирует спрайт в игровом контексте.

        Добавляет спрайт в группу всех спрайтов. Если у спрайта есть атрибут sorting_order,
        он будет добавлен на соответствующий слой.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для регистрации.
        """
        if sprite not in self.all_sprites:
            # If sprite has a declared sorting order, add it at that layer
            layer = getattr(sprite, "sorting_order", None)
            if layer is not None:
                try:
                    self.all_sprites.add(sprite, layer=int(layer))
                except Exception:
                    # Fallback to default add if layer add fails
                    self.all_sprites.add(sprite)
            else:
                self.all_sprites.add(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = True

    def unregister_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отменяет регистрацию спрайта в игровом контексте.

        Удаляет спрайт из группы всех спрайтов.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отмены регистрации.
        """
        self.all_sprites.remove(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = False

    def enable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Включает спрайт (регистрирует его).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для включения.
        """
        self.register_sprite(sprite)

    def disable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отключает спрайт (отменяет его регистрацию).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отключения.
        """
        self.unregister_sprite(sprite)

    def set_sprite_layer(self, sprite: pygame.sprite.Sprite, layer: int) -> None:
        """Устанавливает слой отрисовки для спрайта в глобальной группе со слоями.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для установки слоя.
            layer (int): Номер слоя для отрисовки.
        """
        try:
            # If sprite is not in the group yet, add with layer
            if sprite not in self.all_sprites:
                self.all_sprites.add(sprite, layer=int(layer))
            else:
                self.all_sprites.change_layer(sprite, int(layer))
        except Exception:
            # Silently ignore if the underlying group does not support layers
            pass

    def set_camera(self, position: Vector2 | tuple[float, float]) -> None:
        """Устанавливает позицию камеры.

        Устанавливает камеру в указанную позицию и отменяет следование за целью.

        Args:
            position (Vector2 | tuple[float, float]): Позиция камеры (x, y).
        """
        if isinstance(position, Vector2):
            self.camera.update(position)
        else:
            self.camera.update(float(position[0]), float(position[1]))
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def move_camera(self, dx: float, dy: float) -> None:
        """Перемещает камеру на указанное смещение.

        Если камера следует за целью, смещение добавляется к offset.
        Иначе камера перемещается напрямую.

        Args:
            dx (float): Смещение по оси X.
            dy (float): Смещение по оси Y.
        """
        if self.camera_target is not None:
            self.camera_offset.x += dx
            self.camera_offset.y += dy
        else:
            self.camera.x += dx
            self.camera.y += dy

    def get_camera(self) -> Vector2:
        """Получает текущую позицию камеры.

        Returns:
            Vector2: Позиция камеры.
        """
        return self.camera

    def set_camera_follow(
        self,
        target: pygame.sprite.Sprite | None,
        offset: Vector2 | tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Устанавливает цель для следования камеры.

        Камера будет автоматически следовать за указанным спрайтом с заданным смещением.

        Args:
            target (pygame.sprite.Sprite | None): Целевой спрайт для следования или None для отмены.
            offset (Vector2 | tuple[float, float], optional): Смещение камеры относительно цели. По умолчанию (0.0, 0.0).
        """
        if target is None:
            self.clear_camera_follow()
            return
        self.camera_target = target
        if isinstance(offset, Vector2):
            self.camera_offset = offset.copy()
        else:
            self.camera_offset = Vector2(offset[0], offset[1])
        # При установке цели WH_C может быть еще не инициализирован, используем значение по умолчанию
        self._update_camera_follow()

    def clear_camera_follow(self) -> None:
        """Отменяет следование камеры за целью."""
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def _update_camera_follow(self, wh_c: Vector2 | None = None) -> None:
        """Обновляет позицию камеры при следовании за целью.

        Args:
            wh_c (Vector2 | None, optional): Центр экрана. Если None, используется значение по умолчанию (400, 300).
        """
        target = self.camera_target
        if not target:
            return
        alive_attr = getattr(target, "alive", None)
        if callable(alive_attr) and not alive_attr():
            self.clear_camera_follow()
            return
        center = Vector2(target.rect.center)
        if wh_c is None:
            wh_c = Vector2(400, 300)  # Значение по умолчанию
        desired = center - wh_c + self.camera_offset
        self.camera.update(desired)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает все спрайты на указанной поверхности.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
        """
        self.all_sprites.draw(surface)

    def register_update_object(self, obj) -> None:
        """Регистрирует объект для автоматического обновления.

        Объект должен иметь метод update(), который будет вызываться каждый кадр с dt.

        Args:
            obj: Объект для обновления (TweenManager, Animation, Timer и т.д.).
        """
        if any(getattr(entry, "obj", entry) is obj for entry in self.update_objects):
            return
        supports_dt = self._detect_update_signature(obj)
        self.update_objects.append(_UpdateEntry(obj=obj, supports_dt=supports_dt))

    def unregister_update_object(self, obj) -> None:
        """Отменяет регистрацию объекта для автоматического обновления.

        Args:
            obj: Объект для отмены регистрации.
        """
        for entry in list(self.update_objects):
            entry_obj = getattr(entry, "obj", entry)
            if entry_obj is obj:
                self.update_objects.remove(entry)

    def get_sprites_by_class(
        self, sprite_class: type, active_only: bool = True
    ) -> List:
        """Получает список всех спрайтов указанного класса.

        Args:
            sprite_class (type): Класс спрайтов для поиска.
            active_only (bool, optional): Если True, возвращает только активные спрайты. По умолчанию True.

        Returns:
            List: Список спрайтов указанного класса.

        Example:
            >>> fountain_particles = game.get_sprites_by_class(FountainParticle)
            >>> all_sprites = game.get_sprites_by_class(Sprite, active_only=False)
        """
        result = [
            sprite for sprite in self.all_sprites if isinstance(sprite, sprite_class)
        ]

        if active_only:
            result = [
                sprite
                for sprite in result
                if hasattr(sprite, "active") and sprite.active
            ]

        return result

    def update(self, *args, wh_c: Vector2 | None = None, **kwargs) -> None:
        """Обновляет камеру и все спрайты.

        Args:
            *args: Позиционные аргументы для передачи в update спрайтов.
            wh_c (Vector2 | None, optional): Центр экрана для обновления камеры. По умолчанию None.
            **kwargs: Именованные аргументы для передачи в update спрайтов.
        """
        self._update_camera_follow(wh_c)

        # Автоматически обновляем зарегистрированные объекты
        dt = kwargs.pop("dt", None)
        if dt is None:
            try:
                import spritePro as sp

                dt = sp.dt
            except (AttributeError, NameError):
                dt = None

        for entry in self.update_objects:
            obj = getattr(entry, "obj", entry)
            supports_dt = getattr(entry, "supports_dt", False)
            if not hasattr(obj, "update"):
                continue
            try:
                if supports_dt and dt is not None:
                    obj.update(dt)
                else:
                    obj.update()
            except TypeError:
                try:
                    obj.update(dt)
                except TypeError:
                    import spritePro

                    spritePro.debug_log_error(f"Error update object {obj}")

        self.all_sprites.update(*args, **kwargs)

    def enable_debug(self, enabled: bool = True) -> None:
        """Включает или выключает debug overlay."""
        self.debug_enabled = enabled
        if enabled:
            self.debug_start_time = time.monotonic()

    def disable_debug(self) -> None:
        """Выключает debug overlay."""
        self.debug_enabled = False

    def toggle_debug(self) -> None:
        """Переключает состояние debug overlay."""
        self.debug_enabled = not self.debug_enabled

    def set_debug_logs_enabled(self, enabled: bool = True) -> None:
        """Включает или выключает отображение логов."""
        self.debug_logs_enabled = enabled

    def set_debug_grid_enabled(self, enabled: bool = True) -> None:
        """Включает или выключает отображение сетки."""
        self.debug_grid_enabled = enabled

    def set_debug_log_anchor(self, anchor: str) -> None:
        """Задает угол вывода логов."""
        self.debug_log_anchor = anchor

    def set_debug_grid(
        self,
        size: Optional[int] = None,
        color: Optional[Tuple[int, int, int]] = None,
        alpha: Optional[int] = None,
        label_every: Optional[int] = None,
        label_color: Optional[Tuple[int, int, int]] = None,
        labels_enabled: Optional[bool] = None,
        label_limit: Optional[int] = None,
        label_font_size: Optional[int] = None,
        on_top: Optional[bool] = None,
    ) -> None:
        """Настраивает параметры debug-сетки."""
        if size is not None:
            self.debug_grid_size = max(4, int(size))
        if color is not None:
            self.debug_grid_color = color
        if alpha is not None:
            self.debug_grid_alpha = max(0, min(255, int(alpha)))
        if label_every is not None:
            self.debug_grid_label_every = max(1, int(label_every))
        if label_color is not None:
            self.debug_grid_label_color = label_color
        if labels_enabled is not None:
            self.debug_grid_labels_enabled = bool(labels_enabled)
        if label_limit is not None:
            self.debug_grid_label_limit = max(0, int(label_limit))
        if label_font_size is not None:
            self.debug_grid_label_font_size = max(8, int(label_font_size))
            self._debug_grid_font = None
        if on_top is not None:
            self.debug_grid_on_top = bool(on_top)

    def set_debug_log_style(
        self,
        font_size: int | None = None,
        line_height: int | None = None,
        padding: int | None = None,
        max_lines: int | None = None,
        anchor: str | None = None,
    ) -> None:
        """Настраивает стиль отображения логов."""
        if font_size is not None:
            self.debug_log_font_size = max(8, int(font_size))
            self._debug_font = None
        if line_height is not None:
            self.debug_log_line_height = max(8, int(line_height))
        if padding is not None:
            self.debug_log_padding = max(0, int(padding))
        if max_lines is not None:
            self.debug_log_max = max(1, int(max_lines))
        if anchor is not None:
            self.debug_log_anchor = anchor

    def set_debug_camera_style(
        self,
        color: Tuple[int, int, int] | None = None,
        font_size: int | None = None,
    ) -> None:
        """Настраивает отображение маркера камеры."""
        if color is not None:
            self.debug_camera_color = color
        if font_size is not None:
            self.debug_camera_font_size = max(8, int(font_size))
            self._debug_camera_font = None

    def set_debug_camera_input(self, mouse_button: int | None = 3) -> None:
        """Настраивает кнопку мыши для управления камерой в debug."""
        self.debug_camera_drag_button = mouse_button

    def set_debug_log_file(
        self,
        enabled: bool | None = None,
        path: str | None = None,
    ) -> None:
        """Настраивает запись логов в файл."""
        if enabled is not None:
            self.debug_log_file_enabled = bool(enabled)
        if path is not None:
            self.debug_log_file_path = path
            self._debug_log_file_initialized = False

    def set_console_log_enabled(self, enabled: bool = True) -> None:
        """Включает или выключает вывод логов в консоль."""
        self.console_log_enabled = enabled

    def set_console_log_color_enabled(self, enabled: bool = True) -> None:
        """Включает или выключает цветной вывод логов в консоль."""
        self.console_log_color_enabled = enabled

    def set_debug_hud_style(
        self,
        font_size: int | None = None,
        color: Tuple[int, int, int] | None = None,
        padding: int | None = None,
        anchor: str | None = None,
        on_top: bool | None = None,
    ) -> None:
        """Настраивает стиль HUD с FPS и координатами камеры."""
        if font_size is not None:
            self.debug_hud_font_size = max(8, int(font_size))
            self._debug_hud_font = None
        if color is not None:
            self.debug_hud_color = color
        if padding is not None:
            self.debug_hud_padding = max(0, int(padding))
        if anchor is not None:
            self.debug_hud_anchor = anchor
        if on_top is not None:
            self.debug_hud_on_top = bool(on_top)

    def set_debug_hud_enabled(
        self,
        show_fps: bool | None = None,
        show_camera: bool | None = None,
    ) -> None:
        """Включает или выключает элементы HUD."""
        if show_fps is not None:
            self.debug_show_fps = bool(show_fps)
        if show_camera is not None:
            self.debug_show_camera_coords = bool(show_camera)

    def set_debug_log_stack_enabled(self, enabled: bool = True) -> None:
        """Включает или выключает добавление источника вызова в лог."""
        self.debug_log_stack_enabled = enabled

    def set_debug_log_palette(
        self,
        info: Tuple[int, int, int] | None = None,
        warning: Tuple[int, int, int] | None = None,
        error: Tuple[int, int, int] | None = None,
    ) -> None:
        """Задает цвета для типов логов."""
        if info is not None:
            self.debug_log_colors["info"] = info
        if warning is not None:
            self.debug_log_colors["warning"] = warning
        if error is not None:
            self.debug_log_colors["error"] = error

    def set_debug_log_prefixes(
        self,
        info: str | None = None,
        warning: str | None = None,
        error: str | None = None,
    ) -> None:
        """Задает префиксы для типов логов."""
        if info is not None:
            self.debug_log_prefixes["info"] = info
        if warning is not None:
            self.debug_log_prefixes["warning"] = warning
        if error is not None:
            self.debug_log_prefixes["error"] = error

    def add_debug_log(
        self,
        text: str,
        color: Optional[Tuple[int, int, int]] = None,
        ttl: Optional[float] = None,
        level: str = "info",
        prefix: Optional[str] = None,
    ) -> None:
        """Добавляет строку в очередь debug логов."""
        if text is None:
            return
        level_key = level.lower() if isinstance(level, str) else "info"
        if prefix is None:
            prefix = self.debug_log_prefixes.get(level_key, "[log]")
        if color is None:
            color = self.debug_log_colors.get(level_key, (220, 220, 220))
        if ttl is None:
            ttl = self.debug_log_ttl
        timestamp = self._format_log_time()
        callsite = self._format_log_callsite() if self.debug_log_stack_enabled else ""
        line = f"{prefix} {timestamp} {text}{callsite}"
        self._debug_logs.append(_DebugLogEntry(text=line, color=color, ttl=float(ttl)))
        if len(self._debug_logs) > self.debug_log_max:
            self._debug_logs = self._debug_logs[-self.debug_log_max :]
        self._write_debug_log_to_file(line)
        if self.console_log_enabled:
            self._write_console_log(line, color_enabled=self.console_log_color_enabled)

    def debug_log_info(self, text: str, ttl: Optional[float] = None) -> None:
        """Добавляет информационный лог."""
        self.add_debug_log(text, ttl=ttl, level="info")

    def debug_log_warning(self, text: str, ttl: Optional[float] = None) -> None:
        """Добавляет предупреждение."""
        self.add_debug_log(text, ttl=ttl, level="warning")

    def debug_log_error(self, text: str, ttl: Optional[float] = None) -> None:
        """Добавляет ошибку."""
        self.add_debug_log(text, ttl=ttl, level="error")

    def debug_log_custom(
        self,
        prefix: str,
        text: str,
        color: Tuple[int, int, int],
        ttl: Optional[float] = None,
    ) -> None:
        """Добавляет пользовательский лог с префиксом и цветом."""
        self.add_debug_log(text, color=color, ttl=ttl, level="custom", prefix=prefix)

    def clear_debug_logs(self) -> None:
        """Очищает очередь debug логов."""
        self._debug_logs.clear()

    def draw_debug_grid(self, surface: pygame.Surface) -> None:
        """Рисует debug-сетку под сценой."""
        if not self.debug_enabled or not self.debug_grid_enabled or surface is None:
            return
        self._ensure_debug_fonts()
        self._draw_debug_grid(surface)

    def draw_debug_hud(self, surface: pygame.Surface) -> None:
        """Рисует HUD с FPS и координатами камеры."""
        if not self.debug_enabled or surface is None:
            return
        self._ensure_debug_fonts()
        self._draw_debug_hud(surface)

    def draw_debug_overlay(
        self, surface: pygame.Surface, wh_c: Vector2, dt: float | None = None
    ) -> None:
        """Рисует debug-маркеры и логи поверх сцены."""
        if not self.debug_enabled or surface is None:
            return
        dt_value = 0.0 if dt is None else float(dt)
        self._update_debug_logs(dt_value)
        self._ensure_debug_fonts()

        self._draw_camera_marker(surface, wh_c)

        if self.debug_logs_enabled:
            self._draw_debug_logs(surface)

    def draw_debug(
        self, surface: pygame.Surface, wh_c: Vector2, dt: float | None = None
    ) -> None:
        """Рисует полный debug overlay (сетка + маркеры + логи)."""
        self.draw_debug_grid(surface)
        self.draw_debug_overlay(surface, wh_c, dt=dt)

    def _ensure_debug_fonts(self) -> None:
        """Создает шрифты для debug overlay при необходимости."""
        if self._debug_font is None:
            self._debug_font = pygame.font.SysFont(None, self.debug_log_font_size)
        if self._debug_grid_font is None:
            self._debug_grid_font = pygame.font.SysFont(
                None, self.debug_grid_label_font_size
            )
        if self._debug_camera_font is None:
            self._debug_camera_font = pygame.font.SysFont(
                None, self.debug_camera_font_size
            )
        if self._debug_hud_font is None:
            self._debug_hud_font = pygame.font.SysFont(None, self.debug_hud_font_size)

    def _update_debug_logs(self, dt: float) -> None:
        """Обновляет таймеры и очищает старые логи."""
        if not self._debug_logs:
            return
        for entry in self._debug_logs:
            entry.age += dt
        self._debug_logs = [
            entry
            for entry in self._debug_logs
            if entry.ttl <= 0 or entry.age <= entry.ttl
        ]

    def _draw_debug_logs(self, surface: pygame.Surface) -> None:
        """Рисует список логов в выбранном углу."""
        if not self._debug_logs or self._debug_font is None:
            return
        lines = list(self._debug_logs)
        if self.debug_log_anchor.startswith("bottom"):
            lines = list(reversed(lines))

        padding = self.debug_log_padding
        line_h = self.debug_log_line_height
        width, height = surface.get_size()
        anchor = self.debug_log_anchor

        if anchor.endswith("left"):
            x = padding
        else:
            x = width - padding

        if anchor.startswith("bottom"):
            y = height - padding - line_h
            y_step = -line_h
        else:
            y = padding
            y_step = line_h

        for entry in lines:
            text_surf = self._debug_font.render(entry.text, True, entry.color)
            pos_x = x if anchor.endswith("left") else x - text_surf.get_width()
            surface.blit(text_surf, (pos_x, y))
            y += y_step

    def _draw_debug_grid(self, surface: pygame.Surface) -> None:
        """Рисует мировую сетку и подписи координат."""
        grid_size = max(4, int(self.debug_grid_size))
        width, height = surface.get_size()
        camera = self.camera
        start_x = int(camera.x // grid_size) * grid_size
        start_y = int(camera.y // grid_size) * grid_size

        grid_color = (*self.debug_grid_color, self.debug_grid_alpha)
        grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        x = start_x
        while x <= camera.x + width:
            screen_x = int(x - camera.x)
            pygame.draw.line(
                grid_surface, grid_color, (screen_x, 0), (screen_x, height), 1
            )
            x += grid_size

        y = start_y
        while y <= camera.y + height:
            screen_y = int(y - camera.y)
            pygame.draw.line(
                grid_surface, grid_color, (0, screen_y), (width, screen_y), 1
            )
            y += grid_size

        surface.blit(grid_surface, (0, 0))

        if not self.debug_grid_labels_enabled or self._debug_grid_font is None:
            return

        label_every = max(1, int(self.debug_grid_label_every))
        labels_drawn = 0
        max_labels = self.debug_grid_label_limit
        x_index = 0
        x = start_x
        while x <= camera.x + width and labels_drawn < max_labels:
            y_index = 0
            y = start_y
            while y <= camera.y + height and labels_drawn < max_labels:
                if x_index % label_every == 0 and y_index % label_every == 0:
                    screen_x = int(x - camera.x) + 2
                    screen_y = int(y - camera.y) + 2
                    if 0 <= screen_x <= width - 20 and 0 <= screen_y <= height - 12:
                        label = f"{int(x)},{int(y)}"
                        text_surf = self._debug_grid_font.render(
                            label, True, self.debug_grid_label_color
                        )
                        surface.blit(text_surf, (screen_x, screen_y))
                        labels_drawn += 1
                y += grid_size
                y_index += 1
            x += grid_size
            x_index += 1

    def _draw_camera_marker(self, surface: pygame.Surface, wh_c: Vector2) -> None:
        """Рисует маркер центра камеры и координаты."""
        center = (int(wh_c.x), int(wh_c.y))
        pygame.draw.circle(surface, self.debug_camera_color, center, 3)
        pygame.draw.circle(surface, (0, 0, 0), center, 4, 1)
        if self._debug_camera_font is not None:
            cam = self.camera
            center_world = (int(cam.x + wh_c.x), int(cam.y + wh_c.y))
            mouse_pos = pygame.mouse.get_pos()
            mouse_world = (int(cam.x + mouse_pos[0]), int(cam.y + mouse_pos[1]))

            center_text = f"Point: {center_world[0]}, {center_world[1]}"
            mouse_text = f"Mouse: {mouse_world[0]}, {mouse_world[1]}"

            center_surf = self._debug_camera_font.render(
                center_text, True, self.debug_camera_color
            )
            mouse_surf = self._debug_camera_font.render(
                mouse_text, True, self.debug_camera_color
            )

            center_x = center[0] - center_surf.get_width() // 2
            mouse_x = center[0] - mouse_surf.get_width() // 2
            surface.blit(center_surf, (center_x, center[1] + 8))
            surface.blit(
                mouse_surf, (mouse_x, center[1] + 8 + center_surf.get_height() + 2)
            )

    def _draw_debug_hud(self, surface: pygame.Surface) -> None:
        """Рисует HUD с FPS и координатами камеры."""
        if self._debug_hud_font is None:
            return
        if not self.debug_show_fps and not self.debug_show_camera_coords:
            return
        lines = []
        if self.debug_show_camera_coords:
            cam = self.camera
            lines.append(f"Camera: {int(cam.x)}, {int(cam.y)}")
        if self.debug_show_fps:
            lines.append(f"FPS: {int(self.debug_fps_value)}")

        padding = self.debug_hud_padding
        anchor = self.debug_hud_anchor
        width, height = surface.get_size()

        if anchor.endswith("left"):
            x = padding
        else:
            x = width - padding

        if anchor.startswith("bottom"):
            y = height - padding
            y_step = -self.debug_hud_font_size - 2
        else:
            y = padding
            y_step = self.debug_hud_font_size + 2

        for line in lines:
            text_surf = self._debug_hud_font.render(line, True, self.debug_hud_color)
            pos_x = x if anchor.endswith("left") else x - text_surf.get_width()
            surface.blit(text_surf, (pos_x, y))
            y += y_step

    def _format_log_time(self) -> str:
        """Форматирует время с начала игры (точность 100 мс)."""
        elapsed = max(0.0, time.monotonic() - self.debug_start_time)
        total_ms = int(elapsed * 1000)
        total_ms = (total_ms // 100) * 100
        seconds = total_ms // 1000
        ms = total_ms % 1000
        minutes, sec = divmod(seconds, 60)
        hours, minute = divmod(minutes, 60)
        return f"{hours:02d}:{minute:02d}:{sec:02d}.{ms:03d}"

    def _format_log_callsite(self) -> str:
        """Возвращает строку с источником вызова для лога."""
        import inspect
        import os

        stack = inspect.stack()
        try:
            for frame_info in stack[2:]:
                filename = frame_info.filename
                if os.path.sep + "spritePro" + os.path.sep in filename:
                    continue
                basename = os.path.basename(filename)
                return f" ({basename}:{frame_info.lineno} {frame_info.function})"
        finally:
            del stack
        return ""

    def _write_debug_log_to_file(self, line: str) -> None:
        """Записывает лог в файл, если это включено."""
        if not self.debug_log_file_enabled or not self.debug_log_file_path:
            return
        mode = "w" if not self._debug_log_file_initialized else "a"
        try:
            with open(self.debug_log_file_path, mode, encoding="utf-8") as handle:
                handle.write(line + "\n")
            self._debug_log_file_initialized = True
        except Exception:
            pass

    @staticmethod
    def _write_console_log(line: str, color_enabled: bool = True) -> None:
        """Пишет лог в stdout без использования print."""
        try:
            if color_enabled:
                sys.stdout.write(SpriteProGame._colorize_console_line(line) + "\n")
            else:
                sys.stdout.write(line + "\n")
            sys.stdout.flush()
        except Exception:
            pass

    @staticmethod
    def _colorize_console_line(line: str) -> str:
        """Добавляет ANSI-цвет в зависимости от уровня лога."""
        reset = "\x1b[0m"
        if "[error]" in line.lower():
            return f"\x1b[31m{line}{reset}"
        if "[warning]" in line.lower():
            return f"\x1b[33m{line}{reset}"
        if "[info]" in line.lower():
            return f"\x1b[32m{line}{reset}"
        if "[log]" in line.lower():
            return f"\x1b[36m{line}{reset}"
        return line

    @staticmethod
    def _detect_update_signature(obj) -> bool:
        """Определяет, принимает ли update аргумент dt."""
        try:
            sig = inspect.signature(obj.update)
        except (TypeError, ValueError, AttributeError):
            return False
        params = list(sig.parameters.values())
        if not params:
            return False
        if params[0].name == "self":
            params = params[1:]
        return len(params) >= 1


@dataclass
class _UpdateEntry:
    obj: object
    supports_dt: bool = False


@dataclass
class _DebugLogEntry:
    text: str
    color: Tuple[int, int, int]
    ttl: float
    age: float = 0.0
