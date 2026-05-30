import math
import random

from pygame.math import Vector2

import spritePro as s
from .config import (
    HEAD_SIZE, BOT_SPEED, BOT_INITIAL_LENGTH,
    BOT_AVOID_WALL_DIST,
    WORLD_WIDTH, WORLD_HEIGHT,
)
from .snake import Snake


def _random_pos() -> Vector2:
    return Vector2(
        random.randint(200, WORLD_WIDTH - 200),
        random.randint(200, WORLD_HEIGHT - 200),
    )


class BotSnake(Snake):
    def __init__(self, start_pos: tuple[int, int], scene: s.Scene):
        self.target_dir = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        if self.target_dir.length() > 0:
            self.target_dir.normalize_ip()
        self._wander_target = _random_pos()
        self._wander_timer = 0.0
        super().__init__(start_pos, scene, initial_length=BOT_INITIAL_LENGTH, ctype_head="bot_head", ctype_seg="bot_segment")
        self.speed = BOT_SPEED

    def find_food_target(self, foods: list[s.Sprite]) -> Vector2 | None:
        head = Vector2(self.head.rect.center)
        best: Vector2 | None = None
        best_dist = float("inf")
        for food in foods:
            if not food.active:
                continue
            fpos = Vector2(food.rect.center)
            d = head.distance_squared_to(fpos)
            if d < best_dist:
                best_dist = d
                best = fpos
        return best

    def update(self, dt: float, foods: list[s.Sprite]) -> None:
        if not self.alive:
            return

        desired = self._pick_desired_direction(foods)
        self._smooth_turn(desired, dt)

        head_pos = Vector2(self.head.rect.center)
        dx = self.target_dir.x
        dy = self.target_dir.y

        new_x = head_pos.x + dx * self.speed * dt
        new_y = head_pos.y + dy * self.speed * dt

        self.head.rect.center = (int(new_x), int(new_y))
        self.head.angle = math.degrees(math.atan2(-dy, dx))

        self.trail.append(self.head.rect.center)
        self._update_segments()

    def _pick_desired_direction(self, foods: list[s.Sprite]) -> Vector2:
        head = Vector2(self.head.rect.center)
        target = self.find_food_target(foods)

        steer = Vector2(0, 0)

        if target is not None:
            to_food = target - head
            dist = to_food.length()
            if dist > 0:
                weight = min(1.0, 300.0 / max(dist, 1.0))
                steer += to_food / dist * weight

        margin = BOT_AVOID_WALL_DIST
        if head.x < margin:
            steer.x += (margin - head.x) / margin
        elif head.x > WORLD_WIDTH - margin:
            steer.x -= (head.x - (WORLD_WIDTH - margin)) / margin
        if head.y < margin:
            steer.y += (margin - head.y) / margin
        elif head.y > WORLD_HEIGHT - margin:
            steer.y -= (head.y - (WORLD_HEIGHT - margin)) / margin

        if steer.length() < 0.01:
            self._wander_timer += 0.016
            if self._wander_timer > 2.0:
                self._wander_target = _random_pos()
                self._wander_timer = 0.0
            to_wander = self._wander_target - head
            if to_wander.length() > 0:
                steer = to_wander.normalize() * 0.5

        if steer.length() > 0:
            steer = steer.normalize()
        return steer

    def _smooth_turn(self, desired: Vector2, dt: float) -> None:
        if desired.length() < 0.01:
            return
        turn_rate = 4.0
        angle_current = math.atan2(-self.target_dir.y, self.target_dir.x)
        angle_desired = math.atan2(-desired.y, desired.x)
        diff = angle_desired - angle_current
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        max_step = turn_rate * dt
        if abs(diff) <= max_step:
            self.target_dir = desired
        else:
            angle_new = angle_current + math.copysign(max_step, diff)
            self.target_dir = Vector2(math.cos(angle_new), -math.sin(angle_new))
