"""
Text_fps - Ready-to-use FPS counter sprite

This module provides a Text_fps class that automatically displays and updates
the current FPS (Frames Per Second) using SpritePro's TextSprite.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional, Union

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.components.text import TextSprite


class Text_fps(TextSprite):
    """A ready-to-use FPS counter that inherits from TextSprite.

    This class automatically tracks and displays the current FPS with customizable
    appearance and update behavior. It maintains a rolling average for smooth
    FPS display and can be positioned anywhere on screen.

    Features:
    - Automatic FPS calculation using SpritePro's delta time
    - Rolling average over configurable number of frames
    - Customizable text format and appearance
    - Optional prefix/suffix text
    - Smooth FPS updates with configurable precision

    Args:
        pos (Tuple[int, int]): Position on screen (x, y). Defaults to (10, 10).
        font_size (int): Font size in points. Defaults to 24.
        color (Tuple[int, int, int]): Text color in RGB format. Defaults to (255, 255, 0).
        font_name (Optional[Union[str, Path]]): Path to .ttf font file or None for system font.
        prefix (str): Text to display before FPS value. Defaults to "FPS: ".
        suffix (str): Text to display after FPS value. Defaults to "".
        precision (int): Number of decimal places for FPS display. Defaults to 1.
        average_frames (int): Number of frames to average FPS over. Defaults to 60.
        update_interval (float): Minimum time between FPS updates in seconds. Defaults to 0.1.
        **sprite_kwargs: Additional arguments passed to TextSprite.

    Example:
        # Basic FPS counter in top-left corner
        fps_counter = Text_fps()

        # Customized FPS counter
        fps_counter = Text_fps(
            pos=(800, 10),
            color=(0, 255, 0),
            prefix="Frame Rate: ",
            suffix=" fps",
            precision=0
        )

        # In game loop
        while running:
            # ... game logic ...

            fps_counter.update_fps()  # Update FPS calculation
            fps_counter.update(screen)  # Draw to screen
    """

    def __init__(
        self,
        pos: Tuple[int, int] = (10, 10),
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 0),
        font_name: Optional[Union[str, Path]] = None,
        prefix: str = "FPS: ",
        suffix: str = "",
        precision: int = 1,
        average_frames: int = 60,
        update_interval: float = 0.1,
        **sprite_kwargs,
    ):
        # Initialize with default FPS text
        initial_text = f"{prefix}0{suffix}"
        super().__init__(
            text=initial_text,
            font_size=font_size,
            color=color,
            pos=pos,
            font_name=font_name,
            **sprite_kwargs,
        )

        # FPS tracking configuration
        self.prefix = prefix
        self.suffix = suffix
        self.precision = precision
        self.average_frames = average_frames
        self.update_interval = update_interval

        # FPS calculation state
        self.fps_history = []
        self.last_update_time = 0
        self.current_fps = 0.0
        self.frame_count = 0

        # Performance tracking
        self.min_fps = float("inf")
        self.max_fps = 0.0
        self.total_frames = 0

    def update_fps(self):
        """Update FPS calculation and display text.

        This method should be called once per frame to maintain accurate FPS tracking.
        It uses SpritePro's built-in delta time (s.dt) for calculations.
        """
        self.frame_count += 1
        self.total_frames += 1

        # Calculate FPS using SpritePro's delta time
        if hasattr(s, "dt") and s.dt > 0:
            current_fps = 1.0 / s.dt
            self.fps_history.append(current_fps)

            # Maintain rolling average
            if len(self.fps_history) > self.average_frames:
                self.fps_history.pop(0)

            # Calculate average FPS
            if self.fps_history:
                avg_fps = sum(self.fps_history) / len(self.fps_history)

                # Update min/max tracking
                self.min_fps = min(self.min_fps, avg_fps)
                self.max_fps = max(self.max_fps, avg_fps)

                # Update display text if enough time has passed
                current_time = self.total_frames * s.dt if hasattr(s, "dt") else 0
                if current_time - self.last_update_time >= self.update_interval:
                    self.current_fps = avg_fps
                    self._update_display_text()
                    self.last_update_time = current_time

    def _update_display_text(self):
        """Update the displayed text with current FPS value."""
        fps_text = f"{self.current_fps:.{self.precision}f}"
        new_text = f"{self.prefix}{fps_text}{self.suffix}"
        self.set_text(new_text)

    def get_fps(self) -> float:
        """Get the current FPS value.

        Returns:
            float: Current average FPS value.
        """
        return self.current_fps

    def get_fps_stats(self) -> dict:
        """Get comprehensive FPS statistics.

        Returns:
            dict: Dictionary containing current, min, max FPS and frame count.
        """
        return {
            "current_fps": self.current_fps,
            "min_fps": self.min_fps if self.min_fps != float("inf") else 0.0,
            "max_fps": self.max_fps,
            "total_frames": self.total_frames,
            "average_frames_used": len(self.fps_history),
        }

    def reset_stats(self):
        """Reset FPS statistics and history."""
        self.fps_history.clear()
        self.min_fps = float("inf")
        self.max_fps = 0.0
        self.total_frames = 0
        self.frame_count = 0
        self.current_fps = 0.0
        self._update_display_text()

    def set_format(self, prefix: str = None, suffix: str = None, precision: int = None):
        """Update the display format of the FPS counter.

        Args:
            prefix (str, optional): New prefix text.
            suffix (str, optional): New suffix text.
            precision (int, optional): New decimal precision.
        """
        if prefix is not None:
            self.prefix = prefix
        if suffix is not None:
            self.suffix = suffix
        if precision is not None:
            self.precision = precision

        self._update_display_text()

    def set_averaging(self, frames: int, update_interval: float = None):
        """Configure FPS averaging behavior.

        Args:
            frames (int): Number of frames to average over.
            update_interval (float, optional): Minimum time between display updates.
        """
        self.average_frames = frames
        if update_interval is not None:
            self.update_interval = update_interval

        # Trim history if new frame count is smaller
        if len(self.fps_history) > self.average_frames:
            self.fps_history = self.fps_history[-self.average_frames :]


# Convenience function for quick FPS counter creation
def create_fps_counter(
    pos: Tuple[int, int] = (35, 15),
    color: Tuple[int, int, int] = (255, 255, 0),
    **kwargs,
) -> Text_fps:
    """Create a ready-to-use FPS counter with common settings.

    Args:
        pos (Tuple[int, int]): Position on screen.
        color (Tuple[int, int, int]): Text color.
        **kwargs: Additional arguments passed to Text_fps constructor.

    Returns:
        Text_fps: Configured FPS counter instance.
    """
    return Text_fps(pos=pos, color=color, **kwargs)
