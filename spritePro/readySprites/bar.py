"""
Bar - Ready-to-use progress bar sprite

This module provides a Bar class that displays a fillable progress bar
with customizable fill direction and smooth animation, similar to Unity's
Image.fillAmount functionality.
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
    """A ready-to-use progress bar that inherits from Sprite.

    This class provides a fillable progress bar with customizable fill direction
    and smooth animation. The bar uses pygame's set_clip() for optimal performance
    and correct anchor positioning.

    Features:
    - 4 fill directions (horizontal and vertical, each with 2 orientations)
    - Smooth animation between fill values
    - Correct anchor positioning when clipped
    - Unity-style fillAmount behavior
    - Optional animation duration control

    Args:
        image (str | Path | pygame.Surface): Path to bar image or pygame Surface.
        pos (Tuple[int, int], optional): Position on screen. Defaults to (0, 0).
        size (Tuple[int, int], optional): Bar dimensions. If None, uses image size.
        fill_direction (str | FillDirection, optional): Fill direction. Defaults to HORIZONTAL_LEFT_TO_RIGHT.
        fill_amount (float, optional): Initial fill amount (0.0-1.0). Defaults to 1.0.
        animate_duration (float, optional): Animation duration in seconds. Defaults to 0.3.
        sorting_order (int, optional): Rendering layer order.

    Example:
        # Basic horizontal progress bar
        bar = Bar("health_bar.png", pos=(100, 100), fill_amount=0.7)

        # Vertical health bar with animation
        bar = Bar(
            image="mana_bar.png",
            pos=(50, 50),
            fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
            animate_duration=0.5
        )

        # In game loop
        bar.set_fill_amount(0.5)  # Animate to 50%
        bar.update(screen)
    """

    def __init__(
        self,
        image: Union[str, Path, pygame.Surface],
        pos: Tuple[int, int] = (0, 0),
        size: Optional[Tuple[int, int]] = None,
        fill_direction: Union[str, FillDirection] = FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
        fill_amount: float = 1.0,
        animate_duration: float = 0.3,
        sorting_order: Optional[int] = None,
    ):
        # Load image if path provided
        if isinstance(image, (str, Path)):
            try:
                image_surface = pygame.image.load(str(image)).convert_alpha()
            except pygame.error as e:
                print(f"Error loading bar image: {image}\n{e}")
                # Create fallback surface
                image_surface = pygame.Surface((100, 20), pygame.SRCALPHA)
                image_surface.fill((255, 0, 0))  # Red fallback
        else:
            image_surface = image

        # Initialize parent Sprite with proper image loading
        super().__init__(
            sprite=image_surface,  # Pass the image directly
            size=size,  # Let parent handle scaling
            pos=pos,
            sorting_order=sorting_order,
        )

        # Initialize bar-specific attributes first
        self._current_fill = max(0.0, min(1.0, fill_amount))  # Clamp to 0-1
        self._target_fill = self._current_fill
        self._fill_direction = fill_direction
        self._animate_duration = animate_duration
        self._is_animating = False
        self._animation_timer = 0.0

        # Store original image for clipping (use parent's scaled image)
        self._original_image = self.original_image.copy()

        # Set initial image
        self._update_clipped_image()

    def set_fill_amount(self, value: float, animate: bool = True) -> None:
        """Set the fill amount of the bar.

        Args:
            value (float): Fill amount from 0.0 to 1.0.
            animate (bool, optional): Whether to animate the change. Defaults to True.
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
        """Get the current fill amount.

        Returns:
            float: Current fill amount (0.0-1.0).
        """
        return self._current_fill

    def set_fill_direction(self, direction: Union[str, FillDirection]) -> None:
        """Set the fill direction of the bar.

        Args:
            direction (str | FillDirection): New fill direction.
        """
        self._fill_direction = direction
        self._update_clipped_image()

    def set_animate_duration(self, duration: float) -> None:
        """Set the animation duration for fill changes.

        Args:
            duration (float): Animation duration in seconds. 0 = no animation.
        """
        self._animate_duration = duration

    def set_fill_type(self, fill_direction: Union[str, FillDirection], anchor: Union[str, Anchor] = Anchor.CENTER) -> None:
        """Set the fill direction and anchor for the bar.

        Args:
            fill_direction (str | FillDirection): Fill direction (e.g., "left_to_right", "bottom_to_top").
            anchor (str | Anchor, optional): Anchor point for positioning. Defaults to CENTER.
        """
        # Set fill direction
        self.set_fill_direction(fill_direction)
        
        # Set anchor using parent's set_position method
        current_pos = self.get_position()
        if current_pos:
            self.set_position(current_pos, anchor)

    def set_image(self, image_source: Union[str, Path, pygame.Surface], size: Optional[Tuple[int, int]] = None) -> None:
        """Set a new image for the bar and update clipping.

        Args:
            image_source: Path to image file or pygame Surface.
            size: New dimensions (width, height) or None to keep original size.
        """
        # Use parent's set_image method (handles scaling properly)
        super().set_image(image_source, size)
        
        # Update the original image for clipping (use parent's scaled image)
        self._original_image = self.original_image.copy()
        
        # Recalculate clipping with new image (only if attributes are initialized)
        if hasattr(self, '_current_fill'):
            self._update_clipped_image()

    def _update_clipped_image(self) -> None:
        """Update the bar image based on current fill amount and direction."""
        if self._current_fill <= 0:
            # Empty bar - create transparent surface
            self.image = pygame.Surface(self._original_image.get_size(), pygame.SRCALPHA)
            return

        if self._current_fill >= 1:
            # Full bar - use original image
            self.image = self._original_image.copy()
            return

        # Calculate clip rectangle based on direction
        original_width = self._original_image.get_width()
        original_height = self._original_image.get_height()
        
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
        self.image = pygame.Surface(clip_rect.size, pygame.SRCALPHA)
        self.image.blit(self._original_image, (0, 0), clip_rect)

        # Update rect with proper anchor positioning
        old_anchor_pos = getattr(self.rect, self.anchor_key)
        self.rect = self.image.get_rect()
        setattr(self.rect, self.anchor_key, old_anchor_pos)

    def _update_animation(self, dt: float) -> None:
        """Update fill animation.

        Args:
            dt (float): Delta time in seconds.
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
        """Update the bar (handles animation and drawing).

        Args:
            screen (pygame.Surface): Screen surface to draw on.
        """
        # Update animation if active
        if hasattr(s, "dt") and s.dt > 0:
            self._update_animation(s.dt)

        # Call parent update for drawing
        super().update(screen)


# Convenience function for quick bar creation
def create_bar(
    image: Union[str, Path, pygame.Surface],
    pos: Tuple[int, int] = (0, 0),
    fill_amount: float = 1.0,
    **kwargs,
) -> Bar:
    """Create a ready-to-use progress bar with common settings.

    Args:
        image: Bar image path or surface.
        pos: Position on screen.
        fill_amount: Initial fill amount (0.0-1.0).
        **kwargs: Additional arguments passed to Bar constructor.

    Returns:
        Bar: Configured bar instance.
    """
    return Bar(image=image, pos=pos, fill_amount=fill_amount, **kwargs)


class BarWithBackground(Bar):
    """A progress bar with a background image and fill overlay.
    
    This class extends Bar to include a background image that remains visible
    while the fill area is clipped on top of it.
    """
    
    def __init__(self, 
                 background_image: Union[str, Path, pygame.Surface],
                 fill_image: Union[str, Path, pygame.Surface],
                 size: Tuple[int, int],
                 pos: Tuple[float, float] = (0, 0),
                 fill_amount: float = 1.0,
                 fill_direction: Union[str, FillDirection] = FillDirection.LEFT_TO_RIGHT,
                 animate_duration: float = 0.3,
                 sorting_order: int = 0,
                 background_size: Optional[Tuple[int, int]] = None,
                 fill_size: Optional[Tuple[int, int]] = None):
        """Initialize a bar with background and fill images.
        
        Args:
            background_image: Image for the background (always visible).
            fill_image: Image for the fill area (clipped based on fill_amount).
            size: Default size of the bar (width, height).
            pos: Position on screen.
            fill_amount: Initial fill amount (0.0-1.0).
            fill_direction: Direction of fill (left_to_right, right_to_left, etc.).
            animate_duration: Duration for fill animations in seconds.
            sorting_order: Rendering order (higher = on top).
            background_size: Optional separate size for background image.
            fill_size: Optional separate size for fill image.
        """
        # Initialize background sprite (always visible)
        super().__init__(
            image=background_image,
            size=size,
            pos=pos,
            fill_amount=1.0,  # Background is always 100% visible
            fill_direction=FillDirection.LEFT_TO_RIGHT,  # Background doesn't need fill direction
            animate_duration=0.0,  # No animation for background
            sorting_order=sorting_order
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
        
        # Create fill sprite (will be clipped)
        self._fill_sprite = None
        self._create_fill_sprite()
        
        # Update initial display
        self._update_clipped_image()
    
    def _parse_fill_direction(self, direction):
        """Parse fill direction string to FillDirection constant."""
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
        """Create the fill sprite from the fill image."""
        try:
            if isinstance(self._fill_image_source, str) or isinstance(self._fill_image_source, Path):
                # Load image from file
                fill_surface = pygame.image.load(str(self._fill_image_source)).convert_alpha()
            else:
                # Use provided surface
                fill_surface = self._fill_image_source.copy()
            
            # Scale to bar size
            self._fill_surface = pygame.transform.scale(fill_surface, self._fill_size)
        except Exception as e:
            print(f"Error loading fill image: {e}")
            # Fallback to colored surface
            self._fill_surface = pygame.Surface(self._fill_size, pygame.SRCALPHA)
            self._fill_surface.fill((100, 150, 255))  # Blue fill color
    
    def _update_clipped_image(self):
        """Update the fill sprite with proper clipping."""
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
        """Calculate the clipping rectangle for the fill area."""
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
    
    def set_fill_image(self, fill_image: Union[str, Path, pygame.Surface]):
        """Set a new fill image.
        
        Args:
            fill_image: New fill image path or surface.
        """
        self._fill_image_source = fill_image
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_background_image(self, background_image: Union[str, Path, pygame.Surface]):
        """Set a new background image.
        
        Args:
            background_image: New background image path or surface.
        """
        self.set_image(background_image)
    
    def set_background_size(self, size: Tuple[int, int]):
        """Set a new background size.
        
        Args:
            size: New background size (width, height).
        """
        self._background_size = size
        self.set_size(size)
    
    def set_fill_size(self, size: Tuple[int, int]):
        """Set a new fill size.
        
        Args:
            size: New fill size (width, height).
        """
        self._fill_size = size
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_both_sizes(self, background_size: Tuple[int, int], fill_size: Tuple[int, int]):
        """Set both background and fill sizes.
        
        Args:
            background_size: New background size (width, height).
            fill_size: New fill size (width, height).
        """
        self._background_size = background_size
        self._fill_size = fill_size
        self.set_size(background_size)
        self._create_fill_sprite()
        self._update_clipped_image()
    
    def set_fill_amount(self, value: float, animate: bool = True) -> None:
        """Set the fill amount of the bar.

        Args:
            value (float): Fill amount from 0.0 to 1.0.
            animate (bool, optional): Whether to animate the change. Defaults to True.
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
        """Get the current fill amount.

        Returns:
            float: Current fill amount (0.0-1.0).
        """
        return self._current_fill
    
    def update(self, screen: pygame.Surface = None):
        """Update the bar with animation logic."""
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
        """Draw the bar with background and fill overlay."""
        # Draw background (parent's image)
        super().draw(screen)
        
        # Draw clipped fill on top
        if hasattr(self, '_clipped_fill_surface'):
            # Use the same position as the background sprite
            fill_rect = self._clipped_fill_surface.get_rect()
            # Get the actual screen position (accounting for camera)
            screen_pos = self.get_position()
            fill_rect.center = screen_pos
            # Debug: Draw a border around the fill to see if it's being drawn
            pygame.draw.rect(screen, (255, 0, 0), fill_rect, 2)  # Red border for debugging
            screen.blit(self._clipped_fill_surface, fill_rect)


def create_bar_with_background(background_image: Union[str, Path, pygame.Surface],
                              fill_image: Union[str, Path, pygame.Surface],
                              pos: Tuple[float, float] = (0, 0),
                              fill_amount: float = 1.0,
                              **kwargs) -> BarWithBackground:
    """Create a ready-to-use bar with background and fill images.

    Args:
        background_image: Background image path or surface.
        fill_image: Fill image path or surface.
        pos: Position on screen.
        fill_amount: Initial fill amount (0.0-1.0).
        **kwargs: Additional arguments passed to BarWithBackground constructor.

    Returns:
        BarWithBackground: Configured bar with background instance.
    """
    return BarWithBackground(
        background_image=background_image,
        fill_image=fill_image,
        pos=pos,
        fill_amount=fill_amount,
        **kwargs
    )
