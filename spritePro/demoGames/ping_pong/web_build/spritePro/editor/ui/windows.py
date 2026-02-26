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

        return pygame.Rect(self.rect.x + 10, tabs_top + 30, self.rect.width - 20, self.rect.height - 74)

    def _set_page(self, index: int) -> None:
        self.page_index = max(0, min(index, len(self.page_titles) - 1))


class SettingsWindow(EditorWindow):
    """Окно настроек с несколькими страницами."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(
            window_id="settings",
            title="Settings",
            rect=rect,
            page_titles=["Scene", "View"],
        )

    def render(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_bold: pygame.font.Font,
        colors: Dict[str, Color],
        *,
        scene_grid_visible: bool,
        scene_grid_labels_visible: bool,
        scene_snap_to_grid: bool,
        on_toggle_grid: Callable[[], None],
        on_toggle_grid_labels: Callable[[], None],
        on_toggle_snap: Callable[[], None],
        zoom_text: str,
        grid_text: str,
    ) -> None:
        if not self.visible:
            return
        body = self.render_base(screen, font, font_bold, colors)

        if self.current_page == "Scene":
            self._render_scene_page(
                screen,
                font,
                colors,
                body,
                scene_grid_visible=scene_grid_visible,
                scene_grid_labels_visible=scene_grid_labels_visible,
                scene_snap_to_grid=scene_snap_to_grid,
                on_toggle_grid=on_toggle_grid,
                on_toggle_grid_labels=on_toggle_grid_labels,
                on_toggle_snap=on_toggle_snap,
            )
            return
        self._render_view_page(screen, font, colors, body, zoom_text=zoom_text, grid_text=grid_text)

    def _render_scene_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        scene_grid_visible: bool,
        scene_grid_labels_visible: bool,
        scene_snap_to_grid: bool,
        on_toggle_grid: Callable[[], None],
        on_toggle_grid_labels: Callable[[], None],
        on_toggle_snap: Callable[[], None],
    ) -> None:
        row_h = 26
        y = body.y

        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Grid Visible",
            scene_grid_visible,
            on_toggle_grid,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Grid Labels",
            scene_grid_labels_visible,
            on_toggle_grid_labels,
        )
        y += row_h + 8
        self._render_toggle_row(
            screen,
            font,
            colors,
            pygame.Rect(body.x, y, body.width, row_h),
            "Snap To Grid",
            scene_snap_to_grid,
            on_toggle_snap,
        )

    def _render_view_page(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        colors: Dict[str, Color],
        body: pygame.Rect,
        *,
        zoom_text: str,
        grid_text: str,
    ) -> None:
        line1 = font.render(f"Camera Zoom: {zoom_text}", True, colors["ui_text"])
        line2 = font.render(f"Grid Size: {grid_text}", True, colors["ui_text"])
        hint = font.render("Use sliders in status bar", True, (140, 140, 150))
        screen.blit(line1, (body.x, body.y))
        screen.blit(line2, (body.x, body.y + 28))
        screen.blit(hint, (body.x, body.y + 60))

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
        screen.blit(caption_text, (toggle_rect.centerx - caption_text.get_width() // 2, toggle_rect.y + 4))
        self._add_action(toggle_rect, callback)


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
