"""Верхняя панель инструментов редактора."""

import pygame

from . import layouts
from . import theme


def _menu_specs(editor):
    current_tool = editor.current_tool
    return (
        {
            "id": "file",
            "label": "File",
            "items": (
                {"label": "New Scene", "shortcut": "Ctrl+N", "action": editor._new_scene},
                {"label": "Open...", "shortcut": "Ctrl+O", "action": editor._load_scene},
                {"label": "Save", "shortcut": "Ctrl+S", "action": editor._save_scene},
                {
                    "label": "Save As...",
                    "shortcut": "Ctrl+Shift+S",
                    "action": editor._save_scene_as,
                },
                {"label": "Run Game", "shortcut": "F5", "action": editor._run_project},
            ),
        },
        {
            "id": "game_object",
            "label": "GameObject",
            "items": (
                {"label": "New Image...", "shortcut": "", "action": editor._add_sprite_dialog},
                {"label": "New Text", "shortcut": "Ctrl+Shift+T", "action": editor.add_text},
                {
                    "label": "New Rectangle",
                    "shortcut": "",
                    "action": lambda: editor.add_primitive("rectangle"),
                },
                {
                    "label": "New Circle",
                    "shortcut": "",
                    "action": lambda: editor.add_primitive("circle"),
                },
                {
                    "label": "New Ellipse",
                    "shortcut": "",
                    "action": lambda: editor.add_primitive("ellipse"),
                },
            ),
        },
        {
            "id": "tools",
            "label": "Tools",
            "items": (
                {
                    "label": "Select",
                    "shortcut": "V",
                    "checked": current_tool == editor._toolbar_tools_list[0][0],
                    "action": lambda: _set_tool(editor, editor._toolbar_tools_list[0][0]),
                },
                {
                    "label": "Move",
                    "shortcut": "G",
                    "checked": current_tool == editor._toolbar_tools_list[1][0],
                    "action": lambda: _set_tool(editor, editor._toolbar_tools_list[1][0]),
                },
                {
                    "label": "Rotate",
                    "shortcut": "R",
                    "checked": current_tool == editor._toolbar_tools_list[2][0],
                    "action": lambda: _set_tool(editor, editor._toolbar_tools_list[2][0]),
                },
                {
                    "label": "Scale",
                    "shortcut": "T",
                    "checked": current_tool == editor._toolbar_tools_list[3][0],
                    "action": lambda: _set_tool(editor, editor._toolbar_tools_list[3][0]),
                },
            ),
        },
        {
            "id": "view",
            "label": "View",
            "items": (
                {
                    "label": "Grid",
                    "shortcut": "",
                    "checked": editor.scene.grid_visible,
                    "action": editor._toggle_grid_visibility,
                },
                {
                    "label": "Grid Labels",
                    "shortcut": "",
                    "checked": editor.scene.grid_labels_visible,
                    "action": editor._toggle_grid_labels,
                },
                {
                    "label": "Snap to Grid",
                    "shortcut": "",
                    "checked": editor.scene.snap_to_grid,
                    "action": editor._toggle_snap,
                },
                {
                    "label": "Settings...",
                    "shortcut": "F1",
                    "action": lambda: editor.window_manager.toggle("settings"),
                },
            ),
        },
    )


def _set_tool(editor, tool_type) -> None:
    editor.current_tool = tool_type


def close_menu(editor) -> None:
    editor._toolbar_menu = None


def _measure_menu_width(editor, items) -> int:
    font = editor.font
    width = theme.TOOLBAR_MENU_MIN_WIDTH
    for item in items:
        marker_width = font.size("[x] ")[0]
        label_width = font.size(item["label"])[0]
        shortcut = item.get("shortcut", "")
        shortcut_width = font.size(shortcut)[0] if shortcut else 0
        width = max(
            width,
            marker_width
            + label_width
            + shortcut_width
            + theme.TOOLBAR_MENU_ITEM_PADDING_X * 2
            + (theme.TOOLBAR_MENU_SHORTCUT_GAP if shortcut else 0),
        )
    return width


