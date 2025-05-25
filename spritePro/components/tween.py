from typing import Optional, Callable, Dict, Any
import time
import math
from enum import IntFlag, auto
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
import spritePro


class EasingType(IntFlag):
    """Типы функций плавности."""

    LINEAR = auto()
    EASE_IN = auto()
    EASE_OUT = auto()
    EASE_IN_OUT = auto()
    BOUNCE = auto()
    ELASTIC = auto()
    BACK = auto()
    CIRC = auto()
    QUAD = auto()
    CUBIC = auto()
    QUART = auto()
    QUINT = auto()
    SINE = auto()
    EXPO = auto()


class Tween:
    """Base tween class for smooth transitions between values.

    This class provides functionality for:
    - Smooth transitions between start and end values
    - Various easing functions for different animation styles
    - Looping and yoyo effects
    - Callbacks for updates and completion
    - Pause and resume functionality
    - Progress tracking

    Attributes:
        start_value (float): Initial value of the transition.
        end_value (float): Target value of the transition.
        duration (float): Total duration of the transition in seconds.
        easing (EasingType): Type of easing function to use.
        loop (bool): Whether the tween should loop.
        yoyo (bool): Whether the tween should reverse direction when looping.
        on_update (Callable): Callback function for value updates.
        on_complete (Callable): Callback function when tween completes.
        delay (float): Delay before tween starts in seconds.
    """

    # Словарь доступных функций плавности
    EASING_FUNCTIONS = {
        EasingType.LINEAR: lambda x: x,
        EasingType.EASE_IN: lambda x: x * x,
        EasingType.EASE_OUT: lambda x: 1 - (1 - x) * (1 - x),
        EasingType.EASE_IN_OUT: lambda x: 3 * x * x - 2 * x * x * x,
        EasingType.BOUNCE: lambda x: 1
        - (math.cos(x * 4.5 * math.pi) * math.exp(-x * 3))
        if x < 1
        else 1,
        EasingType.ELASTIC: lambda x: math.sin(x * 13 * math.pi) * math.exp(-x * 3)
        if x < 1
        else 0,
        EasingType.BACK: lambda x: x * x * (2.70158 * x - 1.70158),
        EasingType.CIRC: lambda x: 1 - math.sqrt(1 - x * x),
        EasingType.QUAD: lambda x: x * x,
        EasingType.CUBIC: lambda x: x * x * x,
        EasingType.QUART: lambda x: x * x * x * x,
        EasingType.QUINT: lambda x: x * x * x * x * x,
        EasingType.SINE: lambda x: 1 - math.cos(x * math.pi / 2),
        EasingType.EXPO: lambda x: 0 if x == 0 else math.pow(2, 10 * (x - 1)),
    }

    def __init__(
        self,
        start_value: float,
        end_value: float,
        duration: float,
        easing: EasingType = EasingType.LINEAR,
        on_complete: Optional[Callable] = None,
        loop: bool = False,
        yoyo: bool = False,
        delay: float = 0,
        on_update: Optional[Callable[[float], None]] = None,
    ):
        """Инициализация перехода.

        Args:
            start_value: Начальное значение
            end_value: Конечное значение
            duration: Длительность в секундах
            easing: Тип плавности (из EasingType)
            on_complete: Функция вызываемая при завершении
            loop: Зациклить переход
            yoyo: Двигаться туда-обратно
            delay: Задержка перед началом в секундах
            on_update: Функция вызываемая при обновлении значения
        """
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = self.EASING_FUNCTIONS.get(
            easing, self.EASING_FUNCTIONS[EasingType.LINEAR]
        )
        self.on_complete = on_complete
        self.loop = loop
        self.yoyo = yoyo
        self.delay = delay
        self.on_update = on_update

        self.start_time = time.time()
        self.current_value = start_value
        self.is_playing = True
        self.is_paused = False
        self.pause_time = 0
        self.direction = 1  # 1 для движения вперед, -1 для движения назад

    def update(self, dt: Optional[float] = None) -> Optional[float]:
        """Обновление перехода.

        Args:
            dt: Время с последнего обновления

        Returns:
            Текущее значение или None если завершен
        """
        if not self.is_playing or self.is_paused:
            return self.current_value

        now = time.time()
        elapsed = now - self.start_time - self.delay

        if elapsed < 0:  # Ожидаем задержку
            return self.start_value

        if elapsed >= self.duration:
            if self.loop:
                if self.yoyo:
                    self.direction *= -1
                    self.start_time = now
                    self.start_value, self.end_value = self.end_value, self.start_value
                else:
                    self.start_time = now
                return self.end_value
            else:
                self.is_playing = False
                self.current_value = self.end_value
                if self.on_complete:
                    self.on_complete()
                return None

        progress = elapsed / self.duration
        eased = self.easing(progress)

        self.current_value = (
            self.start_value + (self.end_value - self.start_value) * eased
        )

        if self.on_update:
            self.on_update(self.current_value)

        return self.current_value

    def pause(self) -> None:
        """Пауза перехода."""
        if not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()

    def resume(self) -> None:
        """Возобновление перехода."""
        if self.is_paused:
            self.is_paused = False
            self.start_time += time.time() - self.pause_time

    def stop(self) -> None:
        """Остановка перехода."""
        self.is_playing = False

    def reset(self) -> None:
        """Сброс перехода в начальное состояние."""
        self.start_time = time.time()
        self.current_value = self.start_value
        self.is_playing = True
        self.is_paused = False
        self.direction = 1

    def get_progress(self) -> float:
        """Получение прогресса перехода (0-1).

        Returns:
            Прогресс перехода от 0 до 1
        """
        if not self.is_playing:
            return 1.0 if self.current_value == self.end_value else 0.0

        now = time.time()
        elapsed = now - self.start_time - self.delay

        if elapsed < 0:
            return 0.0

        return min(1.0, elapsed / self.duration)


