"""
Color Effects Module - SpritePro

This module provides various color effects and utilities for creating dynamic,
animated colors in games. All effects are time-based and return RGB color tuples.
"""

import math
import time
from typing import Tuple, Optional, Union
import colorsys


class ColorEffects:
    """Static class containing various color effect methods."""

    @staticmethod
    def pulse(
        speed: float = 1.0,
        base_color: Tuple[int, int, int] = (0, 0, 0),
        target_color: Tuple[int, int, int] = (255, 255, 255),
        intensity: float = 1.0,
        offset: float = 0.0,
    ) -> Tuple[int, int, int]:
        """Create a pulsing color effect between two colors.

        Args:
            speed: Pulse speed multiplier (higher = faster)
            base_color: Starting color RGB (default: black)
            target_color: Target color RGB (default: white)
            intensity: Pulse intensity 0.0-1.0 (default: 1.0)
            offset: Time offset for multiple synchronized pulses

        Returns:
            RGB color tuple
        """
        t = time.time() * speed + offset
        pulse_value = (math.sin(t) + 1) / 2  # Normalize to 0-1
        pulse_value *= intensity

        # Interpolate between base and target colors
        r = int(base_color[0] + (target_color[0] - base_color[0]) * pulse_value)
        g = int(base_color[1] + (target_color[1] - base_color[1]) * pulse_value)
        b = int(base_color[2] + (target_color[2] - base_color[2]) * pulse_value)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def rainbow(
        speed: float = 1.0,
        saturation: float = 1.0,
        brightness: float = 1.0,
        offset: float = 0.0,
    ) -> Tuple[int, int, int]:
        """Create a rainbow color effect cycling through the color spectrum.

        Args:
            speed: Cycle speed multiplier (higher = faster)
            saturation: Color saturation 0.0-1.0 (default: 1.0)
            brightness: Color brightness 0.0-1.0 (default: 1.0)
            offset: Time offset for multiple synchronized rainbows

        Returns:
            RGB color tuple
        """
        t = time.time() * speed + offset
        hue = (t % (2 * math.pi)) / (2 * math.pi)  # Normalize to 0-1

        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

    @staticmethod
    def breathing(
        speed: float = 0.5,
        base_color: Tuple[int, int, int] = (100, 100, 100),
        intensity: float = 0.7,
        offset: float = 0.0,
    ) -> Tuple[int, int, int]:
        """Create a breathing effect by varying brightness.

        Args:
            speed: Breathing speed multiplier
            base_color: Base color RGB
            intensity: Breathing intensity 0.0-1.0
            offset: Time offset

        Returns:
            RGB color tuple
        """
        t = time.time() * speed + offset
        breath_value = (math.sin(t) + 1) / 2  # Normalize to 0-1
        brightness = 1.0 - (intensity * (1.0 - breath_value))

        r = int(base_color[0] * brightness)
        g = int(base_color[1] * brightness)
        b = int(base_color[2] * brightness)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def wave(
        speed: float = 1.0, colors: list = None, offset: float = 0.0
    ) -> Tuple[int, int, int]:
        """Create a wave effect cycling through multiple colors.

        Args:
            speed: Wave speed multiplier
            colors: List of RGB color tuples to cycle through
            offset: Time offset

        Returns:
            RGB color tuple
        """
        if colors is None:
            colors = [
                (255, 0, 0),
                (255, 255, 0),
                (0, 255, 0),
                (0, 255, 255),
                (0, 0, 255),
                (255, 0, 255),
            ]

        if len(colors) < 2:
            return colors[0] if colors else (255, 255, 255)

        t = time.time() * speed + offset
        cycle_length = len(colors)
        position = (t % (2 * math.pi)) / (2 * math.pi) * cycle_length

        # Get current and next color indices
        current_idx = int(position) % cycle_length
        next_idx = (current_idx + 1) % cycle_length

        # Interpolation factor
        factor = position - int(position)

        # Interpolate between current and next colors
        current_color = colors[current_idx]
        next_color = colors[next_idx]

        r = int(current_color[0] + (next_color[0] - current_color[0]) * factor)
        g = int(current_color[1] + (next_color[1] - current_color[1]) * factor)
        b = int(current_color[2] + (next_color[2] - current_color[2]) * factor)

        return (r, g, b)

    @staticmethod
    def flicker(
        speed: float = 10.0,
        base_color: Tuple[int, int, int] = (255, 255, 255),
        flicker_color: Tuple[int, int, int] = (255, 255, 0),
        intensity: float = 0.3,
        randomness: float = 0.5,
    ) -> Tuple[int, int, int]:
        """Create a flickering effect like a candle or broken light.

        Args:
            speed: Flicker speed multiplier
            base_color: Base color RGB
            flicker_color: Flicker accent color RGB
            intensity: Flicker intensity 0.0-1.0
            randomness: Randomness factor 0.0-1.0

        Returns:
            RGB color tuple
        """
        t = time.time() * speed

        # Create pseudo-random flicker using multiple sine waves
        flicker1 = math.sin(t * 1.7) * 0.5 + 0.5
        flicker2 = math.sin(t * 2.3) * 0.3 + 0.7
        flicker3 = math.sin(t * 3.1) * 0.2 + 0.8

        flicker_value = (flicker1 * flicker2 * flicker3) * intensity * randomness

        # Mix base color with flicker color
        r = int(base_color[0] * (1 - flicker_value) + flicker_color[0] * flicker_value)
        g = int(base_color[1] * (1 - flicker_value) + flicker_color[1] * flicker_value)
        b = int(base_color[2] * (1 - flicker_value) + flicker_color[2] * flicker_value)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def strobe(
        speed: float = 5.0,
        on_color: Tuple[int, int, int] = (255, 255, 255),
        off_color: Tuple[int, int, int] = (0, 0, 0),
        duty_cycle: float = 0.5,
        offset: float = 0.0,
    ) -> Tuple[int, int, int]:
        """Create a strobe effect alternating between two colors.

        Args:
            speed: Strobe speed multiplier
            on_color: Color when "on" RGB
            off_color: Color when "off" RGB
            duty_cycle: Fraction of time spent "on" (0.0-1.0)
            offset: Time offset

        Returns:
            RGB color tuple
        """
        t = time.time() * speed + offset
        cycle_position = (t % (2 * math.pi)) / (2 * math.pi)

        return on_color if cycle_position < duty_cycle else off_color

    @staticmethod
    def fade_in_out(
        speed: float = 1.0,
        color: Tuple[int, int, int] = (255, 255, 255),
        min_alpha: float = 0.0,
        max_alpha: float = 1.0,
        offset: float = 0.0,
    ) -> Tuple[int, int, int, int]:
        """Create a fade in/out effect by varying alpha.

        Args:
            speed: Fade speed multiplier
            color: Base color RGB
            min_alpha: Minimum alpha value 0.0-1.0
            max_alpha: Maximum alpha value 0.0-1.0
            offset: Time offset

        Returns:
            RGBA color tuple
        """
        t = time.time() * speed + offset
        alpha_value = (math.sin(t) + 1) / 2  # Normalize to 0-1
        alpha = min_alpha + (max_alpha - min_alpha) * alpha_value

        return (color[0], color[1], color[2], int(alpha * 255))

    @staticmethod
    def temperature(
        value: float,
        min_temp: float = 0.0,
        max_temp: float = 100.0,
        cold_color: Tuple[int, int, int] = (0, 100, 255),
        hot_color: Tuple[int, int, int] = (255, 50, 0),
    ) -> Tuple[int, int, int]:
        """Create a temperature-based color effect.

        Args:
            value: Current temperature value
            min_temp: Minimum temperature
            max_temp: Maximum temperature
            cold_color: Color at minimum temperature RGB
            hot_color: Color at maximum temperature RGB

        Returns:
            RGB color tuple
        """
        # Normalize value to 0-1 range
        normalized = max(0, min(1, (value - min_temp) / (max_temp - min_temp)))

        # Interpolate between cold and hot colors
        r = int(cold_color[0] + (hot_color[0] - cold_color[0]) * normalized)
        g = int(cold_color[1] + (hot_color[1] - cold_color[1]) * normalized)
        b = int(cold_color[2] + (hot_color[2] - cold_color[2]) * normalized)

        return (r, g, b)

    @staticmethod
    def health_bar(
        health: float,
        max_health: float = 100.0,
        healthy_color: Tuple[int, int, int] = (0, 255, 0),
        warning_color: Tuple[int, int, int] = (255, 255, 0),
        critical_color: Tuple[int, int, int] = (255, 0, 0),
        warning_threshold: float = 0.5,
        critical_threshold: float = 0.25,
    ) -> Tuple[int, int, int]:
        """Create a health-based color effect.

        Args:
            health: Current health value
            max_health: Maximum health value
            healthy_color: Color at full health RGB
            warning_color: Color at warning threshold RGB
            critical_color: Color at critical threshold RGB
            warning_threshold: Health percentage for warning (0.0-1.0)
            critical_threshold: Health percentage for critical (0.0-1.0)

        Returns:
            RGB color tuple
        """
        health_percent = max(0, min(1, health / max_health))

        if health_percent > warning_threshold:
            # Interpolate between healthy and warning
            factor = (health_percent - warning_threshold) / (1.0 - warning_threshold)
            r = int(warning_color[0] + (healthy_color[0] - warning_color[0]) * factor)
            g = int(warning_color[1] + (healthy_color[1] - warning_color[1]) * factor)
            b = int(warning_color[2] + (healthy_color[2] - warning_color[2]) * factor)
        elif health_percent > critical_threshold:
            # Interpolate between warning and critical
            factor = (health_percent - critical_threshold) / (
                warning_threshold - critical_threshold
            )
            r = int(critical_color[0] + (warning_color[0] - critical_color[0]) * factor)
            g = int(critical_color[1] + (warning_color[1] - critical_color[1]) * factor)
            b = int(critical_color[2] + (warning_color[2] - critical_color[2]) * factor)
        else:
            # Critical health - use critical color
            r, g, b = critical_color

        return (r, g, b)


