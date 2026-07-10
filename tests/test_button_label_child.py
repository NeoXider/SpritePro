"""Unity-стиль надписи кнопки: текст — дочерний объект в иерархии сцены."""

import json

import pytest

import spritePro as s


def _scene(objects):
    return {"version": "1.0", "name": "t", "objects": objects}


def _button(obj_id="b1", name="btn", parent=None, custom=None):
    return {
        "id": obj_id,
        "name": name,
        "sprite_path": "",
        "sprite_shape": "button",
        "transform": {"x": 100, "y": 100, "rotation": 0, "scale_x": 1, "scale_y": 1},
        "z_index": 1,
        "active": True,
        "parent": parent,
        "custom_data": custom or {"width": 200, "height": 60},
    }


def _text(obj_id="t1", name="Text", parent=None, text="Play", x=100, y=100):
    return {
        "id": obj_id,
        "name": name,
        "sprite_path": "",
        "sprite_shape": "text",
        "transform": {"x": x, "y": y, "rotation": 0, "scale_x": 1, "scale_y": 1},
        "z_index": 2,
        "active": True,
        "parent": parent,
        "custom_data": {"text": text, "font_size": 24},
    }


def _spawn(tmp_path, objects):
    path = tmp_path / "scene.json"
    path.write_text(json.dumps(_scene(objects)), encoding="utf-8")
    return s.spawn_scene(path, apply_camera=False)


class TestButtonLabelFromChild:
    def test_label_taken_from_child_text(self, clean_game, tmp_path):
        rt = _spawn(tmp_path, [_button(), _text(parent="b1", text="GO!")])
        btn = rt.get("btn")
        assert btn.text_sprite.text == "GO!"
        rt.dispose()

    def test_child_text_not_spawned_separately(self, clean_game, tmp_path):
        rt = _spawn(tmp_path, [_button(), _text(parent="b1")])
        assert rt.get("Text") is None
        assert rt.names() == ["btn"]
        rt.dispose()

    def test_button_without_child_has_empty_label(self, clean_game, tmp_path):
        rt = _spawn(tmp_path, [_button()])
        assert rt.get("btn").text_sprite.text == ""
        rt.dispose()

    def test_legacy_custom_data_text_still_works(self, clean_game, tmp_path):
        rt = _spawn(
            tmp_path,
            [_button(custom={"width": 200, "height": 60, "text": "Legacy", "font_size": 24})],
        )
        assert rt.get("btn").text_sprite.text == "Legacy"
        rt.dispose()

    def test_label_offset_applied(self, clean_game, tmp_path):
        rt = _spawn(tmp_path, [_button(), _text(parent="b1", x=100, y=80)])
        btn = rt.get("btn")
        assert btn.text_sprite.rect.centery == 80
        rt.dispose()


class TestEditorAddButton:
    def test_add_button_creates_child_text(self, clean_game):
        from spritePro.editor.editor import SpriteEditor
        from spritePro.editor import object_actions

        ed = SpriteEditor()
        ed.scene.objects.clear()
        btn = object_actions.add_button(ed)
        children = ed.scene.get_children(btn.id)
        assert len(children) == 1
        assert children[0].sprite_shape == "text"
        assert children[0].custom_data.get("text") == "Button"
        assert "text" not in btn.custom_data
