"""Еда с уникальными id.

Авторитет (одиночная игра или хост) — источник истины: спавнит еду,
подтверждает поедание, рассылает снапшоты. Клиент держит копию и
синхронизирует её через события food_eaten и снапшоты food_state.
"""

import random
import time

import spritePro as s
from .config import FOOD_COUNT, FOOD_SIZE, FOOD_MARGIN, FOOD_COLORS, WORLD_WIDTH, WORLD_HEIGHT


GLOW_RADIUS = FOOD_SIZE * 3
GLOW_ALPHA = 60
# Сколько секунд не возвращать локально съеденную еду из снапшота:
# снапшот мог быть собран хостом до того, как он обработал наш eat_food.
_RECENT_REMOVE_TTL = 1.0


class FoodManager:
    def __init__(self, scene: s.Scene, authority: bool, restore: list[dict] | None = None):
        self.scene = scene
        self.authority = authority
        self.foods: dict[int, s.Sprite] = {}
        self._glows: dict[int, s.Sprite] = {}
        self._next_id = 0
        self._recently_removed: dict[int, float] = {}

        if restore:
            self.apply_state(restore)
            self._next_id = max(self.foods, default=-1) + 1
        if authority:
            self.maintain_count()

    def _create(self, food_id: int, pos: tuple[int, int], color: tuple[int, int, int]) -> None:
        food = s.Sprite("", (FOOD_SIZE * 2, FOOD_SIZE * 2), pos, scene=self.scene)
        food.set_circle_shape(radius=FOOD_SIZE, color=color)
        food.set_sorting_order(1)
        glow = s.Sprite("", (GLOW_RADIUS * 2, GLOW_RADIUS * 2), pos, scene=self.scene)
        glow.set_circle_shape(radius=GLOW_RADIUS, color=color)
        glow.set_alpha(GLOW_ALPHA)
        glow.set_sorting_order(0)
        self.foods[food_id] = food
        self._glows[food_id] = glow

    def spawn_at(self, pos: tuple[int, int], color: tuple[int, int, int] | None = None) -> int:
        """Создаёт еду в точке (только на авторитете) и возвращает её id."""
        food_id = self._next_id
        self._next_id += 1
        self._create(food_id, pos, color or random.choice(FOOD_COLORS))
        return food_id

    def spawn(self) -> int:
        x = random.randint(FOOD_MARGIN, WORLD_WIDTH - FOOD_MARGIN)
        y = random.randint(FOOD_MARGIN, WORLD_HEIGHT - FOOD_MARGIN)
        return self.spawn_at((x, y))

    def remove(self, food_id: int) -> bool:
        """Убирает еду по id. False, если её уже нет (кто-то съел раньше)."""
        food = self.foods.pop(food_id, None)
        glow = self._glows.pop(food_id, None)
        if glow is not None and glow.active:
            s.disable_sprite(glow)
        if food is None:
            return False
        if food.active:
            s.disable_sprite(food)
        self._recently_removed[food_id] = time.time()
        return True

    def find_at(self, pos: tuple[int, int], radius: int) -> int | None:
        """id еды, которую накрывает окружность (pos, radius), либо None."""
        rr = (radius + FOOD_SIZE) ** 2
        for food_id, food in self.foods.items():
            fx, fy = food.rect.center
            dx = pos[0] - fx
            dy = pos[1] - fy
            if dx * dx + dy * dy < rr:
                return food_id
        return None

    def maintain_count(self) -> None:
        while len(self.foods) < FOOD_COUNT:
            self.spawn()

    def get_state(self) -> list[dict]:
        return [
            {"id": food_id, "pos": list(food.rect.center), "color": list(food.color)}
            for food_id, food in self.foods.items()
        ]

    def apply_state(self, items: list[dict]) -> None:
        """Сверяет локальную еду со снапшотом: добавляет новую, убирает исчезнувшую."""
        now = time.time()
        self._recently_removed = {
            fid: t for fid, t in self._recently_removed.items()
            if now - t < _RECENT_REMOVE_TTL
        }
        incoming: dict[int, dict] = {int(item["id"]): item for item in items}

        for food_id in list(self.foods):
            if food_id not in incoming:
                self.remove(food_id)
        for food_id, item in incoming.items():
            if food_id in self.foods or food_id in self._recently_removed:
                continue
            self._create(food_id, tuple(item["pos"]), tuple(item["color"]))

    def clear(self) -> None:
        for food_id in list(self.foods):
            self.remove(food_id)
        self._recently_removed.clear()
