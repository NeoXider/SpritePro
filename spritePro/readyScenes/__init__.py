"""Готовые сцены для быстрого подключения в играх.

Чат:
    from spritePro.readyScenes import ChatScene, ChatStyle
    s.multiplayer.init_context(net, role)
    s.get_screen((500, 600), "Игра")
    s.scene.add_scene("chat", ChatScene)
    s.scene.set_scene_by_name("chat", recreate=True)
    while True:
        s.update(fill_color=ChatStyle.color_bg)

Лобби (экран настройки + roster, затем переход в игру):
    s.networking.run(use_lobby=True)
    # или вручную:
    from spritePro.readyScenes import run_multiplayer_lobby
    s.get_screen((500, 520), "Лобби")
    run_multiplayer_lobby(lambda net, role: your_multiplayer_main(net, role))
"""

from .chat import ChatScene, ChatStyle
from .multiplayer_lobby import (
    EVENT_START_GAME,
    MultiplayerLobbyScene,
    run_multiplayer_lobby,
)

__all__ = [
    "ChatScene",
    "ChatStyle",
    "EVENT_START_GAME",
    "MultiplayerLobbyScene",
    "run_multiplayer_lobby",
]
