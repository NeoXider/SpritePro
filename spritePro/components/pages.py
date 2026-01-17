
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
        """Создает страницу с именем и активным состоянием."""
        self.name = name
        self.active = True

    def set_active(self, active: bool):
        """Устанавливает активность страницы и вызывает хуки."""
        if self.active == active:
            return
        self.active = active
        if active:
            self.on_activate()
        else:
            self.on_deactivate()

    def update(self):
        """Обновляет логику страницы."""
        pass

    def on_activate(self):
        """Хук, вызываемый при активации страницы."""
        pass

    def on_deactivate(self):
        """Хук, вызываемый при деактивации страницы."""
        pass

    def is_active(self) -> bool:
        """Возвращает текущее состояние активности страницы."""
        return self.active
    
class PageManager:
    def __init__(self):
        """Инициализирует менеджер страниц."""
        self.pages = {}
        self.active_pageType: Optional[str] = None

    def add_page(self, page: Page):
        """Добавляет страницу в менеджер."""
        if page.name in self.pages:
            print(f"Warning: Page '{page.name}' already exists.")
            return
        self.pages[page.name] = page

    def remove_page(self, page_type: str):
        """Удаляет страницу по имени."""
        if page_type not in self.pages:
            print(f"Warning: Page '{page_type}' does not exist.")
            return
        del self.pages[page_type]

    def deactivate_all_pages(self):
        """Деактивирует все страницы."""
        for page in self.pages.values():
            page.set_active(False)

    def set_active_page(self, page_type: str):
        """Активирует страницу по имени и деактивирует остальные."""
        self.deactivate_all_pages()
        self.active_pageType = page_type
        self.get_active_page().set_active(True)

    def get_active_page(self) -> Optional[Page]:
        """Возвращает активную страницу (если есть)."""
        return self.pages[self.active_pageType]
    
    def get_page(self, page_type: str) -> Page:
        """Возвращает страницу по имени."""
        return self.pages[page_type]


    def update(self):
        """Обновляет активную страницу."""
        if self.active_pageType:
            self.get_active_page().update()
