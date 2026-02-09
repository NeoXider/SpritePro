from typing import Optional, Callable, Dict, Any
import time
import math
from enum import IntFlag, auto
import sys
from pathlib import Path

from pygame.math import Vector2

import spritePro
from spritePro.sprite import SpriteSceneInput


def _is_scene_active(scene: SpriteSceneInput) -> bool:
    if scene is None:
        return True
    try:
        return spritePro.scene.is_scene_active(scene)
    except Exception:
        return True


class EasingType(IntFlag):
    """Типы функций плавности для анимаций.

    Attributes:
        LINEAR: Линейная функция плавности (без ускорения).
        EASE_IN: Плавность с ускорением в начале.
        EASE_OUT: Плавность с замедлением в конце.
        EASE_IN_OUT: Плавность с ускорением в начале и замедлением в конце.
        BOUNCE: Отскок (bounce эффект).
        ELASTIC: Упругая (elastic эффект).
        BACK: Откат назад (back эффект).
        CIRC: Круговая функция плавности.
        QUAD: Квадратичная функция плавности.
        CUBIC: Кубическая функция плавности.
        QUART: Функция плавности четвертой степени.
        QUINT: Функция плавности пятой степени.
        SINE: Синусоидальная функция плавности.
        EXPO: Экспоненциальная функция плавности.
    """

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
    """Базовый класс для плавных переходов между значениями.

    Предоставляет функциональность для:
    - Плавных переходов между начальным и конечным значениями
    - Различных функций плавности для разных стилей анимации
    - Эффектов зацикливания и yoyo
    - Обратных вызовов для обновлений и завершения
    - Функциональности паузы и возобновления
    - Отслеживания прогресса

    Attributes:
        start_value (float): Начальное значение перехода.
        end_value (float): Конечное значение перехода.
        duration (float): Общая длительность перехода в секундах.
        easing (Callable): Функция плавности для использования.
        loop (bool): Должен ли переход зацикливаться.
        yoyo (bool): Должен ли переход обращаться при зацикливании.
        on_update (Optional[Callable[[float], None]]): Функция обратного вызова для обновлений значения.
        on_complete (Optional[Callable]): Функция обратного вызова при завершении перехода.
        delay (float): Задержка перед началом перехода в секундах.
        current_value (float): Текущее значение перехода.
        is_playing (bool): Воспроизводится ли переход.
        is_paused (bool): Находится ли переход на паузе.
    """

    # Словарь доступных функций плавности
    EASING_FUNCTIONS = {
        EasingType.LINEAR: lambda x: x,
        EasingType.EASE_IN: lambda x: x * x,
        EasingType.EASE_OUT: lambda x: 1 - (1 - x) * (1 - x),
        EasingType.EASE_IN_OUT: lambda x: 3 * x * x - 2 * x * x * x,
        EasingType.BOUNCE: lambda x: 1 - (math.cos(x * 4.5 * math.pi) * math.exp(-x * 3))
        if x < 1
        else 1,
        EasingType.ELASTIC: lambda x: math.sin(x * 13 * math.pi) * math.exp(-x * 3) if x < 1 else 0,
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
        start_value: Any,
        end_value: Any,
        duration: float,
        easing: EasingType = EasingType.LINEAR,
        on_complete: Optional[Callable] = None,
        loop: bool = False,
        yoyo: bool = False,
        delay: float = 0,
        on_update: Optional[Callable[[Any], None]] = None,
        auto_start: bool = True,
        auto_register: bool = True,
        value_type: Optional[str] = None,
        scene: SpriteSceneInput = None,
    ):
        """Инициализирует переход.

        Args:
            start_value (Any): Начальное значение (float, Vector2, tuple/list, color).
            end_value (Any): Конечное значение.
            duration (float): Длительность в секундах.
            easing (EasingType, optional): Тип плавности (из EasingType). По умолчанию EasingType.LINEAR.
            on_complete (Optional[Callable], optional): Функция, вызываемая при завершении. По умолчанию None.
            loop (bool, optional): Зациклить переход. По умолчанию False.
            yoyo (bool, optional): Двигаться туда-обратно. По умолчанию False.
            delay (float, optional): Задержка перед началом в секундах. По умолчанию 0.
            on_update (Optional[Callable[[Any], None]], optional): Функция, вызываемая при обновлении значения. По умолчанию None.
            auto_start (bool, optional): Автоматически запускать переход при создании. По умолчанию True.
            auto_register (bool, optional): Автоматически регистрировать твин для обновления в spritePro.update(). По умолчанию True.
            value_type (Optional[str], optional): Тип значения ("vector2", "vector3", "color") или None (авто). По умолчанию None.
            scene (Scene | str, optional): Сцена, в которой активен твин. По умолчанию None.
        """
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = self.EASING_FUNCTIONS.get(easing, self.EASING_FUNCTIONS[EasingType.LINEAR])
        self.on_complete = on_complete
        self.loop = loop
        self.yoyo = yoyo
        self.delay = delay
        self.on_update = on_update
        self.value_type = value_type
        self.scene = scene

        self.start_time = time.time()
        self.current_value = start_value
        self.is_playing = auto_start
        self.is_paused = False
        self.pause_time = 0
        self.direction = 1  # 1 для движения вперед, -1 для движения назад

        # Автоматическая регистрация для обновления
        if auto_register:
            try:
                spritePro.register_update_object(self)
            except (ImportError, AttributeError):
                pass

    def update(self, dt: Optional[float] = None) -> Optional[Any]:
        """Обновляет переход.

        Args:
            dt (Optional[float], optional): Время с последнего обновления.
                Если не указано, берется из spritePro.dt. По умолчанию None.

        Returns:
            Optional[Any]: Текущее значение или None, если завершен.
        """
        if not self.is_playing or self.is_paused:
            return self.current_value
        if not _is_scene_active(self.scene):
            return self.current_value

        if dt is None:
            try:
                dt = getattr(spritePro, "dt", None)
            except AttributeError:
                dt = None

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
                self.current_value = self._lerp_value(self.start_value, self.end_value, 1.0)
                if self.on_update:
                    self.on_update(self.current_value)
                if self.on_complete:
                    self.on_complete()
                return None

        progress = elapsed / self.duration
        eased = self.easing(progress)

        self.current_value = self._lerp_value(self.start_value, self.end_value, eased)

        if self.on_update:
            self.on_update(self.current_value)

        return self.current_value

    def _lerp_value(self, start: Any, end: Any, t: float) -> Any:
        """Интерполирует значение с учетом типа tween."""
        if self.value_type == "color":
            return self._lerp_color(start, end, t)
        if self.value_type == "vector2":
            return Vector2(start).lerp(Vector2(end), t)
        if self.value_type == "vector3":
            return self._lerp_sequence(start, end, t)

        if isinstance(start, Vector2) or isinstance(end, Vector2):
            return Vector2(start).lerp(Vector2(end), t)
        if self._is_sequence(start) and self._is_sequence(end):
            if self._looks_like_color(start, end):
                return self._lerp_color(start, end, t)
            return self._lerp_sequence(start, end, t)

        try:
            return start + (end - start) * t
        except Exception:
            return end if t >= 1.0 else start

    @staticmethod
    def _is_sequence(value: Any) -> bool:
        """Проверяет, является ли значение последовательностью."""
        return isinstance(value, (list, tuple)) and len(value) >= 2

    @staticmethod
    def _looks_like_color(start: Any, end: Any) -> bool:
        """Проверяет, похожи ли значения на RGB-цвет."""
        if not (isinstance(start, (list, tuple)) and isinstance(end, (list, tuple))):
            return False
        if len(start) != 3 or len(end) != 3:
            return False
        for v in start + end:
            if not isinstance(v, int):
                return False
            if v < 0 or v > 255:
                return False
        return True

    @staticmethod
    def _lerp_sequence(start: Any, end: Any, t: float) -> tuple:
        """Интерполирует последовательность чисел поэлементно."""
        return tuple(s + (e - s) * t for s, e in zip(start, end))

    @staticmethod
    def _lerp_color(start: Any, end: Any, t: float) -> tuple[int, int, int]:
        """Интерполирует RGB-цвет с ограничением диапазона."""
        result = []
        for s, e in zip(start, end):
            value = s + (e - s) * t
            result.append(int(max(0, min(255, round(value)))))
        return tuple(result)  # type: ignore[return-value]

    def pause(self) -> None:
        """Ставит переход на паузу."""
        if not self.is_paused:
            self.is_paused = True
            self.pause_time = time.time()

    def resume(self) -> None:
        """Возобновляет переход с паузы."""
        if self.is_paused:
            self.is_paused = False
            self.start_time += time.time() - self.pause_time

    def stop(self, apply_end: bool = True) -> None:
        """Останавливает переход.

        Args:
            apply_end (bool, optional): Применить конечное значение при остановке.
                По умолчанию True.
        """
        self.is_playing = False
        if apply_end:
            self.current_value = self._lerp_value(self.start_value, self.end_value, 1.0)
            if self.on_update:
                self.on_update(self.current_value)

    def start(self) -> None:
        """Запускает переход."""
        self.start_time = time.time()
        self.is_playing = True
        self.is_paused = False

    def reset(self, apply_end: bool = False) -> None:
        """Сбрасывает переход в начальное состояние.

        Args:
            apply_end (bool, optional): Применить конечное значение перед сбросом.
                По умолчанию False.
        """
        if apply_end:
            self.current_value = self._lerp_value(self.start_value, self.end_value, 1.0)
            if self.on_update:
                self.on_update(self.current_value)
        self.start_time = time.time()
        self.current_value = self.start_value
        self.is_playing = True
        self.is_paused = False
        self.direction = 1

    def get_progress(self) -> float:
        """Получает прогресс перехода (0-1).

        Returns:
            float: Прогресс перехода от 0 до 1.
        """
        if not self.is_playing:
            return 1.0 if self.current_value == self.end_value else 0.0

        now = time.time()
        elapsed = now - self.start_time - self.delay

        if elapsed < 0:
            return 0.0

        return min(1.0, elapsed / self.duration)


