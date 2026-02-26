"""Точка входа для веб-сборки (генерируется spritePro.web_build)."""
import spritePro as s
from scene import PingPongScene


def setup() -> None:
    s.get_screen((900, 600), 'Ping Pong')
    s.set_scene(PingPongScene())
