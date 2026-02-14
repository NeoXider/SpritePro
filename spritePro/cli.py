import argparse
import logging
import os
import sys
from pathlib import Path
from textwrap import dedent

# Add parent directory to path for tools
_spritepro_dir = Path(__file__).parent
_parent_dir = _spritepro_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))


MAIN_TEMPLATE = dedent(
    """\
    import spritePro as s

    import config
    from scenes.main_scene import MainScene


    def main():
        s.get_screen(config.WINDOW_SIZE, "My SpritePro Game")
        s.enable_debug(True)
        s.set_debug_camera_input(3)
        s.debug_log_info("Game started")
        s.set_scene(MainScene())

        while True:
            s.update(config.FPS, fill_color=(20, 20, 30))


    if __name__ == "__main__":
        main()
    """
)

MAIN_SCENE_TEMPLATE = dedent(
    """\
    import pygame
    import spritePro as s

    ASSETS_DIR = "assets"
    IMAGES_DIR = f"{ASSETS_DIR}/images"
    AUDIO_DIR = f"{ASSETS_DIR}/audio"


    class MainScene(s.Scene):
        def __init__(self):
            super().__init__()

            self.player = s.Sprite(
                f"{IMAGES_DIR}/player.png",
                (64, 64),
                (400, 300),
                speed=5,
                scene=self,
            )

        def on_enter(self, context):
            pass

        def on_exit(self):
            pass

        def update(self, dt):
            self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_SPACE):
                s.debug_log_info("Space pressed")
    """
)

CONFIG_TEMPLATE = dedent(
    """\
    WINDOW_SIZE = (800, 600)
    FPS = 60
    """
)


def _project_root_from_target(target: Path) -> tuple[Path, Path]:
    if target.suffix == ".py":
        return target.parent, target
    return target, target / "main.py"


def create_project(target: Path) -> Path:
    project_root, main_file = _project_root_from_target(target)
    config_file = project_root / "config.py"
    scenes_root = project_root / "scenes"
    scenes_init = scenes_root / "__init__.py"
    main_scene_file = scenes_root / "main_scene.py"

    project_root.mkdir(parents=True, exist_ok=True)
    assets_root = project_root / "assets"
    assets_root.mkdir(exist_ok=True)
    (assets_root / "audio").mkdir(exist_ok=True)
    (assets_root / "images").mkdir(exist_ok=True)
    scenes_root.mkdir(exist_ok=True)

    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE, encoding="utf-8")
    if not config_file.exists():
        config_file.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    if not scenes_init.exists():
        scenes_init.write_text("", encoding="utf-8")
    if not main_scene_file.exists():
        main_scene_file.write_text(MAIN_SCENE_TEMPLATE, encoding="utf-8")

    return project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="SpritePro tools")
    parser.add_argument(
        "--create",
        metavar="PATH",
        nargs="?",
        const="main.py",
        help="Create a new project: --create [path]",
    )
    parser.add_argument(
        "--editor",
        "-e",
        action="store_true",
        help="Launch the Sprite Editor",
    )
    args = parser.parse_args()

    if args.editor:
        import spritePro as s

        s.editor.launch_editor()
        return

    if not args.create:
        parser.print_help()
        return

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    project_root = create_project(Path(args.create))
    logging.info("Project created at: %s", project_root.resolve())


if __name__ == "__main__":
    main()
