"""Панель иерархии объектов (слева)."""

import pygame

from . import theme

_CONTEXT_MENU_ITEMS = (
    {
        "id": "duplicate",
        "label": "Дублировать",
        "shortcut": "Ctrl+C",
        "text_color": None,
        "hover_text_color": None,
    },
    {
        "id": "delete",
        "label": "Удалить",
        "shortcut": "Del",
        "text_color": (235, 120, 120),
        "hover_text_color": (255, 170, 170),
    },
)


def _fit_text_to_width(text: str, max_width: int, font: pygame.font.Font) -> str:
    if font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    left, right = 0, len(text)
    best = ellipsis
    while left <= right:
        mid = (left + right) // 2
        candidate = text[:mid].rstrip() + ellipsis
        if font.size(candidate)[0] <= max_width:
            best = candidate
            left = mid + 1
        else:
            right = mid - 1
    return best


def _clamp_scroll(editor) -> None:
    total_items = 1 + len(editor.scene.objects)
    cap = max(1, getattr(editor, "_hierarchy_visible_capacity", 1))
    max_scroll = max(0, total_items - cap)
    editor.hierarchy_scroll = max(0, min(editor.hierarchy_scroll, max_scroll))


def render(editor) -> None:
    screen = editor.screen
    font = editor.font
    font_bold = editor.font_bold
    colors = editor.colors
    left_w = theme.UI_LEFT_WIDTH
    top = theme.UI_TOP_HEIGHT
    bottom = theme.UI_BOTTOM_HEIGHT
    height = editor.height

    rect = pygame.Rect(0, top, left_w, height - top - bottom)
    pygame.draw.rect(screen, colors["ui_bg"], rect)
    pygame.draw.line(
        screen,
        colors["ui_border"],
        (left_w, top),
        (left_w, height - bottom),
        1,
    )

    header = font_bold.render("Objects", True, colors["ui_text"])
    screen.blit(header, (10, top + 10))

    list_top = top + theme.HIERARCHY_HEADER_OFFSET
    list_bottom = height - bottom - theme.HIERARCHY_LIST_PADDING
    list_height = max(0, list_bottom - list_top)
    total_items = 1 + len(editor.scene.objects)
    editor._hierarchy_visible_capacity = max(1, list_height // theme.HIERARCHY_ITEM_HEIGHT)
    _clamp_scroll(editor)

    start_index = editor.hierarchy_scroll
    end_index = min(total_items, start_index + editor._hierarchy_visible_capacity)
    mouse_pos = pygame.mouse.get_pos()
    y = list_top

    for i in range(start_index, end_index):
        text_rect = pygame.Rect(5, y, left_w - 10, theme.HIERARCHY_ITEM_HEIGHT)
        is_hovered = text_rect.collidepoint(mouse_pos)
        if i == 0:
            is_selected = editor.camera_selected
            label = "Camera"
            is_active = True
        else:
            obj = editor.scene.objects[i - 1]
            is_selected = obj in editor.selected_objects
            is_active = obj.active
            state_icon = "●" if obj.active else "○"
            max_name_width = left_w - 30
            label = _fit_text_to_width(f"{state_icon} {obj.name}", max_name_width, font)
        if is_selected:
            pygame.draw.rect(screen, colors["ui_accent"], text_rect, border_radius=3)
            color = theme.COLORS["ui_selected_bg"]
        elif is_hovered:
            pygame.draw.rect(screen, theme.COLORS["ui_hover"], text_rect, border_radius=3)
            color = (150, 150, 160) if not is_active else colors["ui_text"]
        else:
            color = (115, 115, 125) if not is_active else colors["ui_text"]
        text = font.render(label, True, color)
        screen.blit(text, (15, y + 3))
        y += theme.HIERARCHY_ITEM_HEIGHT

    _render_scrollbar(editor, list_top, list_bottom)
    _render_context_menu(editor)


def _render_scrollbar(editor, list_top: int, list_bottom: int) -> None:
    total = 1 + len(editor.scene.objects)
    visible = max(1, editor._hierarchy_visible_capacity)
    if total <= visible:
        return
    left_w = theme.UI_LEFT_WIDTH
    track_rect = pygame.Rect(left_w - 8, list_top, 4, list_bottom - list_top)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_scrollbar_track"], track_rect, border_radius=2)
    ratio = visible / total
    thumb_h = max(20, int(track_rect.height * ratio))
    max_scroll = max(1, total - visible)
    t = editor.hierarchy_scroll / max_scroll
    thumb_y = track_rect.y + int((track_rect.height - thumb_h) * t)
    thumb_rect = pygame.Rect(track_rect.x, thumb_y, track_rect.width, thumb_h)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_scrollbar_thumb"], thumb_rect, border_radius=2)


def _render_context_menu(editor) -> None:
    menu = getattr(editor, "_hierarchy_context_menu", None)
    if not menu:
        return
    mouse_pos = pygame.mouse.get_pos()
    menu_rect = menu["rect"]
    pygame.draw.rect(editor.screen, (36, 36, 42), menu_rect, border_radius=4)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_input_border"], menu_rect, 1, border_radius=4)
    item_meta = {item["id"]: item for item in _CONTEXT_MENU_ITEMS}
    for action_id, item_rect in menu["items"]:
        hovered = item_rect.collidepoint(mouse_pos)
        if hovered:
            pygame.draw.rect(editor.screen, theme.COLORS["ui_hover"], item_rect, border_radius=3)
        meta = item_meta[action_id]
        label_color = (
            meta["hover_text_color"]
            if hovered and meta["hover_text_color"] is not None
            else meta["text_color"] or editor.colors["ui_text"]
        )
        shortcut_color = (165, 165, 180) if not hovered else (205, 205, 220)
        label_surf = editor.font.render(meta["label"], True, label_color)
        shortcut_surf = editor.font.render(meta["shortcut"], True, shortcut_color)
        label_y = item_rect.y + (item_rect.height - label_surf.get_height()) // 2
        shortcut_y = item_rect.y + (item_rect.height - shortcut_surf.get_height()) // 2
        editor.screen.blit(label_surf, (item_rect.x + 8, label_y))
        editor.screen.blit(
            shortcut_surf,
            (item_rect.right - shortcut_surf.get_width() - 8, shortcut_y),
        )


def handle_click(editor, pos) -> object:
    """Возвращает SceneObject, '__camera__' или None."""
    list_top = theme.UI_TOP_HEIGHT + theme.HIERARCHY_HEADER_OFFSET
    list_bottom = editor.height - theme.UI_BOTTOM_HEIGHT - theme.HIERARCHY_LIST_PADDING
    if pos.y < list_top or pos.y > list_bottom:
        return None
    _clamp_scroll(editor)
    total_items = 1 + len(editor.scene.objects)
    index = int((pos.y - list_top) // theme.HIERARCHY_ITEM_HEIGHT) + editor.hierarchy_scroll
    if index == 0:
        return "__camera__"
    if 1 <= index < total_items:
        return editor.scene.objects[index - 1]
    return None


def close_context_menu(editor) -> None:
    editor._hierarchy_context_menu = None


def open_context_menu(editor, obj, pos) -> bool:
    if obj in (None, "__camera__"):
        close_context_menu(editor)
        return False
    left_w = theme.UI_LEFT_WIDTH
    top = theme.UI_TOP_HEIGHT
    bottom = theme.UI_BOTTOM_HEIGHT
    max_height = editor.height - bottom
    item_h = 24
    menu_w = max(
        144,
        max(
            editor.font.size(item["label"])[0] + editor.font.size(item["shortcut"])[0] + 28
            for item in _CONTEXT_MENU_ITEMS
        ),
    )
    menu_h = len(_CONTEXT_MENU_ITEMS) * item_h + 4
    x = min(int(pos.x), left_w - menu_w - 6)
    x = max(6, x)
    y = min(int(pos.y), max_height - menu_h - 6)
    y = max(top + 4, y)
    menu_rect = pygame.Rect(x, y, menu_w, menu_h)
    item_rects = []
    for index, item in enumerate(_CONTEXT_MENU_ITEMS):
        action_id = item["id"]
        item_rect = pygame.Rect(x + 2, y + 2 + index * item_h, menu_w - 4, item_h)
        item_rects.append((action_id, item_rect))
    editor._hierarchy_context_menu = {
        "object": obj,
        "rect": menu_rect,
        "items": item_rects,
    }
    return True


def handle_menu_click(editor, pos) -> bool:
    menu = getattr(editor, "_hierarchy_context_menu", None)
    if not menu:
        return False
    menu_rect = menu["rect"]
    if not menu_rect.collidepoint(pos.x, pos.y):
        close_context_menu(editor)
        return False
    target = menu["object"]
    for action_id, item_rect in menu["items"]:
        if not item_rect.collidepoint(pos.x, pos.y):
            continue
        editor.select_object(target)
        if action_id == "duplicate":
            editor.copy_selected()
        elif action_id == "delete":
            editor.delete_selected()
        close_context_menu(editor)
        return True
    return True


def handle_wheel(editor, delta_y: int) -> bool:
    """Обработка колёсика мыши над панелью иерархии."""
    left_w = theme.UI_LEFT_WIDTH
    top = theme.UI_TOP_HEIGHT
    bottom = theme.UI_BOTTOM_HEIGHT
    height = editor.height
    rect = pygame.Rect(0, top, left_w, height - top - bottom)
    if not rect.collidepoint(pygame.mouse.get_pos()):
        return False
    editor.hierarchy_scroll -= delta_y
    _clamp_scroll(editor)
    return True
