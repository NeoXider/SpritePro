import time
import pygame
import spritePro as s
from game.config import (
    WORLD_WIDTH, WORLD_HEIGHT, BOT_COUNT,
    BOT_RESPAWN_DELAY, HEAD_SIZE, FOOD_SIZE,
    SEGMENT_SIZE,
)
from game.snake import Snake, _dim_color
from game.bot import BotSnake
from game.food import FoodManager
from game.world import World
from ui.hud import HUD


def _circle_collide(
    a: tuple[int, int], b: tuple[int, int],
    ra: int, rb: int,
) -> bool:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy < (ra + rb) * (ra + rb)


_REMOTE_TIMEOUT = 5.0
_FOOD_SYNC_INTERVAL = 0.25


class RemoteSnake:
    def __init__(self, scene: s.Scene, client_id: int):
        self.scene = scene
        self.client_id = client_id
        self.last_seen = time.time()
        self.segments: list[s.Sprite] = []
        self.head = s.Sprite("", (HEAD_SIZE, HEAD_SIZE), (0, 0), scene=scene)
        self.head.set_circle_shape(radius=HEAD_SIZE // 2, color=(255, 255, 255))
        self.head.set_sorting_order(10)
        self._seg_color = (180, 180, 180)
        self._set_color((255, 255, 255))

    def _set_color(self, color: tuple[int, int, int]) -> None:
        self.head.set_color(color)
        self._seg_color = _dim_color(color, 0.7)
        for seg in self.segments:
            seg.set_color(self._seg_color)

    def update_from_data(self, data: dict) -> None:
        self.last_seen = time.time()
        head_pos = data["head"]
        seg_positions = data.get("segments", [])

        self.head.rect.center = (int(head_pos[0]), int(head_pos[1]))
        angle = data.get("angle", 0)
        self.head.angle = angle

        rc = data.get("color")
        if rc is not None and tuple(rc) != self.head.color:
            self._set_color(tuple(rc))

        while len(self.segments) < len(seg_positions):
            seg = s.Sprite("", (SEGMENT_SIZE, SEGMENT_SIZE), (0, 0), scene=self.scene)
            seg.set_circle_shape(radius=SEGMENT_SIZE // 2, color=self._seg_color)
            seg.set_sorting_order(5)
            self.segments.append(seg)
        while len(self.segments) > len(seg_positions):
            seg = self.segments.pop()
            if seg.active:
                s.disable_sprite(seg)

        for seg, pos in zip(self.segments, seg_positions):
            seg.rect.center = (int(pos[0]), int(pos[1]))

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    def destroy(self) -> None:
        if self.head.active:
            s.disable_sprite(self.head)
        for seg in self.segments:
            if seg.active:
                s.disable_sprite(seg)
        self.segments.clear()


class GameScene(s.Scene):
    def __init__(self, net=None, role=None):
        self.net = net
        self.role = role
        self.is_multiplayer = net is not None
        self.ctx = s.multiplayer_ctx if self.is_multiplayer else None
        super().__init__()
        self._init_game()

    def _init_game(self) -> None:
        self.score = 0
        self.game_over = False
        self._respawn_queue = 0
        self._respawn_timer = 0.0
        self.remote_snakes: dict[int, RemoteSnake] = {}
        self._food_sync_timer = 0.0

        self.world = World(self)
        start = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.snake = Snake(start, self)

        self.bots: list[BotSnake] = []
        self._spawn_bots()

        self.food = FoodManager(self)
        self.hud = HUD(self)

        s.set_camera_follow(self.snake.head, (0, 0))
        s.set_camera_zoom(0.6)

    def on_exit(self) -> None:
        s.clear_camera_follow()

    def update(self, dt: float) -> None:
        if self.game_over:
            if s.input.was_pressed(pygame.K_r):
                self._restart()
            return

        self.snake.update(dt)
        for bot in self.bots:
            bot.update(dt, self.food.foods)

        if not self.is_multiplayer or self.ctx.is_host:
            self.food.maintain_count()
        self._check_collisions()

        if self.is_multiplayer:
            self._sync_network(dt)

        entries = [("Player", self.snake)]
        for i, bot in enumerate(self.bots):
            if bot.alive:
                entries.append((f"Bot {i+1}", bot))
        for cid, r in sorted(self.remote_snakes.items()):
            entries.append((f"Player {cid}", r))
        self.hud.update_leaderboard(entries)

        self._update_respawn(dt)

    def _sync_network(self, dt: float) -> None:
        ctx = self.ctx
        if ctx is None:
            return

        head = self.snake.head.rect.center
        segs = [seg.rect.center for seg in self.snake.segments]
        ctx.send_every("player_snake", {
            "head": head,
            "segments": segs,
            "angle": self.snake.head.angle,
            "score": self.score,
            "color": self.snake.color,
        }, 1.0 / 30.0)

        if ctx.is_host:
            self._food_sync_timer += dt
            if self._food_sync_timer >= _FOOD_SYNC_INTERVAL:
                self._food_sync_timer = 0.0
                ctx.send("food_state", {"foods": self.food.get_state()})

        now = time.time()
        for msg in ctx.poll():
            data = msg.get("data", {})
            ev = msg.get("event", "")
            sid = data.get("sender_id")

            if ev == "player_snake" and sid is not None and sid != ctx.client_id:
                if sid not in self.remote_snakes:
                    self.remote_snakes[sid] = RemoteSnake(self, sid)
                self.remote_snakes[sid].update_from_data(data)

            if ev == "food_state" and not ctx.is_host:
                self.food.sync_from_data(data.get("foods", []))

        stale = [sid for sid, r in self.remote_snakes.items()
                 if now - r.last_seen > _REMOTE_TIMEOUT]
        for sid in stale:
            self.remote_snakes.pop(sid).destroy()

    def _check_collisions(self) -> None:
        head = self.snake.head

        for food in list(self.food.foods):
            if food.active and _circle_collide(head.rect.center, food.rect.center, HEAD_SIZE // 2, FOOD_SIZE):
                self._player_eat(food)

        for bot in list(self.bots):
            if not bot.alive:
                continue
            for seg in bot.segments:
                if seg.active and head.rect.colliderect(seg.rect):
                    self._trigger_game_over()
                    return

        for r in list(self.remote_snakes.values()):
            if head.rect.colliderect(r.head.rect):
                self._trigger_game_over()
                return
            for seg in r.segments:
                if seg.active and head.rect.colliderect(seg.rect):
                    self._trigger_game_over()
                    return

        for wall in self.world.walls:
            if head.rect.colliderect(wall.rect):
                self._trigger_game_over()
                return

        for bot in list(self.bots):
            if not bot.alive:
                continue
            for food in list(self.food.foods):
                if food.active and _circle_collide(bot.head.rect.center, food.rect.center, HEAD_SIZE // 2, FOOD_SIZE):
                    self._bot_eat(bot.head, food)
                    break
            for seg in self.snake.segments:
                if seg.active and bot.head.rect.colliderect(seg.rect):
                    self._bot_killed(bot.head)
                    break
            for other in list(self.bots):
                if other is bot or not other.alive:
                    continue
                for seg in other.segments:
                    if seg.active and bot.head.rect.colliderect(seg.rect):
                        self._bot_killed(bot.head)
                        break

    def _player_eat(self, food_sprite: s.Sprite) -> None:
        if self.game_over:
            return
        self.food._disable_food(food_sprite)
        if food_sprite in self.food.foods:
            self.food.foods.remove(food_sprite)
        self.score += 1
        self.snake.grow()
        self.hud.update_score(self.score)
        self.hud.update_length(len(self.snake.segments))
        if not self.is_multiplayer or self.ctx.is_host:
            self.food.maintain_count()

    def _bot_eat(self, bot_head: s.Sprite, food_sprite: s.Sprite) -> None:
        self.food._disable_food(food_sprite)
        if food_sprite in self.food.foods:
            self.food.foods.remove(food_sprite)
        for bot in self.bots:
            if bot.head is bot_head and bot.alive:
                bot.grow()
                if not self.is_multiplayer or self.ctx.is_host:
                    self.food.maintain_count()
                break

    def _bot_killed(self, bot_head: s.Sprite) -> None:
        for bot in self.bots:
            if bot.head is bot_head and bot.alive:
                bot.alive = False
                self._kill_bot(bot)
                return

    def _spawn_bots(self) -> None:
        import random as _r
        for _ in range(BOT_COUNT):
            x = _r.randint(200, WORLD_WIDTH - 200)
            y = _r.randint(200, WORLD_HEIGHT - 200)
            self.bots.append(BotSnake((x, y), self))

    def _update_respawn(self, dt: float) -> None:
        if self._respawn_queue <= 0:
            return
        self._respawn_timer += dt
        if self._respawn_timer >= BOT_RESPAWN_DELAY:
            self._respawn_timer = 0.0
            self._respawn_queue -= 1
            import random as _r
            x = _r.randint(200, WORLD_WIDTH - 200)
            y = _r.randint(200, WORLD_HEIGHT - 200)
            self.bots.append(BotSnake((x, y), self))

    def _kill_bot(self, bot: BotSnake) -> None:
        segments = [bot.head] + bot.segments
        for seg in segments:
            self.food.spawn_at(seg.rect.center)
            if seg.active:
                s.disable_sprite(seg)
        bot.segments.clear()
        bot.trail.clear()
        bot.alive = False
        if bot in self.bots:
            self.bots.remove(bot)
        self._respawn_queue += 1
        self.score += 5
        self.hud.update_score(self.score)

    def _trigger_game_over(self) -> None:
        self.game_over = True
        self.snake.die()
        for bot in self.bots:
            for seg in [bot.head] + bot.segments:
                if seg.active:
                    s.disable_sprite(seg)
            bot.segments.clear()
            bot.trail.clear()
            bot.alive = False
        self.bots.clear()
        self.hud.show_game_over(self.score)

    def _restart(self) -> None:
        for sprite in list(s.get_game().all_sprites):
            if getattr(sprite, "scene", None) is self and sprite.active:
                s.disable_sprite(sprite)
        self._init_game()
