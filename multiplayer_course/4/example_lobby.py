"""Пример 4: простое лобби и список игроков.

Каждый клиент при входе шлёт join с именем; хост собирает имена в список
и рассылает roster; все обновляют отображаемый список игроков.
"""

import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 600), "Lesson 4 - Lobby")
    ctx = s.multiplayer.init_context(net, role)

    # Имя по роли; players — множество имён (у хоста), roster — итоговый список для отображения.
    name = "host" if ctx.is_host else "client"
    players = set()
    roster = []
    joined = False

    title = s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    roster_text = s.TextSprite("", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT)
    hint = s.TextSprite(
        "Ожидание игроков...", 20, (180, 180, 180), (20, 520), anchor=s.Anchor.TOP_LEFT
    )

    while True:
        s.update(fill_color=(18, 18, 24))

        # Один раз при входе шлём join, чтобы все (и хост) знали о нас.
        if not joined:
            joined = True
            ctx.send("join", {"name": name})

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "join":
                # Хост добавляет имя и рассылает обновлённый roster.
                player_name = data.get("name")
                if player_name:
                    players.add(player_name)
                    if ctx.is_host:
                        roster = sorted(players)
                        ctx.send("roster", {"players": roster})
            elif event == "roster":
                # Все клиенты (и хост при получении своего же roster) обновляют список.
                roster = list(data.get("players", []))

        roster_text.set_text("Players:\n" + "\n".join(roster))


if __name__ == "__main__":
    # Запуск примера.
    s.networking.run()