def _open_menu(editor, menu_id: str, button_rect: pygame.Rect, items) -> None:
    width = _measure_menu_width(editor, items)
    height = len(items) * theme.TOOLBAR_MENU_ITEM_HEIGHT + 4
    x = min(button_rect.x, max(6, editor.width - width - 6))
    y = min(button_rect.bottom + 2, max(4, editor.height - height - 4))
    menu_rect = pygame.Rect(x, y, width, height)
    item_rects = []
    for index, item in enumerate(items):
        item_rect = pygame.Rect(
            x + 2,
            y + 2 + index * theme.TOOLBAR_MENU_ITEM_HEIGHT,
            width - 4,
            theme.TOOLBAR_MENU_ITEM_HEIGHT,
        )
        item_rects.append((item, item_rect))
    editor._toolbar_menu = {
        "id": menu_id,
        "button_rect": button_rect.copy(),
        "rect": menu_rect,
        "items": item_rects,
    }


def _draw_menu_button(editor, rect: pygame.Rect, label: str, active: bool, hovered: bool) -> None:
    if active:
        bg = editor.colors["ui_accent"]
        text_color = theme.COLORS["ui_selected_bg"]
    elif hovered:
        bg = theme.COLORS["ui_hover"]
        text_color = editor.colors["ui_text"]
    else:
        bg = None
        text_color = editor.colors["ui_text"]
    if bg is not None:
        pygame.draw.rect(editor.screen, bg, rect, border_radius=4)
    text = editor.font_bold.render(label, True, text_color)
    editor.screen.blit(
        text,
        (rect.x + theme.TOOLBAR_MENU_BUTTON_PADDING_X, rect.y + 5),
    )


def _draw_action_button(editor, rect: pygame.Rect, label: str, hovered: bool) -> None:
    bg = (46, 88, 52) if not hovered else (60, 112, 68)
    border = (90, 150, 100) if not hovered else (120, 190, 130)
    pygame.draw.rect(editor.screen, bg, rect, border_radius=4)
    pygame.draw.rect(editor.screen, border, rect, 1, border_radius=4)
    text = editor.font_bold.render(label, True, (230, 244, 232))
    editor.screen.blit(
        text,
        (
            rect.x + (rect.width - text.get_width()) // 2,
            rect.y + (rect.height - text.get_height()) // 2,
        ),
    )


def _render_open_menu(editor) -> None:
    menu = getattr(editor, "_toolbar_menu", None)
    if not menu:
        return
    mouse_pos = pygame.mouse.get_pos()
    menu_rect = menu["rect"]
    pygame.draw.rect(editor.screen, (36, 36, 42), menu_rect, border_radius=4)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_input_border"], menu_rect, 1, border_radius=4)
    marker_width = editor.font.size("[x] ")[0]
    for item, item_rect in menu["items"]:
        hovered = item_rect.collidepoint(mouse_pos)
        checked = item.get("checked", False)
        if hovered:
            pygame.draw.rect(editor.screen, theme.COLORS["ui_hover"], item_rect, border_radius=3)
        label_color = editor.colors["ui_text"]
        shortcut_color = (165, 165, 180) if not hovered else (205, 205, 220)
        marker = "[x]" if checked else ""
        marker_surface = editor.font.render(marker, True, label_color)
        label_surface = editor.font.render(item["label"], True, label_color)
        shortcut = item.get("shortcut", "")
        shortcut_surface = editor.font.render(shortcut, True, shortcut_color) if shortcut else None
        text_y = item_rect.y + (item_rect.height - label_surface.get_height()) // 2
        marker_x = item_rect.x + theme.TOOLBAR_MENU_ITEM_PADDING_X
        editor.screen.blit(marker_surface, (marker_x, text_y))
        editor.screen.blit(label_surface, (marker_x + marker_width, text_y))
        if shortcut_surface is not None:
            editor.screen.blit(
                shortcut_surface,
                (
                    item_rect.right
                    - shortcut_surface.get_width()
                    - theme.TOOLBAR_MENU_ITEM_PADDING_X,
                    item_rect.y + (item_rect.height - shortcut_surface.get_height()) // 2,
                ),
            )


