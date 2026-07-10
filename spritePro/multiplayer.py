"""Утилиты для упрощения мультиплеера (контекст и debug)."""

from __future__ import annotations

import time
from collections import deque
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

PING_SMOOTHING_SAMPLES = 5

# Служебные события пинга: не попадают в пользовательские обработчики и poll().
_PING_EVENTS = ("_ping", "_pong")


class MultiplayerContext:
    """Глобальный контекст мультиплеера для клиента."""

    def __init__(
        self,
        net: NetClient,
        role: str,
        client_id: Optional[int] = None,
        seed: Optional[int] = None,
        debug: Optional[NetDebug] = None,
        server: Optional[Any] = None,
        ping_interval: float = 1.0,
    ) -> None:
        self.net = net
        self.server = server
        self.role = role
        self.is_host = role == "host"
        self.id_assigned = self.is_host
        self.client_id = 0 if role == "host" else (client_id if client_id is not None else 1)
        # players: id -> произвольные данные игрока (например {"name": "Игрок"})
        self.players: Dict[int, Dict[str, Any]] = {}
        self.state: Dict[str, Any] = {}
        self.state["player_ids"] = []
        self.state["players"] = {}
        # roster сохраняем как совместимость: список id игроков
        self.state["roster"] = []
        self.debug = debug or NetDebug(enabled=False)
        self._last_send: Dict[str, float] = {}
        self.seed = DEFAULT_MULTIPLAYER_SEED if seed is None else int(seed)
        self.random = random.Random(self.seed)
        self.ping_interval = float(ping_interval)
        self._last_ping_sent = 0.0
        self._last_ping_ms = 0.0
        self._ping_samples: "deque[float]" = deque(maxlen=PING_SMOOTHING_SAMPLES)

    @property
    def ping_ms(self) -> float:
        """RTT в миллисекундах, сглаженный скользящим средним по последним замерам."""
        if not self._ping_samples:
            return 0.0
        return sum(self._ping_samples) / len(self._ping_samples)

    @property
    def last_ping_ms(self) -> float:
        """Последний измеренный RTT в миллисекундах."""
        return self._last_ping_ms

    @property
    def is_connected(self) -> bool:
        """True, пока сетевой клиент подключен к серверу."""
        return bool(self.net is not None and getattr(self.net, "connected", False))

    def get_player_ids(self) -> list[int]:
        """Удобный доступ к списку подключенных id."""
        ids = self.state.get("player_ids")
        if isinstance(ids, list):
            return [int(x) for x in ids]
        # fallback на старый ключ (если кто-то не обновил)
        roster = self.state.get("roster", [])
        if isinstance(roster, list):
            return [int(x) for x in roster]
        return []

    def get_players(self) -> Dict[int, Dict[str, Any]]:
        """Удобный доступ к данным игроков (id -> data)."""
        return self.players

    def send(
        self, event: str, data: Optional[Dict[str, Any]] = None, group: str = "traffic"
    ) -> None:
        payload = dict(data) if data else {}
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

    def update_frame(self) -> None:
        """Считывает сообщения из сети один раз за кадр.
        Позволяет и декораторам, и ручному ctx.poll() читать сообщения без конфликтов."""
        messages = list(self.net.poll(500))
        if self.server is not None:
            # Сервер кладет каждое игровое сообщение в свою очередь И ретранслирует
            # его всем клиентам (включая NetClient хоста), поэтому игровые сообщения
            # берем только из net.poll(). Из очереди сервера берем лишь служебные
            # события, которые не ретранслируются (client_connected/client_disconnected).
            _service_events = ("client_connected", "client_disconnected")
            for msg in self.server.poll(500):
                if msg.get("event") in _service_events:
                    messages.append(msg)


        self._frame_messages = []
        for msg in messages:
            event = msg.get("event")
            if event in _PING_EVENTS:
                if event == "_pong":
                    self._handle_pong(msg.get("data") or {})
                continue
            self._handle_internal(msg)
            self.debug.log("traffic", "recv", msg.get("event"), msg.get("data", {}))
            self._frame_messages.append(msg)

        self._maybe_send_ping()

    def _maybe_send_ping(self) -> None:
        """Раз в ping_interval секунд отправляет служебный _ping для замера RTT."""
        if self.ping_interval <= 0 or not self.is_connected:
            return
        now = time.monotonic()
        if now - self._last_ping_sent < self.ping_interval:
            return
        self._last_ping_sent = now
        self.net.send("_ping", {"t": now, "sender_id": self.client_id})

    def _handle_pong(self, data: Dict[str, Any]) -> None:
        t = data.get("t")
        if not isinstance(t, (int, float)):
            return
        rtt_ms = max(0.0, (time.monotonic() - float(t)) * 1000.0)
        self._last_ping_ms = rtt_ms
        self._ping_samples.append(rtt_ms)
        self.debug.log("state", "pong", f"rtt={rtt_ms:.2f}ms")

    def get_net_stats(self) -> Dict[str, Any]:
        """Возвращает сетевую статистику: пинг, счётчики трафика, состояние.

        Ключи: ping_ms, last_ping_ms, client_id, is_host, connected,
        clients_count, messages_sent, messages_received, bytes_sent,
        bytes_received. На хосте дополнительно ключ "server" со счётчиками сервера.
        """
        net_stats = self.net.get_stats() if self.net is not None else {}
        clients_count: Optional[int] = None
        if self.server is not None and hasattr(self.server, "clients_count"):
            clients_count = self.server.clients_count
        else:
            ids = self.get_player_ids()
            if ids:
                clients_count = len(ids)
        stats: Dict[str, Any] = {
            "ping_ms": self.ping_ms,
            "last_ping_ms": self.last_ping_ms,
            "client_id": self.client_id,
            "is_host": self.is_host,
            "connected": self.is_connected,
            "clients_count": clients_count,
            "messages_sent": net_stats.get("messages_sent", 0),
            "messages_received": net_stats.get("messages_received", 0),
            "bytes_sent": net_stats.get("bytes_sent", 0),
            "bytes_received": net_stats.get("bytes_received", 0),
        }
        if self.server is not None and hasattr(self.server, "get_stats"):
            stats["server"] = self.server.get_stats()
        return stats

    def poll(self, max_messages: int = 500, ignore_local: bool = True) -> Iterable[NetMessage]:
        """Возвращает сообщения текущего кадра. Больше не уничтожает их при чтении,
        позволяя и декораторам, и скриптам читать одни и те же пакеты.
        """
        result = []
        for msg in getattr(self, "_frame_messages", []):
            data = msg.get("data")
            is_local = False
            if isinstance(data, dict):
                sender_id = data.get("sender_id")
                if sender_id is not None and sender_id == self.client_id:
                    is_local = True
                    
            if not (ignore_local and is_local):
                result.append(msg)
                
        return result

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
            players_raw = data.get("players", [])
            # Поддерживаем оба формата:
            # 1) {"players": [0, 1, 2]}  -> старый формат (список id)
            # 2) {"players": {"0": {"name": "Host"}, "1": {"name": "Alice"}}} -> расширенный формат
            if isinstance(players_raw, dict):
                parsed: Dict[int, Dict[str, Any]] = {}
                for k, v in players_raw.items():
                    try:
                        pid = int(k)
                    except (TypeError, ValueError):
                        continue
                    if isinstance(v, dict):
                        parsed[pid] = dict(v)
                    else:
                        # если сервер отправил просто строку имени
                        parsed[pid] = {"name": str(v)}
                self.players = parsed
                ids = sorted(parsed.keys())
                self.state["players"] = parsed
                self.state["player_ids"] = ids
                # обратно совместимо
                self.state["roster"] = ids
                self.debug.log("state", "roster", {"player_ids": ids, "players": parsed})
            else:
                if not isinstance(players_raw, list):
                    players_raw = []
                ids = [int(x) for x in players_raw]
                # сохраняем уже имеющиеся данные, если они были
                existing = self.players
                self.players = {pid: existing.get(pid, {}) for pid in ids}
                self.state["players"] = self.players
                self.state["player_ids"] = ids
                self.state["roster"] = ids
                self.debug.log("state", "roster", {"player_ids": ids})

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
    server: Optional[Any] = None,
    ping_interval: float = 1.0,
) -> MultiplayerContext:
    """Создает и сохраняет глобальный контекст мультиплеера."""

    global _context
    if server is None and role == "host":
        try:
            from . import networking

            server = networking._host_server
        except Exception:
            pass
    debug_cfg = NetDebug(enabled=debug, color_logs=color_logs)
    _context = MultiplayerContext(
        net=net,
        role=role,
        client_id=client_id,
        seed=seed,
        debug=debug_cfg,
        server=server,
        ping_interval=ping_interval,
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
