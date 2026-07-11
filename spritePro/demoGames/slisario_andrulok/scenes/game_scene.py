"""Игровая сцена: геймплей, столкновения и сетевая синхронизация.

Модель сети — host-authoritative:

- своей змейкой владеет каждый игрок и рассылает её состояние (player_state);
- еда и боты симулируются только авторитетом (хост либо одиночная игра),
  клиенты получают их событиями и снапшотами (food_eaten, food_state, bot_state);
- клиент лишь просит съесть еду (eat_food) и растёт после подтверждения
  хоста (food_eaten) — поэтому двое не могут съесть одну и ту же еду;
- о смерти игрок сообщает сам (player_died), хост превращает его тело в еду;
  отключившихся хост убирает событием player_left.
"""

import random
import time

import pygame
import spritePro as s

from game.config import (
    WORLD_WIDTH, WORLD_HEIGHT, BOT_COUNT, BOT_RESPAWN_DELAY,
    HEAD_SIZE, SEGMENT_SIZE, SPAWN_MARGIN,
    SNAKE_SYNC_INTERVAL, BOT_SYNC_INTERVAL, FOOD_SNAPSHOT_INTERVAL, REMOTE_TIMEOUT,
)
from game.snake import Snake
from game.bot import BotSnake
from game.food import FoodManager
from game.net_view import NetSnakeView
from game.world import World
from ui.hud import HUD

_HEAD_R = HEAD_SIZE // 2
_SEG_R = SEGMENT_SIZE // 2


def _circle_collide(
    a: tuple[int, int], b: tuple[int, int],
    ra: int, rb: int,
) -> bool:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy < (ra + rb) * (ra + rb)


