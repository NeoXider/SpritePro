"""Пример запуска мультиплеерного чата (сцена из spritePro.readyScenes).

Запуск из корня репозитория (SpritePro/):
  python multiplayer_course/Chat/example_chat.py
  python multiplayer_course/Chat/example_chat.py --quick
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import spritePro as s
from spritePro.readyScenes import ChatScene, ChatStyle


def multiplayer_main() -> None:
    def setup() -> None:
        s.scene.add_scene("chat", ChatScene)
        s.scene.set_scene_by_name("chat", recreate=True)

    s.run(
        setup=setup,
        size=(500, 600),
        title="Chat | Multiplayer",
        fill_color=ChatStyle.color_bg,
    )


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main, multiplayer_clients=3)
