"""Модуль цветовых эффектов для SpritePro.

Этот модуль предоставляет различные цветовые эффекты и утилиты для создания динамических,
анимированных цветов в играх. Все эффекты основаны на времени и возвращают кортежи RGB цветов.
"""

import math
import time
from typing import Tuple, Optional, Union
import colorsys


class ColorEffects:
    """Статический класс, содержащий различные методы цветовых эффектов.

    Предоставляет набор статических методов для создания анимированных цветовых эффектов,
    таких как пульсация, радуга, дыхание, мерцание и другие.
    """

    @staticmethod
    def pulse(
        speed: float = 1.0,
        base_color: Tuple[int, int, int] = (0, 0, 0),
        target_color: Tuple[int, int, int] = (255, 255, 255),
        intensity: float = 1.0,
        offset: float = 0.0,
    ) -> Tuple[int, int, int]:
        """Создает эффект пульсации цвета между двумя цветами.

        Args:
            speed (float, optional): Множитель скорости пульсации (больше = быстрее). По умолчанию 1.0.
            base_color (Tuple[int, int, int], optional): Начальный цвет RGB. По умолчанию (0, 0, 0).
            target_color (Tuple[int, int, int], optional): Целевой цвет RGB. По умолчанию (255, 255, 255).
            intensity (float, optional): Интенсивность пульсации 0.0-1.0. По умолчанию 1.0.
            offset (float, optional): Смещение времени для множественных синхронизированных пульсаций. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает эффект радуги, циклически проходящий через цветовой спектр.

        Args:
            speed (float, optional): Множитель скорости цикла (больше = быстрее). По умолчанию 1.0.
            saturation (float, optional): Насыщенность цвета 0.0-1.0. По умолчанию 1.0.
            brightness (float, optional): Яркость цвета 0.0-1.0. По умолчанию 1.0.
            offset (float, optional): Смещение времени для множественных синхронизированных радуг. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает эффект дыхания путем изменения яркости.

        Args:
            speed (float, optional): Множитель скорости дыхания. По умолчанию 0.5.
            base_color (Tuple[int, int, int], optional): Базовый цвет RGB. По умолчанию (100, 100, 100).
            intensity (float, optional): Интенсивность дыхания 0.0-1.0. По умолчанию 0.7.
            offset (float, optional): Смещение времени. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает волновой эффект, циклически проходящий через несколько цветов.

        Args:
            speed (float, optional): Множитель скорости волны. По умолчанию 1.0.
            colors (list, optional): Список кортежей RGB цветов для циклического перехода. По умолчанию None.
            offset (float, optional): Смещение времени. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает эффект мерцания, как у свечи или сломанного света.

        Args:
            speed (float, optional): Множитель скорости мерцания. По умолчанию 10.0.
            base_color (Tuple[int, int, int], optional): Базовый цвет RGB. По умолчанию (255, 255, 255).
            flicker_color (Tuple[int, int, int], optional): Акцентный цвет мерцания RGB. По умолчанию (255, 255, 0).
            intensity (float, optional): Интенсивность мерцания 0.0-1.0. По умолчанию 0.3.
            randomness (float, optional): Фактор случайности 0.0-1.0. По умолчанию 0.5.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает стробоскопический эффект, чередующийся между двумя цветами.

        Args:
            speed (float, optional): Множитель скорости стробоскопа. По умолчанию 5.0.
            on_color (Tuple[int, int, int], optional): Цвет когда "включен" RGB. По умолчанию (255, 255, 255).
            off_color (Tuple[int, int, int], optional): Цвет когда "выключен" RGB. По умолчанию (0, 0, 0).
            duty_cycle (float, optional): Доля времени в состоянии "включен" (0.0-1.0). По умолчанию 0.5.
            offset (float, optional): Смещение времени. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает эффект плавного появления/исчезновения путем изменения альфа-канала.

        Args:
            speed (float, optional): Множитель скорости затухания. По умолчанию 1.0.
            color (Tuple[int, int, int], optional): Базовый цвет RGB. По умолчанию (255, 255, 255).
            min_alpha (float, optional): Минимальное значение альфа 0.0-1.0. По умолчанию 0.0.
            max_alpha (float, optional): Максимальное значение альфа 0.0-1.0. По умолчанию 1.0.
            offset (float, optional): Смещение времени. По умолчанию 0.0.

        Returns:
            Tuple[int, int, int, int]: Кортеж RGBA цвета.
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
        """Создает цветовой эффект на основе температуры.

        Args:
            value (float): Текущее значение температуры.
            min_temp (float, optional): Минимальная температура. По умолчанию 0.0.
            max_temp (float, optional): Максимальная температура. По умолчанию 100.0.
            cold_color (Tuple[int, int, int], optional): Цвет при минимальной температуре RGB. По умолчанию (0, 100, 255).
            hot_color (Tuple[int, int, int], optional): Цвет при максимальной температуре RGB. По умолчанию (255, 50, 0).

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
        """Создает цветовой эффект на основе здоровья.

        Args:
            health (float): Текущее значение здоровья.
            max_health (float, optional): Максимальное значение здоровья. По умолчанию 100.0.
            healthy_color (Tuple[int, int, int], optional): Цвет при полном здоровье RGB. По умолчанию (0, 255, 0).
            warning_color (Tuple[int, int, int], optional): Цвет при пороге предупреждения RGB. По умолчанию (255, 255, 0).
            critical_color (Tuple[int, int, int], optional): Цвет при критическом пороге RGB. По умолчанию (255, 0, 0).
            warning_threshold (float, optional): Процент здоровья для предупреждения (0.0-1.0). По умолчанию 0.5.
            critical_threshold (float, optional): Процент здоровья для критического состояния (0.0-1.0). По умолчанию 0.25.

        Returns:
            Tuple[int, int, int]: Кортеж RGB цвета.
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
    """Удобная функция для эффекта пульсации.

    Args:
        speed (float, optional): Множитель скорости пульсации. По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.pulse.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.pulse(speed, **kwargs)


