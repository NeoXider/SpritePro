import argparse
from pathlib import Path
from textwrap import dedent


MAIN_TEMPLATE = dedent(
    """\
    import pygame
    import spritePro as s


    class MainScene(s.Scene):
        def on_enter(self, context):
            self.player = s.Sprite("assets/player.png", (64, 64), (400, 300), speed=5)

        def update(self, dt):
            self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_SPACE):
                print("Space pressed")


    def main():
        s.get_screen((800, 600), "My SpritePro Game")
        s.set_scene(MainScene())

        while True:
            s.update(fill_color=(20, 20, 30))


    if __name__ == "__main__":
        main()
    """
)


def create_project(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "assets").mkdir(exist_ok=True)
    (root / "scenes").mkdir(exist_ok=True)

    main_file = root / "main.py"
    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a minimal SpritePro project")
    parser.add_argument("name", help="Project folder name")
    args = parser.parse_args()

    create_project(Path(args.name))
    print(f"Project created at: {Path(args.name).resolve()}")


if __name__ == "__main__":
    main()
