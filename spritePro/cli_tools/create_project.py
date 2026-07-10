from __future__ import annotations

from pathlib import Path
from textwrap import dedent


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

    import spritePro as s
    from spritePro.editor.runtime import spawn_scene

    import config


    class MainScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.score = 0
            self.player = None
            self._load_level()
            self.hint = s.TextSprite(
                "WASD: move | Space: score | Enter: next scene | R: restart",
                20,
                (200, 200, 210),
                (20, 20),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )
            self.status = s.TextSprite(
                "Score: 0",
                22,
                (160, 220, 180),
                (20, 52),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )

        def _load_level(self):
            try:
                # Путь резолвится сам: ищется main_level.json рядом со скриптом,
                # в scenes/ и assets/ (расширение можно не писать)
                self.rt = spawn_scene("main_level", scene=self, apply_camera=True)
                self.player = self.rt.Sprite("player", speed=config.PLAYER_SPEED)
            except FileNotFoundError:
                self.player = s.Sprite("", (64, 64), s.WH_C, speed=config.PLAYER_SPEED, scene=self)
                self.player.set_rect_shape((64, 64), (120, 200, 255), border_radius=16)
            s.set_camera_follow(self.player)

        def update(self, dt):
            self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_SPACE):
                self.score += 1
                self.status.set_text(f"Score: {self.score}")
            if s.input.was_pressed(pygame.K_RETURN):
                s.scene.set_scene_by_name(config.SECOND_SCENE_NAME)
            elif s.input.was_pressed(pygame.K_r):
                s.restart_scene()
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
                "Second Scene — Esc/Enter: back",
                28,
                (245, 245, 245),
                s.WH_C,
                scene=self,
            )

        def update(self, dt):
            if s.input.was_pressed(pygame.K_ESCAPE) or s.input.was_pressed(pygame.K_RETURN):
                s.scene.set_scene_by_name(config.MAIN_SCENE_NAME)
    """
)

CONFIG_TEMPLATE = dedent(
    """\
    from pathlib import Path

    WINDOW_SIZE = (800, 600)
    TITLE = "My SpritePro Game"
    FILL_COLOR = (20, 20, 30)
    FPS = 60
    PLAYER_SPEED = 5

    MAIN_SCENE_NAME = "main"
    SECOND_SCENE_NAME = "second"
    START_SCENE_NAME = MAIN_SCENE_NAME

    PROJECT_ROOT = Path(__file__).resolve().parent
    ASSETS_DIR = PROJECT_ROOT / "assets"
    MAIN_LEVEL_PATH = PROJECT_ROOT / "scenes" / "main_level.json"
    """
)

LEVEL_TEMPLATE = dedent(
    """\
    {
        "version": "1.0",
        "name": "main_level",
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
                "active": true,
                "custom_data": {
                    "width": 64,
                    "height": 64
                }
            }
        ]
    }
    """
)

SIMPLE_TEMPLATE = dedent(
    """\
    import pygame

    import spritePro as s


    class GameScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.player = s.Sprite("", (64, 64), s.WH_C, speed=5, scene=self)
            self.player.set_rect_shape((64, 64), (120, 200, 255), border_radius=16)
            self.hint = s.TextSprite(
                "WASD: move | R: restart",
                20,
                (200, 200, 210),
                (20, 20),
                anchor=s.Anchor.TOP_LEFT,
                scene=self,
            )

        def update(self, dt):
            self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_r):
                s.restart_scene()


    if __name__ == "__main__":
        s.run(scene=GameScene, size=(800, 600), title="My Game", fill_color=(20, 20, 30))
    """
)


def project_root_from_target(target: Path) -> tuple[Path, Path]:
    if target.suffix == ".py":
        return target.parent, target
    return target, target / "main.py"


def create_simple_project(target: Path) -> Path:
    """Создаёт минимальный шаблон: один файл, одна сцена."""
    project_root, main_file = project_root_from_target(target)
    project_root.mkdir(parents=True, exist_ok=True)
    if not main_file.exists():
        main_file.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
    return project_root


def create_project(target: Path, simple: bool = False) -> Path:
    """Создаёт шаблон проекта.

    По умолчанию: main.py, config.py, две сцены, сцена редактора и assets/.
    При simple=True — один main.py с одной сценой.
    """
    if simple:
        return create_simple_project(target)

    project_root, main_file = project_root_from_target(target)
    config_file = project_root / "config.py"
    scenes_root = project_root / "scenes"
    scenes_init = scenes_root / "__init__.py"
    main_scene_file = scenes_root / "main_scene.py"
    second_scene_file = scenes_root / "second_scene.py"
    level_file = scenes_root / "main_level.json"

    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "assets").mkdir(exist_ok=True)
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
