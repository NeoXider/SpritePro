"""Окна и страницы редактора для расширяемого UI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import pygame


Color = Tuple[int, int, int]


@dataclass
class WindowAction:
    rect: pygame.Rect
    callback: Callable[[], None]


@dataclass
class EditorWindow:
    window_id: str
    title: str
    rect: pygame.Rect
    page_titles: List[str]
    page_index: int = 0
    visible: bool = False
    actions: List[WindowAction] = field(default_factory=list)

    def toggle(self) -> None:
        self.visible = not self.visible

    def hide(self) -> None:
        self.visible = False

    @property
    def current_page(self) -> str:
        if not self.page_titles:
            return ""
        self.page_index = max(0, min(self.page_index, len(self.page_titles) - 1))
        return self.page_titles[self.page_index]

    def _clear_actions(self) -> None:
        self.actions.clear()

    def _add_action(self, rect: pygame.Rect, callback: Callable[[], None]) -> None:
        self.actions.append(WindowAction(rect=rect, callback=callback))

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        if not self.visible or not self.rect.collidepoint(pos):
            return False
        for action in self.actions:
            if action.rect.collidepoint(pos):
                action.callback()
                return True
        return True

    def render_base(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_bold: pygame.font.Font,
        colors: Dict[str, Color],
    ) -> pygame.Rect:
        self._clear_actions()
        pygame.draw.rect(screen, (20, 20, 24), self.rect, border_radius=8)
        pygame.draw.rect(screen, colors["ui_border"], self.rect, 1, border_radius=8)

        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 34)
        pygame.draw.rect(screen, colors["ui_bg"], header, border_radius=8)
        title_text = font_bold.render(self.title, True, colors["ui_text"])
        screen.blit(title_text, (header.x + 10, header.y + 9))

        close_rect = pygame.Rect(header.right - 28, header.y + 7, 20, 20)
        pygame.draw.rect(screen, (90, 40, 40), close_rect, border_radius=4)
        screen.blit(font.render("x", True, (220, 220, 220)), (close_rect.x + 6, close_rect.y + 3))
        self._add_action(close_rect, self.hide)

        tabs_top = header.bottom + 8
        tab_x = self.rect.x + 10
        for index, page_title in enumerate(self.page_titles):
            tab_rect = pygame.Rect(tab_x, tabs_top, 88, 22)
            active = self.page_index == index
            tab_color = colors["ui_accent"] if active else (45, 45, 50)
            txt_color = (25, 25, 30) if active else colors["ui_text"]
            pygame.draw.rect(screen, tab_color, tab_rect, border_radius=4)
            tab_text = font.render(page_title, True, txt_color)
            screen.blit(tab_text, (tab_rect.x + 8, tab_rect.y + 4))
            self._add_action(tab_rect, lambda i=index: self._set_page(i))
            tab_x += tab_rect.width + 6

        return pygame.Rect(
            self.rect.x + 10, tabs_top + 30, self.rect.width - 20, self.rect.height - 74
        )

    def _set_page(self, index: int) -> None:
        self.page_index = max(0, min(index, len(self.page_titles) - 1))


class SettingsWindow(EditorWindow):
    """Окно настроек с несколькими страницами."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(
            window_id="settings",
            title="Settings",
            rect=rect,
            page_titles=["Scene", "View", "Theme", "Files"],
        )

    def render(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_bold: pygame.font.Font,
        colors: Dict[str, Color],
        *,
        settings: Dict[str, object],
        on_toggle_scene_grid: Callable[[], None],
        on_toggle_scene_labels: Callable[[], None],
        on_toggle_scene_snap: Callable[[], None],
        on_adjust_scene_grid_size: Callable[[int], None],
        on_toggle_camera_preview: Callable[[], None],
        on_toggle_hierarchy_previews: Callable[[], None],
        on_toggle_viewport_tool_badge: Callable[[], None],
        on_adjust_preview_width: Callable[[int], None],
        on_adjust_preview_height: Callable[[int], None],
        on_adjust_font_size: Callable[[int], None],
        on_adjust_font_bold_size: Callable[[int], None],
        on_adjust_theme_color: Callable[[str, int, int], None],
        on_save_settings: Callable[[], None],
        on_reload_settings: Callable[[], None],
        on_export_settings: Callable[[], None],
        on_import_settings: Callable[[], None],
        on_reset_settings: Callable[[], None],
        zoom_text: str,
        grid_text: str,
    ) -> None:
        if not self.visible:
            return
        body = self.render_base(screen, font, font_bold, colors)
        body = self._render_quick_actions(
            screen,
            font,
            colors,
            body,
            on_reset_settings=on_reset_settings,
        )
        scene_settings = settings["scene"]
        view_settings = settings["view"]
        theme_settings = settings["theme"]

        if self.current_page == "Scene":
            self._render_scene_page(
                screen,
                font,
                colors,
                body,
                scene_settings=scene_settings,
                on_toggle_grid=on_toggle_scene_grid,
                on_toggle_grid_labels=on_toggle_scene_labels,
                on_toggle_snap=on_toggle_scene_snap,
                on_adjust_grid_size=on_adjust_scene_grid_size,
            )
            return
        if self.current_page == "View":
            self._render_view_page(
                screen,
                font,
                colors,
                body,
                view_settings=view_settings,
                on_toggle_camera_preview=on_toggle_camera_preview,
                on_toggle_hierarchy_previews=on_toggle_hierarchy_previews,
                on_toggle_viewport_tool_badge=on_toggle_viewport_tool_badge,
                on_adjust_preview_width=on_adjust_preview_width,
                on_adjust_preview_height=on_adjust_preview_height,
                zoom_text=zoom_text,
                grid_text=grid_text,
            )
            return
        if self.current_page == "Theme":
            self._render_theme_page(
                screen,
                font,
                colors,
                body,
                theme_settings=theme_settings,
                on_adjust_font_size=on_adjust_font_size,
                on_adjust_font_bold_size=on_adjust_font_bold_size,
                on_adjust_theme_color=on_adjust_theme_color,
            )
            return
        self._render_files_page(
            screen,
            font,
            colors,
            body,
            on_save_settings=on_save_settings,
            on_reload_settings=on_reload_settings,
            on_export_settings=on_export_settings,
            on_import_settings=on_import_settings,
            on_reset_settings=on_reset_settings,
        )

    def _render_quick_actions(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        on_reset_settings: Callable[[], None],
    ) -> pygame.Rect:
        actions_h = 28
        actions_rect = pygame.Rect(body.x, body.y, body.width, actions_h)
        reset_rect = pygame.Rect(actions_rect.right - 110, actions_rect.y, 110, 24)
        pygame.draw.rect(screen, (96, 64, 64), reset_rect, border_radius=5)
        pygame.draw.rect(screen, colors["ui_border"], reset_rect, 1, border_radius=5)
        text = font.render("Reset", True, colors["ui_text"])
        screen.blit(text, (reset_rect.centerx - text.get_width() // 2, reset_rect.y + 4))
        self._add_action(reset_rect, on_reset_settings)
        return pygame.Rect(body.x, body.y + actions_h, body.width, max(0, body.height - actions_h))

    def _render_scene_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        scene_settings: Dict[str, object],
        on_toggle_grid: Callable[[], None],
        on_toggle_grid_labels: Callable[[], None],
        on_toggle_snap: Callable[[], None],
        on_adjust_grid_size: Callable[[int], None],
    ) -> None:
        row_h = 26
        y = body.y

        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Grid Visible",
            bool(scene_settings["grid_visible"]),
            on_toggle_grid,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Grid Labels",
            bool(scene_settings["grid_labels_visible"]),
            on_toggle_grid_labels,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Snap To Grid",
            bool(scene_settings["snap_to_grid"]),
            on_toggle_snap,
        )
        y += row_h + 10
        self._render_stepper_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Default Grid Size",
            f"{int(scene_settings['grid_size'])} px",
            lambda: on_adjust_grid_size(-2),
            lambda: on_adjust_grid_size(2),
        )

    def _render_view_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        view_settings: Dict[str, object],
        on_toggle_camera_preview: Callable[[], None],
        on_toggle_hierarchy_previews: Callable[[], None],
        on_toggle_viewport_tool_badge: Callable[[], None],
        on_adjust_preview_width: Callable[[int], None],
        on_adjust_preview_height: Callable[[int], None],
        zoom_text: str,
        grid_text: str,
    ) -> None:
        row_h = 26
        y = body.y
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Camera Preview",
            bool(view_settings["camera_preview_enabled"]),
            on_toggle_camera_preview,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Hierarchy Previews",
            bool(view_settings["hierarchy_previews_enabled"]),
            on_toggle_hierarchy_previews,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Viewport Tool Badge",
            bool(view_settings["viewport_tool_badge_enabled"]),
            on_toggle_viewport_tool_badge,
        )
        y += row_h + 10
        self._render_stepper_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Preview Width",
            f"{int(view_settings['camera_preview_width'])} px",
            lambda: on_adjust_preview_width(-40),
            lambda: on_adjust_preview_width(40),
        )
        y += row_h + 8
        self._render_stepper_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Preview Height",
            f"{int(view_settings['camera_preview_height'])} px",
            lambda: on_adjust_preview_height(-40),
            lambda: on_adjust_preview_height(40),
        )
        y += row_h + 16
        line1 = font.render(f"Camera Zoom: {zoom_text}", True, colors["ui_text"])
        line2 = font.render(f"Grid Size: {grid_text}", True, colors["ui_text"])
        hint = font.render("Use sliders in status bar", True, (140, 140, 150))
        screen.blit(line1, (body.x, y))
        screen.blit(line2, (body.x, y + 24))
        screen.blit(hint, (body.x, y + 52))

    def _render_theme_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        theme_settings: Dict[str, object],
        on_adjust_font_size: Callable[[int], None],
        on_adjust_font_bold_size: Callable[[int], None],
        on_adjust_theme_color: Callable[[str, int, int], None],
    ) -> None:
        row_h = 26
        y = body.y
        self._render_stepper_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "UI Font Size",
            str(int(theme_settings["font_size"])),
            lambda: on_adjust_font_size(-1),
            lambda: on_adjust_font_size(1),
        )
        y += row_h + 8
        self._render_stepper_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "UI Bold Font Size",
            str(int(theme_settings["font_bold_size"])),
            lambda: on_adjust_font_bold_size(-1),
            lambda: on_adjust_font_bold_size(1),
        )
        y += row_h + 12
        for color_key in ("ui_text", "ui_accent", "selection", "background"):
            self._render_color_row(
                screen,
                font,
                colors,
                pygame.Rect(body.x, y, body.width, 30),
                color_key,
                tuple(theme_settings["colors"][color_key]),
                lambda ck=color_key, ch=0: on_adjust_theme_color(ck, ch, -8),
                lambda ck=color_key, ch=0: on_adjust_theme_color(ck, ch, 8),
                lambda ck=color_key, ch=1: on_adjust_theme_color(ck, ch, -8),
                lambda ck=color_key, ch=1: on_adjust_theme_color(ck, ch, 8),
                lambda ck=color_key, ch=2: on_adjust_theme_color(ck, ch, -8),
                lambda ck=color_key, ch=2: on_adjust_theme_color(ck, ch, 8),
            )
            y += 38

    def _render_files_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        on_save_settings: Callable[[], None],
        on_reload_settings: Callable[[], None],
        on_export_settings: Callable[[], None],
        on_import_settings: Callable[[], None],
        on_reset_settings: Callable[[], None],
    ) -> None:
        row_h = 30
        y = body.y
        self._render_action_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Save local settings",
            on_save_settings,
        )
        y += row_h + 8
        self._render_action_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Reload from disk",
            on_reload_settings,
        )
        y += row_h + 8
        self._render_action_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Export settings...",
            on_export_settings,
        )
        y += row_h + 8
        self._render_action_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Import settings...",
            on_import_settings,
        )
        y += row_h + 8
        self._render_action_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Reset to defaults",
            on_reset_settings,
            accent=(96, 64, 64),
        )

    def _render_toggle_row(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        row_rect: pygame.Rect,
        label: str,
        value: bool,
        callback: Callable[[], None],
    ) -> None:
        txt = font.render(label, True, colors["ui_text"])
        screen.blit(txt, (row_rect.x, row_rect.y + 5))

        toggle_rect = pygame.Rect(row_rect.right - 86, row_rect.y + 2, 86, 22)
        bg = colors["ui_accent"] if value else (55, 55, 62)
        fg = (24, 24, 28) if value else colors["ui_text"]
        pygame.draw.rect(screen, bg, toggle_rect, border_radius=4)
        caption = "ON" if value else "OFF"
        caption_text = font.render(caption, True, fg)
        screen.blit(
            caption_text, (toggle_rect.centerx - caption_text.get_width() // 2, toggle_rect.y + 4)
        )
        self._add_action(toggle_rect, callback)

    def _render_stepper_row(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        row_rect: pygame.Rect,
        label: str,
        value: str,
        on_minus: Callable[[], None],
        on_plus: Callable[[], None],
    ) -> None:
        txt = font.render(label, True, colors["ui_text"])
        val = font.render(value, True, (200, 210, 225))
        screen.blit(txt, (row_rect.x, row_rect.y + 5))
        value_x = row_rect.right - 120
        minus_rect = pygame.Rect(value_x - 56, row_rect.y + 2, 24, 22)
        plus_rect = pygame.Rect(row_rect.right - 24, row_rect.y + 2, 24, 22)
        value_rect = pygame.Rect(value_x - 28, row_rect.y + 2, 96, 22)
        for rect, label_text, callback in (
            (minus_rect, "-", on_minus),
            (plus_rect, "+", on_plus),
        ):
            pygame.draw.rect(screen, (55, 55, 62), rect, border_radius=4)
            cap = font.render(label_text, True, colors["ui_text"])
            screen.blit(cap, (rect.centerx - cap.get_width() // 2, rect.y + 3))
            self._add_action(rect, callback)
        pygame.draw.rect(screen, (32, 34, 40), value_rect, border_radius=4)
        pygame.draw.rect(screen, colors["ui_border"], value_rect, 1, border_radius=4)
        screen.blit(val, (value_rect.centerx - val.get_width() // 2, value_rect.y + 3))

    def _render_color_row(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        row_rect: pygame.Rect,
        label: str,
        value: Color,
        r_minus: Callable[[], None],
        r_plus: Callable[[], None],
        g_minus: Callable[[], None],
        g_plus: Callable[[], None],
        b_minus: Callable[[], None],
        b_plus: Callable[[], None],
    ) -> None:
        txt = font.render(label, True, colors["ui_text"])
        screen.blit(txt, (row_rect.x, row_rect.y + 5))
        swatch = pygame.Rect(row_rect.x + 130, row_rect.y + 3, 20, 20)
        pygame.draw.rect(screen, value, swatch, border_radius=4)
        pygame.draw.rect(screen, colors["ui_border"], swatch, 1, border_radius=4)
        start_x = row_rect.right - 156
        for index, (name, channel_value, on_minus, on_plus) in enumerate(
            (
                ("R", value[0], r_minus, r_plus),
                ("G", value[1], g_minus, g_plus),
                ("B", value[2], b_minus, b_plus),
            )
        ):
            block_x = start_x + index * 52
            label_surf = font.render(f"{name}:{int(channel_value)}", True, colors["ui_text"])
            screen.blit(label_surf, (block_x, row_rect.y + 5))
            minus_rect = pygame.Rect(block_x, row_rect.y + 15, 20, 14)
            plus_rect = pygame.Rect(block_x + 24, row_rect.y + 15, 20, 14)
            for rect, label_text, callback in (
                (minus_rect, "-", on_minus),
                (plus_rect, "+", on_plus),
            ):
                pygame.draw.rect(screen, (55, 55, 62), rect, border_radius=4)
                cap = font.render(label_text, True, colors["ui_text"])
                screen.blit(cap, (rect.centerx - cap.get_width() // 2, rect.y - 1))
                self._add_action(rect, callback)

    def _render_action_row(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        row_rect: pygame.Rect,
        label: str,
        callback: Callable[[], None],
        accent: Color | None = None,
    ) -> None:
        bg = accent or (48, 52, 62)
        pygame.draw.rect(screen, bg, row_rect, border_radius=5)
        pygame.draw.rect(screen, colors["ui_border"], row_rect, 1, border_radius=5)
        text = font.render(label, True, colors["ui_text"])
        screen.blit(text, (row_rect.centerx - text.get_width() // 2, row_rect.y + 7))
        self._add_action(row_rect, callback)


class WindowManager:
    """Менеджер нескольких окон редактора."""

    def __init__(self) -> None:
        self._windows: Dict[str, EditorWindow] = {}
        self.z_order: List[str] = []

    def register(self, window: EditorWindow) -> None:
        self._windows[window.window_id] = window
        if window.window_id not in self.z_order:
            self.z_order.append(window.window_id)

    def get(self, window_id: str) -> Optional[EditorWindow]:
        return self._windows.get(window_id)

    def toggle(self, window_id: str) -> None:
        window = self.get(window_id)
        if window is None:
            return
        window.toggle()
        self.bring_to_front(window_id)

    def bring_to_front(self, window_id: str) -> None:
        if window_id not in self.z_order:
            return
        self.z_order.remove(window_id)
        self.z_order.append(window_id)

    def handle_click(self, pos: Tuple[int, int]) -> bool:
        for window_id in reversed(self.z_order):
            window = self._windows[window_id]
            if window.handle_click(pos):
                self.bring_to_front(window_id)
                return True
        return False

    @property
    def visible_windows(self) -> List[EditorWindow]:
        return [self._windows[w_id] for w_id in self.z_order if self._windows[w_id].visible]
