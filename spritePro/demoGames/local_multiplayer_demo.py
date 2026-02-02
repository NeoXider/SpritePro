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

import pygame

import spritePro as s  # noqa: E402


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "SpritePro Multiplayer Demo")

    me = s.Sprite("", (50, 50), (200, 300))
    other = s.Sprite("", (50, 50), (600, 300))

    if color == "blue":
        me.set_color((70, 120, 220))
        other.set_color((220, 70, 70))
    else:
        me.set_color((220, 70, 70))
        other.set_color((70, 120, 220))

    other_pos = other.get_world_position()
    remote_pos = [other_pos.x, other_pos.y]
    speed = 240.0

    while True:
        s.update(fill_color=(20, 20, 25))
        dt = getattr(s, "dt", 0.016)

        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        net.send("pos", {"x": pos.x, "y": pos.y})
        for msg in net.poll():
            if msg.get("event") == "pos":
                data = msg.get("data", {})
                remote_pos[0] = float(data.get("x", remote_pos[0]))
                remote_pos[1] = float(data.get("y", remote_pos[1]))
        other.set_position((remote_pos[0], remote_pos[1]))


if __name__ == "__main__":
    s.networking.run()
