import pygame
from .gameSprite import GameSprite

class PhysicalSprite(GameSprite):
    jump_force = 5

    def __init__(
        self,
        sprite: str,
        size: tuple = (50, 50),
        pos: tuple = (0, 0),
        speed: float = 0,
        health: int = 100,
        mass: float = 1.0,
        gravity: float = 9.81,
        bounce_enabled: bool = False,
    ):
        """Инициализация физического спрайта с поддержкой гравитации и отскока."""
        super().__init__(sprite, size, pos, speed, health)
        self.force = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.mass = mass
        self.gravity = gravity
        self.bounce_enabled = bounce_enabled
        self.is_grounded = False
        self.min_velocity_threshold = 0.1
        self.ground_friction = 0.8

    def apply_force(self, force: pygame.math.Vector2):
        """Применение силы к физическому спрайту."""
        self.force += force

    def bounce(self, normal: pygame.math.Vector2):
        """Обработка отскока от поверхности с заданной нормалью."""
        # Отражаем скорость относительно нормали
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

        # Применяем трение только если не было управления по X
        if self.is_grounded and not getattr(self, '_x_controlled_this_frame', False):
            self.velocity.x *= self.ground_friction
            if abs(self.velocity.x) < self.min_velocity_threshold:
                self.velocity.x = 0

        if not collisions_enabled:
            self.position += self.velocity * dt
            self.rect.center = (int(self.position.x), int(self.position.y))

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

        if check_left and self.rect.left < bounds.left + padding_left:
            self.rect.left = bounds.left + padding_left
            self.position.x = self.rect.centerx
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(1, 0))
            else:
                self.velocity.x = 0

        if check_right and self.rect.right > bounds.right - padding_right:
            self.rect.right = bounds.right - padding_right
            self.position.x = self.rect.centerx
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(-1, 0))
            else:
                self.velocity.x = 0

        if check_top and self.rect.top < bounds.top + padding_top:
            self.rect.top = bounds.top + padding_top
            self.position.y = self.rect.centery
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(0, 1))
            else:
                self.velocity.y = 0

        # Проверяем только нижнюю границу для "на земле"
        if check_bottom and self.rect.bottom >= bounds.bottom - padding_bottom:
            self.rect.bottom = bounds.bottom - padding_bottom
            self.position.y = self.rect.centery
            if self.bounce_enabled:
                self.bounce(pygame.math.Vector2(0, -1))
            else:
                # Только если падали вниз, сбрасываем скорость
                if self.velocity.y > 0:
                    self.velocity.y = 0
                self.is_grounded = True
        else:
            self.is_grounded = False

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

    def resolve_collisions(self, *obstacles, fps=60):
        """
        Перемещает спрайт по velocity с учётом коллизий: сначала по Y, затем по X.
        Надёжно работает для платформеров и любых платформ.
        obstacles — любое количество спрайтов, ректов, групп или списков.
        fps — кадров в секунду (для расчёта dt).
        """
        dt = 1.0 / fps
        step = max(1, int(getattr(self, 'collision_step', 1)))
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
        # --- Сначала по Y ---
        dy = self.velocity.y * dt
        steps_y = max(1, int(abs(dy) // step))
        step_dy = dy / steps_y if steps_y else 0
        self.is_grounded = False
        for _ in range(steps_y):
            prev_y = self.position.y
            self.position.y += step_dy
            self.rect.center = (int(self.position.x), int(self.position.y))
            for r in rects:
                if self.rect.colliderect(r):
                    # Приземлились сверху (только если не прыжок вверх)
                    if step_dy > 0 and prev_y + self.rect.height // 2 <= r.top and self.velocity.y >= 0:
                        self.is_grounded = True
                        self.velocity.y = 0
                        self.position.y = r.top - self.rect.height // 2
                        self.rect.center = (int(self.position.x), int(self.position.y))
                        break
                    # Ударились головой (только если двигаемся вверх)
                    elif step_dy < 0 and prev_y - self.rect.height // 2 >= r.bottom:
                        self.velocity.y = 0
                        self.position.y = r.bottom + self.rect.height // 2
                        self.rect.center = (int(self.position.x), int(self.position.y))
                        break
                    # Если прыгаем вверх и есть пересечение — игнорируем платформу
                    elif step_dy < 0:
                        continue
                    else:
                        self.velocity.y = 0
                        break
            else:
                continue
            break
        # --- Затем по X ---
        dx = self.velocity.x * dt
        steps_x = max(1, int(abs(dx) // step))
        step_dx = dx / steps_x if steps_x else 0
        for _ in range(steps_x):
            prev_x = self.position.x
            self.position.x += step_dx
            self.rect.center = (int(self.position.x), int(self.position.y))
            for r in rects:
                if self.rect.colliderect(r):
                    if step_dx > 0 and prev_x + self.rect.width // 2 <= r.left:
                        self.velocity.x = 0
                        self.position.x = r.left - self.rect.width // 2
                        self.rect.center = (int(self.position.x), int(self.position.y))
                        break
                    elif step_dx < 0 and prev_x - self.rect.width // 2 >= r.right:
                        self.velocity.x = 0
                        self.position.x = r.right + self.rect.width // 2
                        self.rect.center = (int(self.position.x), int(self.position.y))
                        break
                    else:
                        self.velocity.x = 0
                        break
            else:
                continue
            break
        # После всех шагов по Y: если стоим на платформе и не прыгаем вверх, выставить is_grounded
        if self.velocity.y >= 0:
            for r in rects:
                if self.rect.bottom == r.top and self.rect.right > r.left and self.rect.left < r.right:
                    self.is_grounded = True
                    break
        else:
            self.is_grounded = False
