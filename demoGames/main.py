import sys
from pathlib import Path

# Корень репозитория — чтобы находился пакет spritePro при запуске из demoGames/
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import spritePro as s

import config
from scenes.main_scene import MainScene


def main():
    s.get_screen(config.WINDOW_SIZE, "My SpritePro Game")
    s.enable_debug(True)
    s.set_debug_hud_enabled(show_camera=False)
    s.set_debug_camera_input(3)
    s.debug_log_info("Game started")
    s.set_scene(MainScene())

    while True:
        s.update(config.FPS, fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()
