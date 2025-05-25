"""Animation Module for SpritePro

This module provides advanced animation capabilities for sprites in the SpritePro framework.
It supports frame-based animations, smooth transitions, and parallel animations.

Key Features:
    - Frame-based animations with customizable frame duration
    - State management for different animation states
    - Smooth transitions using tweening
    - Parallel animation support
    - Callback system for animation events
    - Loop and one-shot animation modes

Classes:
    Animation: Main animation class that handles sprite animations

Example:
    ```python
    # Create a sprite
    sprite = Sprite("", (100, 100), (400, 300))
    
    # Create animation frames
    frames = []
    for i in range(8):
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Draw something on the frame
        frames.append(frame)
    
    # Create and start animation
    animation = Animation(sprite, frames=frames, frame_duration=100)
    animation.play()
    ```

Note:
    This module is designed to work with the SpritePro framework and requires
    a valid Sprite instance as the animation target.
"""

from typing import Dict, List, Optional, Tuple, Union, Callable
import pygame
import math
import time
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
import spritePro
from spritePro.components.tween import Tween, TweenManager, EasingType

class Animation:
    """Продвинутый компонент для анимации спрайтов.
    
    Поддерживает:
    - Последовательные анимации (список кадров)
    - Плавные переходы (tweening)
    - Управление состоянием
    - Обратные вызовы
    - Циклические и однократные анимации
    - Параллельные анимации
    """
    
    def __init__(
        self,
        owner_sprite,
        frames: Optional[List[pygame.Surface]] = None,
        frame_duration: int = 100,
        loop: bool = True,
        on_complete: Optional[Callable] = None,
        on_frame: Optional[Callable] = None
    ):
        """Инициализация анимации.
        
        Args:
            owner_sprite: Спрайт-владелец анимации
            frames: Список кадров анимации
            frame_duration: Длительность кадра в мс
            loop: Зациклить анимацию
            on_complete: Функция вызываемая при завершении
            on_frame: Функция вызываемая при смене кадра
        """
        self.owner = owner_sprite
        self.frames = frames or []
        self.frame_duration = frame_duration
        self.loop = loop
        self.on_complete = on_complete
        self.on_frame = on_frame
        
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.is_playing = False
        self.is_paused = False
        
        # Для плавных переходов
        self.tween_manager = TweenManager()
        
        # Параллельные анимации
        self.parallel_animations: List['Animation'] = []
        
        # Состояния анимации
        self.states: Dict[str, List[pygame.Surface]] = {}
        self.current_state = None
        
        # Устанавливаем первый кадр если есть
        if self.frames:
            self.owner.set_image(self.frames[0])
        
    def add_state(self, name: str, frames: List[pygame.Surface]) -> None:
        """Добавление состояния анимации.
        
        Args:
            name: Имя состояния
            frames: Кадры для состояния
        """
        self.states[name] = frames
        
    def set_state(self, name: str) -> None:
        """Установка текущего состояния.
        
        Args:
            name: Имя состояния
        """
        if name in self.states:
            self.current_state = name
            self.frames = self.states[name]
            self.current_frame = 0
            self.last_update = pygame.time.get_ticks()
            # Устанавливаем первый кадр нового состояния
            if self.frames:
                self.owner.set_image(self.frames[0])
            
    def play(self) -> None:
        """Запуск анимации."""
        self.is_playing = True
        self.is_paused = False
        self.last_update = pygame.time.get_ticks()
        
    def pause(self) -> None:
        """Пауза анимации."""
        self.is_paused = True
        self.tween_manager.pause_all()
        
    def resume(self) -> None:
        """Возобновление анимации."""
        self.is_paused = False
        self.last_update = pygame.time.get_ticks()
        self.tween_manager.resume_all()
        
    def stop(self) -> None:
        """Остановка анимации."""
        self.is_playing = False
        self.current_frame = 0
        self.tween_manager.stop_all()
        
    def reset(self) -> None:
        """Сброс анимации в начальное состояние."""
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        if self.frames:
            self.owner.set_image(self.frames[0])
        self.tween_manager.stop_all()
        
    def add_tween(
        self,
        name: str,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingType = EasingType.LINEAR,
        on_complete: Optional[Callable] = None,
        loop: bool = False,
        yoyo: bool = False,
        delay: float = 0,
        on_update: Optional[Callable[[float], None]] = None
    ) -> None:
        """Add a smooth transition (tween).
        
        Args:
            name: Name of the transition
            start_value: Initial value
            end_value: Target value
            duration: Duration in seconds
            easing: Type of easing (from EasingType)
            on_complete: Callback function called on completion
            loop: Whether to loop the transition
            yoyo: Whether to reverse the transition
            delay: Delay before starting in seconds
            on_update: Callback function called on each update
        """
        self.tween_manager.add_tween(
            name,
            start_value,
            end_value,
            duration,
            easing,
            on_complete,
            loop,
            yoyo,
            delay,
            on_update
        )
        
    def update_tween(self, name: str, dt: Optional[float] = None) -> Optional[float]:
        """Update a specific transition.
        
        Args:
            name: Name of the transition
            dt: Time since last update. If not specified, uses spritePro.dt
            
        Returns:
            Current value of the transition or None if completed
        """
        tween = self.tween_manager.get_tween(name)
        if tween:
            return tween.update(dt if dt is not None else spritePro.dt)
        return None
        
    def add_parallel_animation(self, animation: 'Animation') -> None:
        """Add a parallel animation.
        
        Args:
            animation: Animation to run in parallel
        """
        self.parallel_animations.append(animation)
        
    def update(self, dt: Optional[float] = None) -> None:
        """Update the animation.
        
        Args:
            dt: Time since last update. If not specified, uses spritePro.dt
        """
        if not self.is_playing or self.is_paused:
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = now
            
            # Set new frame
            if self.frames:
                self.owner.set_image(self.frames[self.current_frame])
            
            if self.on_frame:
                self.on_frame(self.current_frame)
                
            if self.current_frame == 0 and not self.loop:
                self.is_playing = False
                if self.on_complete:
                    self.on_complete()
                    
        # Update parallel animations
        for anim in self.parallel_animations:
            anim.update(dt if dt is not None else spritePro.dt)
            
        # Update all tweens
        self.tween_manager.update(dt if dt is not None else spritePro.dt)
                
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get the current animation frame.
        
        Returns:
            Current frame or None if no frames exist
        """
        if not self.frames:
            return None
        return self.frames[self.current_frame]
        
    def set_frame_duration(self, duration: int) -> None:
        """Set the duration of each frame.
        
        Args:
            duration: Duration in milliseconds
        """
        self.frame_duration = duration
        
    def set_loop(self, loop: bool) -> None:
        """Set whether the animation should loop.
        
        Args:
            loop: Whether to loop the animation
        """
        self.loop = loop


if __name__ == "__main__":    
    # Инициализация
    spritePro.init()
    screen = spritePro.get_screen((800, 600), "Animation Demo")
    
    # Создание спрайта
    sprite = spritePro.Sprite("", size=(100, 100), pos=(400, 300))
    
    # Создание кадров анимации для состояния walk (красные оттенки)
    walk_frames = []
    for i in range(8):
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        angle = i * 45
        # Рисуем прямоугольник с красным оттенком
        red_shade = 150 + int(105 * (i / 7))  # От 150 до 255
        pygame.draw.rect(frame, (red_shade, 0, 0), frame.get_rect(), 5)
        # Рисуем стрелку
        pygame.draw.line(frame, (255, 255, 255), (50, 50), 
                        (50 + 40 * math.cos(math.radians(angle)),
                         50 + 40 * math.sin(math.radians(angle))), 3)
        walk_frames.append(frame)
    
    # Создание кадров анимации для состояния idle (зеленые оттенки)
    idle_frames = []
    for i in range(4):
        frame = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Рисуем прямоугольник с зеленым оттенком
        green_shade = 100 + int(155 * (i / 3))  # От 100 до 255
        pygame.draw.rect(frame, (0, green_shade, 0), frame.get_rect(), 5)
        # Рисуем статичную стрелку
        pygame.draw.line(frame, (255, 255, 255), (50, 50), (90, 50), 3)
        idle_frames.append(frame)
    
    # Создание анимации
    animation = Animation(
        sprite,
        frames=idle_frames,  # Начинаем с idle состояния
        frame_duration=200,
        loop=True,
        on_frame=lambda frame: print(f"Frame: {frame}"),
        on_complete=lambda: print("Animation complete!")
    )
    
    # Добавление состояний
    animation.add_state("idle", idle_frames)
    animation.add_state("walk", walk_frames)
    
    # Добавление плавного перехода для масштаба
    animation.add_tween(
        "scale",
        start_value=1.0,
        end_value=1.5,
        duration=1.0,
        easing=EasingType.EASE_IN_OUT,
        loop=True,  # Зацикленный твин
        yoyo=True   # Движение туда-обратно
    )
    
    # Запуск анимации
    animation.play()
    animation.set_state("walk")  # Начинаем с walk состояния
    
    # Главный цикл
    while True:
        spritePro.update(fill_color=(0, 0, 0))
        
        # Обновление анимации
        animation.update()
        
        # Применение плавного перехода
        scale = animation.update_tween("scale")
        if scale is not None:
            sprite.set_scale(scale)
            
        # Обновление спрайта
        sprite.update(screen)
        
        # Обработка событий клавиатуры
        for event in spritePro.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if animation.current_state == "idle":
                    animation.set_state("walk")
                else:
                    animation.set_state("idle") 