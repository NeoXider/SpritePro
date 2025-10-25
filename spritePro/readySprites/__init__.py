"""
Ready Sprites Module

This module contains ready-to-use sprite classes that extend SpritePro's
base components with common functionality. These sprites are designed to
be drop-in solutions for common game development needs.

Available Ready Sprites:
- Text_fps: Automatic FPS counter display
- Bar: Progress bar with fill directions and animation
"""

from .text_fps import Text_fps, create_fps_counter
from .bar import Bar, create_bar, BarWithBackground, create_bar_with_background

__all__ = [
    'Text_fps',
    'create_fps_counter',
    'Bar',
    'create_bar',
    'BarWithBackground',
    'create_bar_with_background'
]