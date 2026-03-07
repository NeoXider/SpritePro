"""Демо мультиплеера на NetServer/NetClient.

Запуск:
1) Сервер:
   python spritePro/demoGames/local_multiplayer_demo.py --server --host 0.0.0.0 --port 5050
   (или хост-режим: сервер + клиент в одном окне)
   python spritePro/demoGames/local_multiplayer_demo.py --host_mode --host 0.0.0.0 --port 5050
   (или быстрый запуск: хост + второй клиент)
   python spritePro/demoGames/local_multiplayer_demo.py --quick --host 127.0.0.1 --port 5050
2) Клиенты (на каждом ПК):
   python spritePro/demoGames/local_multiplayer_demo.py --host IP_СЕРВЕРА --port 5050
3) Лобби (одно окно, выбор хоста/клиента, ввод IP и порта):
   python spritePro/demoGames/local_multiplayer_demo.py --lobby

Управление: WASD

Примечание:
- Запускайте сервер один раз.
- Клиентов можно запускать на разных ПК (укажите IP сервера).

Из кода:
    import sys
    import spritePro as s

    s.run(multiplayer=True, multiplayer_entry=main)
    s.run(
        multiplayer=True,
        multiplayer_entry=main,
        multiplayer_use_lobby=True,
        multiplayer_argv=[arg for arg in sys.argv[1:] if arg != "--lobby"],
    )
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame  # noqa: E402

import spritePro as s  # noqa: E402


class LocalMultiplayerScene(s.Scene):
    def __init__(self, net: s.NetClient, role: str) -> None:
        super().__init__()
        s.multiplayer.init_context(net, role)
        self.ctx = s.multiplayer_ctx
        self.speed = 240.0
        self.tick_rate = 60
        self.other_id: int | None = None

        self.me = s.Sprite("", (50, 50), (200, 300), scene=self)
        self.me.DoScale(1.5, 1).SetLoops(-1).SetYoyo(True)
        self.other = s.Sprite("", (50, 50), (600, 300), scene=self)

        my_color = (220, 70, 70) if self.ctx.is_host else (70, 120, 220)
        other_color = (70, 120, 220) if self.ctx.is_host else (220, 70, 70)
        self.me.set_color(my_color)
        self.other.set_color(other_color)

        other_pos = self.other.get_world_position()
        self.remote_pos = [other_pos.x, other_pos.y]

        self.me_label = s.TextSprite("?", 18, (255, 255, 255), (0, 0), scene=self)
        self.other_label = s.TextSprite("?", 18, (255, 255, 255), (0, 0), scene=self)

    def update(self, dt: float) -> None:
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * self.speed * dt
        pos.y += dy * self.speed * dt
        self.me.set_position(pos)

        self.ctx.send_every("pos", {"pos": list(pos)}, 1.0 / self.tick_rate)
        for msg in self.ctx.poll():
            if msg.get("event") == "pos":
                data = msg.get("data", {})
                self.remote_pos[:] = data.get("pos", [0, 0])
                self.other_id = data.get("sender_id")
        self.other.set_position(self.remote_pos)

        self.me_label.set_text(f"{self.ctx.role} (ID: {self.ctx.client_id})")
        me_pos = self.me.get_world_position()
        self.me_label.set_position((me_pos.x, me_pos.y - 40))

        other_label_str = (
            f"other (ID: {self.other_id})" if self.other_id is not None else "other (ID: ?)"
        )
        self.other_label.set_text(other_label_str)
        other_pos = self.other.get_world_position()
        self.other_label.set_position((other_pos.x, other_pos.y - 40))


def main(net: s.NetClient, role: str) -> None:
    s.run(
        scene=lambda: LocalMultiplayerScene(net, role),
        size=(800, 600),
        title="SpritePro Multiplayer Demo",
        fps=60,
        fill_color=(20, 20, 25),
    )


if __name__ == "__main__":
    lobby_enabled = "--lobby" in sys.argv
    filtered_argv = [arg for arg in sys.argv[1:] if arg != "--lobby"]
    s.run(
        multiplayer=True,
        multiplayer_entry=main,
        multiplayer_argv=filtered_argv,
        multiplayer_use_lobby=lobby_enabled,
    )
