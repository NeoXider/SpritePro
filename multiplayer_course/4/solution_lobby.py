"""Решение 4: лобби и список игроков."""

import spritePro as s


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    # Окно лобби.
    s.get_screen((800, 600), "Lesson 4 - Solution")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role, color)

    # Данные игрока и список.
    name = ctx.role
    players = set()
    roster = []
    joined = False

    # UI‑текст списка.
    roster_text = s.TextSprite(
        "", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT
    )
    s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)

    while True:
        # Основной тик.
        s.update(fill_color=(18, 18, 24))

        # Отправка join один раз.
        if not joined:
            joined = True
            ctx.send("join", {"name": name})

        # Читаем сообщения и обновляем roster.
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "join":
                player_name = data.get("name")
                if player_name:
                    players.add(player_name)
                    if ctx.is_host:
                        roster = sorted(players)
                        ctx.send("roster", {"players": roster})
            elif event == "roster":
                roster = list(data.get("players", []))

        # Показ списка игроков.
        roster_text.set_text("Players:\n" + "\n".join(roster))


if __name__ == "__main__":
    # Запуск решения.
    s.networking.run()
