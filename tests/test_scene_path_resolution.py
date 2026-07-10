"""Резолв пути сцены в spawn_scene: по имени, без расширения, из scenes/."""

import json
import os

import pytest

import spritePro as s
from spritePro.editor.path_utils import resolve_scene_path


SCENE_DATA = {
    "version": "1.0",
    "name": "t",
    "objects": [
        {
            "id": "o1",
            "name": "thing",
            "sprite_path": "",
            "sprite_shape": "rect",
            "transform": {"x": 10, "y": 10, "rotation": 0, "scale_x": 1, "scale_y": 1},
            "z_index": 0,
            "active": True,
            "custom_data": {"width": 10, "height": 10},
        }
    ],
}


@pytest.fixture()
def scene_dir(tmp_path, monkeypatch):
    (tmp_path / "scenes").mkdir()
    path = tmp_path / "scenes" / "level.json"
    path.write_text(json.dumps(SCENE_DATA), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestResolveScenePath:
    def test_full_relative_path(self, scene_dir):
        assert resolve_scene_path("scenes/level.json").is_file()

    def test_bare_name_without_extension(self, scene_dir):
        assert resolve_scene_path("level").name == "level.json"

    def test_name_with_extension_found_in_scenes(self, scene_dir):
        assert resolve_scene_path("level.json").is_file()

    def test_missing_raises_with_candidates(self, scene_dir):
        with pytest.raises(FileNotFoundError) as err:
            resolve_scene_path("nope")
        assert "scenes" in str(err.value)

    def test_spawn_scene_by_bare_name(self, scene_dir, clean_game):
        rt = s.spawn_scene("level", apply_camera=False)
        assert rt.names() == ["thing"]
        rt.dispose()
