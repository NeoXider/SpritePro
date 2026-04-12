import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame
import spritePro as s

class NetDecoratorsDemo(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.speed = 240.0
        self.other_ids = set()

        self.me = s.Sprite("", (50, 50), (400, 300), scene=self)
        my_color = (220, 70, 70) if self.ctx.is_host else (70, 120, 220)
        self.me.set_color(my_color)
        
        self.bullets = []
        self.others = {}

        self.me_label = s.TextSprite(f"{self.ctx.role} (ID: {self.ctx.client_id})", 18, (255, 255, 255), (0, 0), scene=self)

        # Вызываем rpc регистрацию себя (для упрощения)
        # Ученикам: "Каждую секунду говорим серверу обновить нашу позицию"
        # Будем использовать NetEvent для позиций
        
    def update(self, dt: float) -> None:
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        
        # Движение
        pos = self.me.get_world_position()
        pos.x += dx * self.speed * dt
        pos.y += dy * self.speed * dt
        self.me.set_position(pos)
        
        # Обновляем текст
        self.me_label.set_position((pos.x, pos.y - 40))

        # Стрельба (Просим Хост заспавнить пулю)
        if s.input.was_pressed(pygame.K_SPACE):
            spawn_bullet_cmd(pos=(pos.x, pos.y), dir_x=0, dir_y=-1)

        # Синхронизация позиции через NetEvent и send_every
        self.ctx.send_every("sync_pos", {"pos": (pos.x, pos.y)}, interval=1/60.0)
        
        # Если мы хост, можно вывести всех игроков лобби
        if self.ctx.is_host:
            # players это dict: {client_id: {"name": "..."}}
            players_str = str(self.ctx.players)
            s.debug_log_info(f"Lobby players: {players_str}")

# --- Сетевые декораторы ---

@s.NetEvent("sync_pos")
def on_sync_pos(sender_id, pos):
    """Событие: Игрок двигается."""
    scene = s.get_current_scene()
    if not isinstance(scene, NetDecoratorsDemo): return
    if sender_id == scene.ctx.client_id: return
    
    if sender_id not in scene.others:
        sp = s.Sprite("", (50, 50), pos, scene=scene)
        sp.set_color((70, 120, 220) if not scene.ctx.is_host else (220, 70, 70))
        scene.others[sender_id] = sp
    scene.others[sender_id].set_position(pos)

@s.Command
def spawn_bullet_cmd(pos, dir_x, dir_y, sender_id=0):
    """
    Отправляется с Клиента. Выполняется ТОЛЬКО на Хосте.
    Хост решает заспавнить пулю и говорит всем Клиентам об этом.
    """
    print(f"[Host] Игрок {sender_id} выстрелил из {pos}!")
    # Сразу просим всех отрендерить пулю
    spawn_bullet_rpc(pos=pos, dir_x=dir_x, dir_y=dir_y, owner=sender_id)

@s.ClientRpc
def spawn_bullet_rpc(pos, dir_x, dir_y, owner):
    """
    Выполняется на Всех клиентах.
    """
    scene = s.get_current_scene()
    if not isinstance(scene, NetDecoratorsDemo): return
    
    bullet = s.Sprite("", (15, 15), pos, scene=scene)
    bullet.set_color((255, 255, 0))
    # Простая имитация полета через Tween
    bullet.DoMoveBy((dir_x * 800, dir_y * 800), 2.0).OnComplete(bullet.kill)


def main() -> None:
    s.run(
        scene=NetDecoratorsDemo,
        size=(800, 600),
        title="SpritePro Magic Decorators",
        fps=60,
        fill_color=(20, 20, 25),
    )

if __name__ == "__main__":
    if "--host_mode" not in sys.argv and "--server" not in sys.argv and "--client" not in sys.argv:
        # Для удобства тестирования сразу запускаем быструю сессию (хост + клиент в двух окнах)
        # Если пользователь запускает без аргументов, запустим меню как в local_multiplayer_demo
        s.run(
            multiplayer=True,
            multiplayer_entry=main,
            multiplayer_use_lobby=True,
        )
    else:
        s.run(
            multiplayer=True,
            multiplayer_entry=main,
            multiplayer_use_lobby=False, # We usually let SpritePro run lobby automatically via CLI arg, but here we explicitly use args
            multiplayer_argv=sys.argv[1:]
        )
