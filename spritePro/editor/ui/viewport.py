"""Центральная область редактирования сцены: сетка, спрайты, gizmo, камера."""

import pygame
from pygame.math import Vector2

from ... import grid_renderer
from . import theme


def render(editor) -> None:
    viewport = _get_viewport_rect(editor)
    pygame.draw.rect(editor.screen, editor.colors["background"], viewport)
    if editor.scene.grid_visible:
        _render_grid(editor, viewport)
    for obj in editor.scene.objects:
        if not obj.active:
            continue
        _render_sprite(editor, obj)
    for obj in editor.selected_objects:
        _render_gizmo(editor, obj)
    if editor.camera_preview_enabled:
        _render_camera_preview_frame(editor, viewport)
    if getattr(editor, "viewport_tool_badge_enabled", True):
        _render_tool_badge(editor, viewport)
    pygame.draw.rect(editor.screen, editor.colors["ui_border"], viewport, 2)


def _get_viewport_rect(editor) -> pygame.Rect:
    return pygame.Rect(
        theme.UI_LEFT_WIDTH,
        theme.UI_TOP_HEIGHT,
        editor.width - theme.UI_LEFT_WIDTH - theme.UI_RIGHT_WIDTH,
        editor.height - theme.UI_TOP_HEIGHT - theme.UI_BOTTOM_HEIGHT,
    )


def _render_grid(editor, viewport: pygame.Rect) -> None:
    grid_size = editor.scene.grid_size
    zoom = editor.zoom
    top_left = editor.screen_to_world(Vector2(viewport.topleft))
    bottom_right = editor.screen_to_world(Vector2(viewport.bottomright))

    def world_to_screen(wx: float, wy: float) -> tuple:
        p = editor.world_to_screen(Vector2(wx, wy))
        return (p.x, p.y)

    grid_renderer.draw_world_grid(
        editor.screen,
        viewport,
        top_left.x,
        bottom_right.x,
        top_left.y,
        bottom_right.y,
        world_to_screen,
        grid_size,
        zoom,
        grid_color=(35, 35, 40),
        major_color=theme.COLORS["grid"],
        super_color=(70, 70, 80),
        draw_labels=editor.scene.grid_labels_visible,
        label_font=editor.font,
        label_color=(120, 120, 130),
        label_limit=200,
        min_label_px=50,
    )


def _render_sprite(editor, obj) -> None:
    sprite = editor._get_sprite_image(obj)
    display_w, display_h = editor._get_object_display_size(obj)
    if not sprite:
        pos = editor.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
        size = max(10, min(display_w, display_h) or 50) * editor.zoom
        rect = pygame.Rect(0, 0, int(size), int(size))
        rect.center = (int(pos.x), int(pos.y))
        pygame.draw.rect(editor.screen, (80, 80, 80), rect)
        return
    w = display_w * editor.zoom
    h = display_h * editor.zoom
    scaled_w, scaled_h = max(1, int(w)), max(1, int(h))
    scaled = pygame.transform.scale(sprite, (scaled_w, scaled_h))
    if obj.transform.rotation != 0:
        angle = -obj.transform.rotation
        scaled = pygame.transform.rotate(scaled, angle)
        new_w, new_h = scaled.get_size()
        offset_x, offset_y = (new_w - w) // 2, (new_h - h) // 2
    else:
        offset_x, offset_y = 0, 0
    pos = editor.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
    blit_x = int(pos.x - w / 2 - offset_x)
    blit_y = int(pos.y - h / 2 - offset_y)
    editor.screen.blit(scaled, (blit_x, blit_y))


def _render_gizmo(editor, obj) -> None:
    center_screen = editor.world_to_screen(Vector2(obj.transform.x, obj.transform.y))
    display_w, display_h = editor._get_object_display_size(obj)
    w = display_w * editor.zoom if (display_w > 0 and display_h > 0) else 50 * editor.zoom
    h = display_h * editor.zoom if (display_w > 0 and display_h > 0) else 50 * editor.zoom
    rect = pygame.Rect(0, 0, max(18, int(w + 10)), max(18, int(h + 10)))
    rect.center = (int(center_screen.x), int(center_screen.y))
    _draw_selection_frame(editor, rect)
    tool_name = getattr(editor.current_tool, "name", str(editor.current_tool))
    if tool_name == "MOVE":
        _render_gizmo_move(editor, obj, center_screen, rect)
    elif tool_name == "ROTATE":
        _render_gizmo_rotate(editor, obj, center_screen, rect)
    elif tool_name == "SCALE":
        _render_gizmo_scale(editor, obj, center_screen, rect)
    else:
        for pt in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
            _draw_handle(editor.screen, pt, 6, editor.colors["selection"])
        pygame.draw.circle(editor.screen, editor.colors["selection"], rect.center, 5)
        pygame.draw.circle(editor.screen, (240, 247, 255), rect.center, 2)


