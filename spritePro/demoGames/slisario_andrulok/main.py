"""Слизарио — клон Slither.io на SpritePro (автор: andrulok).

Запуск из корня репозитория или из папки демо:

  # Одиночная игра
  python spritePro/demoGames/slisario_andrulok/main.py --single

  # Локальный мультиплеер (сервер + два клиента)
  python spritePro/demoGames/slisario_andrulok/main.py --quick

  # Сервер + хост в одном окне
  python spritePro/demoGames/slisario_andrulok/main.py --host_mode

  # Только клиент (сначала поднимите сервер или --host_mode)
  python spritePro/demoGames/slisario_andrulok/main.py --host 127.0.0.1 --port 5050
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spritePro as s
from game.config import WINDOW_SIZE, FPS, TITLE, FILL_COLOR
from scenes.game_scene import GameScene


def main() -> None:
    s.run(
        scene=GameScene,
        size=WINDOW_SIZE,
        fps=FPS,
        title=TITLE,
        fill_color=FILL_COLOR,
    )


if __name__ == "__main__":
    if "--single" in sys.argv:
        main()
    else:
        s.run(
            multiplayer=True,
            multiplayer_entry=main,
            multiplayer_use_lobby=False,
        )
