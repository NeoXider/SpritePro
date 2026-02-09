"""Пример 10: роутинг событий — local, server, all.

Показывает разницу между отправкой только локально, только в сеть (server)
и локально + в сеть (all). В текущем relay сервер пересылает любое сетевое
сообщение всем кроме отправителя; разница в том, вызываются ли локальные
подписчики и уходит ли сообщение в сокет.
"""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 600), "Lesson 10 - Routing")
    ctx = s.multiplayer.init_context(net, role)

    local_ping_count = 0
    local_emoji_count = 0

    # EventBus: подписываемся на события, чтобы видеть, когда они приходят «локально».
    def on_ping(**payload):
        nonlocal local_ping_count
        local_ping_count += 1
        print(f"  [local] on_ping вызван (раз локально: {local_ping_count})")

    def on_emoji(**payload):
        nonlocal local_emoji_count
        local_emoji_count += 1
        sym = payload.get("symbol", "?")
        print(f"  [local] on_emoji вызван symbol={sym} (раз локально: {local_emoji_count})")

    s.events.connect("ping", on_ping)
    s.events.connect("emoji", on_emoji)

    # UI: подсказки по роутингу.
    role_name = "host" if ctx.is_host else "client"
    s.TextSprite(
        f"Role: {role_name} | E = emoji (all) | P = ping (server)",
        22,
        (220, 220, 220),
        (20, 20),
        anchor=s.Anchor.TOP_LEFT,
    )
    s.TextSprite(
        "Смотри консоль: когда срабатывают локальные обработчики и когда приходят сообщения из сети.",
        18,
        (180, 180, 180),
        (20, 55),
        anchor=s.Anchor.TOP_LEFT,
    )

    while True:
        s.update(fill_color=(18, 18, 24))

        # s.events.send(..., route=..., net=...) — варианты route: "local" (только подписчики), "all" (локально+сеть),
        # "server"/"clients"/"net" (только в сеть, без локального вызова). Подробно: event_bus.EventBus.send в докстринге.
        # E — emoji всем (route="all"): локально on_emoji + в сеть.
        if s.input.was_pressed(pygame.K_e):
            s.events.send("emoji", route="all", net=ctx, symbol="👍")
            print("[send] emoji route=all (локально + сеть)")

        # P — ping только в сеть (route="server"): локальные подписчики не вызываются.
        if s.input.was_pressed(pygame.K_p):
            s.events.send("ping", route="server", net=ctx)
            print("[send] ping route=server (только в сеть, локально не вызываем)")

        # Проброс: send(ev, **data) без route/net — по умолчанию "local", только локальные обработчики (см. event_bus.send).
        for msg in ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)
