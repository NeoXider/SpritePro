"""
Демо системы плагинов: подключает fps_logger и пример логирования, запускает цикл.

Проверка: в debug-логе (внизу окна и в консоли) — [fps_logger] FPS: ... раз в 2 сек.
Запуск: python -m spritePro.demoGames.plugin_demo  или  python spritePro/demoGames/plugin_demo.py
"""
import sys
from pathlib import Path

# При запуске по пути подхватываем пакет из репо (чтобы находился plugin_fps_logger)
_repo_root = Path(__file__).resolve().parent.parent.parent
if _repo_root not in sys.path:
    sys.path.insert(0, str(_repo_root))

import spritePro as s

# Подключаем плагины до get_screen (хуки game_init/game_update должны быть зарегистрированы до цикла)
try:
    import spritePro.plugin_fps_logger  # noqa: F401
except ModuleNotFoundError:
    pass
try:
    import examples.plugin_log_events  # noqa: F401
except ImportError:
    pass


class DemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.label = s.TextSprite(
            "Plugin demo: fps_logger + log_events. Close window to exit.",
            20, (200, 200, 200), (400, 300), anchor=s.Anchor.CENTER, scene=self,
        )
        self.sprite = s.Sprite("", (50, 50), (200, 250), scene=self)
        self.sprite.set_color((100, 150, 255))


def main():
    s.get_screen((800, 600), "Plugin demo")
    s.enable_debug(True)
    s.set_scene(DemoScene())
    while not s.quit_requested():
        s.update(fill_color=(30, 30, 40))


if __name__ == "__main__":
    main()
