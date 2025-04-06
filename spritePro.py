# spritePro.py
import os
from typing import Tuple, Optional, Callable, List
import pygame
import math

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, health: int = 100):
        """
        Инициализация спрайта.
        
        Аргументы:
            sprite: Путь к изображению спрайта или имя ресурса
            size: Размер спрайта (ширина, высота) по умолчанию (50, 50)
            pos: Начальная позиция спрайта (x, y) по умолчанию (0, 0)
            speed: Скорость движения спрайта по умолчанию 0
        """
        super().__init__()
        
        # Загрузка изображения спрайта
        try:
            if os.path.isfile(sprite):
                self.original_image = pygame.image.load(sprite).convert_alpha()
            else:
                self.original_image = pygame.Surface(size, pygame.SRCALPHA)
                self.original_image.fill((255, 0, 255))  # Фиолетовый цвет по умолчанию если спрайт не найден
        except:
            self.original_image = pygame.Surface(size, pygame.SRCALPHA)
            self.original_image.fill((255, 0, 255))  # Фиолетовый цвет по умолчанию если спрайт не найден
        
        # Изменение размера изображения если нужно
        if size != (self.original_image.get_width(), self.original_image.get_height()):
            self.original_image = pygame.transform.scale(self.original_image, size)
        
        # Копия изображения для манипуляций
        self.image = self.original_image.copy()
        
        # Создание прямоугольника из изображения и установка его центра
        self.rect = self.image.get_rect()
        self.rect.center = pos
        
        # Создание маски для более точного определения столкновений
        self.mask = pygame.mask.from_surface(self.image)
        
        # Физические свойства
        self.position = pygame.math.Vector2(pos)  # Позиция с плавающей точкой
        self.velocity = pygame.math.Vector2(0, 0)  # Текущая скорость (направление)
        self.speed = speed  # Максимальная скорость
        
        # Состояние спрайта
        self.alive = True
        self.health = health
        self.max_health = health
        
        # Визуальные эффекты
        self.flipped_h = False  # Отражение по горизонтали
        self.flipped_v = False  # Отражение по вертикали
        self.angle = 0  # Угол поворота
        self.scale = 1.0  # Масштаб
        self.alpha = 255  # Прозрачность
        
        # Состояния спрайта
        self.state = "idle"  # Начальное состояние
        self.states = {"idle", "moving", "hit", "attacking", "dead"}
        
        # Коллбэки для событий
        self.on_collision = None
        self.on_death = None

    def update(self, window: pygame.Surface):
        """Обновление состояния спрайта."""
        # Обновление позиции на основе скорости
        if self.velocity.length() > 0:
            self.position += self.velocity
            self.rect.center = (int(self.position.x), int(self.position.y))

        # Обновляем маску коллизии если изображение изменилось
        self.mask = pygame.mask.from_surface(self.image)
        window.blit(self.image, self.rect)

    def _update_image(self):
        """Обновляет изображение с учетом всех визуальных эффектов."""
        img = self.original_image.copy()

        # Применяем отражение
        if self.flipped_h or self.flipped_v:
            img = pygame.transform.flip(img, self.flipped_h, self.flipped_v)

        # Применяем масштаб
        if self.scale != 1.0:
            new_size = (int(img.get_width() * self.scale), int(img.get_height() * self.scale))
            img = pygame.transform.scale(img, new_size)

        # Применяем вращение
        if self.angle != 0:
            img = pygame.transform.rotate(img, self.angle)

        # Применяем прозрачность
        if self.alpha != 255:
            img.set_alpha(self.alpha)

        # Обновляем изображение и прямоугольник
        self.image = img

        # Сохраняем центр
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def move(self, dx: float, dy: float):
        """
        Перемещение спрайта на заданное расстояние.
        """
        self.position.x += dx
        self.position.y += dy
        self.rect.center = (int(self.position.x), int(self.position.y))

    def move_towards(self, target_pos: Tuple[float, float], speed: Optional[float] = None):
        """
        Перемещение спрайта в направлении целевой позиции.

        Аргументы:
            target_pos: Целевая позиция (x, y)
            speed: Опциональная скорость движения (если None, используется self.speed)
        """
        if speed is None:
            speed = self.speed

        # Расчет вектора направления к цели
        current_pos = pygame.math.Vector2(self.position)
        target_vector = pygame.math.Vector2(target_pos)
        direction = target_vector - current_pos

        # Расчет расстояния до цели
        distance = direction.length()

        # Порог остановки - останавливаемся если мы достаточно близко к цели
        stop_threshold = 1.0

        if distance < stop_threshold:
            # Если мы достаточно близко, просто устанавливаем позицию точно в цель
            self.position = target_vector
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
        else:
            # Нормализуем вектор направления и умножаем на скорость
            if distance > 0:  # Проверка, чтобы избежать деления на ноль
                direction = direction / distance * speed

            # Устанавливаем скорость
            self.velocity = direction
            self.state = "moving"

        # Обновляем положение спрайта
        self.rect.center = (int(self.position.x), int(self.position.y))

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
        self.velocity.y = (speed or self.speed)
        self.state = "moving"

    def move_left(self, speed: Optional[float] = None):
        """Перемещение спрайта влево."""
        self.velocity.x = -(speed or self.speed)
        self.flipped_h = True
        self._update_image()
        self.state = "moving"

    def move_right(self, speed: Optional[float] = None):
        """Перемещение спрайта вправо."""
        self.velocity.x = (speed or self.speed)
        self.flipped_h = False
        self._update_image()
        self.state = "moving"

    def handle_keyboard_input(self, keys=None, up_key=pygame.K_UP, down_key=pygame.K_DOWN,
                             left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT):
        """
        Обработка ввода с клавиатуры для движения спрайта.

        Аргументы:
            keys: Состояние всех клавиш. Если None, будет использован pygame.key.get_pressed()
            up_key: Клавиша для движения вверх (по умолчанию стрелка вверх)
            down_key: Клавиша для движения вниз (по умолчанию стрелка вниз)
            left_key: Клавиша для движения влево (по умолчанию стрелка влево)
            right_key: Клавиша для движения вправо (по умолчанию стрелка вправо)
        """
        if keys is None:
            keys = pygame.key.get_pressed()

        # Сбрасываем скорость
        self.velocity.x = 0
        self.velocity.y = 0
        was_moving = False

        # Проверяем нажатые клавиши и устанавливаем скорость
        if up_key != None:
            if keys[up_key]:
                self.velocity.y = -self.speed
                was_moving = True
        if down_key != None:
            if keys[down_key]:
                self.velocity.y = self.speed
                was_moving = True
        if left_key != None:
            if keys[left_key]:
                self.velocity.x = -self.speed
                self.flipped_h = True
                self._update_image()
                was_moving = True
        if right_key != None:
            if keys[right_key]:
                self.velocity.x = self.speed
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

    def fade_in(self, speed: int = 5):
        """Постепенное увеличение прозрачности."""
        self.alpha = min(255, self.alpha + speed)
        self._update_image()

    def fade_out(self, speed: int = 5):
        """Постепенное уменьшение прозрачности."""
        self.alpha = max(0, self.alpha - speed)
        self._update_image()

    def collide_with(self, other_sprite) -> bool:
        """
        Проверка столкновения с другим спрайтом, используя маски для точности.

        Аргументы:
            other_sprite: Другой экземпляр GameSprite для проверки столкновения

        Возвращает:
            bool: True если есть столкновение, False иначе
        """
        if pygame.sprite.collide_rect(self, other_sprite):
            offset = (
                other_sprite.rect.x - self.rect.x,
                other_sprite.rect.y - self.rect.y
            )
            if other_sprite.mask is not None and self.mask is not None:
                return self.mask.overlap(other_sprite.mask, offset) is not None
            return True
        return False

    def collide_with_group(self, group: pygame.sprite.Group) -> List:
        """
        Проверка столкновения с группой спрайтов, используя маски для точности.

        Аргументы:
            group: Группа спрайтов для проверки столкновения

        Возвращает:
            list: Список спрайтов, с которыми сталкивается данный спрайт
        """
        return pygame.sprite.spritecollide(
            self, group, False, pygame.sprite.collide_mask
        )

    def distance_to(self, other_sprite) -> float:
        """Расчет расстояния до другого спрайта (от центра к центру)."""
        return math.sqrt(
            (self.rect.centerx - other_sprite.rect.centerx) ** 2 +
            (self.rect.centery - other_sprite.rect.centery) ** 2
        )

    def take_damage(self, amount: int) -> bool:
        """
        Уменьшение здоровья на заданное количество.

        Аргументы:
            amount: Количество получаемого урона

        Возвращает:
            bool: True если все еще жив, False если умер
        """
        if not self.alive:
            return False

        self.health = max(0, self.health - amount)
        self.state = "hit"

        if self.health <= 0:
            self.alive = False
            self.state = "dead"
            if self.on_death:
                self.on_death(self)
            return False
        return True

    def heal(self, amount: int):
        """Увеличение здоровья на заданное количество, до max_health."""
        if self.alive:
            self.health = min(self.max_health, self.health + amount)

    def set_state(self, state: str):
        """Установка состояния спрайта, если оно допустимо."""
        if state in self.states:
            self.state = state

    def is_in_state(self, state: str) -> bool:
        """Проверка, находится ли спрайт в заданном состоянии."""
        return self.state == state

    def on_collision_event(self, callback: Callable):
        """Установка функции обратного вызова для событий столкновения."""
        self.on_collision = callback

    def on_death_event(self, callback: Callable):
        """Установка функции обратного вызова для событий смерти."""
        self.on_death = callback

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
