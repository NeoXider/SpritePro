
import pygame
from typing import Tuple, Optional, Union, TYPE_CHECKING
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

from enum import IntEnum
import spritePro
from spritePro.sprite import Sprite

class Page:    
    def __init__(self, name: str):
        self.name = name
        self.active = True

    def set_active(self, active: bool):
        if self.active == active:
            return
        self.active = active
        if active:
            self.on_activate()
        else:
            self.on_deactivate()

    def update(self):
        pass

    def on_activate(self):
        pass

    def on_deactivate(self):
        pass

    def is_active(self) -> bool:
        return self.active
    
class PageManager:
    def __init__(self):
        self.pages = {}
        self.active_pageType: Optional[str] = None

    def add_page(self, page: Page):
        if page.name in self.pages:
            print(f"Warning: Page '{page.name}' already exists.")
            return
        self.pages[page.name] = page

    def remove_page(self, page_type: str):
        if page_type not in self.pages:
            print(f"Warning: Page '{page_type}' does not exist.")
            return
        del self.pages[page_type]

    def deactivate_all_pages(self):
        for page in self.pages.values():
            page.set_active(False)

    def set_active_page(self, page_type: str):
        self.deactivate_all_pages()
        self.active_pageType = page_type
        self.get_active_page().set_active(True)

    def get_active_page(self) -> Optional[Page]:
        return self.pages[self.active_pageType]
    
    def get_page(self, page_type: str) -> Page:
        return self.pages[page_type]


    def update(self):
        if self.active_pageType:
            self.get_active_page().update()
