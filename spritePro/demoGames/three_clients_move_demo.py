"""Демо: перемещение 3 клиентов (host + 2) с ID и цветами.

Запуск:
1) Сервер:
   python spritePro/demoGames/three_clients_move_demo.py --server --host 0.0.0.0 --port 5050
2) Клиенты (3 окна/ПК, один из них хост):
   python spritePro/demoGames/three_clients_move_demo.py --host 127.0.0.1 --port 5050
   python spritePro/demoGames/three_clients_move_demo.py --host 127.0.0.1 --port 5050
   python spritePro/demoGames/three_clients_move_demo.py --host 127.0.0.1 --port 5050

Опционально для --quick:
   --client_spawn_delay 1  # запуск клиента с задержкой в 1 сек
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame  # noqa: E402

import spritePro as s  # noqa: E402


PALETTE = [
    (220, 70, 70),  # id 0
    (70, 120, 220),  # id 1
    (70, 220, 120),  # id 2
    (220, 180, 70),  # id 3+
]


def _color_for_id(client_id: int) -> tuple[int, int, int]:
    return PALETTE[client_id % len(PALETTE)]


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((900, 600), "Three Clients Move Demo")
    _ = s.multiplayer.init_context(net, role, color)
    ctx = s.multiplayer_ctx

    hint = s.TextSprite(
        "WASD — move | IDs above players", 20, (200, 200, 200), (450, 30)
    )
    wait_id = s.TextSprite("Waiting for ID...", 18, (200, 200, 200), (450, 60))
    window_id = s.TextSprite(
        "Window ID: ?", 18, (200, 200, 200), (20, 20), anchor=s.Anchor.TOP_LEFT
    )

    me = s.Sprite("", (50, 50), (200, 300))
    me_id = s.TextSprite("ID: ?", 18, (255, 255, 255), (200, 250))

    others: dict[int, s.Sprite] = {}
    others_id: dict[int, s.TextSprite] = {}
    last_id: int | None = None

    base_positions = {
        0: (200, 300),
        1: (450, 300),
        2: (700, 300),
        3: (450, 450),
    }

    speed = 260.0
    tick_rate = 60

    _ = (hint, window_id, wait_id)

    while True:
        s.update(fps=tick_rate, fill_color=(20, 20, 30))
        dt = s.dt

        if ctx.client_id != last_id:
            last_id = ctx.client_id
            my_color = _color_for_id(ctx.client_id)
            me.set_color(my_color)
            me_id.color = my_color
            window_id.color = my_color
            me_pos = base_positions.get(ctx.client_id)
            if me_pos is not None:
                me.set_position(me_pos)

        wait_id.set_active(not ctx.id_assigned)
        if ctx.id_assigned:
            dx = s.input.get_axis(pygame.K_a, pygame.K_d)
            dy = s.input.get_axis(pygame.K_w, pygame.K_s)
            pos = me.get_world_position()
            pos.x += dx * speed * dt
            pos.y += dy * speed * dt
            me.set_position(pos)

            ctx.send_every(
                "pos",
                {"x": pos.x, "y": pos.y, "sender_id": ctx.client_id},
                1.0 / tick_rate,
            )

        for msg in ctx.poll():
            if msg.get("event") != "pos":
                continue
            data = msg.get("data", {})
            sender_id = data.get("sender_id")
            try:
                sender_id = int(sender_id)
            except (TypeError, ValueError):
                continue
            if sender_id == ctx.client_id:
                continue
            if sender_id not in others:
                other = s.Sprite("", (50, 50), (450, 300))
                other.set_color(_color_for_id(sender_id))
                others[sender_id] = other
                label = s.TextSprite(
                    f"ID: {sender_id}",
                    18,
                    _color_for_id(sender_id),
                    (0, 0),
                )
                others_id[sender_id] = label
            other_pos = (float(data.get("x", 0)), float(data.get("y", 0)))
            others[sender_id].set_position(other_pos)

        current_pos = me.get_world_position()
        me_id.set_text(f"ID: {ctx.client_id}")
        me_id.set_position((current_pos.x, current_pos.y - 40))
        window_id.set_text(f"Window ID: {ctx.client_id}")

        for sender_id, sprite in others.items():
            label = others_id[sender_id]
            spr_pos = sprite.get_world_position()
            label.set_position((spr_pos.x, spr_pos.y - 40))


if __name__ == "__main__":
    s.networking.run(clients=3, client_spawn_delay=2)
