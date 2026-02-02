from __future__ import annotations

import json
import socket
import threading
from queue import Queue, Empty
from typing import Any, Dict, Optional, Tuple, List


NetMessage = Dict[str, Any]


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
    ) -> None:
        self.host = host
        self.port = port
        self.relay = relay
        self._server: Optional[socket.socket] = None
        self._clients: List[socket.socket] = []
        self._lock = threading.Lock()
        self._queue: "Queue[Tuple[Optional[socket.socket], NetMessage]]" = Queue()
        self._running = False

    def start(self) -> None:
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
                with self._lock:
                    self._clients.append(conn)
                thread = threading.Thread(
                    target=self._handle_client, args=(conn,), daemon=True
                )
                thread.start()

    def _handle_client(self, conn: socket.socket) -> None:
        buffer = ""
        try:
            while self._running:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    msg = _decode_message(line.strip())
                    if msg is None:
                        continue
                    self._queue.put((conn, msg))
                    if self.relay:
                        self._broadcast_raw(data, exclude=conn)
        finally:
            with self._lock:
                if conn in self._clients:
                    self._clients.remove(conn)
            try:
                conn.close()
            except OSError:
                pass

    def _broadcast_raw(self, raw: bytes, exclude: Optional[socket.socket] = None) -> None:
        with self._lock:
            for client in list(self._clients):
                if client is exclude:
                    continue
                try:
                    client.sendall(raw)
                except OSError:
                    pass

    def broadcast(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        raw = _encode_message(event, data)
        self._broadcast_raw(raw)

    def poll(self, max_messages: int = 100) -> List[NetMessage]:
        messages: List[NetMessage] = []
        for _ in range(max_messages):
            try:
                _sender, msg = self._queue.get_nowait()
            except Empty:
                break
            messages.append(msg)
        return messages

    def stop(self) -> None:
        self._running = False
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass


class NetClient:
    """Simple TCP client with JSON line protocol."""

    def __init__(self, host: str, port: int = 5050) -> None:
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._queue: "Queue[NetMessage]" = Queue()
        self._running = False

    def connect(self) -> None:
        if self._running:
            return
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._running = True
        thread = threading.Thread(target=self._recv_loop, daemon=True)
        thread.start()

    def _recv_loop(self) -> None:
        buffer = ""
        assert self._sock is not None
        try:
            while self._running:
                data = self._sock.recv(1024)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    msg = _decode_message(line.strip())
                    if msg is not None:
                        self._queue.put(msg)
        finally:
            self._running = False

    def send(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        if not self._sock:
            return
        try:
            self._sock.sendall(_encode_message(event, data))
        except OSError:
            pass

    def poll(self, max_messages: int = 100) -> List[NetMessage]:
        messages: List[NetMessage] = []
        for _ in range(max_messages):
            try:
                msg = self._queue.get_nowait()
            except Empty:
                break
            messages.append(msg)
        return messages

    def close(self) -> None:
        self._running = False
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass


def run(
    argv: Optional[List[str]] = None,
    entry: str = "multiplayer_main",
    host: str = "127.0.0.1",
    port: int = 5050,
    clients: int = 2,
) -> None:
    """Запускает мультиплеер для вашей игры.

    Ожидается функция `multiplayer_main(net, role, color)` в вашем скрипте.
    Если аргументы не переданы, запускается быстрый режим
    (host + второй клиент) на localhost:5050.
    """
    import argparse
    import inspect
    import os
    import sys
    import time
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
                "Создайте def multiplayer_main(net, role, color): ... "
                "или укажите entry='module:function'."
            )
        return func

    def _call_entry(func, net, role: str, color: str) -> None:
        params = list(inspect.signature(func).parameters.values())
        if len(params) >= 3:
            func(net, role, color)
        elif len(params) == 2:
            func(net, role)
        elif len(params) == 1:
            func(net)
        else:
            func()

    def _run_worker(role: str, bind_host: str, connect_host: str, color: str) -> None:
        if role == "host":
            server = NetServer(host=bind_host, port=port)
            server.start()
        if connect_host in ("0.0.0.0", ""):
            connect_host = "127.0.0.1"
        net = NetClient(connect_host, port)
        net.connect()
        func = _resolve_entry(entry)
        _call_entry(func, net, role, color)

    def _get_script_path() -> Path:
        main_module = sys.modules.get("__main__")
        main_file = getattr(main_module, "__file__", None)
        candidate = Path(main_file or sys.argv[0]).resolve()
        if not candidate.exists():
            raise RuntimeError(
                "run() нужно вызывать из файла. "
                "Не удалось определить путь к текущему скрипту."
            )
        return candidate

    def _spawn_client(script: Path, role: str, color: str, bind_host: str, connect_host: str):
        env = os.environ.copy()
        env["SPRITEPRO_NET_ROLE"] = role
        env["SPRITEPRO_NET_BIND"] = bind_host
        env["SPRITEPRO_NET_HOST"] = connect_host
        env["SPRITEPRO_NET_PORT"] = str(port)
        env["SPRITEPRO_NET_COLOR"] = color
        env["SPRITEPRO_NET_ENTRY"] = entry
        subprocess.Popen([sys.executable, str(script)], env=env)

    env_role = os.environ.get("SPRITEPRO_NET_ROLE")
    if env_role:
        bind_host = os.environ.get("SPRITEPRO_NET_BIND", host)
        connect_host = os.environ.get("SPRITEPRO_NET_HOST", host)
        color = os.environ.get("SPRITEPRO_NET_COLOR", "red")
        env_entry = os.environ.get("SPRITEPRO_NET_ENTRY", entry)
        entry = env_entry
        _run_worker(env_role, bind_host, connect_host, color)
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

    if args.server:
        server = NetServer(host=host, port=port)
        server.start()
        while True:
            time.sleep(0.2)

    script = _get_script_path()
    connect_host = host if host not in ("0.0.0.0", "") else "127.0.0.1"

    if args.quick:
        if args.clients < 2:
            raise ValueError("Для --quick нужно минимум 2 клиента.")
        _spawn_client(script, "client", "blue", host, connect_host)
        _run_worker("host", host, connect_host, "red")
        return

    if args.host_mode:
        _run_worker("host", host, connect_host, args.color)
        return

    _run_worker("client", host, connect_host, "blue")
