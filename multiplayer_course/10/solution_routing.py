"""Решение 10: роутинг (ping — server, emoji — all) и ответы на вопросы практики."""

import pygame
import spritePro as s

PING_INTERVAL = 2.0


class RoutingSolutionScene(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.ping_timer = 0.0

        s.events.connect("ping", self.on_ping)
        s.events.connect("emoji", self.on_emoji)

        s.TextSprite(
            "Ping каждые 2 сек (server) | E = emoji (all)",
            22,
            (240, 240, 240),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        s.TextSprite(
            "ping — только в сеть (route=server), не вызываем локально; emoji — всем (route=all), все видят.",
            18,
            (180, 180, 180),
            (20, 50),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def on_ping(self, **payload):
        print("  [local] on_ping")

    def on_emoji(self, **payload):
        print("  [local] on_emoji", payload.get("symbol"))

    def update(self, dt: float) -> None:
        self.ping_timer += dt

        if self.ping_timer >= PING_INTERVAL:
            self.ping_timer = 0.0
            s.events.send("ping", route="server", net=self.ctx)

        if s.input.was_pressed(pygame.K_e):
            s.events.send("emoji", route="all", net=self.ctx, symbol="👋")

        for msg in self.ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)


def multiplayer_main() -> None:
    s.run(
        scene=RoutingSolutionScene,
        size=(800, 600),
        title="Lesson 10 - Solution Routing",
        fill_color=(18, 18, 24),
    )


# Задание 2: Почему хост рассылает score_update, а не клиент всем?
# Хост — источник истины для счёта. Клиент шлёт только заявку «я попал в зону» (score);
# хост проверяет (кулдаун, валидация) и рассылает уже итог (score_update). Иначе любой клиент
# мог бы слать «я набрал 10 очков» всем — без проверки (читы).

# Задание 3: Кто должен рассылать roster в лобби?
# Хост. Список игроков — состояние лобби; хост собирает join от всех и хранит единый roster,
# затем рассылает его всем. Если бы каждый рассылал свой список, состояния разъехались бы.


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main)
