from __future__ import annotations

import json
import os
import socket
import threading
from queue import Queue, Empty
from typing import Any, Dict, Optional, Tuple, List


NetMessage = Dict[str, Any]

# Позиции окон клиентов в quick-режиме (client 0..3).
_CLIENT_WINDOW_POSITIONS = [
    "980,40",  # client 0 (top-right)
    "40,640",  # client 1 (bottom-left)
    "980,640",  # client 2 (bottom-right)
    "510,340",  # client 3 (center-ish)
]


def _is_debug_enabled(value: Optional[bool]) -> bool:
    if value is None:
        return os.environ.get("SPRITEPRO_NET_DEBUG") == "1"
    return value


def _net_log_callsite() -> str:
    """Источник вызова для сетевого лога (файл:строка функция), как в debug_log."""
    import sys

    try:
        frame = sys._getframe(2)
    except ValueError:
        return ""
    try:
        while frame is not None:
            filename = frame.f_code.co_filename
            if (
                os.path.sep + "spritePro" + os.path.sep in filename
                or "networking" in os.path.basename(filename)
            ):
                frame = frame.f_back
                continue
            basename = os.path.basename(filename)
            return f" ({basename}:{frame.f_lineno} {frame.f_code.co_name})"
    finally:
        del frame
    return ""


def _net_log(*message: object) -> None:
    text = " ".join(str(part) for part in message)
    tag = os.environ.get("SPRITEPRO_NET_LOG_TAG", "net")
    callsite = _net_log_callsite()
    line = f"[{tag}] {text}{callsite}"
    _net_log_to_file(line)
    _net_log_to_overlay(text)


def _net_log_to_file(line: str) -> None:
    tag = os.environ.get("SPRITEPRO_NET_LOG_TAG", "net")
    log_dir = os.environ.get("SPRITEPRO_LOG_DIR", "spritepro_logs")
    for dir_candidate in (log_dir, os.getcwd()):
        try:
            os.makedirs(dir_candidate, exist_ok=True)
            path = os.path.join(dir_candidate, f"debug_net_{tag}.log")
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            return
        except OSError:
            continue


def _net_log_to_overlay(text: str) -> None:
    try:
        import spritePro as _s

        if hasattr(_s, "net_log_to_overlay") and callable(getattr(_s, "net_log_to_overlay")):
            _s.net_log_to_overlay(text, level="info")
    except Exception:
        pass


def _format_message(msg: NetMessage) -> str:
    return f"event={msg.get('event')} data={msg.get('data', {})}"


def _safe_peer(conn: socket.socket) -> str:
    try:
        host, port = conn.getpeername()
        return f"{host}:{port}"
    except OSError:
        return "unknown"


def _enable_nodelay(sock: socket.socket) -> None:
    """Отключает алгоритм Нейгла (TCP_NODELAY) — критично для мелких игровых пакетов."""
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except OSError:
        pass


def _encode_message(event: str, data: Optional[Dict[str, Any]] = None) -> bytes:
    payload = {"event": event, "data": data or {}}
    return (json.dumps(payload) + "\n").encode("utf-8")


def _decode_message(raw: str) -> Optional[NetMessage]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


