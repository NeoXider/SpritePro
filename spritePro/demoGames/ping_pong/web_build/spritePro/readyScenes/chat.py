"""Готовая сцена мультиплеерного чата для SpritePro.

Сцена подключается к s.multiplayer (NetClient). События: chat_message, chat_history, chat_request_history.
Использование в игре:
    from spritePro.readyScenes import ChatScene, ChatStyle
    s.multiplayer.init_context(net, role)
    s.get_screen((500, 600), "Чат")
    s.scene.add_scene("chat", ChatScene)
    s.scene.set_scene_by_name("chat", recreate=True)
    while True:
        s.update(fill_color=ChatStyle.color_bg)
"""

from __future__ import annotations

import time
import pygame

import spritePro as s
from spritePro.readyScenes.chat_logic import ChatLogic
from spritePro.readyScenes.ui_chat import ChatStyle, ChatUI


class ChatScene(s.Scene):
    """Сцена мультиплеерного чата: история, ввод имени, сообщения, скролл (колёсико и мышью), обрезка по viewport."""

    def __init__(self) -> None:
        super().__init__()
        self.context: s.GameContext | None = None
        self._logic: ChatLogic | None = None
        self._ui: ChatUI | None = None
        self._style = ChatStyle
        self._requested_history = False

    def on_enter(self, context: s.GameContext) -> None:
        self.context = context
        Style = self._style
        wh = (s.WH.x, s.WH.y) if context is None else context.WH
        wh_c = s.WH_C if context is None else context.WH_C
        view_w = int(wh[0] * 0.88)
        view_h = int(wh[1] * 0.48)
        view_x = int(wh_c[0] - view_w / 2)
        view_y = 98

        self._logic = ChatLogic()
        self._ui = ChatUI(style=Style)
        self._ui.build(self, wh, wh_c, view_x, view_y, view_w, view_h)
        self._ui.set_on_send(self._on_send)

    def _on_send(self) -> None:
        net_ctx = getattr(s.multiplayer, "_context", None)
        ui = self._ui
        if net_ctx is None or ui is None or ui.input_line is None:
            return
        text = (ui.input_line.text or "").strip()
        if not text:
            return
        nick = (ui.name_line.text or "").strip() if ui.name_line else ""
        if not nick:
            nick = f"ID{net_ctx.client_id}"
        t = time.time()
        net_ctx.send(
            "chat_message", {"sender_id": net_ctx.client_id, "nick": nick, "text": text, "time": t}
        )
        ui.input_line.text = ""
        msg = self._logic.add_message(net_ctx.client_id, nick, text, time_ts=t)
        my_id = net_ctx.client_id
        ui.add_message(msg, my_id)

    def draw(self, screen: pygame.Surface) -> None:
        ctx = self.context
        if ctx is None or not hasattr(ctx, "game"):
            return
        game = ctx.game
        try:
            cam = getattr(game, "camera", None)
            cx = getattr(cam, "x", 0) if cam is not None else 0
            cy = getattr(cam, "y", 0) if cam is not None else 0
        except Exception:
            cx, cy = 0, 0
        if self._ui:
            self._ui.draw(screen, game, cx, cy)

    def update(self, dt: float) -> None:
        net_ctx = getattr(s.multiplayer, "_context", None)
        if net_ctx is None:
            return
        logic = self._logic
        ui = self._ui
        if logic is None or ui is None:
            return
        inp = (
            s.input
            if hasattr(s, "input")
            else (getattr(self.context, "input", None) if self.context else None)
        )
        my_id = net_ctx.client_id

        for msg in net_ctx.poll():
            event = msg.get("event")
            data = msg.get("data") or {}
            result = logic.process_network_message(event, data)
            if result:
                action, payload = result
                if action == "add":
                    ui.add_message(payload, my_id)
                elif action == "rebuild":
                    ui.rebuild_message_rows(logic.get_messages(), my_id)
            if event == "chat_request_history" and net_ctx.is_host:
                net_ctx.send("chat_history", {"messages": logic.get_messages()})

        if not self._requested_history:
            self._requested_history = True
            net_ctx.send("chat_request_history", {})

        scroll = ui.scroll
        if scroll is not None:
            drag_dy: float | None = None
            try:
                mx, my = pygame.mouse.get_pos()
                pressed = pygame.mouse.get_pressed()
                in_view = scroll.view_rect.collidepoint(mx, my)
                if in_view and pressed[0]:
                    if ui.scroll_drag_prev_y is not None:
                        drag_dy = ui.scroll_drag_prev_y - my
                    ui.scroll_drag_prev_y = float(my)
                else:
                    ui.scroll_drag_prev_y = None
            except Exception:
                ui.scroll_drag_prev_y = None
            if inp is not None:
                scroll.update_from_input(inp, mouse_drag_delta_y=drag_dy)
            else:
                scroll.apply_scroll()

        if inp is not None:
            for e in getattr(s, "pygame_events", []):
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    ui.update_focus_by_click(*e.pos)
                    break
        ui.apply_focus_to_inputs()

        if ui.focus == "name" and ui.name_line is not None:
            ui.name_line.input(k_delete=pygame.K_ESCAPE)
            if inp is not None and inp.was_pressed(pygame.K_RETURN):
                ui.focus = "message"
        elif ui.input_line is not None:
            ui.input_line.input(k_delete=pygame.K_ESCAPE)
            if inp is not None and inp.was_pressed(pygame.K_RETURN):
                self._on_send()
