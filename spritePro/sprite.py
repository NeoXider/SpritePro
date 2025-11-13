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
    """Base sprite class with movement, animation, and visual effects support.

    This class extends pygame.sprite.Sprite with additional functionality for:
    - Movement and velocity control
    - Rotation and scaling
    - Transparency and color tinting
    - State management
    - Collision detection
    - Movement boundaries

    Attributes:
        auto_flip (bool): Whether to automatically flip sprite horizontally when moving left/right.
        stop_threshold (float): Distance threshold for stopping movement.
        color (Tuple[int, int, int]): Current color tint of the sprite.
        active (bool): Whether the sprite is active and should be rendered.
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
    ):
        """Initializes a new sprite instance.

        Args:
            sprite (str): Path to sprite image or resource name.
            size (tuple, optional): Sprite dimensions (width, height). Defaults to (50, 50).
            pos (tuple, optional): Initial position (x, y). Defaults to (0, 0).
            speed (float, optional): Movement speed. Defaults to 0.
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
        self.rect.center = self.start_pos
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
        return self._scale

    @scale.setter
    def scale(self, value: float):
        if self._scale != value:
            self._scale = value
            self._transform_dirty = True

    def get_scale(self) -> float:
        """Gets the current scale of the sprite."""
        return self.scale

    def set_scale(self, value: float):
        """Sets the scale of the sprite."""
        self.scale = value

    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float):
        if self._angle != value:
            self._angle = value
            self._transform_dirty = True

    def get_angle(self) -> float:
        """Gets the current angle of the sprite."""
        return self.angle

    def set_angle(self, value: float):
        """Sets the angle of the sprite."""
        self.angle = value

    def rotate_to(self, value: float):
        """Alias for set_angle."""
        self.set_angle(value)

    @property
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        value = max(0, min(255, value))
        if self._alpha != value:
            self._alpha = value
            self._color_dirty = True

    def get_alpha(self) -> int:
        """Gets the current alpha transparency of the sprite."""
        return self.alpha

    def set_alpha(self, value: int):
        """Sets the alpha transparency of the sprite."""
        self.alpha = value

    @property
    def color(self) -> Optional[Tuple[int, int, int]]:
        return self._color

    @color.setter
    def color(self, value: Optional[Tuple[int, int, int]]):
        if self._color != value:
            self._color = value
            self._color_dirty = True

    def set_color(self, value: Tuple[int, int, int]):
        """Sets the color of the sprite. For backward compatibility."""
        self.color = value

    def set_sorting_order(self, order: int) -> None:
        """Sets drawing order (layer) similar to Unity's `sortingOrder`. Lower is back, higher is front."""
        self.sorting_order = int(order)
        try:
            spritePro.get_game().set_sprite_layer(self, self.sorting_order)
        except Exception:
            pass

    def set_screen_space(self, locked: bool = True) -> None:
        """Фиксирует спрайт к экрану (без смещения камерой)."""
        self.screen_space = locked

    def set_parent(self, parent: Optional["Sprite"], keep_world_position: bool = True) -> None:
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
        """Устанавливает позицию и обновляет стартовые координаты."""
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
        """Gets the current position of the sprite (center coordinates)."""
        return self.rect.center

    @property
    def position(self) -> Tuple[int, int]:
        """Центральная позиция спрайта (x, y)."""
        return self.rect.center

    @position.setter
    def position(self, value: VectorInput):
        """Устанавливает центральную позицию спрайта."""
        vec = _coerce_vector2(value, (0, 0))
        self.set_position((int(vec.x), int(vec.y)), anchor=Anchor.CENTER)

    @property
    def x(self) -> int:
        """X координата центра спрайта."""
        return self.rect.centerx

    @x.setter
    def x(self, value: float):
        """Устанавливает X координату центра спрайта."""
        self.rect.centerx = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def y(self) -> int:
        """Y координата центра спрайта."""
        return self.rect.centery

    @y.setter
    def y(self, value: float):
        """Устанавливает Y координату центра спрайта."""
        self.rect.centery = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def width(self) -> int:
        """Ширина спрайта."""
        return self.size[0]

    @width.setter
    def width(self, value: float):
        """Устанавливает ширину спрайта."""
        new_size = (int(value), self.size[1])
        self.set_image(self._image_source, size=new_size)

    @property
    def height(self) -> int:
        """Высота спрайта."""
        return self.size[1]

    @height.setter
    def height(self, value: float):
        """Устанавливает высоту спрайта."""
        new_size = (self.size[0], int(value))
        self.set_image(self._image_source, size=new_size)

    def get_size(self) -> Tuple[int, int]:
        """Gets the current size of the sprite (width, height)."""
        return self.size

    def get_world_position(self) -> Vector2:
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
        """Sets a new image for the sprite.

        Args:
            image_source (Union[str, Path, pygame.Surface]): Path to image file or Surface object.
            size (Optional[VectorInput]): New dimensions (width, height) or None to keep original size.
        
        Notes:
            Falls back to a transparent surface if the file is missing.
            The placeholder is tinted only when a sprite color is already set.
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
        if self._game_registered:
            spritePro.unregister_sprite(self)
            self._game_registered = False
        for child in self.children[:]:
            child.set_parent(None, keep_world_position=True)
        super().kill()

    def set_native_size(self):
        """Resets the sprite to its original image dimensions.

        Reloads the image at its native width and height.
        """
        # перезагружаем изображение без параметра size → ставит оригинальный размер
        self.set_image(self._image_source, size=None)

    def update(self, screen: pygame.Surface = None):
        """Updates sprite state and renders it to the window.

        Args:
            screen (pygame.Surface): Surface to render the sprite on.
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
        """Sets the horizontal and vertical flip states of the sprite."""
        if self.flipped_h != flip_h or self.flipped_v != flip_v:
            self.flipped_h = flip_h
            self.flipped_v = flip_v
            self._transform_dirty = True

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool):
        """Включает или выключает спрайт и синхронизирует его с глобальной группой."""
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
        """Gets the current active state of the sprite."""
        return self.active

    def set_active(self, value: bool):
        """Sets the active state of the sprite."""
        self.active = value

    def reset_sprite(self):
        """Resets the sprite to its initial position and state."""
        self.rect.center = self.start_pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = "idle"

    def move(self, dx: float, dy: float):
        """Moves the sprite by the specified distance.

        Args:
            dx (float): Distance to move on X axis.
            dy (float): Distance to move on Y axis.
        """
        cx, cy = self.rect.center
        self.rect.center = (int(cx + dx * self.speed), int(cy + dy * self.speed))

    def move_towards(
        self, target_pos: Tuple[float, float], speed: Optional[float] = None, use_dt: bool = False
    ):
        """Moves the sprite towards a target position.

        Args:
            target_pos (Tuple[float, float]): Target position (x, y).
            speed (Optional[float]): Movement speed. If None, uses self.speed.
            use_dt (bool): Whether to use delta time for frame-rate independent movement. Defaults to False.
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
        """Sets the sprite's velocity directly.

        Args:
            vx (float): Velocity on X axis.
            vy (float): Velocity on Y axis.
        """
        self.velocity.x = vx
        self.velocity.y = vy

    def get_velocity(self) -> Tuple[float, float]:
        """Gets the current velocity of the sprite."""
        return (self.velocity.x, self.velocity.y)

    def move_up(self, speed: Optional[float] = None):
        """Moves the sprite upward.

        Args:
            speed (Optional[float]): Movement speed. If None, uses self.speed.
        """

        self.velocity.y = -(speed or self.speed)
        self.state = "moving"

    def move_down(self, speed: Optional[float] = None):
        """Moves the sprite downward.

        Args:
            speed (Optional[float]): Movement speed. If None, uses self.speed.
        """
        self.velocity.y = speed or self.speed
        self.state = "moving"

    def move_left(self, speed: Optional[float] = None):
        """Moves the sprite leftward.

        Args:
            speed (Optional[float]): Movement speed. If None, uses self.speed.
        """
        self.velocity.x = -(speed or self.speed)
        if self.auto_flip:
            self.set_flip(True, self.flipped_v)
        self.state = "moving"

    def move_right(self, speed: Optional[float] = None):
        """Moves the sprite rightward.

        Args:
            speed (Optional[float]): Movement speed. If None, uses self.speed.
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
        """Handles keyboard input for sprite movement.

        Args:
            up_key (int, optional): Key code for upward movement. Defaults to pygame.K_UP.
            down_key (int, optional): Key code for downward movement. Defaults to pygame.K_DOWN.
            left_key (int, optional): Key code for leftward movement. Defaults to pygame.K_LEFT.
            right_key (int, optional): Key code for rightward movement. Defaults to pygame.K_RIGHT.
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
        """Stops the sprite's movement and resets velocity."""
        self.velocity.x = 0
        self.velocity.y = 0



    def rotate_by(self, angle_change: float):
        """Rotates the sprite by a relative angle.

        Args:
            angle_change (float): Angle change in degrees.
        """
        if angle_change != 0:
            self.angle += angle_change
            self._transform_dirty = True





    def fade_by(self, amount: int, min_alpha: int = 0, max_alpha: int = 255):
        """Changes the sprite's transparency by a relative amount.

        Args:
            amount (int): Amount to change alpha by.
            min_alpha (int, optional): Minimum alpha value. Defaults to 0.
            max_alpha (int, optional): Maximum alpha value. Defaults to 255.
        """
        new_alpha = max(min_alpha, min(max_alpha, self.alpha + amount))
        if self.alpha != new_alpha:
            self.alpha = new_alpha
            self._color_dirty = True

    def scale_by(self, amount: float, min_scale: float = 0.0, max_scale: float = 2.0):
        """Changes the sprite's scale by a relative amount.

        Args:
            amount (float): Amount to change scale by.
            min_scale (float, optional): Minimum scale value. Defaults to 0.0.
            max_scale (float, optional): Maximum scale value. Defaults to 2.0.
        """
        new_scale = max(min_scale, min(max_scale, self.scale + amount))
        if self.scale != new_scale:
            self.scale = new_scale
            self._transform_dirty = True

    def distance_to(self, target: Union["Sprite", VectorInput]) -> float:
        """Calculates the distance to a target.

        The target can be another Sprite, a Vector2, or a tuple of coordinates.

        Args:
            target (Union[Sprite, VectorInput]): The target to measure the distance to.

        Returns:
            float: The distance between the sprite's center and the target.
            
        Raises:
            TypeError: If the target is not a valid type.
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
        """Sets the sprite's current state.

        Args:
            state (str): New state name.
        """
        if state in self.states:
            self.state = state

    def is_in_state(self, state: str) -> bool:
        """Checks if sprite is in a specific state.

        Args:
            state (str): State name to check.

        Returns:
            bool: True if sprite is in the specified state.
        """
        return self.state == state

    def is_visible_on_screen(self, screen: pygame.Surface) -> bool:
        """Checks if sprite is visible within screen bounds.

        Args:
            screen (pygame.Surface): Screen surface to check against.

        Returns:
            bool: True if sprite is visible on screen.
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
        """Limits sprite movement within specified bounds.

        Args:
            bounds (pygame.Rect): Boundary rectangle.
            check_left (bool, optional): Whether to check left boundary. Defaults to True.
            check_right (bool, optional): Whether to check right boundary. Defaults to True.
            check_top (bool, optional): Whether to check top boundary. Defaults to True.
            check_bottom (bool, optional): Whether to check bottom boundary. Defaults to True.
            padding_left (int, optional): Left padding. Defaults to 0.
            padding_right (int, optional): Right padding. Defaults to 0.
            padding_top (int, optional): Top padding. Defaults to 0.
            padding_bottom (int, optional): Bottom padding. Defaults to 0.
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
        """Sets or overwrites the list of sprites to collide with.

        Args:
            obstacles (list): A list or pygame.sprite.Group of sprites.
        """
        self.collision_targets = list(obstacles)

    def add_collision_target(self, obstacle):
        """Adds a single sprite to the collision list."""
        if self.collision_targets is None:
            self.collision_targets = []
        if obstacle not in self.collision_targets:
            self.collision_targets.append(obstacle)

    def add_collision_targets(self, obstacles: list):
        """Adds a list or group of sprites to the collision list."""
        if self.collision_targets is None:
            self.collision_targets = []
        for obstacle in obstacles:
            if obstacle not in self.collision_targets:
                self.collision_targets.append(obstacle)

    def remove_collision_target(self, obstacle):
        """Removes a single sprite from the collision list."""
        if self.collision_targets:
            try:
                self.collision_targets.remove(obstacle)
            except ValueError:
                pass  # Ignore if obstacle is not in the list

    def remove_collision_targets(self, obstacles: list):
        """Removes a list or group of sprites from the collision list."""
        if self.collision_targets:
            for obstacle in obstacles:
                try:
                    self.collision_targets.remove(obstacle)
                except ValueError:
                    pass

    def clear_collision_targets(self):
        """Disables all collisions for this sprite."""
        self.collision_targets = None

    def play_sound(self, sound_file: str):
        """Plays a sound effect.

        Args:
            sound_file (str): Path to sound file.
        """
        try:
            self.sound = pygame.mixer.Sound(sound_file)
            self.sound.play()
        except:
            print("Ошибка загрузки звука: " + sound_file)


if __name__ == "__main__":
    spritePro.init()
    # cоздание окна
    spritePro.get_screen((800, 600), "Sprite")

    # игрок
    img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.rect(img, (255, 255, 255, 255), img.get_rect(), 8, 1000)

    player = Sprite(img, (100, 100), (spritePro.WH_C), 5)
    player.set_color((100, 255, 100))

    # враг
    img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.rect(img, (255, 255, 255, 255), img.get_rect(), 13)

    enemy = Sprite(img, (50, 50), (50, 50), 3)
    enemy.set_alpha(0)
    enemy.rotate = 17
    enemy.set_color((255, 10, 30))

    # группа спрайтов
    game_sprites = pygame.sprite.Group()
    game_sprites.add((player, enemy))

    spritePro.screen.fill((0, 0, 100))

    while True:
        spritePro.update()

        player.handle_keyboard_input()
        enemy.move_towards(player.rect.center)
        enemy.rotate_by(enemy.rotate)
        game_sprites.update()

        for s in game_sprites:
            s.limit_movement(spritePro.screen.get_rect())

        if enemy.rect.colliderect(player.rect):
            player.set_color((0, random.randint(100, 255), 0))
            enemy.fade_by(5, 10, 255)
            player.scale_by(-0.05, 0.3, 1)
        else:
            enemy.fade_by(-5, 10, 255)
            player.scale_by(0.05, 0.3, 1)