def _draw_selection_frame(editor, rect: pygame.Rect) -> None:
    overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
    overlay.fill((0, 150, 255, 28))
    editor.screen.blit(overlay, rect.topleft)
    pygame.draw.rect(editor.screen, (18, 20, 24), rect.inflate(4, 4), 3, border_radius=5)
    pygame.draw.rect(editor.screen, editor.colors["selection"], rect, 2, border_radius=4)


def _draw_handle(screen: pygame.Surface, center: tuple[int, int], radius: int, color) -> None:
    pygame.draw.circle(screen, (18, 20, 24), center, radius + 2)
    pygame.draw.circle(screen, color, center, radius)
    pygame.draw.circle(screen, (245, 248, 255), center, max(1, radius - 4))


def _draw_axis_label(editor, text: str, pos: tuple[float, float], color) -> None:
    label = editor.font_bold.render(text, True, color)
    bg = pygame.Rect(int(pos[0]), int(pos[1]), label.get_width() + 8, label.get_height() + 4)
    pygame.draw.rect(editor.screen, (18, 20, 24), bg, border_radius=4)
    pygame.draw.rect(editor.screen, color, bg, 1, border_radius=4)
    editor.screen.blit(label, (bg.x + 4, bg.y + 2))


def _render_gizmo_move(editor, obj, center: Vector2, rect: pygame.Rect) -> None:
    base_size = max(26, min(80, int(max(rect.width, rect.height) * 0.45)))
    end_x = (center.x + base_size, center.y)
    move_x = theme.COLORS["gizmo_move"]
    move_y = theme.COLORS["gizmo_rotate"]
    pygame.draw.line(editor.screen, (18, 20, 24), center, end_x, 5)
    pygame.draw.line(editor.screen, move_x, center, end_x, 3)
    pygame.draw.polygon(
        editor.screen,
        move_x,
        [
            end_x,
            (end_x[0] - 9, end_x[1] - 5),
            (end_x[0] - 9, end_x[1] + 5),
        ],
    )
    end_y = (center.x, center.y - base_size)
    pygame.draw.line(editor.screen, (18, 20, 24), center, end_y, 5)
    pygame.draw.line(editor.screen, move_y, center, end_y, 3)
    pygame.draw.polygon(
        editor.screen,
        move_y,
        [
            end_y,
            (end_y[0] - 5, end_y[1] + 9),
            (end_y[0] + 5, end_y[1] + 9),
        ],
    )
    pygame.draw.circle(editor.screen, (18, 20, 24), (int(center.x), int(center.y)), 7)
    pygame.draw.circle(editor.screen, (240, 247, 255), (int(center.x), int(center.y)), 4)
    _draw_axis_label(editor, "X", (end_x[0] + 8, end_x[1] - 12), move_x)
    _draw_axis_label(editor, "Y", (end_y[0] + 8, end_y[1] - 20), move_y)
    _draw_axis_label(
        editor,
        f"X {obj.transform.x:.0f}  Y {obj.transform.y:.0f}",
        (center.x - 46, rect.bottom + 8),
        editor.colors["selection"],
    )


def _render_gizmo_rotate(editor, obj, center: Vector2, rect: pygame.Rect) -> None:
    color = theme.COLORS["gizmo_rotate"]
    radius = max(rect.width, rect.height) / 2 + 18
    pygame.draw.circle(editor.screen, (18, 20, 24), (int(center.x), int(center.y)), int(radius) + 2, 4)
    pygame.draw.circle(editor.screen, color, (int(center.x), int(center.y)), int(radius), 2)
    top_point = (center.x, center.y - radius)
    pygame.draw.line(editor.screen, (18, 20, 24), center, top_point, 4)
    pygame.draw.line(editor.screen, color, center, top_point, 2)
    _draw_handle(editor.screen, (int(top_point[0]), int(top_point[1])), 6, color)
    pygame.draw.arc(
        editor.screen,
        color,
        pygame.Rect(int(center.x - radius), int(center.y - radius), int(radius * 2), int(radius * 2)),
        0.45,
        1.9,
        3,
    )
    _draw_axis_label(editor, "ROT", (center.x + radius - 8, center.y - radius - 10), color)
    _draw_axis_label(
        editor,
        f"{obj.transform.rotation:.0f}°",
        (center.x - 28, center.y + radius + 8),
        color,
    )
    pygame.draw.circle(editor.screen, (18, 20, 24), (int(center.x), int(center.y)), 7)
    pygame.draw.circle(editor.screen, (240, 247, 255), (int(center.x), int(center.y)), 4)


