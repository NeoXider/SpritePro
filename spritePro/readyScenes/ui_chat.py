"""UI чата: стиль, построение интерфейса, пузыри сообщений, скролл и отрисовка с обрезкой по viewport."""

from __future__ import annotations

from datetime import datetime as _dt
from typing import Any, Callable, Dict, List, Optional

import pygame

import spritePro as s
from spritePro.constants import Anchor
from spritePro.layout import Layout, LayoutAlignMain, LayoutAlignCross
from spritePro.scroll import ScrollView


class ChatStyle:
    """Стиль сцены чата (цвета, размеры). Можно переопределить атрибуты перед созданием UI."""

    color_bg = (18, 20, 28)
    color_panel = (28, 32, 44)
    color_panel_border = (55, 62, 80)
    color_input_bg = (35, 40, 55)
    color_input_border = (70, 85, 110)
    font_size = 20
    font_size_nick = 16
    font_size_title = 26
    font_size_hint = 13
    color_title = (230, 235, 255)
    color_hint = (120, 130, 155)
    color_text = (220, 225, 240)
    color_self_bg = (45, 75, 55)
    color_self_border = (70, 130, 90)
    color_self_text = (180, 255, 200)
    color_other_bg = (50, 48, 58)
    color_other_border = (85, 80, 95)
    color_other_text = (255, 235, 210)
    gap = 8
    msg_padding = 10
    radius_panel = 12
    radius_input = 10
    radius_bubble = 8


def _time_str(time_ts: Optional[float]) -> str:
    if time_ts is None:
        return ""
    try:
        return _dt.fromtimestamp(time_ts).strftime("%H:%M:%S") + " "
    except (OSError, ValueError):
        return ""


