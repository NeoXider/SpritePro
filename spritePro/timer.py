# utils/advanced_timer.py

import time
from typing import Callable, Optional, Tuple, Dict


class Timer:
    """
    Универсальный таймер на основе поллинга времени системы.

    Особенности:
      • Вызывать update() каждый кадр ― ничего не передавать.
      • Колбэк по истечении времени (однократный или повторяемый).
      • Пауза / возобновление / остановка / сброс.
      • Получение оставшегося и прошедшего времени, прогресса.

    Args:
        duration (float):
            Продолжительность таймера в секундах.
        callback (Optional[Callable]):
            Функция, вызываемая при срабатывании. Аргументы можно задать через args/kwargs.
        args (Tuple, optional):
            Позиционные аргументы для callback.
        kwargs (Dict, optional):
            Именованные аргументы для callback.
        repeat (bool, optional):
            Если True, после срабатывания таймер автоматически перезапускается.
        autostart (bool, optional):
            Если True, запускает таймер сразу при создании.

    Attributes:
        duration (float): Интервал таймера.
        active (bool): True, если таймер запущен и не на паузе.
        done (bool): True, если таймер завершён (и не повторяется).
    """

    def __init__(
        self,
        duration: float,
        callback: Optional[Callable] = None,
        args: Tuple = (),
        kwargs: Dict = None,
        repeat: bool = False,
        autostart: bool = False,
    ):
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

    def start(self, duration: Optional[float] = None) -> None:
        """
        (Re)запустить таймер.

        Args:
            duration (Optional[float]): Заменить длительность перед стартом.
        """
        if duration is not None:
            self.duration = duration
        now = time.monotonic()
        self._start_time = now
        self._next_fire = now + self.duration
        self.active = True
        self.done = False

    def pause(self) -> None:
        """Поставить таймер на паузу."""
        if self.active and not self.done:
            # сохраним остаток
            self._remaining = max(self._next_fire - time.monotonic(), 0.0)
            self.active = False

    def resume(self) -> None:
        """Снять таймер с паузы, продолжить с того же остатка."""
        if not self.active and not self.done:
            now = time.monotonic()
            # восстановим возможность срабатывания через остаток
            self._next_fire = now + getattr(self, "_remaining", self.duration)
            self.active = True

    def stop(self) -> None:
        """Остановить таймер и пометить как завершённый."""
        self.active = False
        self.done = True

    def reset(self) -> None:
        """
        Сбросить таймер: вернуть elapsed=0 и перенести точку срабатывания
        на duration секунд от текущего момента (если active) или оставить
        в неактивном состоянии.
        """
        if self.active:
            now = time.monotonic()
            self._start_time = now
            self._next_fire = now + self.duration
        else:
            # неактивный — просто сбросить done
            self.done = False

    def update(self) -> None:
        """
        Вызывать каждый кадр. Если активен и текущее
        время >= next_fire, выполняет callback и переводит в paused/done
        или перезапускает (если repeat=True).
        """
        if not self.active or self.done:
            return

        now = time.monotonic()
        if now >= (self._next_fire or 0):
            # срабатывание
            if self.callback:
                self.callback(*self.args, **self.kwargs)

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
        """
        Оставшееся время до срабатывания (>=0), без пауз.
        Если таймер завершён, возвращает 0.
        """
        if self.done or not self.active or self._next_fire is None:
            return 0.0
        return max(self._next_fire - time.monotonic(), 0.0)

    def elapsed(self) -> float:
        """
        Прошедшее время с последнего (re)start() без учёта пауз.
        """
        if self._start_time is None:
            return 0.0
        if not self.active and not self.done:
            # в паузе — duration - оставшееся
            return self.duration - getattr(self, "_remaining", self.duration)
        return min(time.monotonic() - self._start_time, self.duration)

    def progress(self) -> float:
        """
        Доля завершённости от 0.0 до 1.0.
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
