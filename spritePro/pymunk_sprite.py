import pygame
import pymunk
from spritePro.gameSprite import GameSprite

"""
Пример использования:

import pymunk
import pygame
from spritePro.pymunk_sprite import PymunkGameSprite

pygame.init()
space = pymunk.Space()
space.gravity = (0, 900)

# Можно путь к файлу или Surface
sprite_img = pygame.image.load("ball.png").convert_alpha()

sprite = PymunkGameSprite(
    sprite=sprite_img,
    pos=(100, 100),
    mass=1.0,
    friction=0.7,
    elasticity=0.2,
    space=space,
    health=100
)

# В основном цикле:
#   space.step(dt)
#   sprite.handle_keyboard_input()
#   sprite.update()
#   screen.blit(sprite.image, sprite.rect)
"""

class PymunkGameSprite(GameSprite):
    """
    Физический спрайт для pygame с поддержкой pymunk и всех фич GameSprite.
    Позволяет использовать здоровье, маски, теги, события, а также pymunk.Body для физики.

    :param sprite: путь к изображению или Surface
    :param pos: tuple (x, y) — начальная позиция (в пикселях)
    :param size: tuple (w, h) — размер изображения (по умолчанию исходный)
    :param mass: float — масса тела
    :param moment: float — момент инерции (по умолчанию рассчитывается для прямоугольника)
    :param friction: float — коэффициент трения
    :param elasticity: float — коэффициент упругости
    :param body_type: pymunk.Body.DYNAMIC/STATIC/KINEMATIC — тип тела
    :param space: pymunk.Space — физический мир, если указан, тело сразу добавляется в него
    :param health: int — здоровье спрайта
    :param gravity_enabled: bool — включена ли гравитация (по умолчанию True)
    """
    def __init__(
        self,
        sprite,
        pos=(0, 0),
        size=None,
        mass=1.0,
        moment=None,
        friction=0.7,
        elasticity=0.0,
        body_type=pymunk.Body.DYNAMIC,
        space: pymunk.Space = None,
        collision_type: int = 1,
        health: int = 100,
        speed: float = 200,
        jump_power: float = 500,
    ):
        super().__init__(sprite=sprite, size=size, pos=pos, speed=speed, health=health)
        w, h = self.rect.width, self.rect.height
        if moment is None:
            moment = pymunk.moment_for_box(mass, (w, h))
        self.body = pymunk.Body(mass, moment, body_type=body_type)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (w, h))
        self.shape.friction = friction
        self.shape.elasticity = elasticity
        self.shape.collision_type = collision_type
        if space is not None:
            space.add(self.body, self.shape)
        self._space = space
        self.mask = pygame.mask.from_surface(self.image)
        self.gravity_enabled = True
        self._last_gravity = None
        self._can_jump = False
        self._collision_handlers_set = False
        self.speed = speed
        self.jump_power = jump_power
        # Автоматически настраиваем обработчик платформера, если space есть
        if self._space is not None:
            self.setup_platformer_handlers(platform_collision_type=2)

    def setup_platformer_handlers(self, platform_collision_type=2):
        """
        Установить обработчик коллизий для платформера.
        Флаг _can_jump будет True только при контакте с платформой снизу (нормаль строго вверх).
        """
        if not self._space or self._collision_handlers_set:
            return
        handler = self._space.add_collision_handler(self.shape.collision_type, platform_collision_type)
        handler.pre_solve = self._on_ground_contact
        self._collision_handlers_set = True

    def _on_ground_contact(self, arbiter, space, data):
        normal = arbiter.contact_point_set.normal
        if normal.y > 0.7 and self.body.velocity.y <= 0:
            self._can_jump = True
        return True

    def update(self):
        self._can_jump = False
        x, y = self.body.position
        self.rect.center = (int(x), int(y))

    def _handle_gravity(self):
        if not self.gravity_enabled and self._space is not None:
            if self._last_gravity is None:
                self._last_gravity = self._space.gravity
            self._space.gravity = (0, 0)
            self.body.velocity = (self.body.velocity.x, 0)
        elif self.gravity_enabled and self._space is not None:
            if self._last_gravity is not None:
                self._space.gravity = self._last_gravity
                self._last_gravity = None

    def _update_jump_flag(self):
        self._can_jump = False
        if self._space is None:
            return
        x, y = self.body.position
        w, h = self.rect.width, self.rect.height
        for shape in self._space.shapes:
            if shape == self.shape:
                continue
            if hasattr(shape.body, 'body_type') and shape.body.body_type == pymunk.Body.STATIC:
                if self._is_on_shape(shape, x, y, w, h) and abs(self.body.velocity.y) < 1:
                    self._can_jump = True
                    return

    def _is_on_shape(self, shape, x, y, w, h, eps=3):
        """
        Проверяет, стоит ли объект на shape (платформе/стене).
        """
        # Для Segment (стена)
        if isinstance(shape, pymunk.Segment):
            a, b = shape.a, shape.b
            y_seg = a[1]
            thickness = shape.radius * 2 if hasattr(shape, 'radius') else 10
            # Проверяем только горизонтальные сегменты (верх/низ)
            if a[1] == b[1]:
                # Мяч должен быть ВЫШЕ сегмента (или почти на нем)
                if (y + h/2) - y_seg < max(eps, thickness) and (y + h/2) - y_seg > -max(eps, thickness):
                    if y < y_seg:  # центр мяча выше сегмента
                        if min(a[0], b[0]) - w/2 < x < max(a[0], b[0]) + w/2:
                            return True
            return False
        # Для Poly (платформы)
        points = [
            (x - w/2 + 2, y + h/2 + 1),
            (x + w/2 - 2, y + h/2 + 1),
            (x, y + h/2 + 1),
        ]
        for pt in points:
            if shape.point_query(pt).distance <= eps:
                # точка под мячом должна быть чуть выше центра мяча
                if pt[1] > y and y < shape.bb.top + eps:
                    return True
        return False

    def handle_keyboard_input(self, left=pygame.K_LEFT, right=pygame.K_RIGHT, up=pygame.K_UP, speed=None):
        keys = pygame.key.get_pressed()
        vx = 0
        move_speed = speed if speed is not None else self.speed
        if left and keys[left]:
            vx -= move_speed
        if right and keys[right]:
            vx += move_speed
        self.set_velocity(vx, self.body.velocity.y)
        if up and keys[up] and self._can_jump:
            self.set_velocity(self.body.velocity.x, 0)
            self.apply_impulse((0, -abs(self.body.mass * self.jump_power)))
            self._can_jump = False

    def can_jump(self):
        """
        Возвращает True, если объект может прыгать (стоит на платформе/стене).
        """
        return self._can_jump

    def move(self, dx, dy):
        """
        Мгновенно перемещает спрайт (без физики).
        :param dx: смещение по X (пиксели)
        :param dy: смещение по Y (пиксели)
        """
        x, y = self.body.position
        self.set_position(x + dx, y + dy)

    def set_velocity(self, vx, vy):
        """
        Устанавливает скорость тела.
        :param vx: float — скорость по X (пикселей/сек)
        :param vy: float — скорость по Y (пикселей/сек)
        """
        self.body.velocity = vx, vy

    def get_velocity(self):
        """
        Возвращает текущую скорость тела.
        :return: tuple (vx, vy)
        """
        return self.body.velocity

    def set_position(self, x, y):
        """
        Устанавливает позицию тела.
        :param x: float — X (пиксели)
        :param y: float — Y (пиксели)
        """
        self.body.position = x, y
        self.rect.center = (int(x), int(y))

    def get_position(self):
        """
        Возвращает текущую позицию тела.
        :return: tuple (x, y)
        """
        return self.body.position

    def set_angle(self, angle):
        """
        Устанавливает угол поворота тела (в радианах).
        :param angle: float — угол в радианах
        """
        self.body.angle = angle

    def get_angle(self):
        """
        Возвращает угол поворота тела (в радианах).
        :return: float
        """
        return self.body.angle

    def move_left(self, speed=None):
        """
        Двигает тело влево (через velocity).
        :param speed: float — скорость (если None, используется текущая)
        """
        v = speed if speed is not None else self.speed
        self.body.velocity = -v, self.body.velocity.y

    def move_right(self, speed=None):
        """
        Двигает тело вправо (через velocity).
        :param speed: float — скорость (если None, используется текущая)
        """
        v = speed if speed is not None else self.speed
        self.body.velocity = v, self.body.velocity.y

    def move_up(self, speed=None):
        """
        Двигает тело вверх (через velocity).
        :param speed: float — скорость (если None, используется текущая)
        """
        v = speed if speed is not None else self.speed
        self.body.velocity = self.body.velocity.x, -v

    def move_down(self, speed=None):
        """
        Двигает тело вниз (через velocity).
        :param speed: float — скорость (если None, используется текущая)
        """
        v = speed if speed is not None else self.speed
        self.body.velocity = self.body.velocity.x, v

    def move_towards(self, target, speed=None):
        """
        Двигает тело в сторону target с заданной скоростью (через velocity).
        :param target: tuple (x, y) — целевая точка (пиксели)
        :param speed: float — скорость (если None, используется текущая)
        """
        x, y = self.body.position
        tx, ty = target
        dx, dy = tx - x, ty - y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist == 0:
            self.body.velocity = 0, 0
            return
        v = speed if speed is not None else self.speed
        if v == 0:
            v = 1
        self.body.velocity = (dx / dist * v, dy / dist * v)

    def apply_impulse(self, impulse):
        """
        Применяет импульс к телу.
        :param impulse: tuple (x, y) — вектор импульса в пикселях*масса/сек
        """
        self.body.apply_impulse_at_local_point(impulse)

    def add_to_space(self, space: pymunk.Space):
        """
        Добавляет тело и shape в pymunk.Space.
        :param space: pymunk.Space
        """
        space.add(self.body, self.shape)
        self._space = space

    def remove_from_space(self, space: pymunk.Space = None):
        """
        Удаляет тело и shape из pymunk.Space.
        :param space: pymunk.Space (если не указан, используется self._space)
        """
        if space is None:
            space = self._space
        if space is not None:
            space.remove(self.body, self.shape)
            self._space = None

    def is_static(self):
        """
        Проверяет, является ли тело статическим.
        :return: bool
        """
        return self.body.body_type == pymunk.Body.STATIC

    def is_dynamic(self):
        """
        Проверяет, является ли тело динамическим.
        :return: bool
        """
        return self.body.body_type == pymunk.Body.DYNAMIC

    def is_kinematic(self):
        """
        Проверяет, является ли тело кинематическим.
        :return: bool
        """
        return self.body.body_type == pymunk.Body.KINEMATIC

    @staticmethod
    def create_walls(space, rect, thickness=10, elasticity=0.0, friction=0.7):
        """
        Универсальный метод создания невидимых стен по границам rect в pymunk.Space.
        :param space: pymunk.Space
        :param rect: pygame.Rect (границы)
        :param thickness: толщина стен
        :param elasticity: упругость
        :param friction: трение
        :return: список созданных стен
        """
        x0, y0, w, h = rect.left, rect.top, rect.width, rect.height
        static_lines = [
            pymunk.Segment(space.static_body, (x0, y0), (x0 + w, y0), thickness),         # верх
            pymunk.Segment(space.static_body, (x0, y0 + h), (x0 + w, y0 + h), thickness), # низ
            pymunk.Segment(space.static_body, (x0, y0), (x0, y0 + h), thickness),         # лево
            pymunk.Segment(space.static_body, (x0 + w, y0), (x0 + w, y0 + h), thickness), # право
        ]
        for line in static_lines:
            line.elasticity = elasticity
            line.friction = friction
        space.add(*static_lines)
        return static_lines

    def limit_movement(self, rect, thickness=10, elasticity=0.0, friction=0.7):
        """
        Создаёт стены-границы в pymunk.Space по rect (если ещё не созданы).
        :param rect: pygame.Rect
        :param thickness: толщина стен
        :param elasticity: упругость
        :param friction: трение
        """
        if not hasattr(self._space, '_walls_created'):
            self._space._walls = self.create_walls(self._space, rect, thickness, elasticity, friction)
            self._space._walls_created = True 