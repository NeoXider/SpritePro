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
    def __init__(self, name: str, scene=None):
        """Создает страницу с именем, сценой и активным состоянием."""
        self.name = name
        self.active = True
        self.scene = scene
        self.sprites: list[Sprite] = []

    def set_active(self, active: bool):
        """Устанавливает активность страницы и вызывает хуки."""
        if self.active == active:
            return
        self.active = active
        for sprite in self.sprites:
            if hasattr(sprite, "set_active"):
                sprite.set_active(active)
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

    def add_sprite(self, sprite: Sprite, use_scene: bool = True) -> Sprite:
        """Добавляет спрайт на страницу и синхронизирует его состояние."""
        if sprite not in self.sprites:
            self.sprites.append(sprite)
        if use_scene and self.scene is not None and hasattr(sprite, "set_scene"):
            sprite.set_scene(self.scene)
        if hasattr(sprite, "set_active"):
            sprite.set_active(self.active)
        return sprite

    def add_sprites(self, *sprites: Sprite, use_scene: bool = True) -> None:
        """Добавляет несколько спрайтов на страницу."""
        for sprite in sprites:
            self.add_sprite(sprite, use_scene=use_scene)

    def remove_sprite(self, sprite: Sprite) -> None:
        """Удаляет спрайт со страницы."""
        if sprite in self.sprites:
            self.sprites.remove(sprite)


class PageManager:
    def __init__(self, scene=None, log_events: bool = False):
        """Инициализирует менеджер страниц."""
        self.pages = {}
        self.active_pageType: Optional[str] = None
        self.scene = scene
        self.log_events = log_events

    def add_page(self, page: Page):
        """Добавляет страницу в менеджер."""
        if page.scene is None:
            page.scene = self.scene
        if page.name in self.pages:
            if self.log_events:
                spritePro.debug_log_warning(
                    f"Warning: Page '{page.name}' already exists."
                )
            return
        self.pages[page.name] = page

    def remove_page(self, page_type: str):
        """Удаляет страницу по имени."""
        if page_type not in self.pages:
            if self.log_events:
                spritePro.debug_log_warning(
                    f"Warning: Page '{page_type}' does not exist."
                )
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

    def set_scene(self, scene) -> None:
        """Назначает сцену для всех страниц менеджера."""
        self.scene = scene
        for page in self.pages.values():
            page.scene = scene
