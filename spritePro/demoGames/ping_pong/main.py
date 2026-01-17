import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import spritePro as s
from scene import PingPongScene


def main():
    s.get_screen((900, 600), "Ping Pong")
    s.enable_debug(True)
    s.set_scene(PingPongScene())

    while True:
        s.update(fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()