class NetServer:
    """Simple TCP relay server with JSON line protocol."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5050,
        relay: bool = True,
        debug: Optional[bool] = None,
        name: str = "server",
    ) -> None:
        """Создает TCP-сервер для ретрансляции сообщений.

        Args:
            host: Адрес биндинга (обычно 0.0.0.0).
            port: Порт сервера.
            relay: Если True, ретранслирует входящие всем клиентам.
            debug: Включить сетевые логи (None = из env).
            name: Имя сервера для логов.
        """
        self.host = host
        self.port = port
        self.relay = relay
        self._debug = _is_debug_enabled(debug)
        self._name = name
        self._server: Optional[socket.socket] = None
        self._clients: List[socket.socket] = []
        self._client_ids: Dict[socket.socket, int] = {}
        # id 0 зарезервирован за хостом (MultiplayerContext хоста всегда
        # использует client_id=0 и игнорирует assign_id), поэтому подключающимся
        # клиентам выдаются id начиная с 1 — коллизия с хостом невозможна
        # независимо от порядка подключения.
        self._next_client_id = 1
        self._lock = threading.Lock()
        self._send_locks: Dict[socket.socket, threading.Lock] = {}
        self._queue: "Queue[Tuple[Optional[socket.socket], NetMessage]]" = Queue()
        self._running = False
        self._stats_lock = threading.Lock()
        self._messages_sent = 0
        self._messages_received = 0
        self._bytes_sent = 0
        self._bytes_received = 0

    @property
    def clients_count(self) -> int:
        """Количество подключенных клиентов."""
        with self._lock:
            return len(self._clients)

    def _count_sent(self, nbytes: int, messages: int = 1) -> None:
        with self._stats_lock:
            self._messages_sent += messages
            self._bytes_sent += nbytes

    def _count_received(self, nbytes: int, messages: int = 0) -> None:
        with self._stats_lock:
            self._messages_received += messages
            self._bytes_received += nbytes

    def get_stats(self) -> Dict[str, int]:
        """Возвращает счётчики трафика сервера (потокобезопасно)."""
        with self._stats_lock:
            return {
                "messages_sent": self._messages_sent,
                "messages_received": self._messages_received,
                "bytes_sent": self._bytes_sent,
                "bytes_received": self._bytes_received,
            }

    def start(self) -> None:
        """Запускает сервер в отдельном потоке."""
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            self._server = server
            while self._running:
                try:
                    conn, _ = server.accept()
                except OSError:
                    break
                _enable_nodelay(conn)
                with self._lock:
                    self._clients.append(conn)
                    client_id = self._next_client_id
                    self._next_client_id += 1
                    self._client_ids[conn] = client_id
                    self._send_locks[conn] = threading.Lock()
                self._send_to(conn, "assign_id", {"id": client_id})
                self._queue.put(
                    (
                        None,
                        {
                            "event": "client_connected",
                            "data": {"client_id": client_id, "peer": _safe_peer(conn)},
                        },
                    )
                )
                if self._debug:
                    _net_log(
                        f"[NetServer:{self._name}] assign_id to={_safe_peer(conn)} id={client_id}"
                    )
                thread = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
                thread.start()

    def _handle_client(self, conn: socket.socket) -> None:
        buffer = bytearray()
        peer = _safe_peer(conn)
        try:
            while self._running:
                try:
                    data = conn.recv(4096)
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                    break
                if not data:
                    break
                self._count_received(len(data))
                buffer.extend(data)
                while b"\n" in buffer:
                    idx = buffer.index(b"\n")
                    line = buffer[:idx].decode("utf-8", errors="ignore")
                    buffer = buffer[idx + 1:]
                    msg = _decode_message(line.strip())
                    if msg is None:
                        continue
                    self._count_received(0, messages=1)
                    if msg.get("event") == "_ping":
                        # Служебный пинг: отвечаем напрямую отправителю и не
                        # ретранслируем остальным клиентам.
                        ping_data = msg.get("data") or {}
                        self._send_to(conn, "_pong", {"t": ping_data.get("t")})
                        continue
                    if self._debug:
                        _net_log(
                            f"[NetServer:{self._name}] recv from={peer} {_format_message(msg)}"
                        )
                    self._queue.put((conn, msg))
                    if self.relay:
                        self._broadcast_raw(line.encode("utf-8") + b"\n", exclude=conn)
                        if self._debug:
                            _net_log(
                                f"[NetServer:{self._name}] relay from={peer} {_format_message(msg)}"
                            )
        finally:
            with self._lock:
                if conn in self._clients:
                    self._clients.remove(conn)
                client_id = self._client_ids.pop(conn, None)
                self._send_locks.pop(conn, None)
            if client_id is not None:
                self._queue.put(
                    (None, {"event": "client_disconnected", "data": {"client_id": client_id}})
                )
            try:
                conn.close()
            except OSError:
                pass

    def _send_to(
        self,
        conn: socket.socket,
        event: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        raw = _encode_message(event, data)
        with self._lock:
            send_lock = self._send_locks.get(conn)
        try:
            if send_lock is not None:
                with send_lock:
                    conn.sendall(raw)
            else:
                conn.sendall(raw)
            self._count_sent(len(raw))
        except OSError:
            pass

    def _broadcast_raw(self, raw: bytes, exclude: Optional[socket.socket] = None) -> None:
        # Под общим lock только копируем список клиентов; сам sendall делаем
        # вне общего lock, но под per-socket lock, чтобы конкурентные записи
        # в один сокет не перемешивали JSON-строки.
        with self._lock:
            targets = [
                (client, self._send_locks.get(client))
                for client in self._clients
                if client is not exclude
            ]
        for client, send_lock in targets:
            try:
                if send_lock is not None:
                    with send_lock:
                        client.sendall(raw)
                else:
                    client.sendall(raw)
                self._count_sent(len(raw))
            except OSError:
                pass

    def broadcast(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Отправляет событие всем подключенным клиентам."""
        raw = _encode_message(event, data)
        self._broadcast_raw(raw)
        if self._debug:
            _net_log(
                f"[NetServer:{self._name}] send {_format_message({'event': event, 'data': data or {}})}"
            )

    def poll(self, max_messages: int = 100) -> List[NetMessage]:
        """Возвращает список входящих сообщений из очереди.

        Args:
            max_messages: Максимум сообщений за вызов.
        """
        messages: List[NetMessage] = []
        for _ in range(max_messages):
            try:
                _sender, msg = self._queue.get_nowait()
            except Empty:
                break
            messages.append(msg)
        return messages

    def stop(self) -> None:
        """Останавливает сервер и закрывает сокет (включая клиентские)."""
        self._running = False
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass
        with self._lock:
            clients = list(self._clients)
            self._clients.clear()
            self._client_ids.clear()
            self._send_locks.clear()
        for conn in clients:
            try:
                conn.close()
            except OSError:
                pass


