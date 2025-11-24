"""Готовые к использованию спрайты полос прогресса.

Этот модуль предоставляет класс Bar, который отображает заполняемую полосу прогресса
с настраиваемым направлением заполнения и плавной анимацией, аналогично функциональности
Unity's Image.fillAmount.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional, Union

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from ..sprite import Sprite
from ..constants import FillDirection, Anchor


class Bar(Sprite):
    """Готовая к использованию полоса прогресса, наследуемая от Sprite.

    Предоставляет заполняемую полосу прогресса с настраиваемым направлением заполнения
    и плавной анимацией. Использует pygame's set_clip() для оптимальной производительности
    и правильного позиционирования якоря.

    Возможности:
    - 4 направления заполнения (горизонтальные и вертикальные, каждое с 2 ориентациями)
    - Плавная анимация между значениями заполнения
    - Правильное позиционирование якоря при обрезке
    - Поведение в стиле Unity fillAmount
    - Опциональный контроль длительности анимации

    Attributes:
        _current_fill (float): Текущее значение заполнения (0.0-1.0).
        _target_fill (float): Целевое значение заполнения (0.0-1.0).
        _fill_direction (Union[str, FillDirection]): Направление заполнения.
        _animate_duration (float): Длительность анимации в секундах.
        _is_animating (bool): Выполняется ли анимация.
    """

    def __init__(
        self,
        image: Union[str, Path, pygame.Surface] = "",
        pos: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        fill_direction: Union[str, FillDirection] = FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
        fill_amount: float = 1.0,
        animate_duration: float = 0.3,
        sorting_order: Optional[int] = None,
        anchor: Union[str, "Anchor"] = None,
    ):
        """Инициализирует полосу прогресса.

        Args:
            image (Union[str, Path, pygame.Surface], optional): Путь к изображению полосы, pygame Surface или пустая строка для создания по умолчанию. По умолчанию "".
            pos (Tuple[int, int], optional): Позиция на экране. По умолчанию (0, 0).
            size (Optional[Tuple[int, int]], optional): Размеры полосы. Если None, используется размер изображения или (100, 20) по умолчанию.
            fill_direction (Union[str, FillDirection], optional): Направление заполнения. По умолчанию HORIZONTAL_LEFT_TO_RIGHT.
            fill_amount (float, optional): Начальное значение заполнения (0.0-1.0). По умолчанию 1.0.
            animate_duration (float, optional): Длительность анимации в секундах. По умолчанию 0.3.
            sorting_order (Optional[int], optional): Порядок отрисовки (слой).
            anchor (Union[str, Anchor], optional): Якорь для позиционирования. По умолчанию None (используется Anchor.CENTER).
        """
        # Определяем якорь (если не передан, используем CENTER для обратной совместимости)
        if anchor is None:
            anchor = Anchor.CENTER
        
        # Initialize parent Sprite with image path/string (Sprite handles loading and fallback)
        # Use default size if not provided
        default_size = size if size is not None else (100, 20)
        super().__init__(
            sprite=image,  # Pass path/string directly, Sprite will handle loading
            size=default_size,
            pos=pos,
            sorting_order=sorting_order,
            anchor=anchor,
        )

        # Initialize bar-specific attributes first
        self._current_fill = max(0.0, min(1.0, fill_amount))  # Clamp to 0-1
        self._target_fill = self._current_fill
        self._fill_direction = fill_direction
        self._animate_duration = animate_duration
        self._is_animating = False
        self._animation_timer = 0.0

        # Store base original image for clipping (before any fill clipping)
        # This is the image that will be clipped based on fill_amount
        self._base_original_image = self.original_image.copy()

        # Set initial image
        self._update_clipped_image()

    def set_fill_amount(self, value: float, animate: bool = True) -> None:
        """Устанавливает значение заполнения полосы.

        Args:
            value (float): Значение заполнения от 0.0 до 1.0.
            animate (bool, optional): Анимировать ли изменение. По умолчанию True.
        """
        self._target_fill = max(0.0, min(1.0, value))  # Clamp to 0-1
        
        if not animate or self._animate_duration <= 0:
            self._current_fill = self._target_fill
            self._is_animating = False
            self._update_clipped_image()
        else:
            self._is_animating = True
            self._animation_timer = 0.0

    def get_fill_amount(self) -> float:
        """Получает текущее значение заполнения.

        Returns:
            float: Текущее значение заполнения (0.0-1.0).
        """
        return self._current_fill

    @property
    def amount(self) -> float:
        """Получает текущее значение заполнения.

        Returns:
            float: Текущее значение заполнения (0.0-1.0).
        """
        return self._current_fill

    @amount.setter
    def amount(self, value: float):
        """Устанавливает значение заполнения полосы.

        Args:
            value (float): Значение заполнения от 0.0 до 1.0.
        """
        self.set_fill_amount(value, animate=True)

    def set_fill_direction(self, direction: Union[str, FillDirection]) -> None:
        """Устанавливает направление заполнения полосы.

        Args:
            direction (Union[str, FillDirection]): Новое направление заполнения.
        """
        self._fill_direction = direction
        self._update_clipped_image()

    def set_animate_duration(self, duration: float) -> None:
        """Устанавливает длительность анимации для изменений заполнения.

        Args:
            duration (float): Длительность анимации в секундах. 0 = без анимации.
        """
        self._animate_duration = duration

    def set_fill_type(self, fill_direction: Union[str, FillDirection], anchor: Union[str, Anchor] = Anchor.CENTER) -> None:
        """Устанавливает направление заполнения и якорь для полосы.

        Args:
            fill_direction (Union[str, FillDirection]): Направление заполнения (например, "left_to_right", "bottom_to_top").
            anchor (Union[str, Anchor], optional): Точка якоря для позиционирования. По умолчанию CENTER.
        """
        # Set fill direction
        self.set_fill_direction(fill_direction)
        
        # Set anchor using parent's set_position method
        current_pos = self.get_position()
        if current_pos:
            self.set_position(current_pos, anchor)

    def set_image(self, image_source: Union[str, Path, pygame.Surface] = "", size: Optional[Tuple[int, int]] = None) -> None:
        """Устанавливает новое изображение для полосы и обновляет обрезку.

        Args:
            image_source (Union[str, Path, pygame.Surface], optional): Путь к файлу изображения, pygame Surface или пустая строка. По умолчанию "".
            size (Optional[Tuple[int, int]], optional): Новые размеры (ширина, высота) или None для сохранения оригинального размера.
        """
        # Use parent's set_image method (handles loading, fallback, and scaling properly)
        super().set_image(image_source, size)
        
        # Update the base original image for clipping (use parent's scaled image)
        # This is the image that will be clipped based on fill_amount
        self._base_original_image = self.original_image.copy()
        
        # Recalculate clipping with new image (only if attributes are initialized)
        if hasattr(self, '_current_fill'):
            self._update_clipped_image()

    def _update_clipped_image(self) -> None:
        """Обновляет изображение полосы на основе текущего значения заполнения и направления.
        
        Обновляет original_image, чтобы базовый Sprite мог применить трансформации (поворот, масштаб и т.д.).
        """
        # Получаем базовое изображение для обрезки (до любых трансформаций)
        base_image = getattr(self, '_base_original_image', self.original_image)
        
        if self._current_fill <= 0:
            # Empty bar - create transparent surface
            clipped_surface = pygame.Surface(base_image.get_size(), pygame.SRCALPHA)
        elif self._current_fill >= 1:
            # Full bar - use original image
            clipped_surface = base_image.copy()
        else:
            # Calculate clip rectangle based on direction
            original_width = base_image.get_width()
            original_height = base_image.get_height()
            
            if self._fill_direction in [FillDirection.HORIZONTAL_LEFT_TO_RIGHT, "horizontal_left_to_right"]:
                # Left to right
                clip_width = int(original_width * self._current_fill)
                clip_rect = pygame.Rect(0, 0, clip_width, original_height)
                
            elif self._fill_direction in [FillDirection.HORIZONTAL_RIGHT_TO_LEFT, "horizontal_right_to_left"]:
                # Right to left
                clip_width = int(original_width * self._current_fill)
                clip_rect = pygame.Rect(original_width - clip_width, 0, clip_width, original_height)
                
            elif self._fill_direction in [FillDirection.VERTICAL_BOTTOM_TO_TOP, "vertical_bottom_to_top"]:
                # Bottom to top
                clip_height = int(original_height * self._current_fill)
                clip_rect = pygame.Rect(0, original_height - clip_height, original_width, clip_height)
                
            elif self._fill_direction in [FillDirection.VERTICAL_TOP_TO_BOTTOM, "vertical_top_to_bottom"]:
                # Top to bottom
                clip_height = int(original_height * self._current_fill)
                clip_rect = pygame.Rect(0, 0, original_width, clip_height)
                
            else:
                # Default to left to right
                clip_width = int(original_width * self._current_fill)
                clip_rect = pygame.Rect(0, 0, clip_width, original_height)

            # Create clipped surface
            clipped_surface = pygame.Surface(clip_rect.size, pygame.SRCALPHA)
            clipped_surface.blit(base_image, (0, 0), clip_rect)
        
        # Обновляем original_image, чтобы базовый Sprite мог применить трансформации
        self.original_image = clipped_surface
        # Помечаем, что нужно обновить трансформации
        self._transform_dirty = True
        self._color_dirty = True

    def _update_animation(self, dt: float) -> None:
        """Обновляет анимацию заполнения.

        Args:
            dt (float): Дельта времени в секундах.
        """
        if not self._is_animating:
            return

        if self._animate_duration <= 0:
            self._current_fill = self._target_fill
            self._is_animating = False
            self._update_clipped_image()
            return

        # Smooth interpolation
        delta = self._target_fill - self._current_fill
        step = (delta / self._animate_duration) * dt

        if abs(delta) < 0.001:
            self._current_fill = self._target_fill
            self._is_animating = False
        else:
            self._current_fill += step

        self._update_clipped_image()

    def update(self, screen: pygame.Surface) -> None:
        """Обновляет полосу (обрабатывает анимацию и отрисовку).

        Args:
            screen (pygame.Surface): Поверхность экрана для отрисовки.
        """
        # Update animation if active
        if hasattr(s, "dt") and s.dt > 0:
            self._update_animation(s.dt)

        # Call parent update for drawing
        super().update(screen)


# Convenience function for quick bar creation
def create_bar(
    image: Union[str, Path, pygame.Surface] = "",
    pos: Tuple[int, int] = (0, 0),
    fill_amount: float = 1.0,
    **kwargs,
) -> Bar:
    """Создает готовую к использованию полосу прогресса с общими настройками.

    Args:
        image (Union[str, Path, pygame.Surface], optional): Путь к изображению полосы, поверхность или пустая строка. По умолчанию "".
        pos (Tuple[int, int], optional): Позиция на экране. По умолчанию (0, 0).
        fill_amount (float, optional): Начальное значение заполнения (0.0-1.0). По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в конструктор Bar.

    Returns:
        Bar: Настроенный экземпляр полосы.
    """
    return Bar(image=image, pos=pos, fill_amount=fill_amount, **kwargs)


class _ColorWrapper:
    """Внутренний класс-обертка для изменения цвета фона или fill."""
    
    def __init__(self, bar_instance, is_background: bool):
        """Инициализирует обертку цвета.
        
        Args:
            bar_instance: Экземпляр BarWithBackground.
            is_background (bool): True для фона, False для fill.
        """
        self._bar = bar_instance
        self._is_background = is_background
        self._alpha = 255  # По умолчанию полностью непрозрачный
    
    @property
    def color(self) -> Optional[Tuple[int, int, int]]:
        """Получает текущий цвет (RGB).
        
        Returns:
            Optional[Tuple[int, int, int]]: Текущий цвет в RGB или None.
        """
        if self._is_background:
            return self._bar.color
        else:
            return getattr(self._bar, '_fill_color', None)
    
    @color.setter
    def color(self, value: Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]]):
        """Устанавливает цвет и обновляет соответствующее изображение.
        
        Поддерживает как RGB (r, g, b), так и RGBA (r, g, b, a) кортежи.
        Если передан RGBA, альфа-канал будет использован.
        
        Args:
            value (Optional[Union[Tuple[int, int, int], Tuple[int, int, int, int]]]): 
                Новый цвет в RGB или RGBA формате, или None.
        """
        if value is None:
            return
        
        # Определяем RGB и альфа
        if len(value) == 4:
            r, g, b, a = value
            self._alpha = max(0, min(255, a))
        else:
            r, g, b = value[:3]
            a = self._alpha
        
        rgb_color = (r, g, b)
        rgba_color = (r, g, b, a)
        
        if self._is_background:
            # Проверяем, есть ли уже загруженное изображение (не пустая строка)
            # Если изображение было загружено из файла или Surface, используем тонировку через Sprite.color
            # Если изображения не было (пустая строка), создаем цветную поверхность
            has_loaded_image = False
            if hasattr(self._bar, '_image_source'):
                img_source = self._bar._image_source
                # Изображение загружено, если это не пустая строка и не None
                # (может быть путь к файлу или pygame.Surface)
                if img_source and img_source != "":
                    # Проверяем, что это не просто созданная нами цветная поверхность
                    # Если original_image имеет тот же размер, что и текущий размер, и это не Surface из файла,
                    # то возможно это созданная нами поверхность
                    has_loaded_image = True
            
            if has_loaded_image:
                # Используем базовый механизм тонировки Sprite (не заменяем изображение!)
                self._bar.color = rgb_color
                if a != 255:
                    self._bar.alpha = a
            else:
                # Создаем новую поверхность с цветом (если изображения не было)
                bg_size = getattr(self._bar, 'size', (100, 20))
                bg_surface = pygame.Surface(bg_size, pygame.SRCALPHA)
                bg_surface.fill(rgba_color)
                self._bar.set_image(bg_surface, bg_size)
        else:
            # Обновляем цвет fill
            self._bar._fill_color = rgb_color
            self._bar._fill_alpha = a
            
            # Проверяем, есть ли уже загруженное изображение fill
            has_loaded_fill_image = False
            if hasattr(self._bar, '_fill_image_source'):
                fill_source = self._bar._fill_image_source
                if fill_source and fill_source != "":
                    has_loaded_fill_image = True
            
            if has_loaded_fill_image:
                # Если изображение было загружено, применяем тонировку к нему
                # Пересоздаем fill sprite, а затем применяем тонировку
                self._bar._create_fill_sprite()
                # Применяем тонировку к загруженному изображению
                if rgb_color != (255, 255, 255):
                    # Создаем поверхность для тонировки
                    tint_surface = pygame.Surface(self._bar._fill_surface.get_size(), pygame.SRCALPHA)
                    tint_surface.fill(rgb_color)
                    # Применяем тонировку через BLEND_RGBA_MULT
                    self._bar._fill_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                # Применяем альфа-канал
                if a != 255:
                    self._bar._fill_surface.set_alpha(a)
            else:
                # Создаем новую поверхность с цветом (если изображения не было)
                fill_surface = pygame.Surface(self._bar._fill_size, pygame.SRCALPHA)
                fill_surface.fill(rgba_color)
                # Обновляем fill поверхность
                self._bar._fill_surface = pygame.transform.scale(fill_surface, self._bar._fill_size)
            
            self._bar._update_clipped_image()
    
    @property
    def alpha(self) -> int:
        """Получает текущую прозрачность.
        
        Returns:
            int: Текущая прозрачность (0-255, где 255 = непрозрачный).
        """
        return self._alpha
    
    @alpha.setter
    def alpha(self, value: int):
        """Устанавливает прозрачность и обновляет изображение.
        
        Args:
            value (int): Новая прозрачность (0-255, где 255 = непрозрачный).
        """
        self._alpha = max(0, min(255, value))
        # Обновляем изображение с новой прозрачностью
        current_color = self.color
        if current_color is not None:
            self.color = current_color  # Переустановим цвет с новым альфа-каналом


class BarWithBackground(Bar):
    """Полоса прогресса с фоновым изображением и наложением заполнения.
    
    Расширяет Bar для включения фонового изображения, которое остается видимым,
    в то время как область заполнения обрезается поверх него.
    
    Attributes:
        bg (_ColorWrapper): Обертка для изменения цвета фона через bg.color.
        fill (_ColorWrapper): Обертка для изменения цвета fill через fill.color.
    """
    
    def __init__(self, 
                 background_image: Union[str, Path, pygame.Surface] = "",
                 fill_image: Union[str, Path, pygame.Surface] = "",
                 size: Tuple[int, int] = (100, 20),
                 pos: Tuple[float, float] = (0, 0),
                 fill_amount: float = 1.0,
                 fill_direction: Union[str, FillDirection] = FillDirection.LEFT_TO_RIGHT,
                 animate_duration: float = 0.3,
                 sorting_order: int = 0,
                 background_size: Optional[Tuple[int, int]] = None,
                 fill_size: Optional[Tuple[int, int]] = None,
                 anchor: Union[str, "Anchor"] = None):
        """Инициализирует полосу с фоновым изображением и изображением заполнения.
        
        Args:
            background_image (Union[str, Path, pygame.Surface], optional): Изображение для фона (всегда видимо) или пустая строка. По умолчанию "".
            fill_image (Union[str, Path, pygame.Surface], optional): Изображение для области заполнения (обрезается на основе fill_amount) или пустая строка. По умолчанию "".
            size (Tuple[int, int], optional): Размер полосы по умолчанию (ширина, высота). По умолчанию (100, 20).
            pos (Tuple[float, float], optional): Позиция на экране. По умолчанию (0, 0).
            fill_amount (float, optional): Начальное значение заполнения (0.0-1.0). По умолчанию 1.0.
            fill_direction (Union[str, FillDirection], optional): Направление заполнения (left_to_right, right_to_left и т.д.). По умолчанию LEFT_TO_RIGHT.
            animate_duration (float, optional): Длительность анимации заполнения в секундах. По умолчанию 0.3.
            sorting_order (int, optional): Порядок отрисовки (больше = сверху). По умолчанию 0.
            background_size (Optional[Tuple[int, int]], optional): Опциональный отдельный размер для фонового изображения.
            fill_size (Optional[Tuple[int, int]], optional): Опциональный отдельный размер для изображения заполнения.
            anchor (Union[str, Anchor], optional): Якорь для позиционирования. По умолчанию None (используется Anchor.CENTER).
        """
        # Initialize background sprite (always visible)
        # Bar.__init__ will handle image loading with fallback
        super().__init__(
            image=background_image,
            size=size,
            pos=pos,
            fill_amount=1.0,  # Background is always 100% visible
            fill_direction=FillDirection.LEFT_TO_RIGHT,  # Background doesn't need fill direction
            animate_duration=0.0,  # No animation for background
            sorting_order=sorting_order,
            anchor=anchor
        )
        
        # Store fill properties
        self._fill_image_source = fill_image
        self._fill_size = fill_size if fill_size is not None else size
        self._background_size = background_size if background_size is not None else size
        self._fill_direction = self._parse_fill_direction(fill_direction)
        self._current_fill = fill_amount
        self._target_fill = fill_amount
        self._animate_duration = animate_duration
        self._is_animating = False
        self._animation_timer = 0.0
        self._fill_color = None  # Цвет fill изображения
        self._fill_alpha = 255  # Альфа-канал fill изображения
        
        # Create fill sprite (will be clipped)
        self._fill_sprite = None
        self._create_fill_sprite()
        
        # Create color wrappers for easy access
        self.bg = _ColorWrapper(self, is_background=True)
        self.fill = _ColorWrapper(self, is_background=False)
        # Инициализируем альфа-канал для fill из существующего значения
        if hasattr(self, '_fill_alpha'):
            self.fill._alpha = self._fill_alpha
        
        # Update initial display
        self._update_clipped_image()
    
    def _parse_fill_direction(self, direction):
        """Преобразует строку направления заполнения в константу FillDirection.
        
        Args:
            direction (Union[str, FillDirection]): Направление заполнения.
        
        Returns:
            FillDirection: Константа направления заполнения.
        """
        if isinstance(direction, str):
            direction_lower = direction.lower()
            if direction_lower in ["left_to_right", "horizontal_left_to_right"]:
                return FillDirection.HORIZONTAL_LEFT_TO_RIGHT
            elif direction_lower in ["right_to_left", "horizontal_right_to_left"]:
                return FillDirection.HORIZONTAL_RIGHT_TO_LEFT
            elif direction_lower in ["bottom_to_top", "vertical_bottom_to_top"]:
                return FillDirection.VERTICAL_BOTTOM_TO_TOP
            elif direction_lower in ["top_to_bottom", "vertical_top_to_bottom"]:
                return FillDirection.VERTICAL_TOP_TO_BOTTOM
            else:
                return FillDirection.HORIZONTAL_LEFT_TO_RIGHT  # Default
        else:
            return direction  # Already a FillDirection constant
    
    def _create_fill_sprite(self):
        """Создает спрайт заполнения из изображения заполнения.
        
        Использует ту же логику загрузки, что и Sprite.set_image - если загрузка не удалась,
        создается прозрачная поверхность с размером fill_size.
        """
        if isinstance(self._fill_image_source, pygame.Surface):
            fill_surface = self._fill_image_source.copy()
        elif not self._fill_image_source:  # Empty string or None
            # Create fallback surface (transparent)
            fill_surface = pygame.Surface(self._fill_size, pygame.SRCALPHA)
            # Fill with color if fill color is set
            if hasattr(self, '_fill_color') and self._fill_color is not None:
                alpha = getattr(self, '_fill_alpha', 255)
                fill_surface.fill((*self._fill_color, alpha))
        else:
            try:
                fill_surface = pygame.image.load(str(self._fill_image_source)).convert_alpha()
            except Exception:
                print(
                    f"[BarWithBackground] не удалось загрузить изображение заполнения из '{self._fill_image_source}'"
                )
                # Create fallback surface (transparent)
                fill_surface = pygame.Surface(self._fill_size, pygame.SRCALPHA)
                # Fill with color if fill color is set
                if hasattr(self, '_fill_color') and self._fill_color is not None:
                    alpha = getattr(self, '_fill_alpha', 255)
                    fill_surface.fill((*self._fill_color, alpha))
        
        # Scale to bar size
        self._fill_surface = pygame.transform.scale(fill_surface, self._fill_size)
    
    def _update_clipped_image(self):
        """Обновляет спрайт заполнения с правильной обрезкой."""
        if not hasattr(self, '_fill_surface'):
            return
            
        # Create new surface for clipped fill
        clipped_surface = pygame.Surface(self._fill_size, pygame.SRCALPHA)
        
        # Calculate clip rectangle based on fill amount and direction
        clip_rect = self._calculate_clip_rect()
        
        if clip_rect.width > 0 and clip_rect.height > 0:
            # Set clipping area
            clipped_surface.set_clip(clip_rect)
            # Blit the fill image to the clipped surface
            clipped_surface.blit(self._fill_surface, (0, 0))
            # Reset clipping
            clipped_surface.set_clip(None)
        
        # Store the clipped surface for rendering
        self._clipped_fill_surface = clipped_surface
    
    def _calculate_clip_rect(self):
        """Вычисляет прямоугольник обрезки для области заполнения.
        
        Returns:
            pygame.Rect: Прямоугольник обрезки.
        """
        width, height = self._fill_size
        fill_width = int(width * self._current_fill)
        fill_height = int(height * self._current_fill)
        
        if self._fill_direction == FillDirection.HORIZONTAL_LEFT_TO_RIGHT:
            return pygame.Rect(0, 0, fill_width, height)
        elif self._fill_direction == FillDirection.HORIZONTAL_RIGHT_TO_LEFT:
            return pygame.Rect(width - fill_width, 0, fill_width, height)
        elif self._fill_direction == FillDirection.VERTICAL_BOTTOM_TO_TOP:
            return pygame.Rect(0, height - fill_height, width, fill_height)
        elif self._fill_direction == FillDirection.VERTICAL_TOP_TO_BOTTOM:
            return pygame.Rect(0, 0, width, fill_height)
        else:
            return pygame.Rect(0, 0, fill_width, height)
    
    def set_fill_image(self, fill_image: Union[str, Path, pygame.Surface] = ""):
        """Устанавливает новое изображение заполнения.
        
        Args:
            fill_image (Union[str, Path, pygame.Surface], optional): Новый путь к изображению заполнения, поверхность или пустая строка. По умолчанию "".
        """
        self._fill_image_source = fill_image
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_fill_color(self, color: Union[Tuple[int, int, int], Tuple[int, int, int, int]], alpha: Optional[int] = None):
        """Устанавливает цвет изображения заполнения.
        
        Создает новую поверхность с указанным цветом для fill изображения.
        Также можно использовать fill.color = (r, g, b) или fill.color = (r, g, b, a).
        
        Args:
            color (Union[Tuple[int, int, int], Tuple[int, int, int, int]]): Цвет в формате RGB или RGBA (0-255).
            alpha (Optional[int], optional): Альфа-канал (0-255). Используется только если color в формате RGB. По умолчанию None (255).
        """
        # Определяем RGB и альфа
        if len(color) == 4:
            r, g, b, a = color
            self._fill_color = (r, g, b)
            self._fill_alpha = max(0, min(255, a))
        else:
            r, g, b = color[:3]
            self._fill_color = (r, g, b)
            self._fill_alpha = max(0, min(255, alpha)) if alpha is not None else 255
        
        # Создаем новую поверхность с указанным цветом и альфа-каналом
        fill_surface = pygame.Surface(self._fill_size, pygame.SRCALPHA)
        fill_surface.fill((r, g, b, self._fill_alpha))
        
        # Обновляем fill поверхность
        self._fill_surface = pygame.transform.scale(fill_surface, self._fill_size)
        self._update_clipped_image()
    
    def set_background_image(self, background_image: Union[str, Path, pygame.Surface] = ""):
        """Устанавливает новое фоновое изображение.
        
        Args:
            background_image (Union[str, Path, pygame.Surface], optional): Новый путь к фоновому изображению, поверхность или пустая строка. По умолчанию "".
        """
        self.set_image(background_image)
    
    def set_background_size(self, size: Tuple[int, int]):
        """Устанавливает новый размер фона.
        
        Args:
            size (Tuple[int, int]): Новый размер фона (ширина, высота).
        """
        self._background_size = size
        self.set_size(size)
    
    def set_fill_size(self, size: Tuple[int, int]):
        """Устанавливает новый размер заполнения.
        
        Args:
            size (Tuple[int, int]): Новый размер заполнения (ширина, высота).
        """
        self._fill_size = size
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_both_sizes(self, background_size: Tuple[int, int], fill_size: Tuple[int, int]):
        """Устанавливает размеры фона и заполнения.
        
        Args:
            background_size (Tuple[int, int]): Новый размер фона (ширина, высота).
            fill_size (Tuple[int, int]): Новый размер заполнения (ширина, высота).
        """
        self._background_size = background_size
        self._fill_size = fill_size
        self.set_size(background_size)
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_fill_amount(self, value: float, animate: bool = True) -> None:
        """Устанавливает значение заполнения полосы.

        Args:
            value (float): Значение заполнения от 0.0 до 1.0.
            animate (bool, optional): Анимировать ли изменение. По умолчанию True.
        """
        self._target_fill = max(0.0, min(1.0, value))  # Clamp to 0-1
        
        if not animate or self._animate_duration <= 0:
            self._current_fill = self._target_fill
            self._is_animating = False
            self._update_clipped_image()
        else:
            self._is_animating = True
            self._animation_timer = 0.0
    
    def get_fill_amount(self) -> float:
        """Получает текущее значение заполнения.

        Returns:
            float: Текущее значение заполнения (0.0-1.0).
        """
        return self._current_fill
    
    def update(self, screen: pygame.Surface = None):
        """Обновляет полосу с логикой анимации.
        
        Args:
            screen (pygame.Surface, optional): Поверхность экрана для отрисовки. По умолчанию None.
        """
        # Update fill animation
        if self._is_animating and self._animate_duration > 0:
            self._animation_timer += 1.0 / 60.0  # Assuming 60 FPS
            
            if self._animation_timer >= self._animate_duration:
                # Animation complete
                self._current_fill = self._target_fill
                self._is_animating = False
                self._animation_timer = 0.0
            else:
                # Interpolate between current and target
                progress = self._animation_timer / self._animate_duration
                self._current_fill = self._current_fill + (self._target_fill - self._current_fill) * progress
            
            # Update clipped image during animation
            self._update_clipped_image()
        
        # Call parent update (this draws the background)
        super().update(screen)
        
        # Draw fill overlay on top of background
        if screen is not None and hasattr(self, '_clipped_fill_surface') and self.active:
            # Get camera position
            import spritePro
            from pygame.math import Vector2
            camera = getattr(spritePro.get_game(), "camera", Vector2())
            
            # Calculate fill position with camera offset
            fill_rect = self._clipped_fill_surface.get_rect()
            if getattr(self, "screen_space", False):
                fill_rect.center = self.rect.center
            else:
                draw_rect = self.rect.copy()
                draw_rect.x -= int(camera.x)
                draw_rect.y -= int(camera.y)
                fill_rect.center = draw_rect.center
            
            # Draw the fill surface
            screen.blit(self._clipped_fill_surface, fill_rect)
    
    def draw(self, screen: pygame.Surface):
        """Отрисовывает полосу с фоном и наложением заполнения.
        
        Args:
            screen (pygame.Surface): Поверхность экрана для отрисовки.
        """
        # Draw background (parent's image) - это уже включает все трансформации (поворот, масштаб и т.д.)
        super().draw(screen)
        
        # Draw clipped fill on top with same transformations
        if hasattr(self, '_clipped_fill_surface') and self.active:
            # Apply same transformations as the main sprite
            fill_img = self._clipped_fill_surface.copy()
            
            # Apply flip
            if self.flipped_h or self.flipped_v:
                fill_img = pygame.transform.flip(fill_img, self.flipped_h, self.flipped_v)
            
            # Apply scale
            if self._scale != 1.0:
                new_size = (
                    int(fill_img.get_width() * self._scale),
                    int(fill_img.get_height() * self._scale),
                )
                fill_img = pygame.transform.scale(fill_img, new_size)
            
            # Apply rotation
            if self._angle != 0:
                fill_img = pygame.transform.rotate(fill_img, self._angle)
            
            # Get screen position (accounting for camera)
            fill_rect = fill_img.get_rect()
            screen_pos = self.get_position()
            fill_rect.center = screen_pos
            
            # Apply alpha if needed
            if self._alpha != 255:
                fill_img.set_alpha(self._alpha)
            
            # Draw the transformed fill surface
            screen.blit(fill_img, fill_rect)


def create_bar_with_background(background_image: Union[str, Path, pygame.Surface] = "",
                              fill_image: Union[str, Path, pygame.Surface] = "",
                              pos: Tuple[float, float] = (0, 0),
                              fill_amount: float = 1.0,
                              **kwargs) -> BarWithBackground:
    """Создает готовую к использованию полосу с фоновым изображением и изображением заполнения.

    Args:
        background_image (Union[str, Path, pygame.Surface], optional): Путь к фоновому изображению, поверхность или пустая строка. По умолчанию "".
        fill_image (Union[str, Path, pygame.Surface], optional): Путь к изображению заполнения, поверхность или пустая строка. По умолчанию "".
        pos (Tuple[float, float], optional): Позиция на экране. По умолчанию (0, 0).
        fill_amount (float, optional): Начальное значение заполнения (0.0-1.0). По умолчанию 1.0.
        **kwargs: Дополнительные аргументы, передаваемые в конструктор BarWithBackground.

    Returns:
        BarWithBackground: Настроенный экземпляр полосы с фоном.
    """
    return BarWithBackground(
        background_image=background_image,
        fill_image=fill_image,
        pos=pos,
        fill_amount=fill_amount,
        **kwargs
    )
