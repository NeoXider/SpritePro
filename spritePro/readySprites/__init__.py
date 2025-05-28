"""
Ready Sprites Module

This module contains ready-to-use sprite classes that extend SpritePro's
base components with common functionality. These sprites are designed to
be drop-in solutions for common game development needs.

Available Ready Sprites:
- Text_fps: Automatic FPS counter display
"""

from .text_fps import Text_fps, create_fps_counter

__all__ = [
    'Text_fps',
    'create_fps_counter'
]