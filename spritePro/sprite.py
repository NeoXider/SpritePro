import random
from typing import Tuple, Optional, Union, Sequence, List
import pygame
from pygame.math import Vector2
import math

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

import spritePro
from .constants import Anchor


VectorInput = Union[Vector2, Sequence[Union[int, float]]]


def _coerce_vector2(value: Optional[VectorInput], default: Tuple[float, float]) -> Vector2:
    if value is None:
        value = default
    if isinstance(value, Vector2):
        return value.copy()
    if isinstance(value, (str, bytes)):
        raise TypeError(f"Expected 2D coordinate, got {type(value)!r}")
    try:
        x, y = value[:2]  # type: ignore[index]
    except (TypeError, ValueError, IndexError):
        raise TypeError(f"Expected 2D coordinate, got {type(value)!r}") from None
    return Vector2(float(x), float(y))


def _vector2_to_int_tuple(vec: Vector2) -> Tuple[int, int]:
    return int(vec.x), int(vec.y)


class Sprite(pygame.sprite.Sprite):
    """Базовый класс спрайта с поддержкой движения, анимации и визуальных эффектов.

    Расширяет pygame.sprite.Sprite дополнительным функционалом для:
    - Управления движением и скоростью
    - Вращения и масштабирования
    - Прозрачности и цветовой тонировки
    - Управления состоянием
    - Обнаружения коллизий
    - Ограничений движения
    - Иерархии спрайтов (родитель-потомок)
    - Работы с камерой и экранным пространством

    Attributes:
        auto_flip (bool): Автоматически переворачивать спрайт горизонтально при движении влево/вправо.
        stop_threshold (float): Порог расстояния для остановки движения.
        color (Tuple[int, int, int]): Текущий цветовой оттенок спрайта.
        active (bool): Активен ли спрайт и должен ли отрисовываться.
        velocity (Vector2): Вектор скорости спрайта.
        speed (float): Базовая скорость движения спрайта.
        state (str): Текущее состояние спрайта.
        states (set): Множество доступных состояний.
        angle (float): Угол поворота спрайта в градусах.
        scale (float): Масштаб спрайта.
        alpha (int): Прозрачность спрайта (0-255).
        sorting_order (int | None): Порядок отрисовки (слой).
        parent (Sprite | None): Родительский спрайт.
        children (List[Sprite]): Список дочерних спрайтов.
    """

    auto_flip: bool = True
    stop_threshold: float = 1.0

    def __init__(
        self,
        sprite: str,
        size: VectorInput = (50, 50),
        pos: VectorInput = (0, 0),
        speed: float = 0,
        sorting_order: int | None = None,
        anchor: str | Anchor = Anchor.CENTER,
    ):
        """Инициализирует новый экземпляр спрайта.

        Args:
            sprite (str): Путь к изображению спрайта или имя ресурса.
            size (VectorInput, optional): Размеры спрайта (ширина, высота). По умолчанию (50, 50).
            pos (VectorInput, optional): Начальная позиция (x, y). По умолчанию (0, 0).
            speed (float, optional): Скорость движения. По умолчанию 0.
            sorting_order (int | None, optional): Порядок отрисовки (слой). По умолчанию None.
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию Anchor.CENTER.
        """
        super().__init__()
        self.size_vector = _coerce_vector2(size, (50, 50))
        self.size = _vector2_to_int_tuple(self.size_vector)
        self.start_pos_vector = _coerce_vector2(pos, (0, 0))
        self.start_pos = _vector2_to_int_tuple(self.start_pos_vector)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = speed
        self._active = True
        self._game_registered = False
        self.screen_space = False
        self.parent: Optional["Sprite"] = None
        self.children: List["Sprite"] = []
        self.local_offset = Vector2()
        self.flipped_h = False
        self.flipped_v = False
        self.update_mask = False
        self._mask_dirty = True
        self._transform_dirty = True
        self._color_dirty = True
        self._color = (255, 255, 255)
        self._angle = 0
        self._scale = 1.0
        self._alpha = 255
        self.state = "idle"
        self.states = {"idle", "moving", "hit", "attacking", "dead"}
        self.anchor_key = Anchor.CENTER
        # Drawing order (layer) similar to Unity's sortingOrder
        self.sorting_order: Optional[int] = int(sorting_order) if sorting_order is not None else None
        self.collision_targets = None
        self._transformed_image = None
        self.mask = None

        self.set_image(sprite, self.size_vector)
        # Устанавливаем позицию с указанным якорем
        self.set_position(self.start_pos, anchor=anchor)
        spritePro.register_sprite(self)
        # Apply initial sorting order if provided
        if self.sorting_order is not None:
            try:
                spritePro.get_game().set_sprite_layer(self, int(self.sorting_order))
            except Exception:
                pass
        self._game_registered = True

    @property
    def scale(self) -> float:
        """Масштаб спрайта.
        
        Returns:
            float: Текущий масштаб спрайта (1.0 = оригинальный размер).
        """
        return self._scale

    @scale.setter
    def scale(self, value: float):
        """Устанавливает масштаб спрайта.
        
        Args:
            value (float): Новый масштаб (1.0 = оригинальный размер).
        """
        if self._scale != value:
            self._scale = value
            self._transform_dirty = True

    def get_scale(self) -> float:
        """Получает текущий масштаб спрайта.
        
        Returns:
            float: Текущий масштаб спрайта.
        """
        return self.scale

    def set_scale(self, value: float):
        """Устанавливает масштаб спрайта.
        
        Args:
            value (float): Новый масштаб спрайта.
        """
        self.scale = value

    @property
    def angle(self) -> float:
        """Угол поворота спрайта в градусах.
        
        Returns:
            float: Текущий угол поворота в градусах.
        """
        return self._angle

    @angle.setter
    def angle(self, value: float):
        """Устанавливает угол поворота спрайта.
        
        Args:
            value (float): Новый угол поворота в градусах.
        """
        if self._angle != value:
            self._angle = value
            self._transform_dirty = True

    def get_angle(self) -> float:
        """Получает текущий угол поворота спрайта.
        
        Returns:
            float: Текущий угол поворота в градусах.
        """
        return self.angle

    def set_angle(self, value: float):
        """Устанавливает угол поворота спрайта.
        
        Args:
            value (float): Новый угол поворота в градусах.
        """
        self.angle = value

    def rotate_to(self, value: float):
        """Поворачивает спрайт к указанному углу.
        
        Args:
            value (float): Целевой угол поворота в градусах.
        """
        self.set_angle(value)

    @property
    def alpha(self) -> int:
        """Прозрачность спрайта.
        
        Returns:
            int: Текущая прозрачность (0-255, где 255 = непрозрачный).
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        """Устанавливает прозрачность спрайта.
        
        Args:
            value (int): Новая прозрачность (0-255, где 255 = непрозрачный).
        """
        value = max(0, min(255, value))
        if self._alpha != value:
            self._alpha = value
            self._color_dirty = True

    def get_alpha(self) -> int:
        """Получает текущую прозрачность спрайта.
        
        Returns:
            int: Текущая прозрачность (0-255).
        """
        return self.alpha

    def set_alpha(self, value: int):
        """Устанавливает прозрачность спрайта.
        
        Args:
            value (int): Новая прозрачность (0-255).
        """
        self.alpha = value

    @property
    def color(self) -> Optional[Tuple[int, int, int]]:
        """Цветовой оттенок спрайта.
        
        Returns:
            Optional[Tuple[int, int, int]]: Текущий цветовой оттенок в RGB или None.
        """
        return self._color

    @color.setter
    def color(self, value: Optional[Tuple[int, int, int]]):
        """Устанавливает цветовой оттенок спрайта.
        
        Args:
            value (Optional[Tuple[int, int, int]]): Новый цветовой оттенок в RGB или None.
        """
        if self._color != value:
            self._color = value
            self._color_dirty = True

    def set_color(self, value: Tuple[int, int, int]):
        """Устанавливает цвет спрайта (для обратной совместимости).
        
        Args:
            value (Tuple[int, int, int]): Новый цвет в формате RGB.
        """
        self.color = value

    def set_sorting_order(self, order: int) -> None:
        """Устанавливает порядок отрисовки (слой), аналогично Unity's sortingOrder.
        
        Меньшие значения отрисовываются сзади, большие - спереди.
        
        Args:
            order (int): Новый порядок отрисовки.
        """
        self.sorting_order = int(order)
        try:
            spritePro.get_game().set_sprite_layer(self, self.sorting_order)
        except Exception:
            pass

    def set_screen_space(self, locked: bool = True) -> None:
        """Фиксирует спрайт к экрану (без смещения камерой).
        
        Args:
            locked (bool, optional): Если True, спрайт не будет смещаться камерой. По умолчанию True.
        """
        self.screen_space = locked

    def set_parent(self, parent: Optional["Sprite"], keep_world_position: bool = True) -> None:
        """Устанавливает родительский спрайт для создания иерархии.
        
        Args:
            parent (Optional[Sprite]): Родительский спрайт или None для удаления родителя.
            keep_world_position (bool, optional): Сохранять ли мировую позицию при установке родителя. По умолчанию True.
        
        Raises:
            ValueError: Если спрайт пытается стать родителем самому себе.
        """
        if parent is self:
            raise ValueError("Sprite cannot be its own parent")
        if parent is self.parent:
            return
        world_pos = self.get_world_position()
        if self.parent:
            try:
                self.parent.children.remove(self)
            except ValueError:
                pass
        self.parent = parent
        if parent:
            if self not in parent.children:
                parent.children.append(self)
            if parent.screen_space:
                self.set_screen_space(True)
            if keep_world_position:
                self.local_offset = world_pos - parent.get_world_position()
            else:
                self.local_offset = Vector2()
            self._apply_parent_transform()
        else:
            if keep_world_position:
                self._set_world_center(world_pos)
            else:
                self._set_world_center(self.get_world_position())
            self.local_offset = Vector2()

    def set_position(self, position: VectorInput, anchor: str | Anchor = Anchor.CENTER) -> None:
        """Устанавливает позицию спрайта с заданным якорем и обновляет стартовые координаты.
        
        Args:
            position (VectorInput): Новая позиция спрайта (x, y).
            anchor (str | Anchor, optional): Якорь для установки позиции. По умолчанию Anchor.CENTER.
        
        Raises:
            ValueError: Если указан неподдерживаемый якорь.
        """
        self.anchor_key = anchor.lower() if isinstance(anchor, str) else anchor
        anchor_key = self.anchor_key
        anchors = Anchor.MAP
        if anchor_key not in anchors:
            raise ValueError(f"Unsupported anchor {anchor!r}")
        vec = _coerce_vector2(position, (0, 0))
        rect = self.rect.copy()
        setattr(rect, anchors[anchor_key], (int(vec.x), int(vec.y)))
        self.rect = rect
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    def get_position(self) -> Tuple[int, int]:
        """Получает текущую позицию спрайта (координаты центра).
        
        Returns:
            Tuple[int, int]: Координаты центра спрайта (x, y).
        """
        return self.rect.center

    @property
    def position(self) -> Tuple[int, int]:
        """Центральная позиция спрайта.
        
        Returns:
            Tuple[int, int]: Координаты центра спрайта (x, y).
        """
        return self.rect.center

    @position.setter
    def position(self, value: VectorInput):
        """Устанавливает центральную позицию спрайта.
        
        Args:
            value (VectorInput): Новые координаты центра (x, y).
        """
        vec = _coerce_vector2(value, (0, 0))
        self.set_position((int(vec.x), int(vec.y)), anchor=Anchor.CENTER)

    @property
    def x(self) -> int:
        """X координата центра спрайта.
        
        Returns:
            int: X координата центра спрайта.
        """
        return self.rect.centerx

    @x.setter
    def x(self, value: float):
        """Устанавливает X координату центра спрайта.
        
        Args:
            value (float): Новая X координата центра.
        """
        self.rect.centerx = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def y(self) -> int:
        """Y координата центра спрайта.
        
        Returns:
            int: Y координата центра спрайта.
        """
        return self.rect.centery

    @y.setter
    def y(self, value: float):
        """Устанавливает Y координату центра спрайта.
        
        Args:
            value (float): Новая Y координата центра.
        """
        self.rect.centery = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def width(self) -> int:
        """Ширина спрайта.
        
        Returns:
            int: Текущая ширина спрайта в пикселях.
        """
        return self.size[0]

    @width.setter
    def width(self, value: float):
        """Устанавливает ширину спрайта.
        
        Args:
            value (float): Новая ширина спрайта в пикселях.
        """
        new_size = (int(value), self.size[1])
        self.set_image(self._image_source, size=new_size)

    @property
    def height(self) -> int:
        """Высота спрайта.
        
        Returns:
            int: Текущая высота спрайта в пикселях.
        """
        return self.size[1]

    @height.setter
    def height(self, value: float):
        """Устанавливает высоту спрайта.
        
        Args:
            value (float): Новая высота спрайта в пикселях.
        """
        new_size = (self.size[0], int(value))
        self.set_image(self._image_source, size=new_size)

    def get_size(self) -> Tuple[int, int]:
        """Получает текущий размер спрайта.
        
        Returns:
            Tuple[int, int]: Размер спрайта (ширина, высота).
        """
        return self.size

    def get_world_position(self) -> Vector2:
        """Получает мировую позицию спрайта (с учетом камеры).
        
        Returns:
            Vector2: Мировая позиция центра спрайта.
        """
        return Vector2(self.rect.center)

    def _set_world_center(self, position: Vector2) -> None:
        self.rect.center = (int(position.x), int(position.y))
        self.start_pos_vector = Vector2(self.rect.center)
        self.start_pos = (self.rect.centerx, self.rect.centery)

    def _apply_parent_transform(self) -> None:
        if not self.parent:
            return
        desired = self.parent.get_world_position() + self.local_offset
        self._set_world_center(desired)

    def _sync_local_offset(self) -> None:
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    def _update_children_world_positions(self) -> None:
        for child in self.children:
            child._apply_parent_transform()
            child._update_children_world_positions()



    def set_image(
        self,
        image_source="",
        size: Optional[VectorInput] = None,
    ):
        """Устанавливает новое изображение для спрайта.

        Args:
            image_source (str | Path | pygame.Surface): Путь к файлу изображения или объект Surface.
            size (Optional[VectorInput]): Новые размеры (ширина, высота) или None для сохранения оригинального размера.
        
        Note:
            Если файл не найден, создается прозрачная поверхность.
            Заглушка окрашивается только если у спрайта уже установлен цвет.
        """
        self._image_source = image_source

        if isinstance(image_source, pygame.Surface):
            img = image_source.copy()
        else:
            try:
                img = pygame.image.load(str(image_source)).convert_alpha()
            except Exception:
                if image_source:
                    print(
                        f"[Sprite] не удалось загрузить изображение для объекта {type(self).__name__} из '{image_source}'"
                    )
                fallback_size = _vector2_to_int_tuple(_coerce_vector2(size, tuple(self.size)))
                img = pygame.Surface(fallback_size, pygame.SRCALPHA)
                if self.color is not None:
                    img.fill(self.color)

        if size is not None:
            requested_size = _coerce_vector2(size, tuple(self.size))
            img = pygame.transform.scale(img, _vector2_to_int_tuple(requested_size))
            self.size_vector = requested_size
            self.size = _vector2_to_int_tuple(requested_size)
        else:
            self.size_vector = Vector2(img.get_width(), img.get_height())
            self.size = _vector2_to_int_tuple(self.size_vector)

        self.original_image = img
        self._transformed_image = self.original_image.copy()
        self.image = self.original_image.copy()
        
        existing_rect = getattr(self, "rect", None)
        if existing_rect is not None:
            # Получаем имя атрибута для текущего якоря (например, 'topleft')
            anchor_attr = Anchor.MAP.get(self.anchor_key, 'center')
            # Сохраняем текущую позицию якоря
            anchor_pos = getattr(existing_rect, anchor_attr)
        else:
            anchor_attr = 'center'
            anchor_pos = getattr(self, "start_pos", (0, 0))

        self.rect = self.image.get_rect()
        
        # Устанавливаем позицию нового rect по сохраненному якорю
        setattr(self.rect, anchor_attr, anchor_pos)

        self._set_world_center(Vector2(self.rect.center))
        self._transform_dirty = True
        self._color_dirty = True
        self._mask_dirty = True

    def kill(self) -> None:
        """Удаляет спрайт из игры и освобождает все связанные ресурсы.
        
        Отменяет регистрацию спрайта, удаляет все дочерние спрайты и вызывает
        родительский метод kill().
        """
        if self._game_registered:
            spritePro.unregister_sprite(self)
            self._game_registered = False
        for child in self.children[:]:
            child.set_parent(None, keep_world_position=True)
        super().kill()

    def set_native_size(self):
        """Сбрасывает спрайт к оригинальным размерам изображения.
        
        Перезагружает изображение с оригинальной шириной и высотой.
        """
        # перезагружаем изображение без параметра size → ставит оригинальный размер
        self.set_image(self._image_source, size=None)

    def update(self, screen: pygame.Surface = None):
        """Обновляет состояние спрайта и отрисовывает его на экране.

        Args:
            screen (pygame.Surface, optional): Поверхность для отрисовки. Если None, используется глобальный экран.
        """
        # Apply velocity
        if self.velocity.length() > 0:
            cx, cy = self.rect.center
            self.rect.center = (int(cx + self.velocity.x), int(cy + self.velocity.y))

        # Resolve collisions automatically if targets are set
        if self.collision_targets is not None:
            self._resolve_collisions()

        self._update_image()

        # Update collision mask if necessary
        if self._mask_dirty:
            # Only update the mask if it's enabled or if it has never been created.
            if self.update_mask or self.mask is None:
                self.mask = pygame.mask.from_surface(self.image)
            self._mask_dirty = False
        if self.active:
            screen = screen or spritePro.screen
            if screen is not None:
                if getattr(self, "screen_space", False):
                    screen.blit(self.image, self.rect)
                else:
                    camera = getattr(spritePro.get_game(), "camera", Vector2())
                    draw_rect = self.rect.copy()
                    draw_rect.x -= int(camera.x)
                    draw_rect.y -= int(camera.y)
                    screen.blit(self.image, draw_rect)
        self._sync_local_offset()
        self._update_children_world_positions()

    def _update_image(self):
        """Updates the sprite image with all visual effects applied."""
        if self._transform_dirty:
            # Create a transformed surface and cache it
            img = self.original_image.copy()
            if self.flipped_h or self.flipped_v:
                img = pygame.transform.flip(img, self.flipped_h, self.flipped_v)
            if self._scale != 1.0:
                new_size = (
                    int(self.original_image.get_width() * self._scale),
                    int(self.original_image.get_height() * self._scale),
                )
                img = pygame.transform.scale(img, new_size)
            if self._angle != 0:
                img = pygame.transform.rotate(img, self._angle)
            
            self._transformed_image = img # cache the transformed image
            
            center = self.rect.center
            self.rect = self._transformed_image.get_rect()
            self.rect.center = center

            self._transform_dirty = False
            self._color_dirty = True  # Force color update after transform
            self._mask_dirty = True

        if self._color_dirty:
            # Start with the transformed image and apply color/alpha
            self.image = self._transformed_image.copy()
            if self._alpha != 255:
                self.image.set_alpha(self._alpha)
            if self._color != (255, 255, 255):
                self.image.fill(self._color, special_flags=pygame.BLEND_RGBA_MULT)
            
            self._color_dirty = False

    def set_flip(self, flip_h: bool, flip_v: bool):
        """Устанавливает состояние горизонтального и вертикального отражения спрайта.
        
        Args:
            flip_h (bool): Отразить спрайт по горизонтали.
            flip_v (bool): Отразить спрайт по вертикали.
        """
        if self.flipped_h != flip_h or self.flipped_v != flip_v:
            self.flipped_h = flip_h
            self.flipped_v = flip_v
            self._transform_dirty = True

    @property
    def active(self) -> bool:
        """Активность спрайта.
        
        Returns:
            bool: True, если спрайт активен и должен отрисовываться.
        """
        return self._active

    @active.setter
    def active(self, value: bool):
        """Включает или выключает спрайт и синхронизирует его с глобальной группой.
        
        Args:
            value (bool): Новое состояние активности.
        """
        if self._active == value:
            return
        self._active = value
        if self._active:
            spritePro.enable_sprite(self)
            self._game_registered = True
        else:
            spritePro.disable_sprite(self)
            self._game_registered = False

        for child in list(self.children):
            if hasattr(child, "set_active"):
                child.set_active(value)

    def get_active(self) -> bool:
        """Получает текущее состояние активности спрайта.
        
        Returns:
            bool: True, если спрайт активен.
        """
        return self.active

    def set_active(self, value: bool):
        """Устанавливает состояние активности спрайта.
        
        Args:
            value (bool): Новое состояние активности.
        """
        self.active = value

    def reset_sprite(self):
        """Сбрасывает спрайт в начальную позицию и состояние.
        
        Восстанавливает начальную позицию, обнуляет скорость и устанавливает
        состояние в "idle".
        """
        self.rect.center = self.start_pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = "idle"

    def move(self, dx: float, dy: float):
        """Перемещает спрайт на указанное расстояние.

        Args:
            dx (float): Расстояние перемещения по оси X.
            dy (float): Расстояние перемещения по оси Y.
        """
        cx, cy = self.rect.center
        self.rect.center = (int(cx + dx * self.speed), int(cy + dy * self.speed))

    def move_towards(
        self, target_pos: Tuple[float, float], speed: Optional[float] = None, use_dt: bool = False
    ):
        """Перемещает спрайт к указанной целевой позиции.

        Args:
            target_pos (Tuple[float, float]): Целевая позиция (x, y).
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
            use_dt (bool, optional): Использовать delta time для независимого от частоты кадров движения. По умолчанию False.
        """
        if speed is None:
            speed = self.speed
        if speed <= 0:
            return
        current_pos = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(target_pos)
        direction = target_vector - current_pos
        distance = direction.length()

        if use_dt:
            dt = getattr(spritePro, "dt", 0.0) or 0.0
            if dt <= 0:
                dt = 1.0 / 60.0
            step_distance = speed * dt
        else:
            step_distance = speed

        if distance <= self.stop_threshold or distance <= step_distance:
            self.rect.center = (int(target_vector.x), int(target_vector.y))
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
            return

        direction.normalize_ip()
        self.velocity = direction * step_distance
        self.state = "moving"
        
        # Auto-flip based on movement direction
        if self.auto_flip and abs(direction.x) > 0.1:  # Only flip if significant horizontal movement
            if direction.x < 0:
                self.set_flip(True, self.flipped_v)
            else:
                self.set_flip(False, self.flipped_v)

    def set_velocity(self, vx: float, vy: float):
        """Устанавливает скорость спрайта напрямую.

        Args:
            vx (float): Скорость по оси X.
            vy (float): Скорость по оси Y.
        """
        self.velocity.x = vx
        self.velocity.y = vy

    def get_velocity(self) -> Tuple[float, float]:
        """Получает текущую скорость спрайта.
        
        Returns:
            Tuple[float, float]: Скорость спрайта (vx, vy).
        """
        return (self.velocity.x, self.velocity.y)

    def move_up(self, speed: Optional[float] = None):
        """Перемещает спрайт вверх.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
        """
        self.velocity.y = -(speed if speed is not None else self.speed)
        self.state = "moving"

    def move_down(self, speed: Optional[float] = None):
        """Перемещает спрайт вниз.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
        """
        self.velocity.y = speed if speed is not None else self.speed
        self.state = "moving"

    def move_left(self, speed: Optional[float] = None):
        """Перемещает спрайт влево.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
        """
        self.velocity.x = -(speed or self.speed)
        if self.auto_flip:
            self.set_flip(True, self.flipped_v)
        self.state = "moving"

    def move_right(self, speed: Optional[float] = None):
        """Перемещает спрайт вправо.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
        """
        self.velocity.x = speed or self.speed
        if self.auto_flip:
            self.set_flip(False, self.flipped_v)
        self.state = "moving"

    def handle_keyboard_input(
        self,
        up_key=pygame.K_UP,
        down_key=pygame.K_DOWN,
        left_key=pygame.K_LEFT,
        right_key=pygame.K_RIGHT,
    ):
        """Обрабатывает ввод с клавиатуры для движения спрайта.

        Args:
            up_key (int, optional): Код клавиши для движения вверх. По умолчанию pygame.K_UP.
            down_key (int, optional): Код клавиши для движения вниз. По умолчанию pygame.K_DOWN.
            left_key (int, optional): Код клавиши для движения влево. По умолчанию pygame.K_LEFT.
            right_key (int, optional): Код клавиши для движения вправо. По умолчанию pygame.K_RIGHT.
        """
        keys = pygame.key.get_pressed()

        # Сбрасываем скорость
        self.velocity.x = 0
        self.velocity.y = 0
        was_moving = False

        # Проверяем нажатые клавиши и устанавливаем скорость
        if up_key is not None:
            if keys[up_key]:
                self.velocity.y = -self.speed
                was_moving = True
        if down_key is not None:
            if keys[down_key]:
                self.velocity.y = self.speed
                was_moving = True
        if left_key is not None:
            if keys[left_key]:
                self.velocity.x = -self.speed
                if self.auto_flip:
                    self.set_flip(True, self.flipped_v)
                was_moving = True
        if right_key is not None:
            if keys[right_key]:
                self.velocity.x = self.speed
                if self.auto_flip:
                    self.set_flip(False, self.flipped_v)
                was_moving = True

        # Обновляем состояние в зависимости от движения
        if was_moving:
            self.state = "moving"
        else:
            if self.state == "moving":
                self.state = "idle"

        # Если двигаемся по диагонали, нормализуем скорость
        if self.velocity.x != 0 and self.velocity.y != 0:
            self.velocity = self.velocity.normalize() * self.speed

    def stop(self):
        """Останавливает движение спрайта и обнуляет скорость."""
        self.velocity.x = 0
        self.velocity.y = 0

    def rotate_by(self, angle_change: float):
        """Поворачивает спрайт на относительный угол.

        Args:
            angle_change (float): Изменение угла в градусах.
        """
        if angle_change != 0:
            self.angle += angle_change
            self._transform_dirty = True





    def fade_by(self, amount: int, min_alpha: int = 0, max_alpha: int = 255):
        """Изменяет прозрачность спрайта на относительное значение.

        Args:
            amount (int): Величина изменения прозрачности.
            min_alpha (int, optional): Минимальное значение прозрачности. По умолчанию 0.
            max_alpha (int, optional): Максимальное значение прозрачности. По умолчанию 255.
        """
        new_alpha = max(min_alpha, min(max_alpha, self.alpha + amount))
        if self.alpha != new_alpha:
            self.alpha = new_alpha
            self._color_dirty = True

    def scale_by(self, amount: float, min_scale: float = 0.0, max_scale: float = 2.0):
        """Изменяет масштаб спрайта на относительное значение.

        Args:
            amount (float): Величина изменения масштаба.
            min_scale (float, optional): Минимальное значение масштаба. По умолчанию 0.0.
            max_scale (float, optional): Максимальное значение масштаба. По умолчанию 2.0.
        """
        new_scale = max(min_scale, min(max_scale, self.scale + amount))
        if self.scale != new_scale:
            self.scale = new_scale
            self._transform_dirty = True

    def distance_to(self, target: Union["Sprite", VectorInput]) -> float:
        """Вычисляет расстояние до цели.

        Целью может быть другой спрайт, Vector2 или кортеж координат.

        Args:
            target (Union[Sprite, VectorInput]): Цель для измерения расстояния.

        Returns:
            float: Расстояние между центром спрайта и целью.
            
        Raises:
            TypeError: Если цель имеет неподдерживаемый тип.
        """
        target_pos: Vector2
        if isinstance(target, Sprite):
            target_pos = target.get_world_position()
        elif isinstance(target, Vector2):
            target_pos = target
        elif isinstance(target, (list, tuple)):
            target_pos = Vector2(target)
        else:
            raise TypeError(f"Unsupported target type for distance calculation: {type(target)}")

        return self.get_world_position().distance_to(target_pos)

    def set_state(self, state: str):
        """Устанавливает текущее состояние спрайта.

        Args:
            state (str): Имя нового состояния.
        """
        if state in self.states:
            self.state = state

    def is_in_state(self, state: str) -> bool:
        """Проверяет, находится ли спрайт в указанном состоянии.

        Args:
            state (str): Имя состояния для проверки.

        Returns:
            bool: True, если спрайт находится в указанном состоянии.
        """
        return self.state == state

    def is_visible_on_screen(self, screen: pygame.Surface) -> bool:
        """Проверяет, виден ли спрайт в пределах экрана.

        Args:
            screen (pygame.Surface): Поверхность экрана для проверки.

        Returns:
            bool: True, если спрайт виден на экране.
        """
        # Получаем прямоугольник экрана
        screen_rect = screen.get_rect()

        # Получаем прямоугольник спрайта
        sprite_rect = self.rect

        # Проверяем пересечение прямоугольников
        return screen_rect.colliderect(sprite_rect)

    def limit_movement(
        self,
        bounds: pygame.Rect,
        check_left: bool = True,
        check_right: bool = True,
        check_top: bool = True,
        check_bottom: bool = True,
        padding_left: int = 0,
        padding_right: int = 0,
        padding_top: int = 0,
        padding_bottom: int = 0,
    ):
        """Ограничивает движение спрайта в пределах указанных границ.

        Args:
            bounds (pygame.Rect): Прямоугольник границ.
            check_left (bool, optional): Проверять ли левую границу. По умолчанию True.
            check_right (bool, optional): Проверять ли правую границу. По умолчанию True.
            check_top (bool, optional): Проверять ли верхнюю границу. По умолчанию True.
            check_bottom (bool, optional): Проверять ли нижнюю границу. По умолчанию True.
            padding_left (int, optional): Отступ слева. По умолчанию 0.
            padding_right (int, optional): Отступ справа. По умолчанию 0.
            padding_top (int, optional): Отступ сверху. По умолчанию 0.
            padding_bottom (int, optional): Отступ снизу. По умолчанию 0.
        """
        if check_left and self.rect.left < bounds.left + padding_left:
            self.rect.left = bounds.left + padding_left
        if check_right and self.rect.right > bounds.right - padding_right:
            self.rect.right = bounds.right - padding_right
        if check_top and self.rect.top < bounds.top + padding_top:
            self.rect.top = bounds.top + padding_top
        if check_bottom and self.rect.bottom > bounds.bottom - padding_bottom:
            self.rect.bottom = bounds.bottom - padding_bottom

    def _resolve_collisions(self):
        """Internal method to resolve penetrations with `self.collision_targets`."""
        if not self.collision_targets:
            return

        # Filter out killed sprites to prevent errors
        self.collision_targets = [s for s in self.collision_targets if s.alive()]

        collider_rect = getattr(self, 'collide', self).rect

        for obstacle in self.collision_targets:
            if not hasattr(obstacle, 'rect'):
                continue

            if collider_rect.colliderect(obstacle.rect):
                # Calculate overlap vector
                overlap_x = min(collider_rect.right, obstacle.rect.right) - max(collider_rect.left, obstacle.rect.left)
                overlap_y = min(collider_rect.bottom, obstacle.rect.bottom) - max(collider_rect.top, obstacle.rect.top)

                # Resolve collision by pushing out on the axis of smaller overlap
                if overlap_x < overlap_y:
                    # Push horizontally
                    if collider_rect.centerx < obstacle.rect.centerx:
                        self.rect.x -= overlap_x
                    else:
                        self.rect.x += overlap_x
                else:
                    # Push vertically
                    if collider_rect.centery < obstacle.rect.centery:
                        self.rect.y -= overlap_y
                    else:
                        self.rect.y += overlap_y
                
                # Sync collider after resolution
                if hasattr(self, 'collide'):
                    collider_rect.center = self.rect.center

    def set_collision_targets(self, obstacles: list):
        """Устанавливает или перезаписывает список спрайтов для коллизий.

        Args:
            obstacles (list): Список спрайтов или pygame.sprite.Group.
        """
        self.collision_targets = list(obstacles)

    def add_collision_target(self, obstacle):
        """Добавляет один спрайт в список коллизий.
        
        Args:
            obstacle: Спрайт для добавления в список коллизий.
        """
        if self.collision_targets is None:
            self.collision_targets = []
        if obstacle not in self.collision_targets:
            self.collision_targets.append(obstacle)

    def add_collision_targets(self, obstacles: list):
        """Добавляет список или группу спрайтов в список коллизий.
        
        Args:
            obstacles (list): Список или группа спрайтов для добавления.
        """
        if self.collision_targets is None:
            self.collision_targets = []
        for obstacle in obstacles:
            if obstacle not in self.collision_targets:
                self.collision_targets.append(obstacle)

    def remove_collision_target(self, obstacle):
        """Удаляет один спрайт из списка коллизий.
        
        Args:
            obstacle: Спрайт для удаления из списка коллизий.
        """
        if self.collision_targets:
            try:
                self.collision_targets.remove(obstacle)
            except ValueError:
                pass  # Ignore if obstacle is not in the list

    def remove_collision_targets(self, obstacles: list):
        """Удаляет список или группу спрайтов из списка коллизий.
        
        Args:
            obstacles (list): Список или группа спрайтов для удаления.
        """
        if self.collision_targets:
            for obstacle in obstacles:
                try:
                    self.collision_targets.remove(obstacle)
                except ValueError:
                    pass

    def clear_collision_targets(self):
        """Отключает все коллизии для этого спрайта."""
        self.collision_targets = None


