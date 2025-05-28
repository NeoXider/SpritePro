import sys
from pathlib import Path
import pygame
from typing import Tuple, Optional, Callable, Union

current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from spritePro.button import Button
import spritePro


class ToggleButton(Button):
    """A toggle button that switches between ON/OFF states with different colors and text.

    This class extends Button to provide toggle functionality with customizable
    ON/OFF states, colors, and text labels.

    Args:
        sprite (str): Path to the sprite image. Defaults to empty string.
        size (Tuple[int, int]): Button dimensions (width, height). Defaults to (250, 70).
        pos (Tuple[int, int]): Button center position on screen. Defaults to (300, 200).
        text_on (str): Text displayed when toggle is ON. Defaults to "ON".
        text_off (str): Text displayed when toggle is OFF. Defaults to "OFF".
        text_size (int): Base font size. Defaults to 24.
        text_color (Tuple[int,int,int]): Text color in RGB. Defaults to (255, 255, 255).
        font_name (Optional[Union[str, Path]]): Path to TTF font or None. Defaults to None.
        on_toggle (Optional[Callable]): Toggle handler function. Defaults to None.
        is_on (bool): Initial toggle state. Defaults to True.
        color_on (Tuple[int,int,int]): Background color when ON. Defaults to (50, 150, 50).
        color_off (Tuple[int,int,int]): Background color when OFF. Defaults to (150, 50, 50).
        hover_brightness (float): Brightness multiplier on hover. Defaults to 1.2.
        press_brightness (float): Brightness multiplier on press. Defaults to 0.8.
        anim_speed (float): Animation speed multiplier. Defaults to 0.2.
        animated (bool): Whether to enable animations. Defaults to True.
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
    ):
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
        )

    def _adjust_brightness(
        self, color: Tuple[int, int, int], factor: float
    ) -> Tuple[int, int, int]:
        """Adjust color brightness by a factor.

        Args:
            color: RGB color tuple
            factor: Brightness multiplier (1.0 = no change, >1.0 = brighter, <1.0 = darker)

        Returns:
            Adjusted RGB color tuple
        """
        return tuple(min(255, max(0, int(c * factor))) for c in color)

    def _handle_toggle(self):
        """Internal method to handle toggle state change."""
        self.toggle()
        if self.on_toggle:
            self.on_toggle(self.is_on)

    def toggle(self):
        """Toggle the button state between ON and OFF."""
        self.is_on = not self.is_on
        self._update_appearance()

    def set_state(self, is_on: bool):
        """Set the toggle state directly.

        Args:
            is_on (bool): True for ON state, False for OFF state
        """
        if self.is_on != is_on:
            self.is_on = is_on
            self._update_appearance()

    def _update_appearance(self):
        """Update button appearance based on current state."""
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
        """Set the ON and OFF colors for the toggle button.

        Args:
            color_on: RGB color for ON state
            color_off: RGB color for OFF state
        """
        self.color_on = color_on
        self.color_off = color_off
        self._update_appearance()

    def set_texts(self, text_on: str, text_off: str):
        """Set the ON and OFF text labels for the toggle button.

        Args:
            text_on: Text to display when ON
            text_off: Text to display when OFF
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