def render(editor) -> None:
    screen = editor.screen
    font_bold = editor.font_bold
    colors = editor.colors
    w = editor.width
    top = theme.UI_TOP_HEIGHT

    rect = pygame.Rect(0, 0, w, top)
    pygame.draw.rect(screen, colors["ui_bg"], rect)
    pygame.draw.line(screen, colors["ui_border"], (0, top), (w, top), 1)

    menus = _menu_specs(editor)
    menu_widths = [
        font_bold.size(menu["label"])[0] + theme.TOOLBAR_MENU_BUTTON_PADDING_X * 2 for menu in menus
    ]
    menubar_strip = layouts.pad(
        pygame.Rect(0, 0, w, top),
        left=theme.TOOLBAR_PADDING_LEFT,
        top=theme.TOOLBAR_PADDING_TOP,
        bottom=theme.TOOLBAR_PADDING_BOTTOM,
    )
    menubar_strip.height = theme.TOOLBAR_MENU_BUTTON_HEIGHT
    menu_rects = layouts.row_rects(
        menubar_strip, menu_widths, gap=theme.TOOLBAR_BUTTON_GAP, align="left"
    )
    mouse_pos = pygame.mouse.get_pos()
    open_menu = getattr(editor, "_toolbar_menu", None)
    open_menu_id = open_menu["id"] if open_menu else None
    editor._toolbar_buttons = {}

    for menu, btn_rect in zip(menus, menu_rects):
        is_hovered = btn_rect.collidepoint(mouse_pos)
        is_open = menu["id"] == open_menu_id
        _draw_menu_button(editor, btn_rect, menu["label"], active=is_open, hovered=is_hovered)
        editor._toolbar_buttons[menu["id"]] = {"kind": "menu", "rect": btn_rect, "menu": menu}

    run_label = "> Run"
    run_width = font_bold.size(run_label)[0] + theme.TOOLBAR_MENU_BUTTON_PADDING_X * 2
    run_rect = pygame.Rect(
        max(6, w - theme.TOOLBAR_PADDING_RIGHT - run_width),
        menubar_strip.y,
        run_width,
        theme.TOOLBAR_MENU_BUTTON_HEIGHT,
    )
    _draw_action_button(editor, run_rect, run_label, hovered=run_rect.collidepoint(mouse_pos))
    editor._toolbar_buttons["run_project"] = {
        "kind": "action",
        "rect": run_rect,
        "action": editor._run_project,
    }

    scene_name = editor.scene.name + ("*" if editor.modified else "")
    text = font_bold.render(scene_name, True, colors["ui_text"])
    screen.blit(text, (w // 2 - text.get_width() // 2, 12))


def render_overlay(editor) -> None:
    _render_open_menu(editor)


def get_tools(editor):
    """Список (tool_type, key, name) — задаётся редактором во избежание циклического импорта."""
    return getattr(editor, "_toolbar_tools_list", ())


def handle_click(editor, pos) -> bool:
    menu = getattr(editor, "_toolbar_menu", None)
    if menu:
        for item, item_rect in menu["items"]:
            if item_rect.collidepoint(pos.x, pos.y):
                close_menu(editor)
                item["action"]()
                return True

    for menu_id, button_data in editor._toolbar_buttons.items():
        button_rect = button_data["rect"]
        if not button_rect.collidepoint(pos.x, pos.y):
            continue
        if button_data["kind"] == "action":
            close_menu(editor)
            button_data["action"]()
        else:
            menu_spec = button_data["menu"]
            if menu and menu["id"] == menu_id:
                close_menu(editor)
            else:
                _open_menu(editor, menu_id, button_rect, menu_spec["items"])
        return True

    if menu:
        menu_rect = menu["rect"]
        if menu_rect.collidepoint(pos.x, pos.y):
            return True
        close_menu(editor)
        return True

    return False
