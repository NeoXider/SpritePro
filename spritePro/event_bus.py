from __future__ import annotations

from typing import Callable, Dict, List, Any


class _SignalBase:
    """Базовый сигнал с локальным списком обработчиков."""

    def __init__(self) -> None:
        self._handlers: List[Callable[..., Any]] = []

    def connect(self, handler: Callable[..., Any]) -> None:
        """Подписывает обработчик на сигнал.

        Args:
            handler (Callable[..., Any]): Функция-обработчик события.
        """
        if handler not in self._handlers:
            self._handlers.append(handler)

    def disconnect(self, handler: Callable[..., Any] | None = None) -> None:
        """Отписывает обработчик или очищает все подписки.

        Args:
            handler (Callable[..., Any] | None): Обработчик для удаления. Если None,
                удаляются все подписки.
        """
        if handler is None:
            self._handlers.clear()
            return
        try:
            self._handlers.remove(handler)
        except ValueError:
            pass

    def send(self, **payload: Any) -> None:
        """Вызывает всех подписчиков сигнала.

        Args:
            **payload: Именованные параметры, передаваемые в обработчики.
        """
        handlers = list(self._handlers)
        for handler in handlers:
            try:
                handler(**payload)
            except Exception:
                continue

    def __call__(self, **payload: Any) -> None:
        """Короткая форма для send()."""
        self.send(**payload)


class EventSignal(_SignalBase):
    """Именованный сигнал, управляемый EventBus."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        """Имя события, на которое подписываются обработчики."""
        return self._name


class GlobalEvents:
    """Список глобальных событий, публикуемых библиотекой."""

    QUIT = "quit"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    TICK = "tick"


class LocalEvent(_SignalBase):
    """Локальное событие, живущее в переменной."""


class EventBus:
    """EventBus для именованных событий с подпиской и отправкой."""

    def __init__(self) -> None:
        """Инициализирует реестр именованных сигналов."""
        self._signals: Dict[str, EventSignal] = {}

    def get_event(self, event_name: str) -> EventSignal:
        """Возвращает объект события по имени.

        Args:
            event_name (str): Имя события.

        Returns:
            EventSignal: Объект сигнала для подписки и отправки.
        """
        if event_name not in self._signals:
            self._signals[event_name] = EventSignal(event_name)
        return self._signals[event_name]

    def connect(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Подписывает обработчик на событие.

        Args:
            event_name (str): Имя события.
            handler (Callable[..., Any]): Функция-обработчик.
        """
        self.get_event(event_name).connect(handler)

    def disconnect(
        self, event_name: str, handler: Callable[..., Any] | None = None
    ) -> None:
        """Отписывает обработчик или очищает подписки события.

        Args:
            event_name (str): Имя события.
            handler (Callable[..., Any] | None): Конкретный обработчик или None для
                удаления всех подписок.
        """
        signal = self._signals.get(event_name)
        if signal is None:
            return
        signal.disconnect(handler)

    def send(self, event_name: str, **payload: Any) -> None:
        """Отправляет событие всем подписчикам.

        Args:
            event_name (str): Имя события.
            **payload: Именованные аргументы, передаваемые обработчикам.
        """
        signal = self._signals.get(event_name)
        if signal is None:
            return
        signal.send(**payload)

    def clear(self, event_name: str | None = None) -> None:
        """Очищает подписки (все или для конкретного события).

        Args:
            event_name (str | None): Имя события или None для очистки всех.
        """
        if event_name is None:
            self._signals.clear()
        else:
            self._signals.pop(event_name, None)

    def disconnect_all(self, event_name: str | None = None) -> None:
        """Алиас для clear()."""
        self.clear(event_name)
