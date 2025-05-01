from typing import Callable, List
import pygame
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from spritePro.sprite import Sprite


class GameSprite(Sprite):
    _last_obstacles_hash = None
    _last_obstacles_rects = None
    collision_step: int = 1

    def __init__(
        self,
        sprite: str,
        size: tuple = (50, 50),
        pos: tuple = (0, 0),
        speed: float = 0,
        health: int = 100,
    ):
        """
        Инициализация спрайта.

        Аргументы:
            sprite: Путь к изображению спрайта или имя ресурса
            size: Размер спрайта (ширина, высота) по умолчанию (50, 50)
            pos: Начальная позиция спрайта (x, y) по умолчанию (0, 0)
            speed: Скорость движения спрайта по умолчанию 0
            health: хп спрайта по умолчанию 100
        """
        super().__init__(sprite, size, pos, speed)

        # Состояние спрайта
        self.alive = True
        self.health = health
        self.max_health = health

        # Коллбэки для событий
        self.on_collision = None
        self.on_death = None

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
                other_sprite.rect.y - self.rect.y,
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

    def on_collision_event(self, callback: Callable):
        """Установка функции обратного вызова для событий столкновения."""
        self.on_collision = callback

    def on_death_event(self, callback: Callable):
        """Установка функции обратного вызова для событий смерти."""
        self.on_death = callback

    def collide_with_tag(self, group: pygame.sprite.Group, tag: str) -> List:
        """Проверка столкновения с группой спрайтов по тегу."""
        return [
            sprite
            for sprite in group
            if sprite.tag == tag and self.collide_with(sprite)
        ]

    def _get_collision_side(self, prev_x, prev_y, rect):
        # Определяет сторону столкновения: 'top', 'bottom', 'left', 'right', 'inside'
        cx, cy = self.rect.center
        if prev_y + self.rect.height // 2 <= rect.top:
            return "bottom"  # мы сверху
        elif prev_y - self.rect.height // 2 >= rect.bottom:
            return "top"  # мы снизу
        elif prev_x + self.rect.width // 2 <= rect.left:
            return "right"  # мы слева
        elif prev_x - self.rect.width // 2 >= rect.right:
            return "left"  # мы справа
        else:
            return "inside"

    def resolve_collisions(self, *obstacles):
        """
        Останавливает движение при столкновении с любыми препятствиями.
        obstacles — любое количество спрайтов, ректов, групп или списков.
        Возвращает список кортежей (rect, side), где side — сторона столкновения.
        """

        def flatten_ids(objs):
            ids = []
            for obj in objs:
                if isinstance(obj, (list, tuple, pygame.sprite.Group)):
                    ids.extend(flatten_ids(obj))
                else:
                    ids.append(id(obj))
            return ids

        obstacles_hash = hash(tuple(flatten_ids(obstacles)))
        if (
            obstacles_hash == self._last_obstacles_hash
            and self._last_obstacles_rects is not None
        ):
            rects = self._last_obstacles_rects
        else:
            rects = []
            for obj in obstacles:
                if isinstance(obj, pygame.sprite.Sprite):
                    rects.append(obj.rect)
                elif isinstance(obj, pygame.Rect):
                    rects.append(obj)
                elif isinstance(obj, (pygame.sprite.Group, list, tuple)):
                    for o in obj:
                        if isinstance(o, pygame.sprite.Sprite):
                            rects.append(o.rect)
                        elif isinstance(o, pygame.Rect):
                            rects.append(o)
            self._last_obstacles_hash = obstacles_hash
            self._last_obstacles_rects = rects
        # --- Шаг проверки теперь задается через self.collision_step ---
        step = max(1, int(getattr(self, "collision_step", 1)))
        total_steps = int(max(abs(self.velocity.x), abs(self.velocity.y)) // step)
        if total_steps == 0:
            return []
        dx = self.velocity.x / (total_steps * step) if total_steps else 0
        dy = self.velocity.y / (total_steps * step) if total_steps else 0
        collisions = []
        for _ in range(total_steps * step):
            prev_x = self.position.x
            prev_y = self.position.y
            self.position.x += dx
            self.position.y += dy
            self.rect.center = (int(self.position.x), int(self.position.y))
            for r in rects:
                if self.rect.colliderect(r):
                    side = self._get_collision_side(prev_x, prev_y, r)
                    collisions.append((r, side))
                    self.position.x -= dx
                    self.position.y -= dy
                    self.rect.center = (int(self.position.x), int(self.position.y))
                    if abs(dx) > abs(dy):
                        self.velocity.x = 0
                    else:
                        self.velocity.y = 0
                    return collisions
        return collisions