class TweenManager:
    """Manager class for handling multiple tweens simultaneously.

    This class provides functionality for:
    - Managing multiple tweens
    - Group operations (pause, resume, stop)
    - Automatic cleanup of completed tweens
    - Independent control of each tween
    - Progress tracking for all tweens

    Attributes:
        tweens (Dict[str, Tween]): Dictionary of active tweens.
        paused (bool): Whether all tweens are paused.
    """

    def __init__(self):
        """Инициализация менеджера переходов."""
        self.tweens: Dict[str, Tween] = {}

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
        on_update: Optional[Callable[[float], None]] = None,
    ) -> None:
        """Добавление нового перехода.

        Args:
            name: Имя перехода
            start_value: Начальное значение
            end_value: Конечное значение
            duration: Длительность в секундах
            easing: Тип плавности (из EasingType)
            on_complete: Функция вызываемая при завершении
            loop: Зациклить переход
            yoyo: Двигаться туда-обратно
            delay: Задержка перед началом
            on_update: Функция вызываемая при обновлении
        """
        self.tweens[name] = Tween(
            start_value,
            end_value,
            duration,
            easing,
            on_complete,
            loop,
            yoyo,
            delay,
            on_update,
        )

    def update(self, dt: Optional[float] = None) -> None:
        """Обновление всех переходов.

        Args:
            dt: Время с последнего обновления
        """
        for name in list(self.tweens.keys()):
            value = self.tweens[name].update(dt)
            if value is None:
                del self.tweens[name]

    def get_tween(self, name: str) -> Optional[Tween]:
        """Получение перехода по имени.

        Args:
            name: Имя перехода

        Returns:
            Переход или None если не найден
        """
        return self.tweens.get(name)

    def remove_tween(self, name: str) -> None:
        """Удаление перехода.

        Args:
            name: Имя перехода
        """
        if name in self.tweens:
            del self.tweens[name]

    def pause_all(self) -> None:
        """Пауза всех переходов."""
        for tween in self.tweens.values():
            tween.pause()

    def resume_all(self) -> None:
        """Возобновление всех переходов."""
        for tween in self.tweens.values():
            tween.resume()

    def stop_all(self) -> None:
        """Остановка всех переходов."""
        for tween in self.tweens.values():
            tween.stop()
        self.tweens.clear()


if __name__ == "__main__":
    import pygame
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent.parent
    sys.path.append(str(parent_dir))
    import spritePro

    # Инициализация
    spritePro.init()

    screen = spritePro.get_screen((800, 800), "Tween Demo")

    # Создание спрайтов для демонстрации разных типов плавности
    sprites = []
    tween_manager = TweenManager()

    # Создаем спрайты для каждого типа плавности
    y_pos = 50
    for easing_type in EasingType:
        # Создаем спрайт с кругом
        sprite = spritePro.Sprite("", size=(50, 50), pos=(100, y_pos))
        # Создаем поверхность с кругом
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 255, 255), (25, 25), 20)
        sprite.set_image(surface)
        sprites.append(sprite)

        # Добавляем твин для движения спрайта
        tween_manager.add_tween(
            f"move_{easing_type.name}",
            start_value=100,
            end_value=700,
            duration=2.0,
            easing=easing_type,
            loop=True,
            yoyo=True,
            on_update=lambda x, s=sprite: setattr(s.rect, "x", int(x)),
        )

        # Добавляем твин для изменения цвета
        tween_manager.add_tween(
            f"color_{easing_type.name}",
            start_value=0,
            end_value=255,
            duration=2.0,
            easing=easing_type,
            loop=True,
            yoyo=True,
            on_update=lambda x, s=sprite: s.set_color(
                (max(0, min(255, int(x))), max(0, min(255, int(255 - x))), 0)
            ),
        )

        y_pos += 60

    # Создаем текст для отображения названий типов плавности
    font = pygame.font.Font(None, 24)
    texts = []
    y_pos = 50
    for easing_type in EasingType:
        text = font.render(easing_type.name, True, (255, 255, 255))
        texts.append((text, (20, y_pos + 15)))
        y_pos += 60

    # Добавляем инструкции
    instructions = font.render(
        "Press SPACE to pause/resume, ESC to exit", True, (255, 255, 255)
    )
    instructions_pos = (screen.get_width() // 2 - instructions.get_width() // 2, 10)

    paused = False

    # Главный цикл
    while True:
        spritePro.update(fill_color=(0, 0, 0))

        # Обновляем все твины
        if not paused:
            tween_manager.update(spritePro.dt)

        # Рисуем линии траектории
        y_pos = 50
        for _ in EasingType:
            # Рисуем линию траектории
            pygame.draw.line(
                screen,
                (50, 50, 50),  # Темно-серый цвет для линий
                (100, y_pos + 25),  # Начало линии (центр начальной позиции спрайта)
                (700, y_pos + 25),  # Конец линии (центр конечной позиции спрайта)
                2,  # Толщина линии
            )
            y_pos += 60

        # Обновляем спрайты
        for sprite in sprites:
            sprite.update(screen)

        # Отображаем названия типов плавности
        for text, pos in texts:
            screen.blit(text, pos)

        # Отображаем инструкции
        screen.blit(instructions, instructions_pos)

        # Обработка событий
        for event in spritePro.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        tween_manager.pause_all()
                    else:
                        tween_manager.resume_all()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
