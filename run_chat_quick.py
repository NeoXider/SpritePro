"""Запуск мультиплеерного чата (хост + 2 клиента, 3 окна).

Из корня репозитория:
  python run_chat_quick.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import spritePro as s
from spritePro.readyScenes import ChatScene, ChatStyle


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.multiplayer.init_context(net, role)
    s.get_screen((500, 600), "Chat | Multiplayer")
    s.scene.add_scene("chat", ChatScene)
    s.scene.set_scene_by_name("chat", recreate=True)
    while True:
        s.update(fill_color=ChatStyle.color_bg)


if __name__ == "__main__":
    s.networking.run(clients=3)
