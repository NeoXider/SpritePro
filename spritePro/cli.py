import argparse
import logging
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
    from scenes.second_scene import SecondScene


    def main():
        def setup():
            s.scene.add_scene(config.MAIN_SCENE_NAME, MainScene)
            s.scene.add_scene(config.SECOND_SCENE_NAME, SecondScene)
            s.scene.set_scene_by_name(config.START_SCENE_NAME)

        s.run(
            setup=setup,
            size=config.WINDOW_SIZE,
            title=config.TITLE,
            fps=config.FPS,
            fill_color=config.FILL_COLOR,
        )


    if __name__ == "__main__":
        main()
    """
)

MAIN_SCENE_TEMPLATE = dedent(
    """\
    import pygame
    from pathlib import Path

    import spritePro as s
    from spritePro.editor.runtime import spawn_scene

    import config

    SCENE_JSON = Path(__file__).resolve().parent / "main_level.json"
    PLAYER_NAME = "player"


    class MainScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.runtime_scene = None
            self.player = None
            self._status = "Loaded editor scene"
            self._load_level()
            self.title = s.TextSprite(
                "Main Scene",
                30,
                (245, 245, 245),
                (20, 20),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.hint = s.TextSprite(
                "WASD: move | Enter: next scene | R: restart",
                20,
                (200, 200, 210),
                (20, 56),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.status = s.TextSprite(
                self._status,
                18,
                (160, 220, 180),
                (20, 84),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )

        def _load_level(self):
            if SCENE_JSON.exists():
                try:
                    self.runtime_scene = spawn_scene(SCENE_JSON, scene=self, apply_camera=True)
                    player_obj = self.runtime_scene.exact(PLAYER_NAME)
                    if player_obj is None:
                        self._status = f"Player '{PLAYER_NAME}' not found, fallback created"
                    else:
                        self.player = player_obj.Sprite(speed=config.PLAYER_SPEED)
                except Exception as exc:
                    self._status = f"Failed to load {SCENE_JSON.name}: {exc}"
            else:
                self._status = f"{SCENE_JSON.name} not found, fallback created"

            if self.player is None:
                self.player = s.Sprite("", (64, 64), s.WH_C, speed=config.PLAYER_SPEED, scene=self)
                self.player.set_rect_shape((64, 64), (120, 200, 255), border_radius=16)

            s.set_camera_follow(self.player)

        def on_enter(self, context):
            pass

        def on_exit(self):
            pass

        def update(self, dt):
            if self.player is not None:
                self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_RETURN) or s.input.was_pressed(pygame.K_KP_ENTER):
                s.scene.set_scene_by_name(config.SECOND_SCENE_NAME)
                return
            if s.input.was_pressed(pygame.K_r):
                s.restart_scene()
                return
    """
)

SECOND_SCENE_TEMPLATE = dedent(
    """\
    import pygame

    import spritePro as s

    import config


    class SecondScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.title = s.TextSprite(
                "Second Scene",
                30,
                (245, 245, 245),
                (20, 20),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.hint = s.TextSprite(
                "This scene is intentionally almost empty.",
                22,
                (220, 220, 230),
                (20, 64),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.help = s.TextSprite(
                "Use it for menu, pause, shop, dialogue or another level. Esc/Enter: back",
                18,
                (190, 190, 205),
                (20, 98),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.panel = s.Sprite("", (460, 180), s.WH_C, scene=self)
            self.panel.set_rect_shape((460, 180), (50, 55, 72), border_radius=18)
            self.placeholder = s.TextSprite(
                "Your next scene starts here",
                28,
                (255, 220, 120),
                s.WH_C,
                anchor=s.Anchor.CENTER,
                scene=self,
            )

        def update(self, dt):
            if (
                s.input.was_pressed(pygame.K_ESCAPE)
                or s.input.was_pressed(pygame.K_RETURN)
                or s.input.was_pressed(pygame.K_KP_ENTER)
            ):
                s.scene.set_scene_by_name(config.MAIN_SCENE_NAME)
                return
    """
)

CONFIG_TEMPLATE = dedent(
    """\
    WINDOW_SIZE = (800, 600)
    TITLE = "My SpritePro Game"
    FILL_COLOR = (20, 20, 30)
    FPS = 60
    PLAYER_SPEED = 5

    MAIN_SCENE_NAME = "main"
    SECOND_SCENE_NAME = "second"
    START_SCENE_NAME = MAIN_SCENE_NAME
    """
)

LEVEL_TEMPLATE = dedent(
    """\
    {
        "version": "1.0",
        "name": "main_level",
        "camera": {
            "scene_x": 0.0,
            "scene_y": 0.0,
            "scene_zoom": 1.0,
            "game_x": 0.0,
            "game_y": 0.0,
            "game_zoom": 1.0
        },
        "objects": [
            {
                "id": "player01",
                "name": "player",
                "sprite_path": "",
                "sprite_shape": "rectangle",
                "sprite_color": [120, 200, 255],
                "transform": {
                    "x": 400.0,
                    "y": 300.0,
                    "rotation": 0.0,
                    "scale_x": 1.0,
                    "scale_y": 1.0
                },
                "z_index": 10,
                "screen_space": false,
                "visible": true,
                "locked": false,
                "custom_data": {
                    "width": 64,
                    "height": 64
                }
            }
        ],
        "grid_size": 10,
        "grid_visible": true,
        "grid_labels_visible": true,
        "snap_to_grid": true
    }
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
    second_scene_file = scenes_root / "second_scene.py"
    level_file = scenes_root / "main_level.json"

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
    if not second_scene_file.exists():
        second_scene_file.write_text(SECOND_SCENE_TEMPLATE, encoding="utf-8")
    if not level_file.exists():
        level_file.write_text(LEVEL_TEMPLATE, encoding="utf-8")

    return project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="SpritePro tools")
    parser.add_argument(
        "--create",
        metavar="PATH",
        nargs="?",
        const="main.py",
        help="Create a new project template with two scenes: --create [path]",
    )
    parser.add_argument(
        "--editor",
        "-e",
        action="store_true",
        help="Launch the Sprite Editor",
    )
    parser.add_argument(
        "--webgl",
        metavar="PATH",
        nargs="?",
        const=".",
        help="Prepare web build (Pygbag): --webgl [path to project dir or main.py]",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        default=None,
        help="Output directory for --webgl (default: <project>/web_build)",
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="With --webgl: also run pygbag --build --archive and show path to ZIP (for Yandex Games, itch.io)",
    )
    args = parser.parse_args()

    if args.editor:
        import spritePro as s

        s.editor.launch_editor()
        return

    if args.webgl is not None:
        from spritePro.web_build import build_web, build_web_archive

        path = Path(args.webgl).resolve()
        if path.is_file() and path.suffix == ".py":
            project_dir = path.parent
        else:
            project_dir = path
        if not project_dir.is_dir():
            sys.stderr.write(f"Ошибка: папка не найдена: {project_dir}\n")
            sys.exit(1)
        out = Path(args.output).resolve() if args.output else None
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        if args.archive:
            try:
                zip_path = build_web_archive(project_dir, output_dir=out)
                build_dir = out or (project_dir / "web_build")
                logging.info("Готово. Папка сборки: %s", build_dir)
                logging.info("Архив для загрузки (Яндекс Игры, itch.io): %s", zip_path)
            except (FileNotFoundError, RuntimeError) as e:
                sys.stderr.write(f"Ошибка сборки архива: {e}\n")
                sys.exit(1)
        else:
            result = build_web(project_dir, output_dir=out)
            logging.info("Готово: %s", result)
            logging.info("Запуск: python -m pygbag %s", result)
        return

    if not args.create:
        parser.print_help()
        return

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    project_root = create_project(Path(args.create))
    logging.info("Project created at: %s", project_root.resolve())


if __name__ == "__main__":
    main()
