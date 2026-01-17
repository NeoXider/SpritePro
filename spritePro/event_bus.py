from __future__ import annotations

from typing import Callable, Dict, List, Any


class EventBus:
    """Простой EventBus для подписки/отписки на события."""

    def __init__(self) -> None:
        """Инициализирует словарь обработчиков событий."""
        self._handlers: Dict[str, List[Callable[..., Any]]] = {}

    def on(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Подписаться на событие."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []
        if handler not in self._handlers[event_name]:
            self._handlers[event_name].append(handler)

    def off(self, event_name: str, handler: Callable[..., Any] | None = None) -> None:
        """Отписаться от события."""
        if event_name not in self._handlers:
            return
        if handler is None:
            self._handlers[event_name].clear()
            return
        try:
            self._handlers[event_name].remove(handler)
        except ValueError:
            pass

    def emit(self, event_name: str, **payload: Any) -> None:
        """Вызвать всех подписчиков события."""
        handlers = list(self._handlers.get(event_name, []))
        for handler in handlers:
            try:
                handler(**payload)
            except Exception:
                # Не прерываем остальные обработчики
                continue

    def clear(self, event_name: str | None = None) -> None:
        """Очистить подписки (все или для конкретного события)."""
        if event_name is None:
            self._handlers.clear()
        else:
            self._handlers.pop(event_name, None)
