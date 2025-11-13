# spritePro/mouse_interactor.py
import pygame
from typing import Callable, Optional, List
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
import spritePro


class MouseInteractor:
    """Добавляет логику взаимодействия с мышью (наведение/клик/нажатие) для спрайтов.

    Этот класс обрабатывает события взаимодействия с мышью для спрайта, включая:
    - Обнаружение наведения (вход/выход)
    - Нажатие/отпускание кнопки мыши
    - Обнаружение клика
    - Поддержка пользовательских обратных вызовов для всех событий

    Attributes:
        sprite (pygame.sprite.Sprite): Спрайт с атрибутом .rect.
        on_click (Optional[Callable[[], None]]): Функция, вызываемая при клике на спрайт.
        on_mouse_down (Optional[Callable[[], None]]): Функция, вызываемая при нажатии кнопки мыши над спрайтом.
        on_mouse_up (Optional[Callable[[], None]]): Функция, вызываемая при отпускании кнопки мыши (независимо от позиции).
        on_hover_enter (Optional[Callable[[], None]]): Функция, вызываемая при первом входе мыши в область спрайта.
        on_hover_exit (Optional[Callable[[], None]]): Функция, вызываемая при выходе мыши из области спрайта.
        is_hovered (bool): Находится ли мышь в данный момент над спрайтом.
        is_pressed (bool): Нажата ли кнопка мыши в данный момент над спрайтом.
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
        """Инициализирует компонент взаимодействия с мышью.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт с атрибутом .rect.
            on_click (Optional[Callable[[], None]], optional): Функция, вызываемая при клике на спрайт. По умолчанию None.
            on_mouse_down (Optional[Callable[[], None]], optional): Функция, вызываемая при нажатии кнопки мыши над спрайтом. По умолчанию None.
            on_mouse_up (Optional[Callable[[], None]], optional): Функция, вызываемая при отпускании кнопки мыши. По умолчанию None.
            on_hover_enter (Optional[Callable[[], None]], optional): Функция, вызываемая при первом входе мыши в область спрайта. По умолчанию None.
            on_hover_exit (Optional[Callable[[], None]], optional): Функция, вызываемая при выходе мыши из области спрайта. По умолчанию None.
        """
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
        """Проверяет, находится ли мышь над спрайтом.
        
        Returns:
            bool: True, если мышь находится над спрайтом.
        """
        return self._hovered

    @property
    def is_pressed(self) -> bool:
        """Проверяет, нажата ли кнопка мыши над спрайтом.
        
        Returns:
            bool: True, если кнопка мыши нажата над спрайтом.
        """
        return self._pressed

    def update(self, events: Optional[List[pygame.event.Event]] = None):
        """Обновляет состояние взаимодействия на основе событий мыши.

        Должен вызываться каждый кадр перед отрисовкой:
            inter.update(pygame.event.get())

        Args:
            events (Optional[List[pygame.event.Event]], optional): Список событий pygame для обработки. Если None, используется spritePro.events.
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
    spritePro.init()

    screen = spritePro.get_screen((800, 600), "Mouse Interactor")

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
        spritePro.update(60)

        screen.fill((255, 255, 255))
        screen.blit(sprite.image, sprite.rect)
        inter.update()
