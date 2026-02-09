"""Решение 9: финальная мини‑игра по требованиям."""

import pygame
import spritePro as s


def _ctx() -> s.multiplayer.MultiplayerContext:
    return s.multiplayer.get_context()


RESULT = {"winner": "", "scores": {"host": 0, "client": 0}}
TARGET_SCORE = 5


def update_score_text(text_sprite: s.TextSprite, scores: dict) -> None:
    # Обновление текста счета.
    text_sprite.set_text(f"Score  host={scores['host']}  client={scores['client']}")


def move_player(sprite: s.Sprite, speed: float, dt: float) -> None:
    # Движение игрока.
    dx = s.input.get_axis(pygame.K_a, pygame.K_d)
    dy = s.input.get_axis(pygame.K_w, pygame.K_s)
    pos = sprite.get_world_position()
    pos.x += dx * speed * dt
    pos.y += dy * speed * dt
    sprite.set_position(pos)


def is_in_target(pos: s.Vector2) -> bool:
    # Проверка попадания в центр.
    dx = pos.x - 400
    dy = pos.y - 300
    return (dx * dx + dy * dy) <= 30 * 30


class GameScene(s.Scene):
    def on_enter(self, context):
        # Игроки и цель.
        ctx = _ctx()
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.other = s.Sprite("", (40, 40), (600, 300), scene=self)
        my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
        other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
        self.me.set_color(my_color)
        self.other.set_color(other_color)

        self.target = s.Sprite("", (60, 60), (400, 300), scene=self)
        self.target.set_color((80, 200, 120))

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
        self.speed = 240.0

    def update(self, dt):
        ctx = _ctx()
        # Локальное движение.
        move_player(self.me, self.speed, dt)
        pos = self.me.get_world_position()

        # Отправка позиции с лимитом.
        ctx.send_every("pos", {"x": pos.x, "y": pos.y}, 0.05)

        # Начисление очков по зоне.
        self.score_cooldown = max(0.0, self.score_cooldown - dt)
        if self.score_cooldown <= 0.0 and is_in_target(pos):
            self.score_cooldown = 0.5
            player_key = "host" if ctx.is_host else "client"
            ctx.send("score", {"id": player_key})

        # Обработка сообщений.
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "pos":
                self.remote_pos[:] = [
                    float(data.get("x", self.remote_pos[0])),
                    float(data.get("y", self.remote_pos[1])),
                ]
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
                s.scene.set_scene_by_name("game", recreate=True)
                return

        # Обновляем отображение.
        self.other.set_position(self.remote_pos)
        update_score_text(self.score_text, self.scores)


class ResultScene(s.Scene):
    def on_enter(self, context):
        # Экран результата.
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
        # Перезапуск от хоста.
        ctx = _ctx()
        if ctx.is_host and s.input.was_pressed(pygame.K_r):
            ctx.send("restart", {})
            s.scene.set_scene_by_name("game", recreate=True)


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    # Инициализация контекста.
    s.multiplayer.init_context(net, role, color)

    # Настройка сцен.
    s.get_screen((800, 600), "Lesson 9 - Final Exam")
    s.scene.add_scene("game", GameScene)
    s.scene.add_scene("result", ResultScene)
    s.scene.set_scene_by_name("game", recreate=True)

    while True:
        # Основной тик.
        s.update(fill_color=(16, 16, 22))


if __name__ == "__main__":
    # Запуск решения.
    s.networking.run()