def _render_gizmo_scale(editor, obj, center: Vector2, rect: pygame.Rect) -> None:
    color = theme.COLORS["gizmo_scale"]
    pygame.draw.line(editor.screen, color, rect.topleft, rect.bottomright, 1)
    pygame.draw.line(editor.screen, color, rect.topright, rect.bottomleft, 1)
    for pos in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
        _draw_handle(editor.screen, pos, 7, color)
    _draw_axis_label(editor, "W", (rect.right + 10, rect.centery - 24), color)
    _draw_axis_label(editor, "H", (rect.centerx + 10, rect.bottom + 8), color)
    display_w, display_h = editor._get_object_display_size(obj)
    _draw_axis_label(
        editor,
        f"{display_w:.0f} x {display_h:.0f}",
        (center.x - 30, rect.bottom + 8),
        color,
    )
    pygame.draw.circle(editor.screen, (18, 20, 24), (int(center.x), int(center.y)), 7)
    pygame.draw.circle(editor.screen, (240, 247, 255), (int(center.x), int(center.y)), 4)


def _render_tool_badge(editor, viewport: pygame.Rect) -> None:
    tool_map = {tool_type: (name, key) for tool_type, key, name in editor._toolbar_tools_list}
    tool_name, shortcut = tool_map.get(editor.current_tool, ("Select", "V"))
    label = editor.font_bold.render(f"Tool: {tool_name} [{shortcut}]", True, (232, 240, 248))
    badge_rect = pygame.Rect(
        viewport.x + 10,
        viewport.y + 10,
        label.get_width() + 14,
        label.get_height() + 8,
    )
    pygame.draw.rect(editor.screen, (20, 24, 30), badge_rect, border_radius=5)
    pygame.draw.rect(editor.screen, (75, 135, 205), badge_rect, 1, border_radius=5)
    editor.screen.blit(label, (badge_rect.x + 7, badge_rect.y + 4))


def _render_camera_preview_frame(editor, viewport: pygame.Rect) -> None:
    editor._sync_scene_camera()
    cam = editor.scene.camera
    preview_w = max(8, int(editor.camera_preview_size.x))
    preview_h = max(8, int(editor.camera_preview_size.y))
    world_w = preview_w / cam.game_zoom
    world_h = preview_h / cam.game_zoom
    corners_world = [
        Vector2(cam.game_x, cam.game_y),
        Vector2(cam.game_x + world_w, cam.game_y),
        Vector2(cam.game_x + world_w, cam.game_y + world_h),
        Vector2(cam.game_x, cam.game_y + world_h),
    ]
    corners_screen = [editor.world_to_screen(p) for p in corners_world]
    xs = [int(p.x) for p in corners_screen]
    ys = [int(p.y) for p in corners_screen]
    frame_rect = pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    if viewport.colliderect(frame_rect.inflate(20, 20)):
        pts = [(int(p.x), int(p.y)) for p in corners_screen]
        pygame.draw.polygon(editor.screen, theme.COLORS["camera_frame"], pts, 1)
    info_x = viewport.x + 8
    info_y = viewport.bottom - 72
    label = editor.font.render(
        f"Camera {preview_w}x{preview_h}", True, theme.COLORS["camera_frame"]
    )
    label_bg = pygame.Rect(info_x, info_y, label.get_width() + 8, label.get_height() + 4)
    pygame.draw.rect(editor.screen, theme.COLORS["camera_info_bg"], label_bg, border_radius=3)
    pygame.draw.rect(
        editor.screen, theme.COLORS["camera_info_border"], label_bg, 1, border_radius=3
    )
    editor.screen.blit(label, (label_bg.x + 4, label_bg.y + 2))
    line_y = label_bg.bottom + 2
    scene_txt = editor.font.render(
        f"Scene: ({cam.scene_x:.0f}, {cam.scene_y:.0f}) {cam.scene_zoom * 100:.0f}%",
        True,
        (200, 200, 200),
    )
    editor.screen.blit(scene_txt, (info_x, line_y))
    line_y += scene_txt.get_height() + 2
    game_txt = editor.font.render(
        f"Game:  ({cam.game_x:.0f}, {cam.game_y:.0f}) {cam.game_zoom * 100:.0f}%",
        True,
        (180, 220, 180),
    )
    editor.screen.blit(game_txt, (info_x, line_y))
    line_y += game_txt.get_height() + 4
    copy_btn = editor.font.render("Copy scene → game", True, theme.COLORS["camera_frame"])
    copy_w = copy_btn.get_width() + 8
    copy_h = copy_btn.get_height() + 4
    editor._camera_preview_copy_rect = pygame.Rect(info_x, line_y, copy_w, copy_h)
    pygame.draw.rect(editor.screen, (40, 45, 50), editor._camera_preview_copy_rect, border_radius=3)
    pygame.draw.rect(
        editor.screen,
        theme.COLORS["camera_info_border"],
        editor._camera_preview_copy_rect,
        1,
        border_radius=3,
    )
    editor.screen.blit(
        copy_btn, (editor._camera_preview_copy_rect.x + 4, editor._camera_preview_copy_rect.y + 2)
    )


def get_viewport_rect(editor) -> pygame.Rect:
    """Публичный доступ к viewport rect для редактора."""
    return _get_viewport_rect(editor)
