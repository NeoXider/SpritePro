"""Демо мультиплеера на NetServer/NetClient.

Запуск:
1) Сервер:
   python spritePro/demoGames/local_multiplayer_demo.py --server --host 0.0.0.0 --port 5050
   (или хост-режим: сервер + клиент в одном окне)
   python spritePro/demoGames/local_multiplayer_demo.py --host_mode --host 0.0.0.0 --port 5050 --color red
   (или быстрый запуск: хост + второй клиент)
   python spritePro/demoGames/local_multiplayer_demo.py --quick --host 127.0.0.1 --port 5050
2) Клиенты (на каждом ПК):
   python spritePro/demoGames/local_multiplayer_demo.py --host IP_СЕРВЕРА --port 5050 --color red
   python spritePro/demoGames/local_multiplayer_demo.py --host IP_СЕРВЕРА --port 5050 --color blue

Управление: WASD

Примечание:
- Запускайте сервер один раз.
- Клиентов можно запускать на разных ПК (укажите IP сервера).

Из кода:
    import spritePro as s
    s.networking.run()
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame  # noqa: E402

import spritePro as s  # noqa: E402


def main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 600), "SpritePro Multiplayer Demo")

    # Контекст мультиплеера: хранит id/role и упрощает send/poll.
    _ = s.multiplayer.init_context(net, role)
    ctx = s.multiplayer_ctx

    me = s.Sprite("", (50, 50), (200, 300))
    other = s.Sprite("", (50, 50), (600, 300))

    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    other_pos = other.get_world_position()
    remote_pos = [other_pos.x, other_pos.y]
    speed = 240.0
    tick_rate = 60
    other_id: int | None = None

    me_id_text = s.TextSprite("ID: ?", 18, (255, 255, 255), (0, 0))
    other_id_text = s.TextSprite("ID: ?", 18, (255, 255, 255), (0, 0))

    while True:
        s.update(fps=tick_rate, fill_color=(20, 20, 25))
        dt = s.dt

        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # Отправляем позицию списком — list(Vector2) даёт [x, y].
        ctx.send_every("pos", {"pos": list(pos)}, 1.0 / tick_rate)
        for msg in ctx.poll():
            if msg.get("event") == "pos":
                data = msg.get("data", {})
                remote_pos[:] = data.get("pos", [0, 0])
                other_id = data.get("sender_id")
        other.set_position(remote_pos)

        me_id_text.set_text(f"ID: {ctx.client_id}")
        me_pos = me.get_world_position()
        me_id_text.set_position((me_pos.x, me_pos.y - 40))

        other_id_label = "?" if other_id is None else str(other_id)
        other_id_text.set_text(f"ID: {other_id_label}")
        other_pos = other.get_world_position()
        other_id_text.set_position((other_pos.x, other_pos.y - 40))


if __name__ == "__main__":
    s.networking.run()
