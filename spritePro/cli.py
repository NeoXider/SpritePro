import argparse
import logging
from pathlib import Path
from textwrap import dedent


MAIN_TEMPLATE = dedent(
    """\
    import pygame
    import spritePro as s

    ASSETS_DIR = "assets"
    IMAGES_DIR = f"{ASSETS_DIR}/images"
    AUDIO_DIR = f"{ASSETS_DIR}/audio"


    class MainScene(s.Scene):
        def on_enter(self, context):
            self.player = s.Sprite(f"{IMAGES_DIR}/player.png", (64, 64), (400, 300), speed=5)

        def update(self, dt):
            self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_SPACE):
                s.debug_log_info("Space pressed")


    def main():
        s.get_screen((800, 600), "My SpritePro Game")
        s.enable_debug(True)
        s.set_debug_camera_input(3)
        s.debug_log_info("Game started")
        s.set_scene(MainScene())

        while True:
            s.update(fill_color=(20, 20, 30))


    if __name__ == "__main__":
        main()
    """
)


def _project_root_from_target(target: Path) -> tuple[Path, Path]:
    if target.suffix == ".py":
        return target.parent, target
    return target, target / "main.py"


def create_project(target: Path) -> Path:
    project_root, main_file = _project_root_from_target(target)

    project_root.mkdir(parents=True, exist_ok=True)
    assets_root = project_root / "assets"
    assets_root.mkdir(exist_ok=True)
    (assets_root / "audio").mkdir(exist_ok=True)
    (assets_root / "images").mkdir(exist_ok=True)
    (project_root / "scenes").mkdir(exist_ok=True)

    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE, encoding="utf-8")

    return project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a minimal SpritePro project")
    parser.add_argument(
        "--create",
        metavar="PATH",
        nargs="?",
        const="main.py",
        help="Project folder or path to main.py",
    )
    args = parser.parse_args()

    if not args.create:
        parser.print_help()
        return

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    project_root = create_project(Path(args.create))
    logging.info("Project created at: %s", project_root.resolve())


if __name__ == "__main__":
    main()
