import random

import spritePro as s
from .config import FOOD_COUNT, FOOD_SIZE, FOOD_COLORS, WORLD_WIDTH, WORLD_HEIGHT


GLOW_RADIUS = FOOD_SIZE * 3
GLOW_ALPHA = 60


class FoodManager:
    def __init__(self, scene: s.Scene):
        self.scene = scene
        self.foods: list[s.Sprite] = []
        self._glows: dict[int, s.Sprite] = {}
        self._spawn_initial()

    def _spawn_initial(self) -> None:
        for _ in range(FOOD_COUNT):
            self.spawn()

    def _make_glow(self, color: tuple[int, int, int], pos: tuple[int, int]) -> s.Sprite:
        glow = s.Sprite("", (GLOW_RADIUS * 2, GLOW_RADIUS * 2), pos, scene=self.scene)
        glow.set_circle_shape(radius=GLOW_RADIUS, color=color)
        glow.set_alpha(GLOW_ALPHA)
        glow.set_sorting_order(0)
        return glow

    def spawn_at(self, pos: tuple[int, int]) -> s.Sprite:
        color = random.choice(FOOD_COLORS)
        food = s.Sprite("", (FOOD_SIZE * 2, FOOD_SIZE * 2), pos, scene=self.scene)
        food.set_circle_shape(radius=FOOD_SIZE, color=color)
        food.set_sorting_order(1)
        food._ctype = "food"
        glow = self._make_glow(color, pos)
        self._glows[id(food)] = glow
        self.foods.append(food)
        return food

    def spawn(self) -> s.Sprite:
        margin = FOOD_SIZE
        x = random.randint(margin, WORLD_WIDTH - margin)
        y = random.randint(margin, WORLD_HEIGHT - margin)
        color = random.choice(FOOD_COLORS)
        return self.spawn_at((x, y))

    def _disable_food(self, food: s.Sprite) -> None:
        glow = self._glows.pop(id(food), None)
        if glow is not None and glow.active:
            s.disable_sprite(glow)
        if food.active:
            s.disable_sprite(food)

    def maintain_count(self) -> None:
        self.foods = [f for f in self.foods if f.active]
        while len(self.foods) < FOOD_COUNT:
            self.spawn()

    def get_state(self) -> list[dict]:
        return [
            {"pos": f.rect.center, "color": f.color}
            for f in self.foods if f.active
        ]

    def sync_from_data(self, foods_data: list[dict]) -> None:
        for food in self.foods:
            self._disable_food(food)
        self.foods.clear()
        self._glows.clear()
        for fd in foods_data:
            pos = tuple(fd["pos"])
            color = tuple(fd["color"])
            food = s.Sprite("", (FOOD_SIZE * 2, FOOD_SIZE * 2), pos, scene=self.scene)
            food.set_circle_shape(radius=FOOD_SIZE, color=color)
            food.set_sorting_order(1)
            food._ctype = "food"
            food.color = color
            glow = self._make_glow(color, pos)
            self._glows[id(food)] = glow
            self.foods.append(food)

    def clear(self) -> None:
        for food in self.foods:
            self._disable_food(food)
        self.foods.clear()
        self._glows.clear()
