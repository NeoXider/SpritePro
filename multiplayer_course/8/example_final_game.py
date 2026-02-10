"""Пример 8: финальная сборка мини‑игры с рефакторингом.

Та же логика, что в уроке 7: меню → игра до TARGET_SCORE → результат → restart.
Константы и вспомогательные функции вынесены в game_config и локальные функции.
"""

import pygame
import spritePro as s

from game_config import (
    SCREEN_SIZE,
    TARGET_SCORE,
    SEND_INTERVAL,
    SCORE_COOLDOWN,
    PLAYER_SPEED,
    COLOR_RED,
    COLOR_BLUE,
    COLOR_BG,
    COLOR_TARGET,
)

RESULT = {"winner": "", "scores": {"host": 0, "client": 0}}


def _ctx() -> s.multiplayer.MultiplayerContext:
    return s.multiplayer.get_context()


def update_score_text(text_sprite: s.TextSprite, scores: dict) -> None:
    text_sprite.set_text(f"Score  host={scores['host']}  client={scores['client']}")


def move_player(sprite: s.Sprite, speed: float, dt: float) -> None:
    """Движение спрайта по WASD с учётом dt."""
    dx = s.input.get_axis(pygame.K_a, pygame.K_d)
    dy = s.input.get_axis(pygame.K_w, pygame.K_s)
    pos = sprite.get_world_position()
    pos.x += dx * speed * dt
    pos.y += dy * speed * dt
    sprite.set_position(pos)


def is_in_target(pos: s.Vector2) -> bool:
    """Попал ли игрок в центральную зону (радиус 30)."""
    dx = pos.x - 400
    dy = pos.y - 300
    return (dx * dx + dy * dy) <= 30 * 30


class MenuScene(s.Scene):
    def on_enter(self, context):
        self.is_ready = False
        self.game_started = False
        self.ready_map = {"host": False, "client": False}

        # UI меню.
        s.TextSprite("Menu", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT, scene=self)
        self.status = s.TextSprite(
            "State: lobby",
            24,
            (220, 220, 220),
            (20, 70),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.ready_button = s.Button(
            "",
            size=(220, 60),
            pos=(SCREEN_SIZE[0] // 2, 300),
            text="Ready: OFF",
            text_size=26,
            base_color=(230, 230, 230),
            on_click=self.toggle_ready,
            scene=self,
        )

    def toggle_ready(self):
        # Переключаем готовность.
        self.is_ready = not self.is_ready
        ctx = _ctx()
        player_key = "host" if ctx.is_host else "client"
        ctx.send("ready", {"id": player_key, "value": self.is_ready})
        self.ready_button.text_sprite.set_text("Ready: ON" if self.is_ready else "Ready: OFF")

    def update(self, dt):
        # Обработка сетевых сообщений.
        ctx = _ctx()
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "ready":
                player_id = data.get("id")
                if player_id in self.ready_map:
                    self.ready_map[player_id] = bool(data.get("value"))
            elif event == "start":
                self.game_started = True
                s.scene.set_scene_by_name("game", recreate=True)
                return

        # Хост запускает матч.
        if ctx.is_host and not self.game_started:
            if all(self.ready_map.values()):
                ctx.send("start", {})
                self.game_started = True
                s.scene.set_scene_by_name("game", recreate=True)
                return

        # Обновляем статус.
        self.status.set_text(
            f"State: lobby | host={self.ready_map['host']} client={self.ready_map['client']}"
        )


class GameScene(s.Scene):
    def on_enter(self, context):
        # Игроки и цель.
        ctx = _ctx()
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.other = s.Sprite("", (40, 40), (600, 300), scene=self)
        my_color = COLOR_RED if ctx.is_host else COLOR_BLUE
        other_color = COLOR_BLUE if ctx.is_host else COLOR_RED
        self.me.set_color(my_color)
        self.other.set_color(other_color)

        self.target = s.Sprite("", (60, 60), (400, 300), scene=self)
        self.target.set_color(COLOR_TARGET)

        # Счет и UI.
        self.scores = {"host": 0, "client": 0}
        self.score_text = s.TextSprite(
            "", 26, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT, scene=self
        )

        # Сетевые параметры.
        self.remote_pos = [
            self.other.get_world_position().x,
            self.other.get_world_position().y,
        ]
        self.score_cooldown = 0.0

    def update(self, dt):
        ctx = _ctx()
        move_player(self.me, PLAYER_SPEED, dt)
        pos = self.me.get_world_position()
        ctx.send_every("pos", {"pos": list(pos)}, SEND_INTERVAL)
        self.score_cooldown = max(0.0, self.score_cooldown - dt)
        if self.score_cooldown <= 0.0 and is_in_target(pos):
            self.score_cooldown = SCORE_COOLDOWN
            player_key = "host" if ctx.is_host else "client"
            ctx.send("score", {"id": player_key})
        # pos, score/score_update, game_over, restart — как в уроке 7.
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "pos":
                self.remote_pos[:] = data.get("pos", self.remote_pos)
            elif event == "score" and ctx.is_host:
                player_id = data.get("id")
                if player_id in self.scores:
                    self.scores[player_id] += 1
                    ctx.send("score_update", {"scores": self.scores})
                    winner = max(self.scores, key=self.scores.get)
                    if self.scores[winner] >= TARGET_SCORE:
                        ctx.send("game_over", {"winner": winner, "scores": self.scores})
            elif event == "score_update":
                self.scores = dict(data.get("scores", self.scores))
            elif event == "game_over":
                RESULT["winner"] = data.get("winner", "")
                RESULT["scores"] = dict(data.get("scores", self.scores))
                s.scene.set_scene_by_name("result", recreate=True)
                return
            elif event == "restart":
                s.scene.set_scene_by_name("menu", recreate=True)
                return
        self.other.set_position(self.remote_pos)
        update_score_text(self.score_text, self.scores)


class ResultScene(s.Scene):
    def on_enter(self, context):
        winner = RESULT.get("winner", "")
        scores = RESULT.get("scores", {"host": 0, "client": 0})
        s.TextSprite(
            "Result",
            34,
            (240, 240, 240),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        s.TextSprite(
            f"Winner: {winner}",
            26,
            (240, 240, 240),
            (20, 80),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        s.TextSprite(
            f"Score  host={scores['host']}  client={scores['client']}",
            24,
            (220, 220, 220),
            (20, 120),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        s.TextSprite(
            "Press R to restart",
            22,
            (180, 180, 180),
            (20, 520),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def update(self, dt):
        ctx = _ctx()
        if ctx.is_host and s.input.was_pressed(pygame.K_r):
            ctx.send("restart", {})
            s.scene.set_scene_by_name("menu", recreate=True)


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.multiplayer.init_context(net, role)
    s.get_screen(SCREEN_SIZE, "Lesson 8 - Final Game")
    s.scene.add_scene("menu", MenuScene)
    s.scene.add_scene("game", GameScene)
    s.scene.add_scene("result", ResultScene)
    s.scene.set_scene_by_name("menu", recreate=True)

    while True:
        # Основной тик.
        s.update(fill_color=COLOR_BG)


if __name__ == "__main__":
    # Запуск примера.
    s.networking.run()