class TweenManager:
    """Менеджер для обработки нескольких переходов одновременно.

    Предоставляет функциональность для:
    - Управления несколькими переходами
    - Групповых операций (пауза, возобновление, остановка)
    - Автоматической очистки завершенных переходов
    - Независимого управления каждым переходом
    - Отслеживания прогресса для всех переходов

    Attributes:
        tweens (Dict[str, Tween]): Словарь активных переходов.
    """

    def __init__(self, auto_register: bool = True, scene: SpriteSceneInput = None):
        """Инициализирует менеджер переходов.

        Args:
            auto_register (bool, optional): Если True, автоматически регистрирует менеджер для обновления в spritePro.update(). По умолчанию True.
            scene (Scene | str, optional): Сцена, в которой активен менеджер. По умолчанию None.
        """
        self.tweens: Dict[str, Tween] = {}
        self.scene = scene

        # Автоматическая регистрация для обновления
        if auto_register:
            try:
                spritePro.register_update_object(self)
            except (ImportError, AttributeError):
                pass

    def add_tween(
        self,
        name: str,
        start_value: Any,
        end_value: Any,
        duration: float,
        easing: EasingType = EasingType.LINEAR,
        on_complete: Optional[Callable] = None,
        loop: bool = False,
        yoyo: bool = False,
        delay: float = 0,
        on_update: Optional[Callable[[Any], None]] = None,
        auto_start: bool = True,
        value_type: Optional[str] = None,
    ) -> None:
        """Добавляет новый переход.

        Args:
            name (str): Имя перехода.
            start_value (Any): Начальное значение.
            end_value (Any): Конечное значение.
            duration (float): Длительность в секундах.
            easing (EasingType, optional): Тип плавности (из EasingType). По умолчанию EasingType.LINEAR.
            on_complete (Optional[Callable], optional): Функция, вызываемая при завершении. По умолчанию None.
            loop (bool, optional): Зациклить переход. По умолчанию False.
            yoyo (bool, optional): Двигаться туда-обратно. По умолчанию False.
            delay (float, optional): Задержка перед началом. По умолчанию 0.
            on_update (Optional[Callable[[Any], None]], optional): Функция, вызываемая при обновлении. По умолчанию None.
            auto_start (bool, optional): Автоматически запускать переход при создании. По умолчанию True.
            value_type (Optional[str], optional): Тип значения ("vector2", "vector3", "color") или None. По умолчанию None.
        """
        # Твины в менеджере не регистрируются отдельно - они обновляются через менеджер
        tween = Tween(
            start_value,
            end_value,
            duration,
            easing,
            on_complete,
            loop,
            yoyo,
            delay,
            on_update,
            auto_start,
            value_type=value_type,
            auto_register=False,  # Твины в менеджере не регистрируются отдельно
            scene=self.scene,
        )
        self.tweens[name] = tween

    def update(self, dt: Optional[float] = None) -> None:
        """Обновляет все переходы.

        Args:
            dt (Optional[float], optional): Время с последнего обновления.
                Если не указано, берется из spritePro.dt. По умолчанию None.
        """
        if not _is_scene_active(self.scene):
            return
        # Если dt не передан, пытаемся взять из spritePro.dt
        if dt is None:
            try:
                dt = getattr(spritePro, "dt", None)
            except AttributeError:
                dt = None

        for name in list(self.tweens.keys()):
            value = self.tweens[name].update(dt)
            if value is None:
                # del self.tweens[name]
                pass

    def get_tween(self, name: str) -> Optional[Tween]:
        """Получает переход по имени.

        Args:
            name (str): Имя перехода.

        Returns:
            Optional[Tween]: Переход или None, если не найден.
        """
        return self.tweens.get(name)

    def remove_tween(self, name: str, apply_end: bool = True) -> None:
        """Удаляет переход.

        Args:
            name (str): Имя перехода.
            apply_end (bool, optional): Применить конечное значение при удалении.
                По умолчанию True.
        """
        if name in self.tweens:
            self.tweens[name].stop(apply_end=apply_end)
            del self.tweens[name]

    def start_tween(self, name: str) -> None:
        """Запускает переход по имени.

        Args:
            name (str): Имя перехода.
        """
        if name in self.tweens:
            self.tweens[name].start()

    def start_all(self, apply_end: bool = False) -> None:
        """Запускает все переходы.

        Args:
            apply_end (bool, optional): Применить конечное значение перед стартом.
                По умолчанию False.
        """
        for tween in self.tweens.values():
            tween.reset(apply_end=apply_end)
            tween.start()

    def pause_all(self) -> None:
        """Ставит все переходы на паузу."""
        for tween in self.tweens.values():
            tween.pause()

    def resume_all(self) -> None:
        """Возобновляет все переходы с паузы."""
        for tween in self.tweens.values():
            tween.resume()

    def stop_all(self, apply_end: bool = True) -> None:
        """Останавливает все переходы и очищает словарь.

        Args:
            apply_end (bool, optional): Применить конечные значения у всех твинов.
                По умолчанию True.
        """
        for tween in self.tweens.values():
            tween.stop(apply_end=apply_end)
        self.tweens.clear()

    def reset_all(self, apply_end: bool = False) -> None:
        """Сбрасывает все переходы в начальное состояние.

        Args:
            apply_end (bool, optional): Применить конечное значение перед сбросом.
                По умолчанию False.
        """
        for tween in self.tweens.values():
            tween.reset(apply_end=apply_end)


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
    instructions = font.render("Press SPACE to pause/resume, ESC to exit", True, (255, 255, 255))
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
        for event in spritePro.pygame_events:
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
