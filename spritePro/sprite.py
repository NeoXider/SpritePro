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
    stop_threshold = 1.0
    color = None
    active = True

    def __init__(
        self,
        sprite: str,
        size: VectorInput = (50, 50),
        pos: VectorInput = (0, 0),
        speed: float = 0,
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
        self._game_registered = False
        self.screen_space = False
        self.parent: Optional["Sprite"] = None
        self.children: List["Sprite"] = []
        self.local_offset = Vector2()
        self.flipped_h = False
        self.flipped_v = False
        self.color = (255, 255, 255)
        self.angle = 0
        self.scale = 1.0
        self.alpha = 255
        self.state = "idle"
        self.states = {"idle", "moving", "hit", "attacking", "dead"}

        self.set_image(sprite, self.size_vector)
        self.rect.center = self.start_pos
        spritePro.register_sprite(self)
        self._game_registered = True

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
        anchor_key = anchor.lower() if isinstance(anchor, str) else anchor
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

    def set_color(self, color: Tuple):
        """Sets the color tint for the sprite.

        If the sprite has an image, the color is applied as a tint using BLEND_RGBA_MULT.
        If no image is present, the sprite will be filled with this color.

        Args:
            color (Tuple): RGB color tuple.
        """
        self.color = color
        self._update_image()

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
        self.image = img.copy()
        existing_rect = getattr(self, "rect", None)
        if existing_rect is not None:
            target_center = existing_rect.center
        else:
            target_center = getattr(self, "start_pos", None)
        self.rect = self.image.get_rect()
        if target_center is not None:
            self.rect.center = (int(target_center[0]), int(target_center[1]))
        self._set_world_center(Vector2(self.rect.center))
        self.mask = pygame.mask.from_surface(self.image)
        self._update_image()

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
        if self.velocity.length() > 0:
            cx, cy = self.rect.center
            self.rect.center = (int(cx + self.velocity.x), int(cy + self.velocity.y))
        # Обновляем маску коллизии если изображение изменилось
        self.mask = pygame.mask.from_surface(self.image)
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
        """Updates the sprite image with all visual effects applied.

        Applies transformations in order: flip → scale → rotate → alpha → color tint.
        """
        img = self.original_image.copy()

        # Применяем отражение
        if self.flipped_h or self.flipped_v:
            img = pygame.transform.flip(img, self.flipped_h, self.flipped_v)

        # Применяем масштаб
        if self.scale != 1.0:
            new_size = (
                int(img.get_width() * self.scale),
                int(img.get_height() * self.scale),
            )
            img = pygame.transform.scale(img, new_size)

        # Применяем вращение
        if self.angle != 0:
            img = pygame.transform.rotate(img, self.angle)

        # Применяем прозрачность
        if self.alpha != 255:
            img.set_alpha(self.alpha)

        # Обновляем изображение и прямоугольник
        self.image = img

        if self.color is not None:
            self.image.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)

        # Сохраняем центр
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def set_active(self, active: bool):
        """Включает или выключает спрайт и синхронизирует его с глобальной группой."""
        if self.active == active:
            return
        self.active = active
        if active:
            spritePro.enable_sprite(self)
            self._game_registered = True
        else:
            spritePro.disable_sprite(self)
            self._game_registered = False

        for child in list(self.children):
            if hasattr(child, "set_active"):
                child.set_active(active)

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
        self, target_pos: Tuple[float, float], speed: Optional[float] = None
    ):
        """Moves the sprite towards a target position.

        Args:
            target_pos (Tuple[float, float]): Target position (x, y).
            speed (Optional[float]): Movement speed. If None, uses self.speed.
        """
        if speed is None:
            speed = self.speed
        if speed <= 0:
            return
        current_pos = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(target_pos)
        direction = target_vector - current_pos
        distance = direction.length()

        dt = getattr(spritePro, "dt", 0.0) or 0.0
        if dt <= 0:
            dt = 1.0 / 60.0
        step_distance = speed * dt

        if distance <= self.stop_threshold or distance <= step_distance:
            self.rect.center = (int(target_vector.x), int(target_vector.y))
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
            return

        direction.normalize_ip()
        self.velocity = direction * step_distance
        self.state = "moving"

    def set_velocity(self, vx: float, vy: float):
        """Sets the sprite's velocity directly.

        Args:
            vx (float): Velocity on X axis.
            vy (float): Velocity on Y axis.
        """
        self.velocity.x = vx
        self.velocity.y = vy

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
            self.flipped_h = True
            self._update_image()
        self.state = "moving"

    def move_right(self, speed: Optional[float] = None):
        """Moves the sprite rightward.

        Args:
            speed (Optional[float]): Movement speed. If None, uses self.speed.
        """
        self.velocity.x = speed or self.speed
        if self.auto_flip:
            self.flipped_h = False
            self._update_image()
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
                    self.flipped_h = True
                    self._update_image()
                was_moving = True
        if right_key is not None:
            if keys[right_key]:
                self.velocity.x = self.speed
                if self.auto_flip:
                    self.flipped_h = False
                    self._update_image()
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

    def rotate_to(self, angle: float):
        """Rotates the sprite to a specific angle.

        Args:
            angle (float): Target angle in degrees.
        """
        self.angle = angle
        self._update_image()

    def rotate_by(self, angle_change: float):
        """Rotates the sprite by a relative angle.

        Args:
            angle_change (float): Angle change in degrees.
        """
        self.angle += angle_change
        self._update_image()

    def set_scale(self, scale: float):
        """Sets the sprite's scale factor.

        Args:
            scale (float): New scale factor.
        """
        self.scale = scale
        self._update_image()

    def set_alpha(self, alpha: int):
        """Sets the sprite's transparency level.

        Args:
            alpha (int): Alpha value (0-255, where 0 is fully transparent).
        """
        self.alpha = max(0, min(255, alpha))
        self._update_image()

    def fade_by(self, amount: int, min_alpha: int = 0, max_alpha: int = 255):
        """Changes the sprite's transparency by a relative amount.

        Args:
            amount (int): Amount to change alpha by.
            min_alpha (int, optional): Minimum alpha value. Defaults to 0.
            max_alpha (int, optional): Maximum alpha value. Defaults to 255.
        """
        self.alpha = max(min_alpha, min(max_alpha, self.alpha + amount))
        self._update_image()

    def scale_by(self, amount: float, min_scale: float = 0.0, max_scale: float = 2.0):
        """Changes the sprite's scale by a relative amount.

        Args:
            amount (float): Amount to change scale by.
            min_scale (float, optional): Minimum scale value. Defaults to 0.0.
            max_scale (float, optional): Maximum scale value. Defaults to 2.0.
        """
        self.scale = max(min_scale, min(max_scale, self.scale + amount))
        self._update_image()

    def distance_to(self, other_sprite) -> float:
        """Calculates distance to another sprite.

        Args:
            other_sprite (Sprite): Target sprite to measure distance to.

        Returns:
            float: Distance between sprite centers.
        """
        return math.sqrt(
            (self.rect.centerx - other_sprite.rect.centerx) ** 2
            + (self.rect.centery - other_sprite.rect.centery) ** 2
        )

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
