"""
Utils Module - SpritePro

This module contains utility functions and classes for various game development tasks.
"""

from .surface import round_corners, set_mask
from .color_effects import (
    ColorEffects,
    pulse, rainbow, breathing, wave, flicker, strobe, fade_in_out,
    temperature, health_bar,
    lerp_color, adjust_brightness, adjust_saturation, invert_color, to_grayscale
)

__all__ = [
    # Surface utilities
    "round_corners",
    "set_mask",
    
    # Color effects class
    "ColorEffects",
    
    # Color effect functions
    "pulse",
    "rainbow", 
    "breathing",
    "wave",
    "flicker",
    "strobe",
    "fade_in_out",
    "temperature",
    "health_bar",
    
    # Color utility functions
    "lerp_color",
    "adjust_brightness",
    "adjust_saturation", 
    "invert_color",
    "to_grayscale"
]