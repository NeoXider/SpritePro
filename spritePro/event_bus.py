from __future__ import annotations

from typing import Callable, Dict, List, Any, Optional


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
        self._net_sender: Optional[Any] = None

    def set_network_sender(self, sender: Any | None) -> None:
        """Назначает объект для отправки сетевых событий.

        Ожидается метод send(event, data).
        """
        self._net_sender = sender

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

    def send(
        self,
        event_name: str,
        *,
        route: str = "local",
        net: Any | None = None,
        include_local: bool | None = None,
        **payload: Any,
    ) -> None:
        """Отправляет событие подписчикам и опционально в сеть.

        Позволяет выбрать, куда доставить событие: только локально (подписчики
        на этом процессе), только в сеть, или и туда и туда. Используется для
        игровых событий (ready, start, shoot) с единой точкой входа.

        Args:
            event_name: Имя события. Подписчики регистрируются через
                connect(event_name, handler). При совпадении имени вызываются
                все зарегистрированные обработчики с **payload.
            route: Куда доставить событие. «В сеть» — это вызов net.send(event, data):
                объект net (аргумент ниже, или заданный через set_network_sender)
                отправляет сообщение на сервер; при relay-архитектуре сервер
                рассылает его другим клиентам. Варианты:
                "local" — только локальные подписчики на этом процессе, в сеть
                    ничего не уходит. По умолчанию.
                "all" — локальные подписчики вызываются и сообщение уходит в
                    сеть (через net). Удобно для «сделал действие — обнови себя
                    и всех» (ready, shoot, чат).
                "server" — в сеть уходит, локальные подписчики по умолчанию не
                    вызываются. Семантика: «только серверу» (запросы, heartbeat).
                "clients" — то же, что server, с семантикой «только клиентам».
                "net" — то же: только отправка в сеть (через net).
                При неизвестном значении route попадает в payload и маршрут
                считается "local".
            net: Объект с методом send(event: str, data: dict). Обычно
                MultiplayerContext или NetClient. Используется при route в
                ("server", "clients", "all", "net"). Если None, берётся
                ранее установленный set_network_sender().
            include_local: Вызвать ли локальных подписчиков. По умолчанию True
                для "local" и "all", False для остальных. Можно переопределить
                вручную (например, route="server", include_local=True).
            **payload: Именованные аргументы, которые получат обработчики как
                keyword-аргументы. Сериализуются в data при отправке в сеть.

        Note:
            При пробросе входящих из сети в EventBus вызывают без route и net:
            ``s.events.send(msg["event"], **msg.get("data", {}))`` — тогда
            срабатывают только локальные подписчики (эмуляция «получили событие
            из сети»). Так обрабатывают и свои (route="all"), и чужие сообщения
            одним кодом.
        """
        allowed_routes = {"local", "server", "clients", "all", "net"}
        if route not in allowed_routes:
            payload["route"] = route
            route = "local"

        if include_local is None:
            include_local = route in ("local", "all")

        if include_local:
            signal = self._signals.get(event_name)
            if signal is not None:
                signal.send(**payload)

        if route in ("server", "clients", "all", "net"):
            sender = net or self._net_sender
            if sender is not None:
                sender.send(event_name, payload)

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
