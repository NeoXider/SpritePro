# spritePro/mouse_interactor.py
import pygame
from typing import Callable, Optional, List
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import spritePro


class MouseInteractor:
    """
    Добавляет спрайту hover/click/press-логику.

    Args:
        sprite: любой pygame.sprite.Sprite с атрибутом .rect
        on_click: вызывается при отпускании кнопки над спрайтом
        on_mouse_down: при нажатии над спрайтом
        on_mouse_up: при отпускании (вне зависимости от позиции)
        on_hover_enter: при первом наведении мыши
        on_hover_exit: при уходе мыши
    """

    def __init__(
        self,
        sprite: pygame.sprite.Sprite,
        on_click: Optional[Callable[[], None]] = None,
        on_mouse_down: Optional[Callable[[], None]] = None,
        on_mouse_up: Optional[Callable[[], None]] = None,
        on_hover_enter: Optional[Callable[[], None]] = None,
        on_hover_exit: Optional[Callable[[], None]] = None,
    ):
        self.sprite = sprite
        self.on_click = on_click
        self.on_mouse_down = on_mouse_down
        self.on_mouse_up = on_mouse_up
        self.on_hover_enter = on_hover_enter
        self.on_hover_exit = on_hover_exit

        self._hovered = False
        self._pressed = False

    @property
    def is_hovered(self) -> bool:
        return self._hovered

    @property
    def is_pressed(self) -> bool:
        return self._pressed

    def update(self, events: Optional[List[pygame.event.Event]] = None):
        """
        Надо вызывать каждый кадр (до отрисовки):
            inter.update(pygame.event.get())
        """
        events = events or spritePro.events
        pos = pygame.mouse.get_pos()
        collided = self.sprite.rect.collidepoint(pos)

        # hover enter / exit
        if collided and not self._hovered:
            self._hovered = True
            if self.on_hover_enter:
                self.on_hover_enter()
        elif not collided and self._hovered:
            self._hovered = False
            if self.on_hover_exit:
                self.on_hover_exit()

        # mouse down / up
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and collided:
                self._pressed = True
                if self.on_mouse_down:
                    self.on_mouse_down()
            elif e.type == pygame.MOUSEBUTTONUP:
                if self._pressed:
                    if collided and self.on_click:
                        self.on_click()
                    if self.on_mouse_up:
                        self.on_mouse_up()
                self._pressed = False


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    fps = 60

    sprite = pygame.sprite.Sprite()
    sprite.image = pygame.Surface((250, 50))
    sprite.rect = sprite.image.get_rect()
    sprite.rect.center = (400, 300)
    sprite.color = (255, 0, 0)

    inter = MouseInteractor(
        sprite=sprite,
        on_hover_enter=lambda: print("entered"),
        on_hover_exit=lambda: print("left"),
        on_mouse_down=lambda: print("down"),
        on_mouse_up=lambda: print("up"),
        on_click=lambda: print("Clicked!"),
    )

    while True:
        spritePro.update()
        screen.fill((255, 255, 255))
        screen.blit(sprite.image, sprite.rect)
        inter.update()

        pygame.display.flip()
        clock.tick(fps)
