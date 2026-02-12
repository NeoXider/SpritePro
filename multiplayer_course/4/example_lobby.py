"""Пример 4: простое лобби и список игроков.

Каждый клиент при входе шлёт join с именем; хост собирает имена в список
и рассылает roster; все обновляют отображаемый список игроков.
"""

import os

import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    client_index = int(os.environ.get("SPRITEPRO_NET_INDEX", "0"))
    window_tag = "HOST" if role == "host" else f"CLIENT {client_index + 1}"
    s.get_screen((800, 600), f"Lesson 4 - Lobby [{window_tag}]")
    ctx = s.multiplayer.init_context(net, role)

    # Отображаемое имя этого участника (не «получение сервера»).
    # «Это наш компьютер» = этот процесс; кто мы — задаётся ctx.is_host и ctx.client_id.
    # Имя задаём сами, чтобы в roster были видны host, client_1, client_2.
    name = "host" if ctx.is_host else f"client_{client_index + 1}"
    players = set()
    roster = []
    joined = False

    title = s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    me_text = s.TextSprite("", 20, (170, 220, 255), (20, 58), anchor=s.Anchor.TOP_LEFT)
    roster_text = s.TextSprite("", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT)
    hint = s.TextSprite(
        "Host + 2 clients: client_2 появляется через 6 сек.",
        20,
        (180, 180, 180),
        (20, 520),
        anchor=s.Anchor.TOP_LEFT,
    )

    while True:
        s.update(fill_color=(18, 18, 24))
        me_text.set_text(f"Я: {name} | role={ctx.role} | id={ctx.client_id} | window={window_tag}")

        # Один раз при входе шлём join. Реле не отдаёт сообщение обратно отправителю,
        # поэтому добавляем себя в players локально — иначе хост не увидит себя в roster.
        if not joined:
            joined = True
            ctx.send("join", {"name": name})
            players.add(name)

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "join":
                player_name = data.get("name")
                if not player_name:
                    continue
                players.add(player_name)
                if ctx.is_host:
                    roster = sorted(players)
                    ctx.send("roster", {"players": roster})
            elif event == "roster":
                # Все клиенты (и хост при получении своего же roster) обновляют список.
                roster = list(data.get("players", []))

        roster_text.set_text("Players:\n" + "\n".join(roster))


if __name__ == "__main__":
    # clients=3 => host + client_1 через 3 сек + client_2 через 6 сек.
    s.networking.run(clients=3, client_spawn_delay=3, net_debug=True)
