"""Тесты UX редактора сцен: панель инструментов viewport, кнопка «+» иерархии, меню Create."""

import pygame
import pytest
from pygame.math import Vector2

from spritePro.editor import event_actions, file_actions, settings_actions
from spritePro.editor.editor import SpriteEditor, ToolType


def _mousedown(editor, pos, button=1):
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(int(pos[0]), int(pos[1])), button=button)
    event_actions.handle_mousedown(editor, event)


def _menu_item_rect(editor, label):
    return next(rect for item, rect in editor._create_menu["items"] if item["label"] == label)


@pytest.fixture()
def editor(game, monkeypatch):
    monkeypatch.setattr(file_actions, "get_last_scene_path", lambda: None)
    monkeypatch.setattr(settings_actions, "load_into_editor", lambda _editor: None)
    ed = SpriteEditor((1000, 700))
    ed.render()
    yield ed
    pygame.display.set_mode((320, 240))


def test_tool_panel_rendered_and_click_switches_tool(editor):
    buttons = dict(editor._viewport_tool_buttons)
    assert set(buttons) == {ToolType.SELECT, ToolType.MOVE, ToolType.ROTATE, ToolType.SCALE}
    viewport = editor._get_viewport_rect()
    for rect in buttons.values():
        assert viewport.contains(rect)
    assert editor.current_tool == ToolType.SELECT
    _mousedown(editor, buttons[ToolType.MOVE].center)
    assert editor.current_tool == ToolType.MOVE
    editor.render()
    _mousedown(editor, dict(editor._viewport_tool_buttons)[ToolType.SCALE].center)
    assert editor.current_tool == ToolType.SCALE


def test_hierarchy_plus_opens_menu_and_creates_at_viewport_center(editor):
    btn = editor._hierarchy_add_button_rect
    assert btn is not None
    _mousedown(editor, btn.center)
    assert editor._create_menu is not None
    expected = editor.screen_to_world(Vector2(editor._get_viewport_rect().center))
    _mousedown(editor, _menu_item_rect(editor, "Rectangle").center)
    assert editor._create_menu is None
    obj = editor.scene.objects[-1]
    assert obj.sprite_shape == "rectangle"
    assert obj.transform.x == pytest.approx(expected.x)
    assert obj.transform.y == pytest.approx(expected.y)


def test_viewport_right_click_empty_creates_at_world_pos(editor):
    viewport = editor._get_viewport_rect()
    click = (viewport.centerx + 150, viewport.centery + 90)
    _mousedown(editor, click, button=3)
    assert editor._create_menu is not None
    expected = editor.screen_to_world(Vector2(click))
    assert editor._create_menu["world_pos"] == expected
    _mousedown(editor, _menu_item_rect(editor, "Circle").center)
    obj = editor.scene.objects[-1]
    assert obj.sprite_shape == "circle"
    assert obj.transform.x == pytest.approx(expected.x)
    assert obj.transform.y == pytest.approx(expected.y)


def test_viewport_right_click_on_object_does_not_open_create_menu(editor):
    world = editor.screen_to_world(Vector2(editor._get_viewport_rect().center))
    editor.add_primitive("rectangle", world)
    editor.render()
    _mousedown(editor, editor._get_viewport_rect().center, button=3)
    assert editor._create_menu is None


def test_click_outside_closes_create_menu_without_creating(editor):
    _mousedown(editor, editor._hierarchy_add_button_rect.center)
    assert editor._create_menu is not None
    count = len(editor.scene.objects)
    outside = (editor._create_menu["rect"].right + 50, editor._create_menu["rect"].bottom + 50)
    _mousedown(editor, outside)
    assert editor._create_menu is None
    assert len(editor.scene.objects) == count


def test_tools_menu_removed_from_menubar(editor):
    assert "tools" not in editor._toolbar_buttons
    assert {"file", "game_object", "view"} <= set(editor._toolbar_buttons)
