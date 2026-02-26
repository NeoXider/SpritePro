"""Верхняя панель инструментов редактора."""

import pygame

from . import layouts
from . import theme


def render(editor) -> None:
    screen = editor.screen
    font = editor.font
    font_bold = editor.font_bold
    colors = editor.colors
    w = editor.width
    top = theme.UI_TOP_HEIGHT

    rect = pygame.Rect(0, 0, w, top)
    pygame.draw.rect(screen, colors["ui_bg"], rect)
    pygame.draw.line(screen, colors["ui_border"], (0, top), (w, top), 1)

    tools = get_tools(editor)
    tool_widths = [font_bold.size(f"{name} ({key})")[0] + 20 for _, key, name in tools]
    tools_strip = layouts.pad(
        pygame.Rect(0, 0, w, top),
        left=theme.TOOLBAR_PADDING_LEFT,
        top=theme.TOOLBAR_PADDING_TOP,
        bottom=theme.TOOLBAR_PADDING_BOTTOM,
    )
    tool_rects = layouts.row_rects(tools_strip, tool_widths, gap=theme.TOOLBAR_BUTTON_GAP, align="left")
    mouse_pos = pygame.mouse.get_pos()

    for (tool_type, key, name), btn_rect in zip(tools, tool_rects):
        is_hovered = btn_rect.collidepoint(mouse_pos)
        is_selected = editor.current_tool == tool_type
        if is_selected:
            pygame.draw.rect(screen, colors["ui_accent"], btn_rect, border_radius=4)
            color = theme.COLORS["ui_selected_bg"]
        elif is_hovered:
            pygame.draw.rect(screen, theme.COLORS["ui_hover"], btn_rect, border_radius=4)
            color = colors["ui_text"]
        else:
            color = colors["ui_text"]
        text = font_bold.render(f"{name} ({key})", True, color)
        screen.blit(text, (btn_rect.x + 10, 12))

    scene_name = editor.scene.name + ("*" if editor.modified else "")
    text = font_bold.render(scene_name, True, colors["ui_text"])
    screen.blit(text, (w // 2 - text.get_width() // 2, 12))

    toolbar_strip = layouts.pad(
        pygame.Rect(0, 0, w, top),
        top=8,
        right=theme.TOOLBAR_PADDING_RIGHT,
        bottom=8,
    )
    toolbar_strip.height = theme.TOOLBAR_RIGHT_BUTTON_HEIGHT
    btn_rects = layouts.row_rects(
        toolbar_strip,
        [tw for _, __, tw in theme.TOOLBAR_RIGHT_BUTTONS],
        gap=theme.TOOLBAR_RIGHT_BUTTON_GAP,
        align="right",
    )
    editor._toolbar_buttons = {}
    for (key, label, width), rect in zip(theme.TOOLBAR_RIGHT_BUTTONS, btn_rects):
        is_hovered = rect.collidepoint(mouse_pos)
        cfg = theme.TOOLBAR_BUTTON_COLORS.get(key, theme.TOOLBAR_BUTTON_COLORS["default"])
        if key == "grid":
            base = colors["ui_accent"] if editor.scene.grid_visible else cfg["normal"]
            color = base if not is_hovered else (cfg.get("active_hover", cfg["hover"]) if editor.scene.grid_visible else cfg["hover"])
        else:
            color = cfg["hover"] if is_hovered else cfg["normal"]
        pygame.draw.rect(screen, color, rect, border_radius=4)
        text_color = theme.COLORS["ui_selected_bg"] if key == "grid" and editor.scene.grid_visible else colors["ui_text"]
        label_surface = font.render(label, True, text_color)
        screen.blit(label_surface, (rect.centerx - label_surface.get_width() // 2, rect.y + 5))
        editor._toolbar_buttons[key] = rect


def get_tools(editor):
    """Список (tool_type, key, name) — задаётся редактором во избежание циклического импорта."""
    return getattr(editor, "_toolbar_tools_list", ())


def handle_click(editor, pos) -> bool:
    if editor._toolbar_buttons.get("load", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor._load_scene()
        return True
    if editor._toolbar_buttons.get("save", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor._save_scene()
        return True
    if editor._toolbar_buttons.get("new", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor._new_scene()
        return True
    if editor._toolbar_buttons.get("add", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor._add_sprite_dialog()
        return True
    if editor._toolbar_buttons.get("rect", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor.add_primitive("rectangle")
        return True
    if editor._toolbar_buttons.get("circle", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor.add_primitive("circle")
        return True
    if editor._toolbar_buttons.get("ellipse", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor.add_primitive("ellipse")
        return True
    if editor._toolbar_buttons.get("grid", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor.scene.grid_visible = not editor.scene.grid_visible
        editor._save_state()
        return True
    if editor._toolbar_buttons.get("settings", pygame.Rect(0, 0, 0, 0)).collidepoint(pos.x, pos.y):
        editor.window_manager.toggle("settings")
        return True

    tools = get_tools(editor)
    if not tools:
        return False
    tool_widths = [
        editor.font_bold.size(f"{name} ({key})")[0] + 20
        for _, key, name in tools
    ]
    tools_strip = layouts.pad(
        pygame.Rect(0, 0, editor.width, theme.UI_TOP_HEIGHT),
        left=theme.TOOLBAR_PADDING_LEFT,
        top=theme.TOOLBAR_PADDING_TOP,
        bottom=theme.TOOLBAR_PADDING_BOTTOM,
    )
    tool_rects = layouts.row_rects(tools_strip, tool_widths, gap=theme.TOOLBAR_BUTTON_GAP, align="left")
    for tool_type, btn_rect in zip([t[0] for t in tools], tool_rects):
        if btn_rect.collidepoint(pos.x, pos.y):
            editor.current_tool = tool_type
            return True
    return False
