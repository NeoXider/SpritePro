"""Практика 7: экран результатов и перезапуск (TODO).

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал.
"""

import pygame
import spritePro as s

RESULT = {"winner": "", "scores": {"host": 0, "client": 0}}
TARGET_SCORE = 5


def _ctx() -> s.multiplayer.MultiplayerContext:
    return s.multiplayer.get_context()


class MenuScene(s.Scene):
    def on_enter(self, context):
        # Состояние лобби.
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
            pos=(400, 300),
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
        # Обработка сетевых событий.
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
        my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
        other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
        self.me.set_color(my_color)
        self.other.set_color(other_color)

        # Целевая зона.
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
        # Движение локального игрока.
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * self.speed * dt
        pos.y += dy * self.speed * dt
        self.me.set_position(pos)

        # Отправка позиции.
        ctx.send_every("pos", {"pos": list(pos)}, 0.05)

        # Начисление очков.
        self.score_cooldown = max(0.0, self.score_cooldown - dt)
        dx_t = pos.x - 400
        dy_t = pos.y - 300
        if self.score_cooldown <= 0.0 and (dx_t * dx_t + dy_t * dy_t) <= 30 * 30:
            self.score_cooldown = 0.5
            player_key = "host" if ctx.is_host else "client"
            ctx.send("score", {"id": player_key})

        # Обработка сетевых сообщений.
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
                    # TODO: если кто-то достиг TARGET_SCORE, отправьте "game_over".
            elif event == "score_update":
                self.scores = dict(data.get("scores", self.scores))
            elif event == "game_over":
                # TODO: сохраните результат и перейдите в "result".
                pass
            elif event == "restart":
                # TODO: вернитесь в "menu".
                pass

        # Обновляем отображение.
        self.other.set_position(self.remote_pos)
        self.score_text.set_text(
            f"Score  host={self.scores['host']}  client={self.scores['client']}"
        )


class ResultScene(s.Scene):
    def on_enter(self, context):
        # Экран результатов.
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
            # TODO: отправьте "restart" и вернитесь в "menu".
            pass


def multiplayer_main(net: s.NetClient, role: str) -> None:
    # Инициализация контекста.
    s.multiplayer.init_context(net, role)

    # Настройка сцен.
    s.get_screen((800, 600), "Lesson 7 - Practice")
    s.scene.add_scene("menu", MenuScene)
    s.scene.add_scene("game", GameScene)
    s.scene.add_scene("result", ResultScene)
    s.scene.set_scene_by_name("menu", recreate=True)

    while True:
        # Основной тик.
        s.update(fill_color=(16, 16, 22))


if __name__ == "__main__":
    # Запуск практики.
    s.networking.run()
