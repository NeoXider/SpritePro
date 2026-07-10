"""Тесты редактора сцен: кнопки, два пайплайна доступа к объектам, иерархия parent/child."""

import json

import pygame
import pytest

import spritePro as s
from spritePro.editor import history_actions
from spritePro.editor import sprite_types as st
from spritePro.editor.runtime import spawn_scene
from spritePro.editor.scene import Scene, SceneObject, Transform


def _make_scene_data() -> dict:
    return {
        "version": "1.0",
        "name": "Test Scene",
        "objects": [
            {
                "id": "panel01",
                "name": "panel",
                "sprite_shape": "rectangle",
                "sprite_color": [40, 40, 60],
                "transform": {"x": 400, "y": 300},
                "custom_data": {"width": 300, "height": 200},
            },
            {
                "id": "label01",
                "name": "label",
                "sprite_shape": "text",
                "sprite_color": [200, 220, 255],
                "transform": {"x": 400, "y": 260},
                "parent": "panel01",
                "custom_data": {"text": "Hello", "font_size": 30},
            },
            {
                "id": "btn01",
                "name": "play_btn",
                "sprite_shape": "button",
                "sprite_color": [90, 180, 90],
                "transform": {"x": 400, "y": 400},
                "custom_data": {
                    "text": "Play",
                    "font_size": 26,
                    "text_color": [10, 20, 10],
                    "width": 200,
                    "height": 60,
                },
            },
        ],
    }


@pytest.fixture()
def runtime_scene(clean_game, tmp_path):
    scene_file = tmp_path / "scene.json"
    scene_file.write_text(json.dumps(_make_scene_data()), encoding="utf-8")
    rt = spawn_scene(scene_file, apply_camera=False)
    yield rt
    rt.dispose()


def test_button_spawned_from_editor_scene(runtime_scene):
    btn = runtime_scene.get("play_btn")
    assert isinstance(btn, s.Button)
    assert btn.text_sprite.text == "Play"
    assert btn.text_sprite.font_size == 26
    assert btn.base_color == (90, 180, 90)
    assert btn.rect.size == (200, 60)
    assert btn.rect.center == (400, 400)


def test_button_on_click_via_scene_handle(runtime_scene):
    clicked = []
    btn = runtime_scene.Button("play_btn", on_click=lambda: clicked.append(1))
    assert btn is runtime_scene.get("play_btn")
    assert btn.interactor.on_click is not None
    btn.interactor.on_click()
    assert clicked == [1]


def test_get_without_arguments_keeps_editor_settings(runtime_scene):
    label = runtime_scene.TextSprite("label")
    assert label.text == "Hello"
    assert label.font_size == 30
    assert tuple(label.color) == (200, 220, 255)
    assert runtime_scene.Button("play_btn").text_sprite.text == "Play"


def test_get_with_arguments_overrides_only_passed(runtime_scene):
    label = runtime_scene.TextSprite("label", text="Changed")
    assert label is runtime_scene.get("label")
    assert label.text == "Changed"
    assert label.font_size == 30
    assert tuple(label.color) == (200, 220, 255)

    btn = runtime_scene.Button("play_btn", text="Go", base_color=(1, 2, 3))
    assert btn.text_sprite.text == "Go"
    assert btn.base_color == (1, 2, 3)
    assert btn.text_sprite.font_size == 26


def test_sprite_pipeline_overrides_only_passed(runtime_scene):
    panel = runtime_scene.get("panel")
    same = runtime_scene.Sprite("panel")
    assert same is panel
    runtime_scene.Sprite("panel", speed=5)
    assert panel.speed == 5


def test_runtime_parent_applied_and_moves_children(runtime_scene):
    panel = runtime_scene.get("panel")
    label = runtime_scene.get("label")
    assert label.parent is panel
    assert label in panel.children
    before = label.rect.center
    panel.set_position((500, 350))
    assert label.rect.center == (before[0] + 100, before[1] + 50)


def test_get_missing_object(runtime_scene):
    assert runtime_scene.get("missing") is None
    with pytest.raises(KeyError):
        runtime_scene.Button("missing")


def test_scene_object_parent_serialization_roundtrip():
    obj = SceneObject(name="child", parent="parent_id")
    restored = SceneObject.from_dict(obj.to_dict())
    assert restored.parent == "parent_id"
    # Обратная совместимость: старые сцены без поля parent
    legacy = SceneObject.from_dict({"id": "a1", "name": "old"})
    assert legacy.parent is None


def test_remove_parent_frees_children():
    scene = Scene()
    parent = SceneObject(id="p1", name="parent")
    child = SceneObject(id="c1", name="child", parent="p1")
    scene.add_object(parent)
    scene.add_object(child)
    scene.remove_object("p1")
    assert scene.get_object("c1") is not None
    assert scene.get_object("c1").parent is None


def test_can_set_parent_rejects_cycles():
    scene = Scene()
    a = SceneObject(id="a", name="a")
    b = SceneObject(id="b", name="b", parent="a")
    scene.add_object(a)
    scene.add_object(b)
    assert scene.can_set_parent("b", None)
    assert not scene.can_set_parent("a", "a")
    assert not scene.can_set_parent("a", "b")
    assert scene.get_descendants("a") == [b]


class _FakeEditor:
    """Минимальный editor для проверки снапшотов undo/redo."""

    def __init__(self, scene: Scene):
        self.scene = scene
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50
        self.modified = False
        self.selected_objects = []
        self.camera = pygame.math.Vector2(0, 0)
        self.zoom = 1.0

    def _sync_scene_camera(self):
        pass


def test_undo_redo_preserves_parent():
    scene = Scene()
    parent = SceneObject(id="p1", name="parent", transform=Transform(x=10, y=20))
    child = SceneObject(id="c1", name="child")
    scene.add_object(parent)
    scene.add_object(child)
    editor = _FakeEditor(scene)

    history_actions.save_state(editor, mark_modified=False)
    child.parent = "p1"
    history_actions.save_state(editor)

    history_actions.undo(editor)
    assert editor.scene.get_object("c1").parent is None
    history_actions.redo(editor)
    assert editor.scene.get_object("c1").parent == "p1"


def test_button_preview_surface(game):
    surf = st.render_button_surface(120, 40, (200, 200, 200), "Play", 20, (0, 0, 0))
    assert surf.get_size() == (120, 40)