class GameScene(s.Scene):
    def __init__(self, net=None, role=None):
        self.net = net
        self.role = role
        self.ctx = s.multiplayer_ctx if net is not None else None
        self.is_multiplayer = self.ctx is not None
        self.is_authority = self.ctx is None or self.ctx.is_host
        super().__init__()
        self._init_game()

    # ------------------------------------------------------------------ setup

    def _init_game(self, food_restore: list[dict] | None = None) -> None:
        self.score = 0
        self.game_over = False
        self._death_sent = False
        self.remote_snakes: dict[int, NetSnakeView] = {}
        self.bot_views: dict[int, NetSnakeView] = {}
        self.bots: list[BotSnake] = []
        self._next_bot_id = 0
        self._bot_respawn_timers: list[float] = []
        self._food_snapshot_timer = 0.0

        self.world = World(self)
        self.snake = Snake(self._spawn_point(), self)
        self.food = FoodManager(self, authority=self.is_authority, restore=food_restore)
        if self.is_authority:
            for _ in range(BOT_COUNT):
                self._spawn_bot()
        self.hud = HUD(self, show_ping=self.is_multiplayer)

        s.set_camera_follow(self.snake.head, (0, 0))
        s.set_camera_zoom(0.6)

    def _spawn_point(self) -> tuple[int, int]:
        # В мультиплеере — случайная точка, чтобы игроки не спавнились друг в друге.
        if self.is_multiplayer:
            return (
                random.randint(SPAWN_MARGIN, WORLD_WIDTH - SPAWN_MARGIN),
                random.randint(SPAWN_MARGIN, WORLD_HEIGHT - SPAWN_MARGIN),
            )
        return (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

    def _spawn_bot(self) -> None:
        pos = (
            random.randint(SPAWN_MARGIN, WORLD_WIDTH - SPAWN_MARGIN),
            random.randint(SPAWN_MARGIN, WORLD_HEIGHT - SPAWN_MARGIN),
        )
        self.bots.append(BotSnake(self._next_bot_id, pos, self))
        self._next_bot_id += 1

    def on_exit(self) -> None:
        s.clear_camera_follow()

    # ----------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        if not self.game_over:
            self.snake.update(dt)

        if self.is_authority:
            foods = list(self.food.foods.values())
            for bot in self.bots:
                bot.update(dt, foods)
            self._authority_collisions()
            self._update_bot_respawns(dt)
            self.food.maintain_count()

        if not self.game_over:
            self._player_collisions()

        if self.is_multiplayer:
            self._sync_network(dt)

        self._update_hud()

        if self.game_over and s.input.was_pressed(pygame.K_r):
            self._restart()

    # ------------------------------------------------------------- collisions

    @staticmethod
    def _hits_body(pos: tuple[int, int], segments: list[s.Sprite]) -> bool:
        return any(
            _circle_collide(pos, seg.rect.center, _HEAD_R, _SEG_R)
            for seg in segments
        )

    def _player_collisions(self) -> None:
        head = self.snake.head
        head_c = head.rect.center

        food_id = self.food.find_at(head_c, _HEAD_R)
        if food_id is not None:
            self._eat(food_id)

        for wall in self.world.walls:
            if head.rect.colliderect(wall.rect):
                self._die()
                return

        if self.is_authority:
            for bot in list(self.bots):
                # Лоб в лоб — гибнут оба.
                if _circle_collide(head_c, bot.head.rect.center, _HEAD_R, _HEAD_R):
                    self._kill_bot(bot)
                    self._die()
                    return
                if self._hits_body(head_c, bot.segments):
                    self._die()
                    return
        else:
            for view in self.bot_views.values():
                if (
                    _circle_collide(head_c, view.head.rect.center, _HEAD_R, _HEAD_R)
                    or self._hits_body(head_c, view.segments)
                ):
                    self._die()
                    return

        for view in self.remote_snakes.values():
            if (
                _circle_collide(head_c, view.head.rect.center, _HEAD_R, _HEAD_R)
                or self._hits_body(head_c, view.segments)
            ):
                self._die()
                return

    def _authority_collisions(self) -> None:
        for bot in list(self.bots):
            head_c = bot.head.rect.center

            food_id = self.food.find_at(head_c, _HEAD_R)
            if food_id is not None and self.food.remove(food_id):
                bot.grow()
                if self.ctx is not None:
                    self.ctx.send("food_eaten", {"food_id": food_id, "eater_id": None})

            if self._bot_hits_deadly(bot):
                self._kill_bot(bot)

    def _bot_hits_deadly(self, bot: BotSnake) -> bool:
        head_c = bot.head.rect.center
        for wall in self.world.walls:
            if bot.head.rect.colliderect(wall.rect):
                return True
        if not self.game_over and self._hits_body(head_c, self.snake.segments):
            return True
        for other in self.bots:
            if other is not bot and self._hits_body(head_c, other.segments):
                return True
        for view in self.remote_snakes.values():
            if self._hits_body(head_c, view.segments):
                return True
        return False

    # --------------------------------------------------------------- gameplay

    def _eat(self, food_id: int) -> None:
        # Еду убираем сразу (отзывчивость), но рост на клиенте происходит
        # только после подтверждения хоста событием food_eaten.
        self.food.remove(food_id)
        if self.is_authority:
            self._grow_player()
            if self.ctx is not None:
                self.ctx.send("food_eaten", {"food_id": food_id, "eater_id": self.ctx.client_id})
        else:
            self.ctx.send("eat_food", {"food_id": food_id})

    def _grow_player(self) -> None:
        self.score += 1
        self.snake.grow()
        self.hud.update_score(self.score)
        self.hud.update_length(len(self.snake.segments))

    def _die(self) -> None:
        if self.game_over:
            return
        self.game_over = True
        self.snake.die()
        if self.is_multiplayer and not self._death_sent:
            self._death_sent = True
            self.ctx.send(
                "player_died",
                {"segments": [list(p) for p in self.snake.body_positions()]},
            )
        if self.is_authority and self.is_multiplayer:
            self._drop_food(self.snake.body_positions())
        self.hud.show_game_over(self.score)

    def _kill_bot(self, bot: BotSnake) -> None:
        if bot not in self.bots:
            return
        self.bots.remove(bot)
        positions = bot.body_positions()
        bot.destroy()
        self._drop_food(positions)
        self._bot_respawn_timers.append(BOT_RESPAWN_DELAY)

    def _drop_food(self, positions: list[tuple[int, int]]) -> None:
        for pos in positions:
            self.food.spawn_at((int(pos[0]), int(pos[1])))
        # Форсируем ближайший снапшот, чтобы клиенты увидели выпавшую еду сразу.
        self._food_snapshot_timer = FOOD_SNAPSHOT_INTERVAL

    def _update_bot_respawns(self, dt: float) -> None:
        remaining: list[float] = []
        for timer in self._bot_respawn_timers:
            timer -= dt
            if timer <= 0:
                self._spawn_bot()
            else:
                remaining.append(timer)
        self._bot_respawn_timers = remaining

    # ---------------------------------------------------------------- network

    def _sync_network(self, dt: float) -> None:
        ctx = self.ctx

        if not self.game_over:
            state = self.snake.get_state()
            state["score"] = self.score
            ctx.send_every("player_state", state, SNAKE_SYNC_INTERVAL)

        if self.is_authority:
            self._food_snapshot_timer += dt
            if self._food_snapshot_timer >= FOOD_SNAPSHOT_INTERVAL:
                self._food_snapshot_timer = 0.0
                ctx.send("food_state", {"foods": self.food.get_state()})
            ctx.send_every(
                "bot_state",
                {"bots": [bot.get_state() for bot in self.bots]},
                BOT_SYNC_INTERVAL,
            )

        self._handle_net_messages()
        self._drop_stale_remotes()

    def _handle_net_messages(self) -> None:
        for msg in self.ctx.poll():
            event = msg.get("event", "")
            data = msg.get("data") or {}
            sender_id = data.get("sender_id")

            if event == "player_state" and sender_id is not None:
                view = self.remote_snakes.get(sender_id)
                if view is None:
                    view = self.remote_snakes[sender_id] = NetSnakeView(self)
                view.apply_state(data)

            elif event == "player_died" and sender_id is not None:
                self._remove_remote(sender_id, drop_positions=data.get("segments"))

            elif event == "player_left":
                self._remove_remote(data.get("id"))

            elif event == "eat_food" and self.is_authority:
                food_id = data.get("food_id")
                if food_id is not None and self.food.remove(int(food_id)):
                    self.ctx.send(
                        "food_eaten",
                        {"food_id": int(food_id), "eater_id": sender_id},
                    )

            elif event == "food_eaten":
                food_id = data.get("food_id")
                if food_id is not None:
                    self.food.remove(int(food_id))
                if data.get("eater_id") == self.ctx.client_id and not self.game_over:
                    self._grow_player()

            elif event == "food_state" and not self.is_authority:
                self.food.apply_state(data.get("foods", []))

            elif event == "bot_state" and not self.is_authority:
                self._apply_bot_state(data.get("bots", []))

            elif event == "client_disconnected" and self.is_authority:
                client_id = data.get("client_id")
                self._remove_remote(client_id)
                self.ctx.send("player_left", {"id": client_id})

    def _apply_bot_state(self, bots: list[dict]) -> None:
        seen: set[int] = set()
        for state in bots:
            bot_id = state.get("id")
            if bot_id is None:
                continue
            seen.add(bot_id)
            view = self.bot_views.get(bot_id)
            if view is None:
                view = self.bot_views[bot_id] = NetSnakeView(self)
            view.apply_state(state)
        for bot_id in [bid for bid in self.bot_views if bid not in seen]:
            self.bot_views.pop(bot_id).destroy()

    def _remove_remote(self, sender_id, drop_positions: list | None = None) -> None:
        if sender_id is None:
            return
        view = self.remote_snakes.pop(int(sender_id), None)
        positions = drop_positions or (view.body_positions() if view else [])
        if view is not None:
            view.destroy()
        if self.is_authority and positions:
            self._drop_food([(int(p[0]), int(p[1])) for p in positions])

    def _drop_stale_remotes(self) -> None:
        now = time.time()
        stale = [
            sender_id for sender_id, view in self.remote_snakes.items()
            if now - view.last_seen > REMOTE_TIMEOUT
        ]
        for sender_id in stale:
            self._remove_remote(sender_id)

    # -------------------------------------------------------------------- hud

    def _update_hud(self) -> None:
        entries: list[tuple[str, int]] = []
        if not self.game_over:
            name = f"You (id {self.ctx.client_id})" if self.is_multiplayer else "You"
            entries.append((name, len(self.snake.segments)))
        if self.is_authority:
            for bot in self.bots:
                entries.append((f"Bot {bot.bot_id}", len(bot.segments)))
        else:
            for bot_id, view in self.bot_views.items():
                entries.append((f"Bot {bot_id}", view.segment_count))
        for sender_id, view in sorted(self.remote_snakes.items()):
            entries.append((f"Player {sender_id}", view.segment_count))
        self.hud.update_leaderboard(entries)

        if self.is_multiplayer:
            self.hud.update_ping(self.ctx.ping_ms)

    # ---------------------------------------------------------------- restart

    def _restart(self) -> None:
        # На хосте сохраняем еду, чтобы рестарт хоста не перемешивал её у всех.
        food_restore = (
            self.food.get_state()
            if self.is_multiplayer and self.is_authority
            else None
        )
        for sprite in list(s.get_game().all_sprites):
            if getattr(sprite, "scene", None) is self and sprite.active:
                s.disable_sprite(sprite)
        self._init_game(food_restore=food_restore)
