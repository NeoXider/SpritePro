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

Kivy/mobile:
   python spritePro/demoGames/three_clients_move_demo.py
   python spritePro/demoGames/three_clients_move_demo.py --pygame
   python -m spritePro.demoGames.three_clients_move_demo --kivy
   python -m spritePro.demoGames.three_clients_move_demo --kivy --host 192.168.1.10 --port 5050

При прямом запуске demo использует единый `s.run(..., multiplayer=True)`:
- по умолчанию стартует quick-режим на 3 окна (host + 2 клиента)
- `--pygame` / `--kivy` переключают runtime
- `--server`, `--host_mode`, `--quick`, `--host`, `--port`, `--clients`
  продолжают работать как terminal-аргументы multiplayer runner
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


class ThreeClientsMoveScene(s.Scene):
    def __init__(self, net: s.NetClient, role: str) -> None:
        super().__init__()
        s.multiplayer.init_context(net, role)
        self.ctx = s.multiplayer_ctx
        self.hint = s.TextSprite(
            "WASD — move | IDs above players", 20, (200, 200, 200), (450, 30), scene=self
        )
        self.wait_id = s.TextSprite("Waiting for ID...", 18, (200, 200, 200), (450, 60), scene=self)
        self.window_id = s.TextSprite(
            "Window ID: ?",
            18,
            (200, 200, 200),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

        self.me = s.Sprite("", (50, 50), (200, 300), scene=self)
        self.me_id = s.TextSprite("ID: ?", 18, (255, 255, 255), (200, 250), scene=self)
        self.others: dict[int, s.Sprite] = {}
        self.others_id: dict[int, s.TextSprite] = {}
        self.last_id: int | None = None
        self.base_positions = {
            0: (200, 300),
            1: (450, 300),
            2: (700, 300),
            3: (450, 450),
        }
        self.speed = 260.0
        self.tick_rate = 60

    def update(self, dt: float) -> None:
        if self.ctx.client_id != self.last_id:
            self.last_id = self.ctx.client_id
            my_color = _color_for_id(self.ctx.client_id)
            self.me.set_color(my_color)
            self.me_id.color = my_color
            self.window_id.color = my_color
            me_pos = self.base_positions.get(self.ctx.client_id)
            if me_pos is not None:
                self.me.set_position(me_pos)

        self.wait_id.set_active(not self.ctx.id_assigned)
        if self.ctx.id_assigned:
            dx = s.input.get_axis(pygame.K_a, pygame.K_d)
            dy = s.input.get_axis(pygame.K_w, pygame.K_s)
            pos = self.me.get_world_position()
            pos.x += dx * self.speed * dt
            pos.y += dy * self.speed * dt
            self.me.set_position(pos)

            self.ctx.send_every(
                "pos",
                {"pos": list(pos), "sender_id": self.ctx.client_id},
                1.0 / self.tick_rate,
            )

        for msg in self.ctx.poll():
            if msg.get("event") != "pos":
                continue
            data = msg.get("data", {})
            sender_id = data.get("sender_id")
            if sender_id is None:
                continue
            if sender_id == self.ctx.client_id:
                continue
            if sender_id not in self.others:
                other = s.Sprite("", (50, 50), (450, 300), scene=self)
                other.set_color(_color_for_id(sender_id))
                self.others[sender_id] = other
                label = s.TextSprite(
                    f"ID: {sender_id}",
                    18,
                    _color_for_id(sender_id),
                    (0, 0),
                    scene=self,
                )
                self.others_id[sender_id] = label
            self.others[sender_id].set_position(data.get("pos", [0, 0]))

        current_pos = self.me.get_world_position()
        self.me_id.set_text(f"ID: {self.ctx.client_id}")
        self.me_id.set_position((current_pos.x, current_pos.y - 40))
        self.window_id.set_text(f"Window ID: {self.ctx.client_id}")

        for sender_id, sprite in self.others.items():
            label = self.others_id[sender_id]
            spr_pos = sprite.get_world_position()
            label.set_position((spr_pos.x, spr_pos.y - 40))


def main(default_platform: str = "kivy") -> None:
    s.run(
        scene=ThreeClientsMoveScene,
        size=(900, 600),
        title="Three Clients Move Demo",
        fps=60,
        fill_color=(20, 20, 30),
        platform=default_platform,
        multiplayer=True,
        multiplayer_argv=sys.argv[1:],
        multiplayer_clients=3,
        multiplayer_client_spawn_delay=2,
    )


if __name__ == "__main__":
    main(default_platform="kivy")
