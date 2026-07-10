"""Тесты мультиплеера: relay, пинг, счётчики трафика (headless, loopback)."""

import random
import time

import pytest

from spritePro.networking import NetClient, NetServer
from spritePro.multiplayer import MultiplayerContext, NetDebug


def _wait_until(condition, timeout: float = 5.0, step: float = 0.02) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(step)
    return False


def _make_ctx(net, role, server=None, ping_interval=0.05):
    return MultiplayerContext(
        net=net,
        role=role,
        debug=NetDebug(enabled=False),
        server=server,
        ping_interval=ping_interval,
    )


@pytest.fixture()
def net_env():
    """Локальный сервер + фабрика клиентов на случайном порту, с автозакрытием."""
    port = random.randint(20000, 30000)
    server = NetServer(host="127.0.0.1", port=port, name="test_server")
    server.start()
    clients = []

    def make_client(name="test_client"):
        client = NetClient("127.0.0.1", port, name=name)
        client.connect(max_attempts=20, retry_delay=0.1)
        clients.append(client)
        return client

    yield server, make_client

    for client in clients:
        client.close()
    server.stop()


def _drain_events(client, events):
    """Собирает входящие сообщения клиента с нужными событиями."""
    collected = []

    def check():
        for msg in client.poll():
            if msg.get("event") in events:
                collected.append(msg)
        return bool(collected)

    _wait_until(check)
    return collected


def test_relay_between_clients(net_env):
    server, make_client = net_env
    c1 = make_client("c1")
    c2 = make_client("c2")
    assert _wait_until(lambda: server.clients_count == 2)

    c1.send("hello", {"value": 42})
    received = _drain_events(c2, {"hello"})
    assert received and received[0]["data"]["value"] == 42


def test_counters_grow_thread_safe(net_env):
    server, make_client = net_env
    c1 = make_client("c1")
    c2 = make_client("c2")
    assert _wait_until(lambda: server.clients_count == 2)

    for i in range(5):
        c1.send("tick", {"i": i})
    assert _wait_until(lambda: c2.get_stats()["messages_received"] >= 5)

    c1_stats = c1.get_stats()
    assert c1_stats["messages_sent"] >= 5
    assert c1_stats["bytes_sent"] > 0
    # assign_id всегда приходит первым — счётчики приема ненулевые
    assert c1_stats["messages_received"] >= 1
    assert c1_stats["bytes_received"] > 0

    srv_stats = server.get_stats()
    assert srv_stats["messages_received"] >= 5
    assert srv_stats["messages_sent"] >= 5
    assert srv_stats["bytes_sent"] > 0
    assert srv_stats["bytes_received"] > 0


def test_client_ping_measured(net_env):
    server, make_client = net_env
    client = make_client("pinger")
    ctx = _make_ctx(client, "client")

    def ping_ready():
        ctx.update_frame()
        return ctx.last_ping_ms > 0 or len(ctx._ping_samples) > 0

    assert _wait_until(ping_ready)
    assert ctx.ping_ms >= 0
    assert ctx.last_ping_ms >= 0


def test_ping_pong_hidden_from_user_poll(net_env):
    server, make_client = net_env
    c1 = make_client("c1")
    c2 = make_client("c2")
    ctx1 = _make_ctx(c1, "client")
    ctx2 = _make_ctx(c2, "client")

    seen_events = set()
    deadline = time.monotonic() + 1.5
    while time.monotonic() < deadline:
        ctx1.update_frame()
        ctx2.update_frame()
        for ctx in (ctx1, ctx2):
            for msg in ctx.poll():
                seen_events.add(msg.get("event"))
        time.sleep(0.02)

    assert "_ping" not in seen_events
    assert "_pong" not in seen_events
    # Пинги при этом реально измерялись
    assert len(ctx1._ping_samples) > 0
    assert len(ctx2._ping_samples) > 0


def test_ping_not_relayed_to_other_clients(net_env):
    server, make_client = net_env
    c1 = make_client("c1")
    c2 = make_client("c2")
    assert _wait_until(lambda: server.clients_count == 2)

    c1.send("_ping", {"t": time.monotonic(), "sender_id": 1})
    # _pong возвращается только отправителю
    assert _wait_until(lambda: any(m.get("event") == "_pong" for m in c1.poll()))

    time.sleep(0.3)
    c2_events = {m.get("event") for m in c2.poll()}
    assert "_ping" not in c2_events
    assert "_pong" not in c2_events


def test_host_ping_via_own_server(net_env):
    server, make_client = net_env
    host_client = make_client("host")
    ctx = _make_ctx(host_client, "host", server=server)
    assert ctx.is_host
    assert ctx.client_id == 0

    def ping_ready():
        ctx.update_frame()
        return len(ctx._ping_samples) > 0

    assert _wait_until(ping_ready)
    assert ctx.ping_ms >= 0


def test_get_net_stats(net_env):
    server, make_client = net_env
    host_client = make_client("host")
    ctx = _make_ctx(host_client, "host", server=server)
    other = make_client("other")
    assert _wait_until(lambda: server.clients_count == 2)

    ctx.send("state_sync", {"hp": 100})

    def stats_ready():
        ctx.update_frame()
        stats = ctx.get_net_stats()
        return stats["ping_ms"] > 0 or len(ctx._ping_samples) > 0

    assert _wait_until(stats_ready)

    stats = ctx.get_net_stats()
    assert stats["ping_ms"] >= 0
    assert stats["last_ping_ms"] >= 0
    assert stats["client_id"] == 0
    assert stats["is_host"] is True
    assert stats["connected"] is True
    assert ctx.is_connected is True
    assert stats["clients_count"] == 2
    assert stats["messages_sent"] >= 1
    assert stats["messages_received"] >= 1
    assert stats["bytes_sent"] > 0
    assert stats["bytes_received"] > 0
    assert stats["server"]["messages_sent"] >= 1
    assert stats["server"]["bytes_received"] > 0


def test_client_stats_and_disconnect(net_env):
    server, make_client = net_env
    client = make_client("c1")
    ctx = _make_ctx(client, "client")
    assert _wait_until(lambda: client.connected)
    assert ctx.is_connected

    stats = ctx.get_net_stats()
    assert stats["is_host"] is False
    assert stats["connected"] is True
    assert "server" not in stats

    client.close()
    assert _wait_until(lambda: not ctx.is_connected)
    assert ctx.get_net_stats()["connected"] is False
