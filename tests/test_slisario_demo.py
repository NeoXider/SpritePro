"""Тесты демо «Слизарио»: host-authoritative протокол (еда, боты, игроки).

Сеть подменяется FakeNet: сообщения «доставляются» через ctx._frame_messages,
поэтому проверяется именно игровая логика обмена, а не транспорт.
"""

import sys
from pathlib import Path

import pytest

import spritePro as s
from spritePro.multiplayer import MultiplayerContext, NetDebug

_DEMO_DIR = Path(__file__).resolve().parent.parent / "spritePro" / "demoGames" / "slisario_andrulok"


class FakeNet:
    def __init__(self):
        self.sent = []
        self.connected = True

    def send(self, event, data=None):
        self.sent.append((event, dict(data or {})))

    def poll(self, n=500):
        return []

    def get_stats(self):
        return {}


def _inject(scene, event, data):
    """Кладёт сообщение в очередь кадра и обрабатывает его сценой."""
    scene.ctx._frame_messages = [{"event": event, "data": data}]
    scene._handle_net_messages()
    scene.ctx._frame_messages = []


@pytest.fixture()
def game_scene_cls(game):
    # Демо — не пакет: его модули (game, scenes, ui) импортируются от папки демо.
    sys.path.insert(0, str(_DEMO_DIR))
    try:
        from scenes.game_scene import GameScene

        yield GameScene
    finally:
        sys.path.remove(str(_DEMO_DIR))


def _make_scene(game_scene_cls, role, client_id=None):
    net = FakeNet()
    ctx = MultiplayerContext(net=net, role=role, client_id=client_id, debug=NetDebug(enabled=False))
    s.multiplayer_ctx = ctx
    scene = game_scene_cls(net=net, role=role)
    return scene, net


@pytest.fixture()
def client_scene(clean_game, game_scene_cls):
    scene, net = _make_scene(game_scene_cls, "client", client_id=2)
    yield scene, net
    s.multiplayer_ctx = None


@pytest.fixture()
def host_scene(clean_game, game_scene_cls):
    scene, net = _make_scene(game_scene_cls, "host")
    yield scene, net
    s.multiplayer_ctx = None


def _food_snapshot(count=10):
    return [{"id": i, "pos": [200 + i * 30, 300], "color": [255, 0, 0]} for i in range(count)]


def test_client_late_join_food_snapshot(client_scene):
    scene, _ = client_scene
    assert not scene.is_authority
    assert len(scene.food.foods) == 0

    _inject(scene, "food_state", {"foods": _food_snapshot(), "sender_id": 0})
    assert len(scene.food.foods) == 10


def test_client_eats_only_after_host_confirm(client_scene):
    scene, net = client_scene
    _inject(scene, "food_state", {"foods": _food_snapshot(), "sender_id": 0})

    net.sent.clear()
    scene._eat(3)
    assert 3 not in scene.food.foods, "еда убирается локально сразу"
    assert ("eat_food", {"food_id": 3, "sender_id": 2}) in net.sent
    assert scene.score == 0, "рост до подтверждения запрещён"

    _inject(scene, "food_eaten", {"food_id": 3, "eater_id": 2, "sender_id": 0})
    assert scene.score == 1

    # Снапшот, собранный хостом до обработки eat_food, не воскрешает еду.
    _inject(scene, "food_state", {"foods": _food_snapshot(), "sender_id": 0})
    assert 3 not in scene.food.foods


def test_client_remote_player_lifecycle(client_scene):
    scene, _ = client_scene
    _inject(scene, "player_state", {
        "sender_id": 5, "head": [500, 500], "angle": 0,
        "segments": [[490, 500], [480, 500]], "color": [200, 100, 100], "score": 7,
    })
    assert scene.remote_snakes[5].segment_count == 2

    _inject(scene, "player_died", {"sender_id": 5, "segments": [[490, 500], [480, 500]]})
    assert 5 not in scene.remote_snakes

    _inject(scene, "player_state", {
        "sender_id": 7, "head": [1, 1], "angle": 0, "segments": [], "color": [1, 2, 3],
    })
    _inject(scene, "player_left", {"id": 7, "sender_id": 0})
    assert 7 not in scene.remote_snakes


def test_client_bot_views_follow_bot_state(client_scene):
    scene, _ = client_scene
    _inject(scene, "bot_state", {"sender_id": 0, "bots": [
        {"id": 0, "head": [700, 700], "angle": 0, "segments": [[690, 700]], "color": [90, 90, 200]},
        {"id": 1, "head": [800, 800], "angle": 0, "segments": [[790, 800]], "color": [90, 200, 90]},
    ]})
    assert set(scene.bot_views) == {0, 1}

    _inject(scene, "bot_state", {"sender_id": 0, "bots": [
        {"id": 1, "head": [810, 800], "angle": 0, "segments": [[800, 800]], "color": [90, 200, 90]},
    ]})
    assert set(scene.bot_views) == {1}, "исчезнувший бот убирается"


def test_host_confirms_eat_once(host_scene):
    scene, net = host_scene
    assert scene.is_authority
    assert scene.food.foods and scene.bots

    food_id = next(iter(scene.food.foods))
    net.sent.clear()
    _inject(scene, "eat_food", {"food_id": food_id, "sender_id": 2})
    assert food_id not in scene.food.foods
    assert ("food_eaten", {"food_id": food_id, "eater_id": 2, "sender_id": 0}) in net.sent

    net.sent.clear()
    _inject(scene, "eat_food", {"food_id": food_id, "sender_id": 3})
    assert not net.sent, "повторное поедание той же еды не подтверждается"


def test_host_turns_dead_bodies_into_food(host_scene):
    scene, net = host_scene
    before = len(scene.food.foods)
    _inject(scene, "player_died", {"sender_id": 2, "segments": [[900, 900], [910, 900], [920, 900]]})
    assert len(scene.food.foods) == before + 3

    _inject(scene, "player_state", {
        "sender_id": 4, "head": [600, 600], "angle": 0, "segments": [[590, 600]], "color": [5, 6, 7],
    })
    net.sent.clear()
    _inject(scene, "client_disconnected", {"client_id": 4})
    assert 4 not in scene.remote_snakes
    assert any(e == "player_left" and d.get("id") == 4 for e, d in net.sent)


def test_host_death_and_restart_keeps_food(host_scene):
    scene, net = host_scene
    before = len(scene.food.foods)
    net.sent.clear()
    scene._die()
    assert scene.game_over
    assert any(e == "player_died" for e, _ in net.sent)
    assert len(scene.food.foods) > before, "тело превращается в еду"

    foods_before = {fid: f.rect.center for fid, f in scene.food.foods.items()}
    scene._restart()
    assert not scene.game_over
    kept = {fid: f.rect.center for fid, f in scene.food.foods.items() if fid in foods_before}
    assert kept == foods_before, "рестарт хоста не перемешивает еду"
