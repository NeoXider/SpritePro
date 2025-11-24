import sys
from pathlib import Path
import pygame
from typing import Tuple, Optional, Callable, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from spritePro.constants import Anchor

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from spritePro.button import Button
import spritePro


class ToggleButton(Button):
    """Кнопка-переключатель, которая переключается между состояниями ВКЛ/ВЫКЛ с разными цветами и текстом.

    Расширяет Button для предоставления функциональности переключения с настраиваемыми
    состояниями ВКЛ/ВЫКЛ, цветами и текстовыми метками.

    Attributes:
        is_on (bool): Текущее состояние переключателя (True = ВКЛ, False = ВЫКЛ).
        text_on (str): Текст, отображаемый когда переключатель ВКЛ.
        text_off (str): Текст, отображаемый когда переключатель ВЫКЛ.
        color_on (Tuple[int, int, int]): Цвет фона когда ВКЛ.
        color_off (Tuple[int, int, int]): Цвет фона когда ВЫКЛ.
        hover_brightness (float): Множитель яркости при наведении.
        press_brightness (float): Множитель яркости при нажатии.
        on_toggle (Optional[Callable[[bool], None]]): Функция обработчик переключения.
    """

    def __init__(
        self,
        sprite: str = "",
        size: Tuple[int, int] = (250, 70),
        pos: Tuple[int, int] = (300, 200),
        text_on: str = "ON",
        text_off: str = "OFF",
        text_size: int = 24,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        font_name: Optional[Union[str, Path]] = None,
        on_toggle: Optional[Callable[[bool], None]] = None,
        is_on: bool = True,
        color_on: Tuple[int, int, int] = (50, 150, 50),
        color_off: Tuple[int, int, int] = (150, 50, 50),
        hover_brightness: float = 1.2,
        press_brightness: float = 0.8,
        anim_speed: float = 0.2,
        animated: bool = True,
        anchor: Union[str, "Anchor", None] = None,
    ):
        """Инициализирует новую кнопку-переключатель.

        Args:
            sprite (str, optional): Путь к изображению спрайта. По умолчанию пустая строка.
            size (Tuple[int, int], optional): Размеры кнопки (ширина, высота). По умолчанию (250, 70).
            pos (Tuple[int, int], optional): Позиция кнопки на экране. По умолчанию (300, 200).
            text_on (str, optional): Текст, отображаемый когда переключатель ВКЛ. По умолчанию "ON".
            text_off (str, optional): Текст, отображаемый когда переключатель ВЫКЛ. По умолчанию "OFF".
            text_size (int, optional): Базовый размер шрифта. По умолчанию 24.
            text_color (Tuple[int, int, int], optional): Цвет текста в RGB. По умолчанию (255, 255, 255).
            font_name (Optional[Union[str, Path]], optional): Путь к TTF шрифту или None. По умолчанию None.
            on_toggle (Optional[Callable[[bool], None]], optional): Функция обработчик переключения. По умолчанию None.
            is_on (bool, optional): Начальное состояние переключателя. По умолчанию True.
            color_on (Tuple[int, int, int], optional): Цвет фона когда ВКЛ. По умолчанию (50, 150, 50).
            color_off (Tuple[int, int, int], optional): Цвет фона когда ВЫКЛ. По умолчанию (150, 50, 50).
            hover_brightness (float, optional): Множитель яркости при наведении. По умолчанию 1.2.
            press_brightness (float, optional): Множитель яркости при нажатии. По умолчанию 0.8.
            anim_speed (float, optional): Множитель скорости анимации. По умолчанию 0.2.
            animated (bool, optional): Включены ли анимации. По умолчанию True.
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию None (используется Anchor.CENTER).
        """
        # Store toggle-specific properties
        self.text_on = text_on
        self.text_off = text_off
        self.color_on = color_on
        self.color_off = color_off
        self.hover_brightness = hover_brightness
        self.press_brightness = press_brightness
        self.is_on = is_on
        self.on_toggle = on_toggle

        # Calculate hover and press colors based on current state
        base_color = color_on if is_on else color_off
        hover_color = self._adjust_brightness(base_color, hover_brightness)
        press_color = self._adjust_brightness(base_color, press_brightness)

        # Определяем якорь (если не передан, используем CENTER для обратной совместимости)
        if anchor is None:
            anchor = spritePro.Anchor.CENTER
        
        # Initialize parent Button with current state
        super().__init__(
            sprite=sprite,
            size=size,
            pos=pos,
            text=text_on if is_on else text_off,
            text_size=text_size,
            text_color=text_color,
            font_name=font_name,
            on_click=self._handle_toggle,
            base_color=base_color,
            hover_color=hover_color,
            press_color=press_color,
            anim_speed=anim_speed,
            animated=animated,
            anchor=anchor,
        )

    def _adjust_brightness(
        self, color: Tuple[int, int, int], factor: float
    ) -> Tuple[int, int, int]:
        """Изменяет яркость цвета на множитель.

        Args:
            color (Tuple[int, int, int]): Кортеж RGB цвета.
            factor (float): Множитель яркости (1.0 = без изменений, >1.0 = ярче, <1.0 = темнее).

        Returns:
            Tuple[int, int, int]: Скорректированный кортеж RGB цвета.
        """
        return tuple(min(255, max(0, int(c * factor))) for c in color)

    def _handle_toggle(self):
        """Внутренний метод для обработки изменения состояния переключателя."""
        self.toggle()
        if self.on_toggle:
            self.on_toggle(self.is_on)

    def toggle(self):
        """Переключает состояние кнопки между ВКЛ и ВЫКЛ."""
        self.is_on = not self.is_on
        self._update_appearance()

    def set_state(self, is_on: bool):
        """Устанавливает состояние переключателя напрямую.

        Args:
            is_on (bool): True для состояния ВКЛ, False для состояния ВЫКЛ.
        """
        if self.is_on != is_on:
            self.is_on = is_on
            self._update_appearance()

    def _update_appearance(self):
        """Обновляет внешний вид кнопки на основе текущего состояния."""
        # Update text
        new_text = self.text_on if self.is_on else self.text_off
        self.text_sprite.set_text(new_text)

        # Update colors
        base_color = self.color_on if self.is_on else self.color_off
        self.set_color(base_color)
        self.hover_color = self._adjust_brightness(base_color, self.hover_brightness)
        self.press_color = self._adjust_brightness(base_color, self.press_brightness)

    def set_colors(
        self, color_on: Tuple[int, int, int], color_off: Tuple[int, int, int]
    ):
        """Устанавливает цвета ВКЛ и ВЫКЛ для кнопки-переключателя.

        Args:
            color_on (Tuple[int, int, int]): RGB цвет для состояния ВКЛ.
            color_off (Tuple[int, int, int]): RGB цвет для состояния ВЫКЛ.
        """
        self.color_on = color_on
        self.color_off = color_off
        self._update_appearance()

    def set_texts(self, text_on: str, text_off: str):
        """Устанавливает текстовые метки ВКЛ и ВЫКЛ для кнопки-переключателя.

        Args:
            text_on (str): Текст для отображения когда ВКЛ.
            text_off (str): Текст для отображения когда ВЫКЛ.
        """
        self.text_on = text_on
        self.text_off = text_off
        self._update_appearance()


