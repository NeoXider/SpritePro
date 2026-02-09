"""Решение 10: роутинг (ping — server, emoji — all) и ответы на вопросы практики."""

import pygame
import spritePro as s

PING_INTERVAL = 2.0


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "Lesson 10 - Solution Routing")
    ctx = s.multiplayer.init_context(net, role, color)

    ping_timer = 0.0

    def on_ping(**payload):
        print("  [local] on_ping")

    def on_emoji(**payload):
        print("  [local] on_emoji", payload.get("symbol"))

    s.events.connect("ping", on_ping)
    s.events.connect("emoji", on_emoji)

    s.TextSprite(
        "Ping каждые 2 сек (server) | E = emoji (all)",
        22,
        (240, 240, 240),
        (20, 20),
        anchor=s.Anchor.TOP_LEFT,
    )
    s.TextSprite(
        "ping — только в сеть (route=server), не вызываем локально; emoji — всем (route=all), все видят.",
        18,
        (180, 180, 180),
        (20, 50),
        anchor=s.Anchor.TOP_LEFT,
    )

    while True:
        s.update(fill_color=(18, 18, 24))
        dt = s.dt
        ping_timer += dt

        if ping_timer >= PING_INTERVAL:
            ping_timer = 0.0
            s.events.send("ping", route="server", net=ctx)

        if s.input.was_pressed(pygame.K_e):
            s.events.send("emoji", route="all", net=ctx, symbol="👋")

        for msg in ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)


# Задание 2: Почему хост рассылает score_update, а не клиент всем?
# Хост — источник истины для счёта. Клиент шлёт только заявку «я попал в зону» (score);
# хост проверяет (кулдаун, валидация) и рассылает уже итог (score_update). Иначе любой клиент
# мог бы слать «я набрал 10 очков» всем — без проверки (читы).

# Задание 3: Кто должен рассылать roster в лобби?
# Хост. Список игроков — состояние лобби; хост собирает join от всех и хранит единый roster,
# затем рассылает его всем. Если бы каждый рассылал свой список, состояния разъехались бы.
