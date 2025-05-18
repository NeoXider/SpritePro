import os
from typing import Tuple, Optional, Union
import pygame
import math
from pathlib import Path


class Sprite(pygame.sprite.Sprite):
    auto_flip: bool = True
    stop_threshold = 1.0
    color = None
    active = True

    def __init__(
        self,
        sprite: str,
        size: tuple = (50, 50),
        pos: tuple = (0, 0),
        speed: float = 0,
    ):
        """
        Инициализация спрайта.

        Аргументы:
            sprite: Путь к изображению спрайта или имя ресурса
            size: Размер спрайта (ширина, высота) по умолчанию (50, 50)
            pos: Начальная позиция спрайта (x, y) по умолчанию (0, 0)
            speed: Скорость движения спрайта по умолчанию 0
        """
        super().__init__()
        self.size = size
        self.start_pos = pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = speed
        self.flipped_h = False
        self.flipped_v = False
        self.color = (255, 255, 255)
        self.angle = 0
        self.scale = 1.0
        self.alpha = 255
        self.state = "idle"
        self.states = {"idle", "moving", "hit", "attacking", "dead"}

        self.set_image(sprite, size)
        self.rect.center = pos

    def set_color(self, color: Tuple):
        """
        Устанавливает цветовой оттенок (tint) для спрайта.

        Если у спрайта есть изображение, цвет применяется как оттенок (tint) с помощью режима BLEND_RGBA_MULT.
        Если изображения нет, спрайт будет просто закрашен этим цветом.
        """
        self.color = color
        self._update_image()

    def set_image(
        self,
        image_source="",
        size: Optional[Tuple[int, int]] = None,
    ):
        """
        Устанавливает новое изображение для спрайта.
        image_source: путь к файлу (str/Path) или Surface
        size: кортеж (ширина, высота) или None (оставить оригинальный размер)
        """
        img = None
        if isinstance(image_source, pygame.Surface):
            img = image_source.copy()
        else:
            try:
                img = pygame.image.load(str(image_source)).convert_alpha()
            except Exception:
                print(
                    f"[Sprite] Не удалось загрузить картинку для объекта {type(self).__name__} из '{image_source}'"
                )
                img = pygame.Surface(size or self.size, pygame.SRCALPHA)
                img.fill(self.color)
        if size is not None:
            img = pygame.transform.scale(img, size)
            self.size = size
        else:
            self.size = (img.get_width(), img.get_height())
        self.original_image = img
        self.image = img.copy()
        center = getattr(self, "rect", None)
        center = center.center if center is not None else None
        self.rect = self.image.get_rect()
        if center:
            self.rect.center = center
        self.mask = pygame.mask.from_surface(self.image)
        self._update_image()

    def update(self, window: pygame.Surface):
        """Обновление состояния спрайта.
        
            Аргументы:
                window (pygame.Surface): Окно для рисования спрайта.
        """
        if self.velocity.length() > 0:
            cx, cy = self.rect.center
            self.rect.center = (int(cx + self.velocity.x), int(cy + self.velocity.y))
        # Обновляем маску коллизии если изображение изменилось
        self.mask = pygame.mask.from_surface(self.image)
        if self.active:
            window.blit(self.image, self.rect)

    def _update_image(self):
        """Обновляет изображение с учетом всех визуальных эффектов."""
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
        """Устанавливает активность спрайта.
        Аргументы:
           active: Булевый флаг активности (True - активен, False - неактивен)
        """
        self.active = active

    def reset_sprite(self):
        """Возвращает спрайт в стартовую позицию."""
        self.rect.center = self.start_pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = "idle"

    def move(self, dx: float, dy: float):
        """
        Перемещение спрайта на заданное расстояние.
        Аргументы:
            dx: Скорость перемещения по оси X
            dy: Скорость перемещения по оси Y
        """
        cx, cy = self.rect.center
        self.rect.center = (int(cx + dx * self.speed), int(cy + dy * self.speed))

    def move_towards(
        self, target_pos: Tuple[float, float], speed: Optional[float] = None
    ):
        """
        Перемещение спрайта в направлении целевой позиции.

        Аргументы:
            target_pos: Целевая позиция (x, y)
            speed: Опциональная скорость движения (если None, используется self.speed)
        """
        if speed is None:
            speed = self.speed
        current_pos = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(target_pos)
        direction = target_vector - current_pos
        distance = direction.length()
        if distance < self.stop_threshold:
            self.rect.center = (int(target_vector.x), int(target_vector.y))
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
        else:
            if distance > 0:
                direction = direction / distance * speed
            self.velocity = direction
            self.state = "moving"

    def set_velocity(self, vx: float, vy: float):
        """Прямая установка скорости спрайта."""
        self.velocity.x = vx
        self.velocity.y = vy

    def move_up(self, speed: Optional[float] = None):
        """Перемещение спрайта вверх."""
        self.velocity.y = -(speed or self.speed)
        self.state = "moving"

    def move_down(self, speed: Optional[float] = None):
        """Перемещение спрайта вниз."""
        self.velocity.y = speed or self.speed
        self.state = "moving"

    def move_left(self, speed: Optional[float] = None):
        """Перемещение спрайта влево."""
        self.velocity.x = -(speed or self.speed)
        if self.auto_flip:
            self.flipped_h = True
            self._update_image()
        self.state = "moving"

    def move_right(self, speed: Optional[float] = None):
        """Перемещение спрайта вправо."""
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
        """
        Обработка ввода с клавиатуры для движения спрайта.

        Аргументы:
            up_key: Клавиша для движения вверх (по умолчанию стрелка вверх)
            down_key: Клавиша для движения вниз (по умолчанию стрелка вниз)
            left_key: Клавиша для движения влево (по умолчанию стрелка влево)
            right_key: Клавиша для движения вправо (по умолчанию стрелка вправо)
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
        """Остановка всякого движения."""
        self.velocity.x = 0
        self.velocity.y = 0

    def rotate_to(self, angle: float):
        """Установка вращения спрайта на заданный угол в градусах."""
        self.angle = angle
        self._update_image()

    def rotate_by(self, angle_change: float):
        """Вращение спрайта на заданное количество градусов."""
        self.angle += angle_change
        self._update_image()

    def set_scale(self, scale: float):
        """Установка масштаба спрайта."""
        self.scale = scale
        self._update_image()

    def set_alpha(self, alpha: int):
        """Установка прозрачности спрайта (0-255)."""
        self.alpha = max(0, min(255, alpha))
        self._update_image()

    def fade_by(self, amount: int, min_alpha: int = 0, max_alpha: int = 255):
        """Изменение прозрачности спрайта на заданное количество с ограничениями."""
        self.alpha = max(min_alpha, min(max_alpha, self.alpha + amount))
        self._update_image()

    def scale_by(self, amount: float, min_scale: float = 0.0, max_scale: float = 2.0):
        """Изменение масштаба спрайта на заданное количество с ограничениями."""
        self.scale = max(min_scale, min(max_scale, self.scale + amount))
        self._update_image()

    def distance_to(self, other_sprite) -> float:
        """Расчет расстояния до другого спрайта (от центра к центру)."""
        return math.sqrt(
            (self.rect.centerx - other_sprite.rect.centerx) ** 2
            + (self.rect.centery - other_sprite.rect.centery) ** 2
        )

    def set_state(self, state: str):
        """Установка состояния спрайта, если оно допустимо."""
        if state in self.states:
            self.state = state

    def is_in_state(self, state: str) -> bool:
        """Проверка, находится ли спрайт в заданном состоянии."""
        return self.state == state

    def is_visible_on_screen(self, screen: pygame.Surface) -> bool:
        """Проверка, видим ли спрайт на экране.

        Args:
            screen: Поверхность экрана Pygame

        Returns:
            bool: True если спрайт виден на экране, False в противном случае
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
        """
        Ограничивает движение спрайта в пределах заданных границ с учетом отступов.

        Аргументы:
            bounds: Прямоугольник, определяющий границы движения спрайта.
            check_left: Проверять границу слева (по умолчанию True).
            check_right: Проверять границу справа (по умолчанию True).
            check_top: Проверять верхнюю границу (по умолчанию True).
            check_bottom: Проверять нижнюю границу (по умолчанию True).
            padding_left: Отступ слева (по умолчанию 0).
            padding_right: Отступ справа (по умолчанию 0).
            padding_top: Отступ сверху (по умолчанию 0).
            padding_bottom: Отступ снизу (по умолчанию 0).
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
        """Воспроизведение звукового эффекта."""
        if self.sound_file != sound_file:
            self.sound_file = sound_file
            self.sound = pygame.mixer.Sound(sound_file)
        self.sound.play()
