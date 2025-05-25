# utils/advanced_timer.py

import time
from typing import Callable, Optional, Tuple, Dict


class Timer:
    """A universal timer based on system time polling.

    Features:
        - Call update() every frame with no parameters
        - Callback on timer completion (one-time or repeating)
        - Pause/resume/stop/reset functionality
        - Get remaining time, elapsed time, and progress

    Args:
        duration (float): Timer duration in seconds.
        callback (Optional[Callable]): Function to call when timer triggers. Can use args/kwargs.
        args (Tuple, optional): Positional arguments for callback. Defaults to ().
        kwargs (Dict, optional): Keyword arguments for callback. Defaults to {}.
        repeat (bool, optional): If True, timer automatically restarts after triggering. Defaults to False.
        autostart (bool, optional): If True, starts timer immediately on creation. Defaults to False.

    Attributes:
        duration (float): Timer interval.
        active (bool): True if timer is running and not paused.
        done (bool): True if timer is completed (and not repeating).
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
        """(Re)starts the timer.

        Args:
            duration (Optional[float]): New duration to set before starting. Defaults to None.
        """
        if duration is not None:
            self.duration = duration
        now = time.monotonic()
        self._start_time = now
        self._next_fire = now + self.duration
        self.active = True
        self.done = False

    def pause(self) -> None:
        """Pauses the timer, preserving remaining time."""
        if self.active and not self.done:
            # сохраним остаток
            self._remaining = max(self._next_fire - time.monotonic(), 0.0)
            self.active = False

    def resume(self) -> None:
        """Resumes the timer from pause, continuing with remaining time."""
        if not self.active and not self.done:
            now = time.monotonic()
            # восстановим возможность срабатывания через остаток
            self._next_fire = now + getattr(self, "_remaining", self.duration)
            self.active = True

    def stop(self) -> None:
        """Stops the timer and marks it as completed."""
        self.active = False
        self.done = True

    def reset(self) -> None:
        """Resets the timer state.

        If active, resets elapsed time to 0 and sets next trigger to duration seconds from now.
        If inactive, just clears the done flag.
        """
        if self.active:
            now = time.monotonic()
            self._start_time = now
            self._next_fire = now + self.duration
        else:
            # неактивный — просто сбросить done
            self.done = False

    def update(self) -> None:
        """Updates timer state, should be called every frame.

        If active and current time >= next_fire, executes callback and either:
        - Pauses/completes the timer (if not repeating)
        - Restarts the timer (if repeating)
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
        """Gets remaining time until trigger (>=0), excluding pauses.

        Returns:
            float: Remaining time in seconds, or 0 if timer is completed.
        """
        if self.done or not self.active or self._next_fire is None:
            return 0.0
        return max(self._next_fire - time.monotonic(), 0.0)

    def elapsed(self) -> float:
        """Gets elapsed time since last (re)start, excluding pauses.

        Returns:
            float: Elapsed time in seconds.
        """
        if self._start_time is None:
            return 0.0
        if not self.active and not self.done:
            # в паузе — duration - оставшееся
            return self.duration - getattr(self, "_remaining", self.duration)
        return min(time.monotonic() - self._start_time, self.duration)

    def progress(self) -> float:
        """Gets completion progress from 0.0 to 1.0.

        Returns:
            float: Progress value between 0.0 and 1.0.
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
