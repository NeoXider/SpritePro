from __future__ import annotations

import inspect
from functools import wraps
from typing import Callable, Dict, List, Any

# Глобальный реестр обработчиков сетевых событий
_net_handlers: Dict[str, List[Callable]] = {}

def dispatch_net_events() -> None:
    """Вызывает зарегистрированные декораторы для всех пришедших сообщений.
    Должно вызываться в основном цикле, если мультиплеер активен."""
    try:
        import spritePro as s
    except ImportError:
        return

    ctx = getattr(s, "multiplayer_ctx", None)
    if not ctx:
        return

    for msg in ctx.poll():
        event = msg.get("event")
        if event in _net_handlers:
            data = msg.get("data", {})
            for handler in _net_handlers[event]:
                try:
                    handler(data)
                except Exception:
                    import traceback
                    traceback.print_exc()


def _invoke_handler(func: Callable, data: Dict[str, Any]) -> None:
    """Безопасный вызов функции с передачей только тех аргументов, которые она ожидает."""
    sig = inspect.signature(func)
    valid_args = {}
    
    # Если функция принимает **kwargs, передаем все
    has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    if has_kwargs:
        valid_args = data.copy()
    else:
        for name in sig.parameters.keys():
            if name in data:
                valid_args[name] = data[name]

    func(**valid_args)


def _send_net(event_name: str, func: Callable, *args, **kwargs) -> None:
    """Отправляет сетевое сообщение, упаковывая аргументы."""
    try:
        import spritePro as s
    except ImportError:
        return func(*args, **kwargs)

    ctx = getattr(s, "multiplayer_ctx", None)
    if not ctx:
        return func(*args, **kwargs)

    sig = inspect.signature(func)
    bound = sig.bind_partial(*args, **kwargs)
    bound.apply_defaults()

    data = dict(bound.arguments)
    # Исключаем self, так как его нельзя сериализовать JSON
    data.pop("self", None)

    # Принудительно устанавливаем sender_id при отправке
    data["sender_id"] = ctx.client_id

    # Отправляем сообщение на сервер, который ретранслирует его
    # 0 = обычно target (можно оставить None, чтобы отправить всем, 
    # NetServer все равно ретранслирует всем)
    if hasattr(ctx, "net") and ctx.net:
        ctx.net.send(event_name, data)


def Command(func: Callable) -> Callable:
    """
    Mirror-style Command: Вызывается на Клиенте, исполняется ТОЛЬКО на Хосте.
    """
    event_name = f"Cmd_{func.__name__}"
    if event_name not in _net_handlers:
        _net_handlers[event_name] = []

    def _handler(data: Dict[str, Any]) -> None:
        try:
            import spritePro as s
        except ImportError:
            return
        ctx = getattr(s, "multiplayer_ctx", None)
        if ctx and ctx.is_host:
            _invoke_handler(func, data)

    _net_handlers[event_name].append(_handler)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import spritePro as s
            ctx = getattr(s, "multiplayer_ctx", None)
            if ctx and ctx.is_host:
                # Если вызывает Хост, Команда не должна идти по сети к самому себе, 
                # мы просто локально её исполняیم.
                sig = inspect.signature(func)
                bound = sig.bind_partial(*args, **kwargs)
                bound.apply_defaults()
                data = dict(bound.arguments)
                data.pop("self", None)
                data["sender_id"] = ctx.client_id
                _invoke_handler(func, data)
                return
        except ImportError:
            pass

        _send_net(event_name, func, *args, **kwargs)

    return wrapper


def ClientRpc(func: Callable) -> Callable:
    """
    Mirror-style ClientRpc: Вызывается на Хосте, исполняется на ВСЕХ Клиентах (включая Хост).
    """
    event_name = f"Rpc_{func.__name__}"
    if event_name not in _net_handlers:
        _net_handlers[event_name] = []

    def _handler(data: Dict[str, Any]) -> None:
        _invoke_handler(func, data)

    _net_handlers[event_name].append(_handler)

    @wraps(func)
    def wrapper(*args, **kwargs):
        ctx = None
        # Предупреждение, если вызвано не на хосте (Mirror-поведение)
        try:
            import spritePro as s
            ctx = getattr(s, "multiplayer_ctx", None)
            if ctx and not ctx.is_host:
                if hasattr(s, "debug_log_warning"):
                    s.debug_log_warning(f"ClientRpc {func.__name__} вызван с Клиента! Игнорируется сетью, должно вызываться только на Хосте.")
                return 
        except ImportError:
            pass
            
        _send_net(event_name, func, *args, **kwargs)
        
        # Хост также должен выполнить этот Rpc локально для себя, 
        # так как сервер (хост) не ретранслирует сообщения самому отправителю.
        if ctx and ctx.is_host:
            sig = inspect.signature(func)
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            data = dict(bound.arguments)
            data.pop("self", None)
            data["sender_id"] = ctx.client_id
            _invoke_handler(func, data)

    return wrapper


def NetEvent(name: str | None = None) -> Callable:
    """
    Универсальный сетевой обработчик (подписка на любое входящее сообщение).
    
    @NetEvent("player_joined")
    def on_join(sender_id, data):
        ...
    """
    def decorator(func: Callable) -> Callable:
        event_name = name or func.__name__
        if event_name not in _net_handlers:
            _net_handlers[event_name] = []

        def _handler(data: Dict[str, Any]) -> None:
            _invoke_handler(func, data)

        _net_handlers[event_name].append(_handler)

        return func
    return decorator