# Convenience functions for easier access
def pulse(speed: float = 1.0, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for pulse effect."""
    return ColorEffects.pulse(speed, **kwargs)


def rainbow(speed: float = 1.0, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for rainbow effect."""
    return ColorEffects.rainbow(speed, **kwargs)


def breathing(speed: float = 0.5, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for breathing effect."""
    return ColorEffects.breathing(speed, **kwargs)


def wave(speed: float = 1.0, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for wave effect."""
    return ColorEffects.wave(speed, **kwargs)


def flicker(speed: float = 10.0, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for flicker effect."""
    return ColorEffects.flicker(speed, **kwargs)


def strobe(speed: float = 5.0, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for strobe effect."""
    return ColorEffects.strobe(speed, **kwargs)


def fade_in_out(speed: float = 1.0, **kwargs) -> Tuple[int, int, int, int]:
    """Convenience function for fade in/out effect."""
    return ColorEffects.fade_in_out(speed, **kwargs)


def temperature(value: float, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for temperature effect."""
    return ColorEffects.temperature(value, **kwargs)


def health_bar(health: float, **kwargs) -> Tuple[int, int, int]:
    """Convenience function for health bar effect."""
    return ColorEffects.health_bar(health, **kwargs)


# Color utility functions
def lerp_color(
    color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Linear interpolation between two colors.

    Args:
        color1: Starting color RGB
        color2: Ending color RGB
        factor: Interpolation factor 0.0-1.0

    Returns:
        Interpolated RGB color tuple
    """
    factor = max(0, min(1, factor))
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)


def adjust_brightness(
    color: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Adjust color brightness by a factor.

    Args:
        color: RGB color tuple
        factor: Brightness multiplier (1.0 = no change, >1.0 = brighter, <1.0 = darker)

    Returns:
        Adjusted RGB color tuple
    """
    r = int(max(0, min(255, color[0] * factor)))
    g = int(max(0, min(255, color[1] * factor)))
    b = int(max(0, min(255, color[2] * factor)))
    return (r, g, b)


def adjust_saturation(
    color: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Adjust color saturation by a factor.

    Args:
        color: RGB color tuple
        factor: Saturation multiplier (1.0 = no change, 0.0 = grayscale, >1.0 = more saturated)

    Returns:
        Adjusted RGB color tuple
    """
    # Convert to HSV
    r, g, b = [c / 255.0 for c in color]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Adjust saturation
    s = max(0, min(1, s * factor))

    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def invert_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Invert a color.

    Args:
        color: RGB color tuple

    Returns:
        Inverted RGB color tuple
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])


def to_grayscale(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Convert color to grayscale.

    Args:
        color: RGB color tuple

    Returns:
        Grayscale RGB color tuple
    """
    # Use luminance formula for better grayscale conversion
    gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    return (gray, gray, gray)