def rainbow(speed: float = 1.0, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для эффекта радуги.

    Args:
        speed (float, optional): Множитель скорости цикла. По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.rainbow.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.rainbow(speed, **kwargs)


def breathing(speed: float = 0.5, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для эффекта дыхания.

    Args:
        speed (float, optional): Множитель скорости дыхания. По умолчанию 0.5.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.breathing.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.breathing(speed, **kwargs)


def wave(speed: float = 1.0, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для волнового эффекта.

    Args:
        speed (float, optional): Множитель скорости волны. По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.wave.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.wave(speed, **kwargs)


def flicker(speed: float = 10.0, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для эффекта мерцания.

    Args:
        speed (float, optional): Множитель скорости мерцания. По умолчанию 10.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.flicker.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.flicker(speed, **kwargs)


def strobe(speed: float = 5.0, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для стробоскопического эффекта.

    Args:
        speed (float, optional): Множитель скорости стробоскопа. По умолчанию 5.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.strobe.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.strobe(speed, **kwargs)


def fade_in_out(speed: float = 1.0, **kwargs) -> Tuple[int, int, int, int]:
    """Удобная функция для эффекта плавного появления/исчезновения.

    Args:
        speed (float, optional): Множитель скорости затухания. По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.fade_in_out.

    Returns:
        Tuple[int, int, int, int]: Кортеж RGBA цвета.
    """
    return ColorEffects.fade_in_out(speed, **kwargs)


def temperature(value: float, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для температурного эффекта.

    Args:
        value (float): Текущее значение температуры.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.temperature.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.temperature(value, **kwargs)


def health_bar(health: float, **kwargs) -> Tuple[int, int, int]:
    """Удобная функция для эффекта полосы здоровья.

    Args:
        health (float): Текущее значение здоровья.
        **kwargs: Дополнительные аргументы, передаваемые в ColorEffects.health_bar.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета.
    """
    return ColorEffects.health_bar(health, **kwargs)


# Color utility functions
def lerp_color(
    color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Линейная интерполяция между двумя цветами.

    Args:
        color1 (Tuple[int, int, int]): Начальный цвет RGB.
        color2 (Tuple[int, int, int]): Конечный цвет RGB.
        factor (float): Фактор интерполяции 0.0-1.0.

    Returns:
        Tuple[int, int, int]: Интерполированный кортеж RGB цвета.
    """
    factor = max(0, min(1, factor))
    r = int(color1[0] + (color2[0] - color1[0]) * factor)
    g = int(color1[1] + (color2[1] - color1[1]) * factor)
    b = int(color1[2] + (color2[2] - color1[2]) * factor)
    return (r, g, b)


def adjust_brightness(
    color: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Изменяет яркость цвета на заданный множитель.

    Args:
        color (Tuple[int, int, int]): Кортеж RGB цвета.
        factor (float): Множитель яркости (1.0 = без изменений, >1.0 = ярче, <1.0 = темнее).

    Returns:
        Tuple[int, int, int]: Скорректированный кортеж RGB цвета.
    """
    r = int(max(0, min(255, color[0] * factor)))
    g = int(max(0, min(255, color[1] * factor)))
    b = int(max(0, min(255, color[2] * factor)))
    return (r, g, b)


def adjust_saturation(
    color: Tuple[int, int, int], factor: float
) -> Tuple[int, int, int]:
    """Изменяет насыщенность цвета на заданный множитель.

    Args:
        color (Tuple[int, int, int]): Кортеж RGB цвета.
        factor (float): Множитель насыщенности (1.0 = без изменений, 0.0 = оттенки серого, >1.0 = более насыщенный).

    Returns:
        Tuple[int, int, int]: Скорректированный кортеж RGB цвета.
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
    """Инвертирует цвет.

    Args:
        color (Tuple[int, int, int]): Кортеж RGB цвета.

    Returns:
        Tuple[int, int, int]: Инвертированный кортеж RGB цвета.
    """
    return (255 - color[0], 255 - color[1], 255 - color[2])


def to_grayscale(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Преобразует цвет в оттенки серого.

    Args:
        color (Tuple[int, int, int]): Кортеж RGB цвета.

    Returns:
        Tuple[int, int, int]: Кортеж RGB цвета в оттенках серого.
    """
    # Use luminance formula for better grayscale conversion
    gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
    return (gray, gray, gray)
