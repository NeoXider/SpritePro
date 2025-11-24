# utils/advanced_timer.py

import time
from typing import Callable, Optional, Tuple, Dict


class Timer:
    """Универсальный таймер на основе опроса системного времени.

    Возможности:
        - Вызов update() каждый кадр без параметров
        - Обратный вызов при завершении таймера (однократный или повторяющийся)
        - Функциональность паузы/возобновления/остановки/сброса
        - Получение оставшегося времени, прошедшего времени и прогресса

    Attributes:
        duration (float): Длительность таймера в секундах.
        callback (Optional[Callable]): Функция, вызываемая при срабатывании таймера. Может использовать args/kwargs.
        args (Tuple): Позиционные аргументы для обратного вызова.
        kwargs (Dict): Именованные аргументы для обратного вызова.
        repeat (bool): Если True, таймер автоматически перезапускается после срабатывания.
        active (bool): True, если таймер запущен и не на паузе.
        done (bool): True, если таймер завершен (и не повторяется).
    """

    def __init__(
        self,
        duration: float,
        callback: Optional[Callable] = None,
        args: Tuple = (),
        kwargs: Dict = None,
        repeat: bool = False,
        autostart: bool = True,
        auto_register: bool = True,
    ):
        """Инициализирует таймер.

        Args:
            duration (float): Длительность таймера в секундах.
            callback (Optional[Callable], optional): Функция, вызываемая при срабатывании таймера. Может использовать args/kwargs. По умолчанию None.
            args (Tuple, optional): Позиционные аргументы для обратного вызова. По умолчанию ().
            kwargs (Dict, optional): Именованные аргументы для обратного вызова. По умолчанию {}.
            repeat (bool, optional): Если True, таймер автоматически перезапускается после срабатывания. По умолчанию False.
            autostart (bool, optional): Если True, запускает таймер сразу при создании. По умолчанию True.
            auto_register (bool, optional): Если True, автоматически регистрирует таймер для обновления в spritePro.update(). По умолчанию True.
        """
        self.duration = duration
        self.callback = callback
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.repeat = repeat

        self.active = False
        self.done = False

        self._start_time: Optional[float] = None
        self._next_fire: Optional[float] = None

        if autostart:
            self.start()
        
        # Автоматическая регистрация для обновления
        if auto_register:
            try:
                import spritePro
                spritePro.register_update_object(self)
            except (ImportError, AttributeError):
                pass

    def start(self, duration: Optional[float] = None) -> None:
        """(Пере)запускает таймер.

        Args:
            duration (Optional[float], optional): Новая длительность для установки перед запуском. По умолчанию None.
        """
        if duration is not None:
            self.duration = duration
        now = time.monotonic()
        self._start_time = now
        self._next_fire = now + self.duration
        self.active = True
        self.done = False

    def pause(self) -> None:
        """Ставит таймер на паузу, сохраняя оставшееся время."""
        if self.active and not self.done:
            # сохраним остаток
            self._remaining = max(self._next_fire - time.monotonic(), 0.0)
            self.active = False

    def resume(self) -> None:
        """Возобновляет таймер с паузы, продолжая с оставшимся временем."""
        if not self.active and not self.done:
            now = time.monotonic()
            # восстановим возможность срабатывания через остаток
            self._next_fire = now + getattr(self, "_remaining", self.duration)
            self.active = True

    def stop(self) -> None:
        """Останавливает таймер и помечает его как завершенный."""
        self.active = False
        self.done = True

    def reset(self) -> None:
        """Сбрасывает состояние таймера.

        Если активен, сбрасывает прошедшее время до 0 и устанавливает следующее срабатывание
        на duration секунд от текущего момента.
        Если неактивен, просто очищает флаг done.
        """
        if self.active:
            now = time.monotonic()
            self._start_time = now
            self._next_fire = now + self.duration
        else:
            # неактивный — просто сбросить done
            self.done = False

    def update(self) -> None:
        """Обновляет состояние таймера, должен вызываться каждый кадр.

        Если активен и текущее время >= next_fire, выполняет обратный вызов и либо:
        - Ставит на паузу/завершает таймер (если не повторяется)
        - Перезапускает таймер (если повторяется)
        """
        if not self.active or self.done:
            return

        now = time.monotonic()
        if now >= (self._next_fire or 0):
            old_next_fire = self._next_fire
            # срабатывание
            if self.callback:
                self.callback(*self.args, **self.kwargs)

            if old_next_fire != self._next_fire:
                return

            if self.repeat:
                # запланировать следующее срабатывание, учитывая «проскоченные» интервалы
                # (вдруг update вызывали с долгим лагом)
                cycles = int((now - self._start_time) // self.duration) + 1
                self._start_time += self.duration * cycles
                self._next_fire = self._start_time + self.duration
            else:
                self.done = True
                self.active = False

    def time_left(self) -> float:
        """Получает оставшееся время до срабатывания (>=0), исключая паузы.

        Returns:
            float: Оставшееся время в секундах или 0, если таймер завершен.
        """
        if self.done or not self.active or self._next_fire is None:
            return 0.0
        return max(self._next_fire - time.monotonic(), 0.0)

    def elapsed(self) -> float:
        """Получает прошедшее время с последнего (пере)запуска, исключая паузы.

        Returns:
            float: Прошедшее время в секундах.
        """
        if self._start_time is None:
            return 0.0
        if not self.active and not self.done:
            # в паузе — duration - оставшееся
            return self.duration - getattr(self, "_remaining", self.duration)
        return min(time.monotonic() - self._start_time, self.duration)

    def progress(self) -> float:
        """Получает прогресс завершения от 0.0 до 1.0.

        Returns:
            float: Значение прогресса от 0.0 до 1.0.
        """
        return min((self.duration - self.time_left()) / self.duration, 1.0)


if __name__ == "__main__":

    def say_hello():
        print("Hello at", time.strftime("%H:%M:%S"))

    t1 = Timer(3.0, callback=say_hello, autostart=True)

    t2 = Timer(1.0, callback=lambda: print("Tick"), repeat=True, autostart=True)

    while True:
        t1.update()
        t2.update()
