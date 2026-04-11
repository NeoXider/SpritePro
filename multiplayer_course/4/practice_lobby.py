"""Практика 4: лобби и roster по id (ctx.client_id / data["sender_id"]).

Что нужно сделать:
- В обработчике join: добавьте id игрока в player_ids; если вы host — постройте roster и отправьте.
- В обработчике roster: обновите список из data.
"""

import spritePro as s


def _display_name(pid: int) -> str:
    return "Host" if pid == 0 else f"Player {pid}"


def multiplayer_main() -> None:
    s.get_screen((800, 600), f"Lesson 4 - Practice [{s.multiplayer_ctx.role}]")
    ctx = s.multiplayer_ctx

    player_ids: set[int] = set()
    roster: list[int] = []
    joined = False

    me_text = s.TextSprite("", 20, (170, 220, 255), (20, 58), anchor=s.Anchor.TOP_LEFT)
    roster_text = s.TextSprite("", 24, (240, 240, 240), (20, 80), anchor=s.Anchor.TOP_LEFT)
    s.TextSprite("Lobby", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    s.TextSprite(
        "Host + 2 clients: второй клиент через 6 сек.",
        20,
        (180, 180, 180),
        (20, 520),
        anchor=s.Anchor.TOP_LEFT,
    )

    while True:
        s.update(fill_color=(18, 18, 24))
        me_text.set_text(f"id={ctx.client_id} | role={ctx.role}")

        if ctx.id_assigned and not joined:
            joined = True
            ctx.send("join")
            player_ids.add(ctx.client_id)

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "join":
                # TODO: добавьте id игрока (data["sender_id"]) в player_ids; если host — roster = sorted(player_ids), ctx.send("roster", {"players": roster}).
                pass
            elif event == "roster":
                # TODO: roster = list(data.get("players", [])).
                pass

        roster_text.set_text("Players:\n" + "\n".join(_display_name(pid) for pid in roster))


if __name__ == "__main__":
    # clients=3 => host + client_1 через 3 сек + client_2 через 6 сек.
    s.run(
        multiplayer=True,
        multiplayer_entry=multiplayer_main,
        multiplayer_clients=3,
        multiplayer_client_spawn_delay=3,
        multiplayer_net_debug=True,
    )