if __name__ == "__main__":

    def on_sound_toggle(is_on: bool):
        print(f"Sound is now {'ON' if is_on else 'OFF'}")

    def on_music_toggle(is_on: bool):
        print(f"Music is now {'ON' if is_on else 'OFF'}")

    pygame.init()
    screen = spritePro.get_screen((800, 600), "Toggle Button Demo")

    # Create sound toggle (starts ON)
    sound_toggle = ToggleButton(
        pos=(400, 200),
        text_on="Sound ON",
        text_off="Sound OFF",
        is_on=True,
        color_on=(50, 200, 50),
        color_off=(200, 50, 50),
        on_toggle=on_sound_toggle,
        size=(200, 60),
    )

    # Create music toggle (starts OFF)
    music_toggle = ToggleButton(
        pos=(400, 300),
        text_on="Music ON",
        text_off="Music OFF",
        is_on=False,
        color_on=(50, 50, 200),
        color_off=(100, 100, 100),
        on_toggle=on_music_toggle,
        size=(200, 60),
    )

    # Create custom toggle with different styling
    custom_toggle = ToggleButton(
        pos=(400, 400),
        text_on="✓ Enabled",
        text_off="✗ Disabled",
        is_on=True,
        color_on=(255, 165, 0),  # Orange
        color_off=(128, 128, 128),  # Gray
        text_size=20,
        size=(180, 50),
    )

    while True:
        spritePro.update()

        screen.fill((40, 40, 40))

        # Draw title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Toggle Button Demo", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 100))
        screen.blit(title_text, title_rect)

        # Update and draw toggles
        sound_toggle.update(screen)
        music_toggle.update(screen)
        custom_toggle.update(screen)
