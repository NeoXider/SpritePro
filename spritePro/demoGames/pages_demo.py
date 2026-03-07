import sys
from pathlib import Path

import enum

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class PageType(enum.StrEnum):
    MENU = "Menu"
    GAME = "Game"


class BasePage(s.Page):
    def __init__(self, pageType, scene=None):
        super().__init__(pageType, scene=scene)
        self.bg = self.add_sprite(s.Sprite("", s.WH, s.WH_C, scene=scene))
        self.text = self.add_sprite(
            s.TextSprite(
                pageType.name,
                64,
                pos=(s.WH_C.x, 20),
                anchor=s.Anchor.MID_TOP,
                scene=scene,
            )
        )
        self.btn = self.add_sprite(s.Button(text="text", pos=s.WH_C), use_scene=False)

        self.anim = s.TweenManager()
        self.anim.add_tween(
            "text",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update=lambda x: self.text.set_scale(x),
        )
        self.anim.add_tween(
            "bg",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update=lambda x: self.bg.set_scale(x),
        )
        self.anim.add_tween(
            "btn",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update=lambda x: self.btn.set_scale(x),
        )

    def on_activate(self):
        self.anim.start_all()

    def on_deactivate(self):
        if hasattr(self, "anim"):
            self.anim.pause_all()


class Menu(BasePage):
    def __init__(self, page_manager: s.PageManager, scene=None):
        super().__init__(PageType.MENU, scene=scene)
        self.btn.on_click(lambda: page_manager.set_active_page(PageType.GAME))
        self.btn.text_sprite.text = "Go to Game"
        self.bg.color = (100, 100, 200)


class Game(BasePage):
    def __init__(self, page_manager: s.PageManager, scene=None):
        super().__init__(PageType.GAME, scene=scene)
        self.btn.on_click(lambda: page_manager.set_active_page(PageType.MENU))
        self.btn.text_sprite.text = "BACK to Menu"
        self.btn.set_position((20, 20), s.Anchor.TOP_LEFT)
        self.bg.color = (100, 200, 100)

class PagesScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.page_manager = s.PageManager(scene=self)
        self.page_manager.add_page(Menu(self.page_manager, scene=self))
        self.page_manager.add_page(Game(self.page_manager, scene=self))
        self.page_manager.set_active_page(PageType.MENU)

    def update(self, dt):
        self.page_manager.update()

def run_demo(platform: str = "pygame") -> None:
    s.run(
        scene=PagesScene,
        title="Pages Demo",
        fill_color=(0, 0, 30),
        platform=platform,
    )


if __name__ == "__main__":
    run_demo("kivy" if "--kivy" in sys.argv else "pygame")
