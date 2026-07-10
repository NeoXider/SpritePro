"""Урок 11. Сетевые декораторы: @NetEvent, @Command, @ClientRpc.

Управление: WASD — движение, E — попросить хоста полечить (Command → ClientRpc).
Запуск: python multiplayer_course/11/example_decorators.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pygame
import spritePro as s

MAX_HP = 100
HEAL_AMOUNT = 25


class DecoratorsDemo(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.speed = 240.0
        self.hp = 60  # стартуем побитыми, чтобы было что лечить

        self.me = s.Sprite("", (50, 50), (400, 300), scene=self)
        self.me.set_color((220, 70, 70) if self.ctx.is_host else (70, 120, 220))
        self.others: dict[int, s.Sprite] = {}

        self.hp_label = s.TextSprite(
            f"HP: {self.hp} | E — лечение | ping: --",
            18,
            (230, 230, 230),
            (10, 10),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )

    def update(self, dt: float) -> None:
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * self.speed * dt
        pos.y += dy * self.speed * dt
        self.me.set_position(pos)

        self.ctx.send_every("sync_pos", {"pos": (pos.x, pos.y)}, interval=0.05)

        if s.input.was_pressed(pygame.K_e):
            request_heal_cmd()

        self.hp_label.set_text(
            f"HP: {self.hp} | E — лечение | ping: {self.ctx.ping_ms:.0f} ms"
        )


@s.NetEvent("sync_pos")
def on_sync_pos(sender_id, pos):
    """Позиция чужого игрока: создаём спрайт при первом пакете."""
    scene = s.get_current_scene()
    if not isinstance(scene, DecoratorsDemo):
        return
    if sender_id == scene.ctx.client_id:
        return
    if sender_id not in scene.others:
        sprite = s.Sprite("", (50, 50), pos, scene=scene)
        sprite.set_color((150, 150, 150))
        scene.others[sender_id] = sprite
    scene.others[sender_id].set_position(pos)


@s.Command
def request_heal_cmd(sender_id=0):
    """Клиент ПРОСИТ лечение. Выполняется только на хосте — он решает."""
    print(f"[Host] Игрок {sender_id} просит лечение — одобрено")
    heal_rpc(target_id=sender_id, amount=HEAL_AMOUNT)


@s.ClientRpc
def heal_rpc(target_id, amount):
    """Хост скомандовал: у всех проигрываем лечение цели."""
    scene = s.get_current_scene()
    if not isinstance(scene, DecoratorsDemo):
        return
    if target_id == scene.ctx.client_id:
        scene.hp = min(MAX_HP, scene.hp + amount)
        scene.me.DoColor((120, 255, 120), 0.3)
    elif target_id in scene.others:
        scene.others[target_id].DoColor((120, 255, 120), 0.3)


def main() -> None:
    s.run(
        scene=DecoratorsDemo,
        size=(800, 600),
        title="Lesson 11 - Net Decorators",
        fill_color=(20, 20, 25),
        multiplayer=True,
    )


if __name__ == "__main__":
    main()
