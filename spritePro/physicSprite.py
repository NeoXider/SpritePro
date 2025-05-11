import pygame
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from spritePro.gameSprite import GameSprite

PIXELS_PER_METER = 50  # 1 метр = 50 пикселей
SKIN = 2


class PhysicalSprite(GameSprite):
    jump_force = 7  # м/с, как в Unity
    MAX_STEPS = 8

    def __init__(
        self,
        sprite: str,
        size: tuple = (50, 50),
        pos: tuple = (0, 0),
        speed: float = 5,  # м/с
        health: int = 100,
        mass: float = 1.0,
        gravity: float = 9.8,
        bounce_enabled: bool = False,
    ):
        """Инициализация физического спрайта с поддержкой гравитации и отскока."""
        super().__init__(sprite, size, pos, speed, health)
        self.force = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.mass = mass
        self.gravity = gravity  # м/с^2
        self.bounce_enabled = bounce_enabled
        self.is_grounded = False
        self.min_velocity_threshold = 0.01
        self.ground_friction = 0.8
        # Позиция и скорость в метрах
        self.position = pygame.math.Vector2(
            pos[0] / PIXELS_PER_METER, pos[1] / PIXELS_PER_METER
        )
        self.velocity = pygame.math.Vector2(0, 0)  # м/с
        self.rect.center = (
            int(self.position.x * PIXELS_PER_METER),
            int(self.position.y * PIXELS_PER_METER),
        )

    def apply_force(self, force: pygame.math.Vector2):
        """Применение силы к физическому спрайту."""
        self.force += force

    def bounce(self, normal: pygame.math.Vector2):
        """Обработка отскока от поверхности с заданной нормалью."""
        self.velocity = self.velocity - 2 * self.velocity.dot(normal) * normal

    def update_physics(self, fps: float, collisions_enabled: bool = True):
        """Обновление физики спрайта с учетом гравитации и состояния на земле. fps - кадров в секунду.
        Если collisions_enabled=False, позиция обновляется по velocity (без коллизий).
        """
        dt = 1.0 / fps
        if not self.is_grounded:
            self.velocity.y += self.gravity * dt

        if self.mass > 0:
            self.acceleration = self.force / self.mass
        else:
            self.acceleration = pygame.math.Vector2(0, 0)

        self.velocity += self.acceleration * dt

        if self.is_grounded and not getattr(self, "_x_controlled_this_frame", False):
            self.velocity.x *= self.ground_friction
            if abs(self.velocity.x) < self.min_velocity_threshold:
                self.velocity.x = 0

        if not collisions_enabled:
            self.position += self.velocity * dt
            self.rect.center = (
                int(self.position.x * PIXELS_PER_METER),
                int(self.position.y * PIXELS_PER_METER),
            )

        self.force = pygame.math.Vector2(0, 0)
        self._x_controlled_this_frame = False

    def update(self, window: pygame.Surface):
        """
        Только отрисовка! Не обновляет физику.
        В основном цикле используйте:
            handle_keyboard_input()
            update_physics(dt)
            limit_movement(...)
            update(SCREEN)
        """
        super().update(window)

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
        Ограничивает движение спрайта в пределах заданных границ с учетом отступов и возможности отскока.

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
        self.is_grounded = False
        x, y = self.position.x, self.position.y
        px, py = int(x * PIXELS_PER_METER), int(y * PIXELS_PER_METER)
        if check_left and self.rect.left < bounds.left + padding_left:
            self.rect.left = bounds.left + padding_left
            px = self.rect.centerx
            x = px / PIXELS_PER_METER
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(1, 0))
            else:
                self.velocity.x = 0

        if check_right and self.rect.right > bounds.right - padding_right:
            self.rect.right = bounds.right - padding_right
            px = self.rect.centerx
            x = px / PIXELS_PER_METER
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(-1, 0))
            else:
                self.velocity.x = 0

        if check_top and self.rect.top < bounds.top + padding_top:
            self.rect.top = bounds.top + padding_top
            py = self.rect.centery
            y = py / PIXELS_PER_METER
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(0, 1))
            else:
                self.velocity.y = 0

        if check_bottom and self.rect.bottom >= bounds.bottom - padding_bottom:
            self.rect.bottom = bounds.bottom - padding_bottom
            py = self.rect.centery
            y = py / PIXELS_PER_METER
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(0, -1))
            else:
                if self.velocity.y > 0:
                    self.velocity.y = 0
                self.is_grounded = True
        else:
            self.is_grounded = False
        self.position.x, self.position.y = x, y
        self.rect.center = (
            int(self.position.x * PIXELS_PER_METER),
            int(self.position.y * PIXELS_PER_METER),
        )

    def handle_keyboard_input(
        self,
        keys=None,
        left_key=pygame.K_LEFT,
        right_key=pygame.K_RIGHT,
        up_key=pygame.K_UP,
    ):
        """
        Обработка ввода с клавиатуры для движения физического спрайта.

        Аргументы:
            keys: Состояние всех клавиш. Если None, будет использован pygame.key.get_pressed()
            up_key: Клавиша для движения вверх (по умолчанию стрелка вверх)
            down_key: Клавиша для движения вниз (по умолчанию стрелка вниз)
            left_key: Клавиша для движения влево (по умолчанию стрелка влево)
            right_key: Клавиша для движения вправо (по умолчанию стрелка вправо)
        """
        if keys is None:
            keys = pygame.key.get_pressed()
        self._x_controlled_this_frame = False
        self.velocity.x = 0
        if left_key is not None and keys[left_key]:
            self.velocity.x = -self.speed
            self.flipped_h = True
            self._update_image()
            self._x_controlled_this_frame = True
        if right_key is not None and keys[right_key]:
            self.velocity.x = self.speed
            self.flipped_h = False
            self._update_image()
            self._x_controlled_this_frame = True
        if up_key is not None and keys[up_key]:
            self.jump(self.jump_force)

    def jump(self, jump_force: float):
        """Применение силы для прыжка."""
        if self.is_grounded:
            self.is_grounded = False
            self.velocity.y = -jump_force

    def force_in_direction(self, direction: pygame.math.Vector2, force: float):
        """Применение силы в заданном направлении."""
        self.apply_force(direction.normalize() * force)

    def _check_grounded(self, rects):
        for r in rects:
            if (
                abs(self.rect.bottom - r.top) <= SKIN
                and self.rect.right > r.left
                and self.rect.left < r.right
            ):
                return True
        return False

    def resolve_collisions(
        self,
        *obstacles,
        fps=60,
        limit_top=True,
        limit_bottom=True,
        limit_left=True,
        limit_right=True,
    ):
        """
        Перемещает спрайт по velocity с учётом коллизий: сначала по Y, затем по X.
        Надёжно работает для платформеров и любых платформ.
        obstacles — любое количество спрайтов, ректов, групп или списков.
        fps — кадров в секунду (для расчёта dt).
        """
        dt = 1.0 / fps
        rects = []

        def collect_rects(objs):
            for obj in objs:
                if isinstance(obj, pygame.sprite.Sprite):
                    rects.append(obj.rect)
                elif isinstance(obj, pygame.Rect):
                    rects.append(obj)
                elif isinstance(obj, (pygame.sprite.Group, list, tuple)):
                    collect_rects(obj)

        collect_rects(obstacles)
        x, y = self.position.x, self.position.y
        px, py = int(x * PIXELS_PER_METER), int(y * PIXELS_PER_METER)
        # --- Y ---
        dy = self.velocity.y * dt
        steps_y = max(1, min(self.MAX_STEPS, int(abs(dy * PIXELS_PER_METER)) + 1))
        step_dy = dy / steps_y if steps_y else 0
        for _ in range(steps_y):
            prev_y = y
            y += step_dy
            py = int(y * PIXELS_PER_METER)
            self.rect.center = (int(px), py)
            collided = False
            for r in rects:
                if self.rect.colliderect(r):
                    # Приземление сверху (туннелирование)
                    if (
                        limit_top
                        and step_dy > 0
                        and prev_y * PIXELS_PER_METER + self.rect.height // 2 <= r.top
                        and y * PIXELS_PER_METER + self.rect.height // 2 >= r.top
                    ):
                        y = (r.top - self.rect.height // 2) / PIXELS_PER_METER
                        py = int(y * PIXELS_PER_METER)
                        self.position.y = y
                        self.rect.center = (int(px), py)
                        if self.velocity.y > 0:
                            self.velocity.y = 0
                        collided = True
                        break
                    # Удар головой (туннелирование снизу)
                    elif (
                        limit_bottom
                        and step_dy < 0
                        and prev_y * PIXELS_PER_METER - self.rect.height // 2
                        >= r.bottom
                        and y * PIXELS_PER_METER - self.rect.height // 2 <= r.bottom
                    ):
                        y = (r.bottom + self.rect.height // 2) / PIXELS_PER_METER
                        py = int(y * PIXELS_PER_METER)
                        self.position.y = y
                        self.rect.center = (int(px), py)
                        if self.velocity.y < 0:
                            self.velocity.y = 0
                        collided = True
                        break
            if collided:
                break
        # --- X ---
        dx = self.velocity.x * dt
        steps_x = max(1, min(self.MAX_STEPS, int(abs(dx * PIXELS_PER_METER)) + 1))
        step_dx = dx / steps_x if steps_x else 0
        for _ in range(steps_x):
            prev_x = x
            x += step_dx
            px = int(x * PIXELS_PER_METER)
            self.rect.center = (px, int(py))
            collided = False
            for r in rects:
                if self.rect.colliderect(r):
                    # Движение по платформе
                    if self._check_grounded([r]):
                        continue
                    # Столкновение справа
                    if (
                        limit_right
                        and step_dx > 0
                        and prev_x * PIXELS_PER_METER + self.rect.width // 2 <= r.left
                        and x * PIXELS_PER_METER + self.rect.width // 2 >= r.left
                    ):
                        x = (r.left - self.rect.width // 2) / PIXELS_PER_METER
                        px = int(x * PIXELS_PER_METER)
                        self.position.x = x
                        self.rect.center = (px, int(py))
                        self.velocity.x = 0
                        collided = True
                        break
                    # Столкновение слева
                    elif (
                        limit_left
                        and step_dx < 0
                        and prev_x * PIXELS_PER_METER - self.rect.width // 2 >= r.right
                        and x * PIXELS_PER_METER - self.rect.width // 2 <= r.right
                    ):
                        x = (r.right + self.rect.width // 2) / PIXELS_PER_METER
                        px = int(x * PIXELS_PER_METER)
                        self.position.x = x
                        self.rect.center = (px, int(py))
                        self.velocity.x = 0
                        collided = True
                        break
            if collided:
                break
        self.position.x, self.position.y = x, y
        self.rect.center = (
            int(self.position.x * PIXELS_PER_METER),
            int(self.position.y * PIXELS_PER_METER),
        )
        self.is_grounded = self._check_grounded(rects)
