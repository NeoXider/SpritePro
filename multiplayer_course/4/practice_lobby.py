"""Практика 4: лобби и roster с TODO.

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал.
"""

import os

import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    client_index = int(os.environ.get("SPRITEPRO_NET_INDEX", "0"))
    window_tag = "HOST" if role == "host" else f"CLIENT {client_index + 1}"
    s.get_screen((800, 600), f"Lesson 4 - Practice [{window_tag}]")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role)

    # Отображаемое имя этого процесса (задаём сами по ctx.is_host и client_index).
    name = "host" if ctx.is_host else f"client_{client_index + 1}"
    players = set()
    roster = []
    joined = False

    # UI‑текст списка.
    me_text = s.TextSprite("", 20, (170, 220, 255), (20, 58), anchor=s.Anchor.TOP_LEFT)
    roster_text = s.TextSprite("", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT)
    s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    s.TextSprite(
        "Host + 2 clients: client_2 появляется через 6 сек.",
        20,
        (180, 180, 180),
        (20, 520),
        anchor=s.Anchor.TOP_LEFT,
    )

    while True:
        # Тик обновления.
        s.update(fill_color=(18, 18, 24))
        me_text.set_text(
            f"Я: {name} | role={ctx.role} | id={ctx.client_id} | window={window_tag}"
        )

        # Отправляем join один раз. Реле не отдаёт сообщение обратно отправителю,
        # поэтому добавляем себя в players локально (иначе хост не в roster).
        if not joined:
            joined = True
            ctx.send("join", {"name": name})
            players.add(name)

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
    # clients=3 => host + client_1 через 3 сек + client_2 через 6 сек.
    s.networking.run(clients=3, client_spawn_delay=3, net_debug=True)
