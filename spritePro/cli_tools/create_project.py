from __future__ import annotations

from pathlib import Path
from textwrap import dedent


MAIN_TEMPLATE = dedent(
    """\
    import spritePro as s

    import config
    import game_events
    from scenes.main_scene import MainScene
    from scenes.second_scene import SecondScene


    def main():
        def setup():
            game_events.register_event_handlers()
            s.scene.add_scene(config.MAIN_SCENE_NAME, MainScene)
            s.scene.add_scene(config.SECOND_SCENE_NAME, SecondScene)
            s.scene.set_scene_by_name(config.START_SCENE_NAME)

        s.run(
            setup=setup,
            size=config.WINDOW_SIZE,
            reference_size=config.REFERENCE_SIZE,
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
    from game.services.game_service import GameService

    import config
    import game_events

    SCENE_JSON = config.MAIN_LEVEL_PATH
    PLAYER_NAME = "player"


    class MainScene(s.Scene):
        def __init__(self):
            super().__init__()
            self.game_service = GameService()
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
                "WASD: move | Space: score | Enter: next scene | R: restart",
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
            game_events.emit_game_started(self.name or config.MAIN_SCENE_NAME)

        def on_exit(self):
            pass

        def update(self, dt):
            if self.player is not None:
                self.player.handle_keyboard_input()
            if s.input.was_pressed(pygame.K_SPACE):
                self.game_service.add_score(1)
                self.status.set_text(f"Score: {self.game_service.state.score}")
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
    from pathlib import Path

    WINDOW_SIZE = (800, 600)
    TITLE = "My SpritePro Game"
    FILL_COLOR = (20, 20, 30)
    FPS = 60
    PLAYER_SPEED = 5
    REFERENCE_SIZE = None

    MAIN_SCENE_NAME = "main"
    SECOND_SCENE_NAME = "second"
    START_SCENE_NAME = MAIN_SCENE_NAME

    PROJECT_ROOT = Path(__file__).resolve().parent
    ASSETS_DIR = PROJECT_ROOT / "assets"
    AUDIO_DIR = ASSETS_DIR / "audio"
    IMAGES_DIR = ASSETS_DIR / "images"
    SCENES_DIR = PROJECT_ROOT / "scenes"
    GAME_DIR = PROJECT_ROOT / "game"
    DOMAIN_DIR = GAME_DIR / "domain"
    SERVICES_DIR = GAME_DIR / "services"
    MAIN_LEVEL_PATH = SCENES_DIR / "main_level.json"
    """
)

EVENTS_TEMPLATE = dedent(
    """\
    import spritePro as s

    class GameEvents:
        GAME_STARTED = s.events.get_event("game_started")


    def _on_game_started(scene_name: str | None = None) -> None:
        suffix = f" | scene={scene_name}" if scene_name else ""
        s.debug_log_info(f"[event] game_started{suffix}")


    def register_event_handlers() -> None:
        GameEvents.GAME_STARTED.disconnect(_on_game_started)
        GameEvents.GAME_STARTED.connect(_on_game_started)


    def emit_game_started(scene_name: str | None = None) -> None:
        GameEvents.GAME_STARTED.send(scene_name=scene_name)
    """
)

GAME_INIT_TEMPLATE = dedent(
    """\
    \"\"\"Игровая логика проекта: domain, services и вспомогательные модули.\"\"\"
    """
)

DOMAIN_INIT_TEMPLATE = dedent(
    """\
    \"\"\"Domain-модели проекта.\"\"\"
    """
)

SERVICES_INIT_TEMPLATE = dedent(
    """\
    \"\"\"Сервисы и orchestration-логика проекта.\"\"\"
    """
)

GAME_STATE_TEMPLATE = dedent(
    """\
    from dataclasses import dataclass


    @dataclass
    class GameState:
        score: int = 0
    """
)

GAME_SERVICE_TEMPLATE = dedent(
    """\
    from game.domain.game_state import GameState


    class GameService:
        def __init__(self) -> None:
            self.state = GameState()

        def add_score(self, amount: int = 1) -> int:
            self.state.score += int(amount)
            return self.state.score

        def reset(self) -> None:
            self.state.score = 0
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


def project_root_from_target(target: Path) -> tuple[Path, Path]:
    if target.suffix == ".py":
        return target.parent, target
    return target, target / "main.py"


def create_project(target: Path) -> Path:
    project_root, main_file = project_root_from_target(target)
    config_file = project_root / "config.py"
    events_file = project_root / "game_events.py"
    scenes_root = project_root / "scenes"
    game_root = project_root / "game"
    domain_root = game_root / "domain"
    services_root = game_root / "services"
    scenes_init = scenes_root / "__init__.py"
    game_init = game_root / "__init__.py"
    domain_init = domain_root / "__init__.py"
    services_init = services_root / "__init__.py"
    game_state_file = domain_root / "game_state.py"
    game_service_file = services_root / "game_service.py"
    main_scene_file = scenes_root / "main_scene.py"
    second_scene_file = scenes_root / "second_scene.py"
    level_file = scenes_root / "main_level.json"

    project_root.mkdir(parents=True, exist_ok=True)
    assets_root = project_root / "assets"
    assets_root.mkdir(exist_ok=True)
    (assets_root / "audio").mkdir(exist_ok=True)
    (assets_root / "images").mkdir(exist_ok=True)
    scenes_root.mkdir(exist_ok=True)
    domain_root.mkdir(parents=True, exist_ok=True)
    services_root.mkdir(parents=True, exist_ok=True)

    if not main_file.exists():
        main_file.write_text(MAIN_TEMPLATE, encoding="utf-8")
    if not config_file.exists():
        config_file.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    if not events_file.exists():
        events_file.write_text(EVENTS_TEMPLATE, encoding="utf-8")
    if not scenes_init.exists():
        scenes_init.write_text("", encoding="utf-8")
    if not game_init.exists():
        game_init.write_text(GAME_INIT_TEMPLATE, encoding="utf-8")
    if not domain_init.exists():
        domain_init.write_text(DOMAIN_INIT_TEMPLATE, encoding="utf-8")
    if not services_init.exists():
        services_init.write_text(SERVICES_INIT_TEMPLATE, encoding="utf-8")
    if not game_state_file.exists():
        game_state_file.write_text(GAME_STATE_TEMPLATE, encoding="utf-8")
    if not game_service_file.exists():
        game_service_file.write_text(GAME_SERVICE_TEMPLATE, encoding="utf-8")
    if not main_scene_file.exists():
        main_scene_file.write_text(MAIN_SCENE_TEMPLATE, encoding="utf-8")
    if not second_scene_file.exists():
        second_scene_file.write_text(SECOND_SCENE_TEMPLATE, encoding="utf-8")
    if not level_file.exists():
        level_file.write_text(LEVEL_TEMPLATE, encoding="utf-8")

    return project_root
