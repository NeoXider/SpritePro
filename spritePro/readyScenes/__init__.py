"""Готовые сцены для быстрого подключения в играх.

Подключение чата в своей игре:
    from spritePro.readyScenes import ChatScene, ChatStyle
    s.multiplayer.init_context(net, role)
    s.get_screen((500, 600), "Игра")
    s.scene.add_scene("chat", ChatScene)
    s.scene.set_scene_by_name("chat", recreate=True)
    while True:
        s.update(fill_color=ChatStyle.color_bg)
"""

from .chat import ChatScene, ChatStyle

__all__ = ["ChatScene", "ChatStyle"]
