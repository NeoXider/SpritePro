import sys
from pathlib import Path

import pygame
import enum

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s

class PageType(enum.StrEnum):
    MENU = "Menu"
    GAME = "Game"


class BasePage(s.Page):
    def __init__(self, pageType):
        super().__init__(pageType)
        self.sprites = []
        self.bg = s.Sprite("", s.WH, s.WH_C)
        self.sprites.append(self.bg)
        self.text = s.TextSprite(pageType.name, 64, pos = (s.WH_C.x, 20), anchor=s.Anchor.MID_TOP)
        self.sprites.append(self.text)
        self.btn = s.Button(text = "text", pos = s.WH_C)
        self.sprites.append(self.btn)

        self.anim = s.TweenManager()
        self.anim.add_tween(
            "text",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update= lambda x: self.text.set_scale(x))
        self.anim.add_tween(
            "bg",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update= lambda x: self.bg.set_scale(x))
        self.anim.add_tween(
            "btn",
            0,
            1,
            1,
            s.EasingType.EASE_OUT,
            on_update= lambda x: self.btn.set_scale(x))

    def on_activate(self):
        for sprite in self.sprites:
            sprite.active = True

        self.anim.start_all()
        print("activate")

    def on_deactivate(self):
        for sprite in self.sprites:
            sprite.active = False

        if hasattr(self, 'anim'):
            self.anim.pause_all()
        print("deactivate")

class Menu(BasePage):
    def __init__(self):
        super().__init__(PageType.MENU)
        self.btn.on_click(lambda: pm.set_active_page(PageType.GAME))
        self.btn.text_sprite.text = "Go to Game"
        self.bg.color = (100,100,200)

class Game(BasePage):
    def __init__(self):
        super().__init__(PageType.GAME)        
        self.btn.on_click(lambda: pm.set_active_page(PageType.MENU))
        self.btn.text_sprite.text = "BACK to Menu"
        self.btn.set_position((20,20), s.Anchor.TOP_LEFT)
        self.bg.color = (100,200, 100)

s.get_screen()

pm = s.PageManager()
pm.add_page(Menu())
pm.add_page(Game())
pm.set_active_page(PageType.MENU)
pm.get_page(PageType.MENU)

while True:
    s.update(fill_color=(0,0,30)) 
    pm.update()