"""Панель иерархии объектов (слева)."""

import pygame

from . import theme


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
        else:
            obj = editor.scene.objects[i - 1]
            is_selected = obj in editor.selected_objects
            visibility = "👁" if obj.visible else "○"
            max_name_width = left_w - 30
            label = _fit_text_to_width(f"{visibility} {obj.name}", max_name_width, font)
        if is_selected:
            pygame.draw.rect(screen, colors["ui_accent"], text_rect, border_radius=3)
            color = theme.COLORS["ui_selected_bg"]
        elif is_hovered:
            pygame.draw.rect(screen, theme.COLORS["ui_hover"], text_rect, border_radius=3)
            color = colors["ui_text"]
        else:
            color = colors["ui_text"]
        text = font.render(label, True, color)
        screen.blit(text, (15, y + 3))
        y += theme.HIERARCHY_ITEM_HEIGHT

    _render_scrollbar(editor, list_top, list_bottom)


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