class ChatUI:
    """Построение и отрисовка UI чата: заголовок, поле имени, панель со скроллом сообщений, ввод и кнопка.

    Отрисовка контента скролла выполняется на отдельную поверхность размером viewport,
    чтобы контент гарантированно не выходил за границы видимой области.
    """

    def __init__(self, style: Optional[type] = None) -> None:
        self._style = style or ChatStyle
        self._scene: Optional[s.Scene] = None
        self._scroll: Optional[ScrollView] = None
        self._layout_messages: Optional[Layout] = None
        self._message_sprites: List[Any] = []
        self._title: Optional[s.TextSprite] = None
        self._hint: Optional[s.TextSprite] = None
        self._name_line: Optional[s.TextSprite] = None
        self._name_bg: Optional[s.Sprite] = None
        self._input_line: Optional[s.TextSprite] = None
        self._input_bg: Optional[s.Sprite] = None
        self._input_inner: Optional[s.Sprite] = None
        self._send_btn: Optional[s.Button] = None
        self._focus: str = "message"
        self._scroll_drag_prev_y: Optional[float] = None
        self._on_send: Optional[Callable[[], None]] = None

    @property
    def style(self) -> type:
        return self._style

    @property
    def scroll(self) -> Optional[ScrollView]:
        return self._scroll

    @property
    def layout_messages(self) -> Optional[Layout]:
        return self._layout_messages

    @property
    def input_line(self) -> Optional[s.TextSprite]:
        return self._input_line

    @property
    def name_line(self) -> Optional[s.TextSprite]:
        return self._name_line

    @property
    def send_btn(self) -> Optional[s.Button]:
        return self._send_btn

    @property
    def focus(self) -> str:
        return self._focus

    @focus.setter
    def focus(self, value: str) -> None:
        self._focus = value

    @property
    def scroll_drag_prev_y(self) -> Optional[float]:
        return self._scroll_drag_prev_y

    @scroll_drag_prev_y.setter
    def scroll_drag_prev_y(self, value: Optional[float]) -> None:
        self._scroll_drag_prev_y = value

    def set_on_send(self, callback: Callable[[], None]) -> None:
        self._on_send = callback

    def build(
        self,
        scene: s.Scene,
        wh: tuple,
        wh_c: tuple,
        view_x: int,
        view_y: int,
        view_w: int,
        view_h: int,
    ) -> None:
        """Создаёт все элементы UI и привязывает их к сцене."""
        self._scene = scene
        Style = self._style

        self._title = s.TextSprite(
            "Чат",
            font_size=Style.font_size_title,
            color=Style.color_title,
            pos=(wh_c[0], 28),
            scene=scene,
        )
        self._hint = s.TextSprite(
            "Колёсико или перетаскивание мыши — скролл · Enter или кнопка — отправить",
            font_size=Style.font_size_hint,
            color=Style.color_hint,
            pos=(wh_c[0], 52),
            scene=scene,
        )
        name_label = s.TextSprite(
            "Имя:",
            font_size=Style.font_size_hint,
            color=Style.color_hint,
            pos=(view_x + 42, 78),
            anchor=Anchor.MID_RIGHT,
            scene=scene,
        )
        name_w, name_h = 140, 28
        self._name_bg = s.Sprite(
            "",
            (name_w + 4, name_h + 4),
            (view_x + 42 + name_w // 2 + 6, 78),
            scene=scene,
            sorting_order=-3,
        )
        self._name_bg.set_rect_shape(
            size=(name_w + 4, name_h + 4),
            color=Style.color_input_border,
            border_radius=Style.radius_input,
        )
        name_inner = s.Sprite(
            "",
            (name_w, name_h),
            (view_x + 42 + name_w // 2 + 6, 78),
            scene=scene,
            sorting_order=-2,
        )
        name_inner.set_rect_shape(
            size=(name_w, name_h),
            color=Style.color_input_bg,
            border_radius=Style.radius_input - 2,
        )
        self._name_line = s.TextSprite(
            "",
            font_size=Style.font_size_hint + 1,
            color=Style.color_text,
            pos=(view_x + 52, 78),
            anchor=Anchor.MID_LEFT,
            scene=scene,
        )

        panel = s.Sprite(
            "",
            (view_w + 4, view_h + 4),
            (wh_c[0], view_y + view_h // 2 + 2),
            scene=scene,
            sorting_order=-5,
        )
        panel.set_rect_shape(
            size=(view_w + 4, view_h + 4),
            color=Style.color_panel_border,
            border_radius=Style.radius_panel + 2,
        )
        panel_bg = s.Sprite(
            "",
            (view_w, view_h),
            (wh_c[0], view_y + view_h // 2),
            scene=scene,
            sorting_order=-4,
        )
        panel_bg.set_rect_shape(
            size=(view_w, view_h),
            color=Style.color_panel,
            border_radius=Style.radius_panel,
        )

        content_w = view_w - Style.msg_padding * 2
        content_h = 8000
        messages_container = s.layout_vertical(
            None,
            [],
            gap=Style.gap,
            padding=Style.msg_padding,
            align_main=LayoutAlignMain.END,
            align_cross=LayoutAlignCross.START,
            use_local=True,
            pos=(view_x + view_w // 2, view_y + content_h // 2),
            size=(content_w, content_h),
            scene=scene,
            auto_apply=True,
        )
        self._layout_messages = messages_container
        self._scroll = ScrollView(pos=(view_x, view_y), size=(view_w, view_h), scroll_speed=40)
        self._scroll.set_content(messages_container)
        self._scroll.apply_scroll()
        self._scroll.scroll_y = 0

        input_h = 40
        btn_w = 100
        gap = 10
        input_w = view_w - btn_w - gap
        input_left = view_x
        input_center_x = input_left + input_w // 2
        input_y = view_y + view_h + 44
        btn_center_x = input_left + input_w + gap + btn_w // 2

        self._input_bg = s.Sprite(
            "",
            (input_w + 4, input_h + 4),
            (input_center_x, input_y + 2),
            scene=scene,
            sorting_order=-3,
        )
        self._input_bg.set_rect_shape(
            size=(input_w + 4, input_h + 4),
            color=Style.color_input_border,
            border_radius=Style.radius_input + 2,
        )
        self._input_inner = s.Sprite(
            "",
            (input_w, input_h),
            (input_center_x, input_y),
            scene=scene,
            sorting_order=-2,
        )
        self._input_inner.set_rect_shape(
            size=(input_w, input_h),
            color=Style.color_input_bg,
            border_radius=Style.radius_input,
        )
        self._input_line = s.TextSprite(
            "",
            font_size=Style.font_size,
            color=Style.color_text,
            pos=(input_left + Style.msg_padding + 8, input_y),
            anchor=Anchor.MID_LEFT,
            scene=scene,
        )
        self._send_btn = s.Button(
            "",
            (btn_w, input_h),
            (btn_center_x, input_y),
            text="Отправить",
            text_size=Style.font_size_hint + 1,
            text_color=Style.color_self_text,
            scene=scene,
        ).set_rect_shape(color=Style.color_self_bg, border_radius=Style.radius_input)
        self._send_btn.on_click(self._invoke_send)

        self._viewport_surface = None

    def _invoke_send(self, *args: Any, **kwargs: Any) -> None:
        if self._on_send:
            self._on_send()

    def _make_bubble(
        self,
        is_self: bool,
        nick: str,
        text: str,
        time_ts: Optional[float] = None,
    ) -> tuple:
        if self._scene is None or self._layout_messages is None:
            raise RuntimeError("ChatUI.build() must be called first")
        Style = self._style
        time_str = _time_str(time_ts)
        line_text = f"{time_str}{nick}: {text}"
        text_color = Style.color_self_text if is_self else Style.color_other_text
        bg_color = Style.color_self_bg if is_self else Style.color_other_bg
        pad = Style.msg_padding
        txt = s.TextSprite(
            line_text,
            font_size=Style.font_size_nick,
            color=text_color,
            pos=(0, 0),
            anchor=Anchor.TOP_LEFT,
            scene=self._scene,
        )
        tw, th = txt.rect.width, txt.rect.height
        bw, bh = tw + pad * 2, th + pad * 2
        bubble = s.Sprite("", (bw, bh), (0, 0), scene=self._scene, sorting_order=10)
        bubble.set_rect_shape(
            size=(bw, bh),
            color=bg_color,
            border_radius=Style.radius_bubble,
        )
        txt.set_parent(bubble, keep_world_position=False)
        txt.local_position = (pad, pad)
        return bubble, txt

    def rebuild_message_rows(self, messages: List[Dict[str, Any]], my_id: int) -> None:
        if self._layout_messages is None or self._scroll is None:
            return
        for bubble in self._message_sprites:
            bubble.set_scene(None, unregister_when_none=True)
            for c in getattr(bubble, "children", [])[:]:
                if hasattr(c, "set_scene"):
                    c.set_scene(None, unregister_when_none=True)
        self._message_sprites.clear()
        arranged = list(self._layout_messages.arranged_children)
        if arranged:
            self._layout_messages.remove_children(*arranged)
        for m in messages:
            nick = m.get("nick", f"ID{m.get('sender_id', '?')}")
            text = m.get("text", "")
            time_ts = m.get("time")
            is_self = m.get("sender_id") == my_id
            bubble, _ = self._make_bubble(is_self, nick, text, time_ts=time_ts)
            self._message_sprites.append(bubble)
            self._layout_messages.add(bubble)
        self._scroll.scroll_y = self._scroll.scroll_max
        self._scroll.apply_scroll()

    def add_message(self, msg: Dict[str, Any], my_id: int) -> None:
        if self._layout_messages is None or self._scroll is None:
            return
        nick = msg.get("nick", f"ID{msg.get('sender_id', '?')}")
        text = msg.get("text", "")
        time_ts = msg.get("time")
        is_self = msg.get("sender_id") == my_id
        bubble, _ = self._make_bubble(is_self, nick, text, time_ts=time_ts)
        self._message_sprites.append(bubble)
        self._layout_messages.add(bubble)
        self._scroll.scroll_y = self._scroll.scroll_max
        self._scroll.apply_scroll()

    def _content_sprites(self) -> List[Any]:
        """Список спрайтов контента скролла (layout + все потомки) для отрисовки на view_surf."""
        if self._scroll is None or self._scroll._content is None:
            return []
        root = self._scroll._content
        out: List[Any] = []
        stack = [root]
        while stack:
            node = stack.pop()
            out.append(node)
            stack.extend(getattr(node, "children", []))
        return out

    def _blit_sprite(
        self,
        surface: pygame.Surface,
        sprite: Any,
        camera_x: float,
        camera_y: float,
        offset_x: float = 0,
        offset_y: float = 0,
    ) -> None:
        if getattr(sprite, "screen_space", False):
            surface.blit(sprite.image, (sprite.rect.x - offset_x, sprite.rect.y - offset_y))
        else:
            x = int(sprite.rect.x - camera_x - offset_x)
            y = int(sprite.rect.y - camera_y - offset_y)
            surface.blit(sprite.image, (x, y))

    def draw(self, screen: pygame.Surface, game: Any, camera_x: float, camera_y: float) -> None:
        if self._scroll is None or self._scroll._content is None:
            game.draw(screen)
            return
        view_rect = self._scroll.view_rect
        vw, vh = int(view_rect.width), int(view_rect.height)
        if vw <= 0 or vh <= 0:
            game.draw(screen)
            return

        content_list = self._content_sprites()
        content_set = {s for s in content_list}

        for sprite in game.all_sprites:
            if sprite in content_set:
                continue
            self._blit_sprite(screen, sprite, camera_x, camera_y, 0, 0)

        old_clip = screen.get_clip()
        screen.set_clip(view_rect)
        for sprite in content_list:
            self._blit_sprite(screen, sprite, camera_x, camera_y, 0, 0)
        screen.set_clip(old_clip)

    def update_focus_by_click(self, mx: int, my: int) -> None:
        if self._name_bg is not None and self._name_bg.rect.collidepoint(mx, my):
            self._focus = "name"
            return
        if self._input_inner is not None and self._input_inner.rect.collidepoint(mx, my):
            self._focus = "message"
            return

    def apply_focus_to_inputs(self) -> None:
        if self._name_line is not None:
            self._name_line.input_active = self._focus == "name"
        if self._input_line is not None:
            self._input_line.input_active = self._focus == "message"
