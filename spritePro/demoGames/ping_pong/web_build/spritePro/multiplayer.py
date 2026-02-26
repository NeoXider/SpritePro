"""Утилиты для упрощения мультиплеера (контекст и debug)."""

from __future__ import annotations

import time
from dataclasses import dataclass
import random
from typing import Any, Dict, Optional, Iterable

from .networking import NetClient, NetMessage


@dataclass
class NetDebug:
    enabled: bool = False
    traffic: bool = True
    state: bool = True
    errors: bool = True
    color_logs: bool = True

    def _color(self, code: str, text: str) -> str:
        if not self.color_logs:
            return text
        return f"\x1b[{code}m{text}\x1b[0m"

    def _tag(self, group: str) -> str:
        if group == "traffic":
            return self._color("36", "[NET:TRAFFIC]")
        if group == "state":
            return self._color("35", "[NET:STATE]")
        if group == "errors":
            return self._color("31", "[NET:ERROR]")
        return self._color("33", "[NET]")

    def log(self, group: str, *message: object) -> None:
        if not self.enabled:
            return
        if group == "traffic" and not self.traffic:
            return
        if group == "state" and not self.state:
            return
        if group == "errors" and not self.errors:
            return
        text = " ".join(str(part) for part in message)
        print(self._tag(group), text)


DEFAULT_MULTIPLAYER_SEED = 1337


class MultiplayerContext:
    """Глобальный контекст мультиплеера для клиента."""

    def __init__(
        self,
        net: NetClient,
        role: str,
        client_id: Optional[int] = None,
        seed: Optional[int] = None,
        debug: Optional[NetDebug] = None,
    ) -> None:
        self.net = net
        self.role = role
        self.is_host = role == "host"
        self.id_assigned = self.is_host
        self.client_id = 0 if role == "host" else (client_id if client_id is not None else 1)
        self.players: Dict[str, Dict[str, Any]] = {}
        self.state: Dict[str, Any] = {}
        self.debug = debug or NetDebug(enabled=False)
        self._last_send: Dict[str, float] = {}
        self.seed = DEFAULT_MULTIPLAYER_SEED if seed is None else int(seed)
        self.random = random.Random(self.seed)

    def send(
        self, event: str, data: Optional[Dict[str, Any]] = None, group: str = "traffic"
    ) -> None:
        payload = data or {}
        payload.setdefault("sender_id", self.client_id)
        self.net.send(event, payload)
        self.debug.log(group, "send", event, payload)

    def send_every(
        self,
        event: str,
        data: Optional[Dict[str, Any]],
        interval: float,
        group: str = "traffic",
    ) -> bool:
        now = time.monotonic()
        last = self._last_send.get(event, 0.0)
        if now - last < interval:
            return False
        self._last_send[event] = now
        self.send(event, data, group=group)
        return True

    def poll(self, max_messages: int = 100) -> Iterable[NetMessage]:
        messages = self.net.poll(max_messages)
        for msg in messages:
            self._handle_internal(msg)
            self.debug.log("traffic", "recv", msg.get("event"), msg.get("data", {}))
        return messages

    def _handle_internal(self, msg: NetMessage) -> None:
        event = msg.get("event")
        data = msg.get("data", {})
        if event == "assign_id":
            if self.is_host:
                self.debug.log("state", "assign_id_ignored", data.get("id"))
                return
            new_id = int(data.get("id", self.client_id))
            self.client_id = new_id
            self.id_assigned = True
            self.debug.log("state", "assign_id", new_id)
        elif event == "roster":
            players = data.get("players", [])
            self.state["roster"] = players
            self.debug.log("state", "roster", players)

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.debug.log("state", "set", key, value)

    def get_state(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set_seed(self, seed: int) -> None:
        self.seed = int(seed)
        self.random.seed(self.seed)
        self.debug.log("state", "seed", self.seed)


_context: Optional[MultiplayerContext] = None


def init_context(
    net: NetClient,
    role: str,
    client_id: Optional[int] = None,
    seed: Optional[int] = None,
    debug: bool = False,
    color_logs: bool = True,
) -> MultiplayerContext:
    """Создает и сохраняет глобальный контекст мультиплеера."""

    global _context
    debug_cfg = NetDebug(enabled=debug, color_logs=color_logs)
    _context = MultiplayerContext(
        net=net,
        role=role,
        client_id=client_id,
        seed=seed,
        debug=debug_cfg,
    )
    try:
        import spritePro

        spritePro.events.set_network_sender(net)
        spritePro.multiplayer_ctx = _context
    except Exception:
        pass
    return _context


def get_context() -> MultiplayerContext:
    """Возвращает текущий контекст (должен быть инициализирован)."""

    if _context is None:
        raise RuntimeError("MultiplayerContext не инициализирован. Вызовите init_context().")
    return _context


def set_seed(seed: int) -> None:
    """Устанавливает общий сид контекста."""
    ctx = get_context()
    ctx.set_seed(seed)


def get_random() -> random.Random:
    """Возвращает генератор случайных чисел из контекста."""
    return get_context().random
