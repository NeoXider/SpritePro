"""Готовый к использованию спрайт счетчика FPS.

Этот модуль предоставляет класс Text_fps, который автоматически отображает и обновляет
текущий FPS (Frames Per Second) с использованием TextSprite из SpritePro.
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
    """Готовый к использованию счетчик FPS, наследуемый от TextSprite.

    Автоматически отслеживает и отображает текущий FPS с настраиваемым
    внешним видом и поведением обновления. Поддерживает скользящее среднее для плавного
    отображения FPS и может быть размещен в любом месте экрана.

    Возможности:
    - Автоматический расчет FPS с использованием delta time из SpritePro
    - Скользящее среднее за настраиваемое количество кадров
    - Настраиваемый формат текста и внешний вид
    - Опциональный префикс/суффикс текста
    - Плавные обновления FPS с настраиваемой точностью

    Attributes:
        prefix (str): Текст перед значением FPS.
        suffix (str): Текст после значения FPS.
        precision (int): Количество знаков после запятой для отображения FPS.
        average_frames (int): Количество кадров для усреднения FPS.
        update_interval (float): Минимальное время между обновлениями FPS в секундах.
        current_fps (float): Текущее среднее значение FPS.
        min_fps (float): Минимальное значение FPS.
        max_fps (float): Максимальное значение FPS.
        total_frames (int): Общее количество обработанных кадров.
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
        """Инициализирует счетчик FPS.

        Args:
            pos (Tuple[int, int], optional): Позиция на экране (x, y). По умолчанию (10, 10).
            font_size (int, optional): Размер шрифта в пунктах. По умолчанию 24.
            color (Tuple[int, int, int], optional): Цвет текста в формате RGB. По умолчанию (255, 255, 0).
            font_name (Optional[Union[str, Path]], optional): Путь к файлу шрифта .ttf или None для системного шрифта.
            prefix (str, optional): Текст перед значением FPS. По умолчанию "FPS: ".
            suffix (str, optional): Текст после значения FPS. По умолчанию "".
            precision (int, optional): Количество знаков после запятой для отображения FPS. По умолчанию 1.
            average_frames (int, optional): Количество кадров для усреднения FPS. По умолчанию 60.
            update_interval (float, optional): Минимальное время между обновлениями FPS в секундах. По умолчанию 0.1.
            **sprite_kwargs: Дополнительные аргументы, передаваемые в TextSprite.
        """
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
        """Обновляет расчет FPS и отображаемый текст.

        Этот метод должен вызываться один раз за кадр для поддержания точного отслеживания FPS.
        Использует встроенное delta time из SpritePro (s.dt) для расчетов.
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
        """Обновляет отображаемый текст текущим значением FPS."""
        fps_text = f"{self.current_fps:.{self.precision}f}"
        new_text = f"{self.prefix}{fps_text}{self.suffix}"
        self.set_text(new_text)

    def get_fps(self) -> float:
        """Получает текущее значение FPS.

        Returns:
            float: Текущее среднее значение FPS.
        """
        return self.current_fps

    def get_fps_stats(self) -> dict:
        """Получает полную статистику FPS.

        Returns:
            dict: Словарь, содержащий текущий, минимальный, максимальный FPS и количество кадров.
        """
        return {
            "current_fps": self.current_fps,
            "min_fps": self.min_fps if self.min_fps != float("inf") else 0.0,
            "max_fps": self.max_fps,
            "total_frames": self.total_frames,
            "average_frames_used": len(self.fps_history),
        }

    def reset_stats(self):
        """Сбрасывает статистику FPS и историю."""
        self.fps_history.clear()
        self.min_fps = float("inf")
        self.max_fps = 0.0
        self.total_frames = 0
        self.frame_count = 0
        self.current_fps = 0.0
        self._update_display_text()

    def set_format(self, prefix: str = None, suffix: str = None, precision: int = None):
        """Обновляет формат отображения счетчика FPS.

        Args:
            prefix (str, optional): Новый префикс текста.
            suffix (str, optional): Новый суффикс текста.
            precision (int, optional): Новая точность десятичных знаков.
        """
        if prefix is not None:
            self.prefix = prefix
        if suffix is not None:
            self.suffix = suffix
        if precision is not None:
            self.precision = precision

        self._update_display_text()

    def set_averaging(self, frames: int, update_interval: float = None):
        """Настраивает поведение усреднения FPS.

        Args:
            frames (int): Количество кадров для усреднения.
            update_interval (float, optional): Минимальное время между обновлениями отображения.
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
    """Создает готовый к использованию счетчик FPS с общими настройками.

    Args:
        pos (Tuple[int, int], optional): Позиция на экране. По умолчанию (35, 15).
        color (Tuple[int, int, int], optional): Цвет текста. По умолчанию (255, 255, 0).
        **kwargs: Дополнительные аргументы, передаваемые в конструктор Text_fps.

    Returns:
        Text_fps: Настроенный экземпляр счетчика FPS.
    """
    return Text_fps(pos=pos, color=color, **kwargs)
