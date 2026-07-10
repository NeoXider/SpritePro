"""Тесты эргономики API: snake_case-алиасы твинов, s.spawn_scene, доступ к объектам RuntimeScene."""

import json

import pytest

import spritePro as s
from spritePro.components.tween import FrameTweenHandle
from spritePro.editor.runtime import RuntimeScene, SpawnedObject


def _make_scene_data() -> dict:
    return {
        "version": "1.0",
        "name": "Ergonomics Scene",
        "objects": [
            {
                "id": "panel01",
                "name": "panel",
                "sprite_shape": "rectangle",
                "sprite_color": [40, 40, 60],
                "transform": {"x": 160, "y": 120},
                "custom_data": {"width": 120, "height": 80},
            },
            {
                "id": "btn01",
                "name": "play_btn",
                "sprite_shape": "button",
                "sprite_color": [90, 180, 90],
                "transform": {"x": 160, "y": 200},
                "custom_data": {
                    "text": "Play",
                    "font_size": 20,
                    "text_color": [10, 20, 10],
                    "width": 100,
                    "height": 40,
                },
            },
        ],
    }


@pytest.fixture()
def runtime_scene(clean_game, tmp_path):
    scene_file = tmp_path / "scene.json"
    scene_file.write_text(json.dumps(_make_scene_data()), encoding="utf-8")
    rt = s.spawn_scene(scene_file, apply_camera=False)
    yield rt
    rt.dispose()


class TestFluentTweenChains:
    def test_do_move_returns_handle_and_chains(self, clean_game):
        sprite = s.Sprite("", size=(40, 40), pos=(50, 50))
        handle = sprite.DoMove((150, 150), duration=0.2)
        assert isinstance(handle, s.TweenHandle)
        chained = handle.SetLoops(2).SetYoyo(True).SetEase(s.Ease.Linear)
        assert chained is handle
        assert handle.tween.loop_count == 2
        assert handle.tween.yoyo is True
        handle.Kill()
        assert handle.tween.is_playing is False
        sprite.kill()

    def test_do_kill_returns_sprite(self, clean_game):
        sprite = s.Sprite("", size=(40, 40), pos=(50, 50))
        sprite.DoScale(2.0, duration=0.2)
        assert sprite.DoKill() is sprite
        sprite.kill()


class TestSpawnSceneTopLevel:
    def test_spawn_scene_exported(self):
        assert "spawn_scene" in s.__all__
        assert callable(s.spawn_scene)

    def test_spawn_scene_creates_runtime(self, runtime_scene):
        assert isinstance(runtime_scene, RuntimeScene)
        assert runtime_scene.get("panel") is not None
        assert isinstance(runtime_scene.get("play_btn"), s.Button)


class TestRuntimeSceneErgonomics:
    def test_getitem_returns_sprite(self, runtime_scene):
        assert runtime_scene["panel"] is runtime_scene.get("panel")
        assert runtime_scene["play_btn"] is runtime_scene.get("play_btn")

    def test_getitem_missing_lists_available(self, runtime_scene):
        with pytest.raises(KeyError) as exc_info:
            runtime_scene["missing"]
        message = str(exc_info.value)
        assert "panel" in message
        assert "play_btn" in message

    def test_contains(self, runtime_scene):
        assert "panel" in runtime_scene
        assert "play_btn" in runtime_scene
        assert "missing" not in runtime_scene
        assert 42 not in runtime_scene

    def test_len_and_iter(self, runtime_scene):
        assert len(runtime_scene) == 2
        spawned = list(runtime_scene)
        assert len(spawned) == 2
        assert all(isinstance(obj, SpawnedObject) for obj in spawned)
        assert {obj.data.name for obj in spawned} == {"panel", "play_btn"}

    def test_names(self, runtime_scene):
        assert runtime_scene.names() == ["panel", "play_btn"]

    def test_on_click_shortcut(self, runtime_scene):
        clicked = []
        btn = runtime_scene.on_click("play_btn", lambda: clicked.append(1))
        assert btn is runtime_scene.get("play_btn")
        btn.interactor.on_click()
        assert clicked == [1]

    def test_on_click_on_non_button_raises(self, runtime_scene):
        with pytest.raises(TypeError) as exc_info:
            runtime_scene.on_click("panel", lambda: None)
        assert "not a Button" in str(exc_info.value)

    def test_on_click_missing_raises_key_error(self, runtime_scene):
        with pytest.raises(KeyError):
            runtime_scene.on_click("missing", lambda: None)
