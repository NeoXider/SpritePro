"""Практика 10: роутинг и лучшие практики.

Что нужно сделать:
- Задание 1: добавьте отправку ping (route=\"server\") раз в 2 сек и emoji (route=\"all\") по клавише.
  В комментарии напишите, зачем разный маршрут.
- Задание 2: в комментарии или docstring ответьте, почему в игре со счётом хост рассылает score_update, а не клиент всем.
- Задание 3: в комментарии ответьте, кто должен рассылать roster в лобби (урок 4) и почему.
"""

import spritePro as s


class RoutingPracticeScene(s.Scene):
    def __init__(self, net: s.NetClient, role: str) -> None:
        super().__init__()
        self.ctx = s.multiplayer.init_context(net, role)

        # TODO 1: добавьте таймер ping_interval (2 сек) и по истечении — s.events.send("ping", route="server", net=ctx).
        # TODO 1: по нажатию клавиши (например E) — s.events.send("emoji", route="all", net=ctx, symbol="👋").
        # Комментарий: ping шлём только на сервер, чтобы не засорять всех (сервер может только учитывать); emoji — всем, чтобы все видели.

        self.ping_timer = 0.0
        self.PING_INTERVAL = 2.0

        s.TextSprite(
            "TODO: ping каждые 2 сек (server), E = emoji (all)",
            22,
            (240, 240, 240),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def update(self, dt: float) -> None:
        self.ping_timer += dt

        # TODO 1: if ping_timer >= PING_INTERVAL: отправить ping, сбросить ping_timer.
        # TODO 1: if s.input.was_pressed(pygame.K_e): отправить emoji.

        for msg in self.ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.run(
        scene=lambda: RoutingPracticeScene(net, role),
        size=(800, 600),
        title="Lesson 10 - Practice Routing",
        fill_color=(18, 18, 24),
    )


# Задание 2 (ответ в комментарии здесь или в lesson.md):
# Почему хост рассылает score_update, а не клиент всем?
# Ответ: ...

# Задание 3 (ответ в комментарии):
# Кто должен рассылать roster в лобби и почему?
# Ответ: ...


if __name__ == "__main__":
    s.networking.run(entry="multiplayer_main")
