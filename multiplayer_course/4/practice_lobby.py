"""Практика 4: лобби и roster с TODO.

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал.
"""

import spritePro as s


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    # Окно лобби.
    s.get_screen((800, 600), "Lesson 4 - Practice")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role, color)

    # Локальные данные игрока.
    name = "host" if ctx.is_host else "client"
    players = set()
    roster = []
    joined = False

    # UI‑текст списка.
    roster_text = s.TextSprite(
        "", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT
    )
    s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)

    while True:
        # Тик обновления.
        s.update(fill_color=(18, 18, 24))

        # Отправляем join один раз.
        if not joined:
            joined = True
            ctx.send("join", {"name": name})

        # Читаем сообщения.
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "join":
                # TODO: добавьте игрока в players и, если вы host, отправьте roster.
                pass
            elif event == "roster":
                # TODO: обновите roster из data.
                pass

        # Рендер списка игроков.
        roster_text.set_text("Players:\n" + "\n".join(roster))


if __name__ == "__main__":
    # Запуск практики.
    s.networking.run()
