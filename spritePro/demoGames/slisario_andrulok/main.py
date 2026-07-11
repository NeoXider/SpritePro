"""Слизарио — клон Slither.io на SpritePro (автор: andrulok).

Запуск из корня репозитория или из папки демо:

  # Одиночная игра
  python spritePro/demoGames/slisario_andrulok/main.py --single

  # Локальный мультиплеер (хост + клиент, два окна)
  python spritePro/demoGames/slisario_andrulok/main.py --quick

  # Сервер + хост в одном окне
  python spritePro/demoGames/slisario_andrulok/main.py --host_mode

  # Только клиент (сначала поднимите сервер или --host_mode)
  python spritePro/demoGames/slisario_andrulok/main.py --host 127.0.0.1 --port 5050

Как устроена сеть — см. ARCHITECTURE.md рядом с этим файлом.
"""

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))
# Запуск из git-репозитория без установленного пакета spritepro.
REPO_ROOT = DEMO_DIR.parent.parent.parent
if (REPO_ROOT / "spritePro" / "__init__.py").exists():
    sys.path.insert(1, str(REPO_ROOT))

import spritePro as s
from game.config import WINDOW_SIZE, FPS, TITLE, FILL_COLOR
from scenes.game_scene import GameScene


def main() -> None:
    single = "--single" in sys.argv
    # В мультиплеере s.run сам передаёт (net, role) в конструктор GameScene.
    s.run(
        scene=GameScene,
        size=WINDOW_SIZE,
        fps=FPS,
        title=TITLE,
        fill_color=FILL_COLOR,
        multiplayer=not single,
        multiplayer_use_lobby=False,
    )


if __name__ == "__main__":
    main()