class NetClient:
    """Simple TCP client with JSON line protocol."""

    def __init__(
        self,
        host: str,
        port: int = 5050,
        debug: Optional[bool] = None,
        name: str = "client",
    ) -> None:
        """Создает TCP-клиент.

        Args:
            host: Адрес сервера.
            port: Порт сервера.
            debug: Включить сетевые логи (None = из env).
            name: Имя клиента для логов.
        """
        self.host = host
        self.port = port
        self._debug = _is_debug_enabled(debug)
        self._name = name
        self._sock: Optional[socket.socket] = None
        self._queue: "Queue[NetMessage]" = Queue()
        self._running = False
        self._stats_lock = threading.Lock()
        self._messages_sent = 0
        self._messages_received = 0
        self._bytes_sent = 0
        self._bytes_received = 0

    @property
    def connected(self) -> bool:
        """True, пока соединение активно и поток приема работает."""
        return self._running and self._sock is not None

    def _count_sent(self, nbytes: int, messages: int = 1) -> None:
        with self._stats_lock:
            self._messages_sent += messages
            self._bytes_sent += nbytes

    def _count_received(self, nbytes: int, messages: int = 0) -> None:
        with self._stats_lock:
            self._messages_received += messages
            self._bytes_received += nbytes

    def get_stats(self) -> Dict[str, int]:
        """Возвращает счётчики трафика клиента (потокобезопасно)."""
        with self._stats_lock:
            return {
                "messages_sent": self._messages_sent,
                "messages_received": self._messages_received,
                "bytes_sent": self._bytes_sent,
                "bytes_received": self._bytes_received,
            }

    def connect(self, max_attempts: int = 10, retry_delay: float = 0.3) -> None:
        """Подключается к серверу и запускает поток приема.

        При ConnectionRefusedError/TimeoutError повторяет попытку
        (в quick-режиме клиенты могут стартовать раньше сервера).
        """
        if self._running:
            return
        import time

        for attempt in range(1, max(1, max_attempts) + 1):
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._sock.connect((self.host, self.port))
                _enable_nodelay(self._sock)
                break
            except (ConnectionRefusedError, TimeoutError) as e:
                try:
                    self._sock.close()
                except OSError:
                    pass
                self._sock = None
                if attempt >= max(1, max_attempts):
                    _net_log(
                        f"[NetClient:{self._name}] Ошибка подключения к {self.host}:{self.port}: {e}. "
                        "Запустите с --quick (хост+клиенты) или сначала сервер: --server."
                    )
                    raise
                time.sleep(retry_delay)
            except OSError as e:
                _net_log(
                    f"[NetClient:{self._name}] Ошибка подключения к {self.host}:{self.port}: {e}. "
                    "Запустите с --quick (хост+клиенты) или сначала сервер: --server."
                )
                raise
        self._running = True
        thread = threading.Thread(target=self._recv_loop, daemon=True)
        thread.start()

    def _recv_loop(self) -> None:
        buffer = bytearray()
        assert self._sock is not None
        try:
            while self._running:
                try:
                    data = self._sock.recv(4096)
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                    break
                if not data:
                    break
                self._count_received(len(data))
                buffer.extend(data)
                while b"\n" in buffer:
                    idx = buffer.index(b"\n")
                    line = buffer[:idx].decode("utf-8", errors="ignore")
                    buffer = buffer[idx + 1:]
                    msg = _decode_message(line.strip())
                    if msg is not None:
                        self._count_received(0, messages=1)
                        if self._debug:
                            _net_log(f"[NetClient:{self._name}] recv {_format_message(msg)}")
                        self._queue.put(msg)
        finally:
            self._running = False

    def send(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Отправляет событие на сервер.

        Args:
            event: Имя события.
            data: Данные события.
        """
        if not self._sock:
            return
        try:
            raw = _encode_message(event, data)
            self._sock.sendall(raw)
            self._count_sent(len(raw))
            if self._debug:
                _net_log(
                    f"[NetClient:{self._name}] send {_format_message({'event': event, 'data': data or {}})}"
                )
        except OSError:
            pass

    def poll(self, max_messages: int = 100) -> List[NetMessage]:
        """Возвращает список входящих сообщений из очереди.

        Args:
            max_messages: Максимум сообщений за вызов.
        """
        messages: List[NetMessage] = []
        for _ in range(max_messages):
            try:
                msg = self._queue.get_nowait()
            except Empty:
                break
            messages.append(msg)
        return messages

    def close(self) -> None:
        """Закрывает соединение и останавливает прием."""
        self._running = False
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass


_host_server: Optional["NetServer"] = None


def run(
    argv: Optional[List[str]] = None,
    entry: str = "multiplayer_main",
    host: str = "127.0.0.1",
    port: int = 5050,
    clients: int = 2,
    server_tick_rate: int = 30,
    net_debug: bool = False,
    client_spawn_delay: float = 0.0,
    use_lobby: bool = False,
) -> None:
    """Запускает мультиплеер для вашей игры.

    Ожидается функция `multiplayer_main(net, role)` в вашем скрипте.
    По умолчанию (use_lobby=False): без аргументов — быстрый режим (host + клиент),
    два окна. Для готового приложения: run(use_lobby=True) — одно окно с лобби
    (имя, хост/клиент, порт, IP), затем «В игру».
    """
    import argparse
    import inspect
    import os
    import sys
    import time
    import traceback
    import subprocess
    from pathlib import Path

    def _resolve_entry(name: str):
        if ":" in name:
            module_name, func_name = name.split(":", 1)
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name, None)
        else:
            main_module = sys.modules.get("__main__")
            func = getattr(main_module, name, None) if main_module else None
        if not callable(func):
            raise ValueError(
                f"Не найдена функция '{name}'. "
                "Создайте def multiplayer_main(net, role): ... "
                "или укажите entry='module:function'."
            )
        return func

    def _call_entry(func, net, role: str) -> None:
        params = list(inspect.signature(func).parameters.values())
        if len(params) >= 2:
            func(net, role)
        elif len(params) == 1:
            func(net)
        else:
            func()

    def _find_entry(entry_name: str):
        try:
            return _resolve_entry(entry_name)
        except ValueError:
            pass
        if entry_name == "multiplayer_main":
            try:
                return _resolve_entry("main")
            except ValueError:
                pass
        raise ValueError(
            "Не найдена функция multiplayer_main или main. "
            "Создайте def multiplayer_main(net, role): ... "
            "или вызовите run(entry='module:function')."
        )

    def _set_window_pos(role: str, color: str) -> None:
        if os.environ.get("SPRITEPRO_WINDOW_POS"):
            return
        index_env = os.environ.get("SPRITEPRO_NET_INDEX")
        if role == "host":
            os.environ["SPRITEPRO_WINDOW_POS"] = "40,40"
            return
        if role != "client":
            os.environ["SPRITEPRO_WINDOW_POS"] = "40,600"
            return
        if index_env is not None:
            try:
                index = int(index_env)
            except ValueError:
                index = 0
        else:
            index = 0
        os.environ["SPRITEPRO_WINDOW_POS"] = _CLIENT_WINDOW_POSITIONS[
            index % len(_CLIENT_WINDOW_POSITIONS)
        ]

    def _run_worker(
        role: str, bind_host: str, connect_host: str, color: str, debug_enabled: bool
    ) -> None:
        _set_window_pos(role, color)
        log_tag = (
            "host" if role == "host" else f"client_{os.environ.get('SPRITEPRO_NET_INDEX', '0')}"
        )
        os.environ["SPRITEPRO_NET_LOG_TAG"] = log_tag
        _net_log("Worker started", f"role={role}", f"connect={connect_host}:{port}")
        global _host_server
        if role == "host":
            server = NetServer(host=bind_host, port=port, debug=debug_enabled, name=role)
            server.start()
            _host_server = server
        if connect_host in ("0.0.0.0", ""):
            connect_host = "127.0.0.1"
        net = NetClient(connect_host, port, debug=debug_enabled, name=color)
        net.connect()
        func = _find_entry(entry)
        try:
            try:
                import spritePro.multiplayer as _mp
                _mp.init_context(net, role)
            except Exception:
                pass

            _call_entry(func, net, role)
        except Exception as e:
            tag = os.environ.get("SPRITEPRO_NET_LOG_TAG", "net")
            fatal_msg = f"FATAL {type(e).__name__}: {e}"
            _net_log(fatal_msg)
            for tb_line in traceback.format_exc().splitlines():
                _net_log_to_file(f"[{tag}] {tb_line}")
            try:
                import spritePro as _s

                if hasattr(_s, "debug_log_error"):
                    _s.debug_log_error(fatal_msg, ttl=30.0)
                    for tb_line in traceback.format_exc().splitlines():
                        _s.debug_log_error(tb_line, ttl=30.0)
            except Exception:
                pass
            raise

    def _get_script_path() -> Path:
        main_module = sys.modules.get("__main__")
        main_file = getattr(main_module, "__file__", None)
        candidate = Path(main_file or sys.argv[0]).resolve()
        if not candidate.exists():
            raise RuntimeError(
                "run() нужно вызывать из файла. Не удалось определить путь к текущему скрипту."
            )
        return candidate

    def _spawn_client(
        script: Path,
        role: str,
        color: str,
        bind_host: str,
        connect_host: str,
        debug_enabled: bool,
        index: int,
        spawn_delay: float,
    ):
        env = os.environ.copy()
        env["SPRITEPRO_NET_ROLE"] = role
        env["SPRITEPRO_NET_BIND"] = bind_host
        env["SPRITEPRO_NET_HOST"] = connect_host
        env["SPRITEPRO_NET_PORT"] = str(port)
        env["SPRITEPRO_NET_COLOR"] = color
        env["SPRITEPRO_NET_ENTRY"] = entry
        env["SPRITEPRO_NET_DEBUG"] = "1" if debug_enabled else "0"
        env["SPRITEPRO_NET_INDEX"] = str(index)
        env["SPRITEPRO_NET_DELAY"] = str(spawn_delay)
        env["SPRITEPRO_NET_LOG_TAG"] = f"client_{index}"
        env["SPRITEPRO_LOG_DIR"] = str(script.parent / "spritepro_logs")
        if "SPRITEPRO_WINDOW_POS" not in env:
            env["SPRITEPRO_WINDOW_POS"] = _CLIENT_WINDOW_POSITIONS[
                index % len(_CLIENT_WINDOW_POSITIONS)
            ]
        subprocess.Popen([sys.executable, str(script)], env=env)

    env_role = os.environ.get("SPRITEPRO_NET_ROLE")
    if env_role:
        bind_host = os.environ.get("SPRITEPRO_NET_BIND", host)
        connect_host = os.environ.get("SPRITEPRO_NET_HOST", host)
        color = os.environ.get("SPRITEPRO_NET_COLOR", "red")
        env_entry = os.environ.get("SPRITEPRO_NET_ENTRY", entry)
        debug_enabled = os.environ.get("SPRITEPRO_NET_DEBUG") == "1"
        if env_role == "client":
            try:
                delay = float(os.environ.get("SPRITEPRO_NET_DELAY", "0"))
            except ValueError:
                delay = 0.0
            try:
                index = int(os.environ.get("SPRITEPRO_NET_INDEX", "0"))
            except ValueError:
                index = 0
            if delay > 0:
                # Delay applies to every client spawn in quick mode:
                # client_0 waits 1*delay, client_1 waits 2*delay, etc.
                time.sleep(delay * max(0, index + 1))
        entry = env_entry
        _run_worker(env_role, bind_host, connect_host, color, debug_enabled)
        return

    if use_lobby:

        def _on_lobby_start(net_client: NetClient, role_str: str) -> None:
            func = _find_entry(entry)
            _call_entry(func, net_client, role_str)

        from spritePro.readyScenes.multiplayer_lobby import run_multiplayer_lobby

        platform_env = os.environ.get("SPRITEPRO_PLATFORM", "pygame")

        # Для use_lobby и clients>1 поднимаем несколько процессов с лобби
        # (как для quick-режима), но без назначения ролей заранее.
        if (
            clients > 1
            and not os.environ.get("SPRITEPRO_LOBBY_SPAWNED")
        ):
            script = _get_script_path()
            base_env = os.environ.copy()
            base_env["SPRITEPRO_LOBBY_SPAWNED"] = "1"
            for idx in range(clients - 1):
                env_child = base_env.copy()
                env_child["SPRITEPRO_NET_LOG_TAG"] = f"lobby_client_{idx}"
                # Spread out lobby windows if using Pygame/desktop
                if platform_env.lower().strip() in {"pygame", "desktop"}:
                    positions = [
                        "520,40",  # client 1 (next to parent at 40,40)
                        "980,40",  # client 2
                        "520,600", # client 3
                    ]
                    env_child["SPRITEPRO_WINDOW_POS"] = positions[idx % len(positions)]
                subprocess.Popen([sys.executable, str(script)], env=env_child)
            os.environ["SPRITEPRO_LOBBY_SPAWNED"] = "1"

        run_multiplayer_lobby(_on_lobby_start, platform=platform_env)
        return

    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="SpritePro multiplayer runner (server/client/host/quick).",
    )
    parser.add_argument("--server", action="store_true", help="Запустить только сервер")
    parser.add_argument("--host_mode", action="store_true", help="Сервер + клиент")
    parser.add_argument("--quick", action="store_true", help="Хост + второй клиент")
    parser.add_argument("--host", default=host, help="IP сервера")
    parser.add_argument("--port", type=int, default=port, help="Порт сервера")
    parser.add_argument("--clients", type=int, default=clients, help="Кол-во клиентов")
    parser.add_argument(
        "--client_spawn_delay",
        type=float,
        default=client_spawn_delay,
        help="Задержка (сек) перед запуском каждого клиента в --quick",
    )
    parser.add_argument(
        "--tick_rate",
        type=int,
        default=server_tick_rate,
        help="Тикрейт сервера (только для режима --server)",
    )
    parser.add_argument("--net_debug", action="store_true", help="Сетевой debug в консоль")
    parser.add_argument(
        "--entry",
        default=entry,
        help="Функция входа (multiplayer_main или module:function)",
    )
    parser.add_argument(
        "--color", choices=("red", "blue"), default="red", help="Цвет игрока (host)"
    )
    if len(argv) == 0:
        argv = ["--quick"]
    args = parser.parse_args(argv)
    entry = args.entry
    host = args.host
    port = args.port
    server_tick_rate = max(1, int(args.tick_rate))
    net_debug = bool(args.net_debug or net_debug)

    if args.server:
        server = NetServer(host=host, port=port, debug=net_debug, name="server")
        server.start()
        while True:
            # Дренируем очередь сообщений сервера, чтобы она не росла бесконечно.
            drained = server.poll()
            if net_debug:
                for msg in drained:
                    _net_log(f"[NetServer:server] drained {_format_message(msg)}")
            time.sleep(1.0 / server_tick_rate)

    script = _get_script_path()
    log_dir = str(script.parent / "spritepro_logs")
    os.environ["SPRITEPRO_LOG_DIR"] = log_dir
    try:
        os.makedirs(log_dir, exist_ok=True)
    except OSError:
        pass
    connect_host = host if host not in ("0.0.0.0", "") else "127.0.0.1"

    if args.quick:
        for idx in range(args.clients - 1):
            client_color = "blue" if idx % 2 == 0 else "red"
            _spawn_client(
                script,
                "client",
                client_color,
                host,
                connect_host,
                net_debug,
                idx,
                args.client_spawn_delay,
            )
        _run_worker("host", host, connect_host, "red", net_debug)
        return

    if args.host_mode:
        _run_worker("host", host, connect_host, args.color, net_debug)
        return

    _run_worker("client", host, connect_host, "blue", net_debug)
