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
        if not obj.visible:
            continue
        _render_sprite(editor, obj)
    for obj in editor.selected_objects:
        _render_gizmo(editor, obj)
    if editor.camera_preview_enabled:
        _render_camera_preview_frame(editor, viewport)
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
    tool_name = getattr(editor.current_tool, "name", str(editor.current_tool))
    if tool_name == "MOVE":
        _render_gizmo_move(editor, center_screen, w, h)
    elif tool_name == "ROTATE":
        _render_gizmo_rotate(editor, center_screen, w, h)
    elif tool_name == "SCALE":
        _render_gizmo_scale(editor, center_screen, w, h)
    else:
        rect = pygame.Rect(0, 0, w + 10, h + 10)
        rect.center = (int(center_screen.x), int(center_screen.y))
        pygame.draw.rect(editor.screen, editor.colors["selection"], rect, 2)
        for pt in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
            pygame.draw.circle(editor.screen, editor.colors["selection"], pt, 6)
        pygame.draw.circle(editor.screen, editor.colors["selection"], rect.center, 4)


def _render_gizmo_move(editor, center: Vector2, w: float, h: float) -> None:
    base_size = 20 * editor.zoom
    end_x = (center.x + base_size, center.y)
    pygame.draw.line(editor.screen, (255, 80, 80), center, end_x, 3)
    pygame.draw.polygon(editor.screen, (255, 80, 80), [
        end_x, (end_x[0] - 6, end_x[1] - 3), (end_x[0] - 6, end_x[1] + 3),
    ])
    end_y = (center.x, center.y - base_size)
    pygame.draw.line(editor.screen, (80, 255, 80), center, end_y, 3)
    pygame.draw.polygon(editor.screen, (80, 255, 80), [
        end_y, (end_y[0] - 3, end_y[1] + 6), (end_y[0] + 3, end_y[1] + 6),
    ])
    rect = pygame.Rect(0, 0, w + 10, h + 10)
    rect.center = (int(center.x), int(center.y))
    pygame.draw.rect(editor.screen, (255, 80, 80), rect, 1)


def _render_gizmo_rotate(editor, center: Vector2, w: float, h: float) -> None:
    radius = max(w, h) / 2 + 15 * editor.zoom
    pygame.draw.circle(editor.screen, (80, 255, 80), (int(center.x), int(center.y)), int(radius), 2)
    top_point = (center.x, center.y - radius)
    pygame.draw.line(editor.screen, (80, 255, 80), center, top_point, 2)
    pygame.draw.circle(editor.screen, (80, 255, 80), (int(top_point[0]), int(top_point[1])), 5)
    rect = pygame.Rect(0, 0, w + 10, h + 10)
    rect.center = (int(center.x), int(center.y))
    pygame.draw.rect(editor.screen, (80, 255, 80), rect, 1)


def _render_gizmo_scale(editor, center: Vector2, w: float, h: float) -> None:
    rect = pygame.Rect(0, 0, w + 10, h + 10)
    rect.center = (int(center.x), int(center.y))
    pygame.draw.rect(editor.screen, (100, 100, 255), rect, 2)
    for pos in [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]:
        pygame.draw.circle(editor.screen, (100, 100, 255), pos, 8)
        pygame.draw.circle(editor.screen, (255, 255, 255), pos, 4)


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
    label = editor.font.render(f"Camera {preview_w}x{preview_h}", True, theme.COLORS["camera_frame"])
    label_bg = pygame.Rect(info_x, info_y, label.get_width() + 8, label.get_height() + 4)
    pygame.draw.rect(editor.screen, theme.COLORS["camera_info_bg"], label_bg, border_radius=3)
    pygame.draw.rect(editor.screen, theme.COLORS["camera_info_border"], label_bg, 1, border_radius=3)
    editor.screen.blit(label, (label_bg.x + 4, label_bg.y + 2))
    line_y = label_bg.bottom + 2
    scene_txt = editor.font.render(
        f"Scene: ({cam.scene_x:.0f}, {cam.scene_y:.0f}) {cam.scene_zoom * 100:.0f}%",
        True, (200, 200, 200),
    )
    editor.screen.blit(scene_txt, (info_x, line_y))
    line_y += scene_txt.get_height() + 2
    game_txt = editor.font.render(
        f"Game:  ({cam.game_x:.0f}, {cam.game_y:.0f}) {cam.game_zoom * 100:.0f}%",
        True, (180, 220, 180),
    )
    editor.screen.blit(game_txt, (info_x, line_y))
    line_y += game_txt.get_height() + 4
    copy_btn = editor.font.render("Copy scene → game", True, theme.COLORS["camera_frame"])
    copy_w = copy_btn.get_width() + 8
    copy_h = copy_btn.get_height() + 4
    editor._camera_preview_copy_rect = pygame.Rect(info_x, line_y, copy_w, copy_h)
    pygame.draw.rect(editor.screen, (40, 45, 50), editor._camera_preview_copy_rect, border_radius=3)
    pygame.draw.rect(editor.screen, theme.COLORS["camera_info_border"], editor._camera_preview_copy_rect, 1, border_radius=3)
    editor.screen.blit(copy_btn, (editor._camera_preview_copy_rect.x + 4, editor._camera_preview_copy_rect.y + 2))


def get_viewport_rect(editor) -> pygame.Rect:
    """Публичный доступ к viewport rect для редактора."""
    return _get_viewport_rect(editor)
