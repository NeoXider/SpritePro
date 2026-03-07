"""Пример 10: роутинг событий — local, server, all.

Показывает разницу между отправкой только локально, только в сеть (server)
и локально + в сеть (all). В текущем relay сервер пересылает любое сетевое
сообщение всем кроме отправителя; разница в том, вызываются ли локальные
подписчики и уходит ли сообщение в сокет.
"""

import pygame
import spritePro as s


class RoutingScene(s.Scene):
    def __init__(self, net: s.NetClient, role: str) -> None:
        super().__init__()
        self.ctx = s.multiplayer.init_context(net, role)

        self.local_ping_count = 0
        self.local_emoji_count = 0

        # EventBus: подписываемся на события, чтобы видеть, когда они приходят «локально».
        s.events.connect("ping", self.on_ping)
        s.events.connect("emoji", self.on_emoji)

        # UI: подсказки по роутингу.
        role_name = "host" if self.ctx.is_host else "client"
        s.TextSprite(
            f"Role: {role_name} | E = emoji (all) | P = ping (server)",
            22,
            (220, 220, 220),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        s.TextSprite(
            "Смотри консоль: когда срабатывают локальные обработчики и когда приходят сообщения из сети.",
            18,
            (180, 180, 180),
            (20, 55),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def on_ping(self, **payload):
        self.local_ping_count += 1
        print(f"  [local] on_ping вызван (раз локально: {self.local_ping_count})")

    def on_emoji(self, **payload):
        self.local_emoji_count += 1
        sym = payload.get("symbol", "?")
        print(f"  [local] on_emoji вызван symbol={sym} (раз локально: {self.local_emoji_count})")

    def update(self, dt: float) -> None:
        # s.events.send(..., route=..., net=...) — варианты route: "local" (только подписчики), "all" (локально+сеть),
        # "server"/"clients"/"net" (только в сеть, без локального вызова). Подробно: event_bus.EventBus.send в докстринге.
        # E — emoji всем (route="all"): локально on_emoji + в сеть.
        if s.input.was_pressed(pygame.K_e):
            s.events.send("emoji", route="all", net=self.ctx, symbol="👍")
            print("[send] emoji route=all (локально + сеть)")

        # P — ping только в сеть (route="server"): локальные подписчики не вызываются.
        if s.input.was_pressed(pygame.K_p):
            s.events.send("ping", route="server", net=self.ctx)
            print("[send] ping route=server (только в сеть, локально не вызываем)")

        # Проброс: send(ev, **data) без route/net — по умолчанию "local", только локальные обработчики (см. event_bus.send).
        for msg in self.ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.run(
        scene=lambda: RoutingScene(net, role),
        size=(800, 600),
        title="Lesson 10 - Routing",
        fill_color=(18, 18, 24),
    )


if __name__ == "__main__":
    s.networking.run(entry="multiplayer_main")
