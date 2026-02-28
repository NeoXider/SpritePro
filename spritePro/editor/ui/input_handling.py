"""Обработка ввода: текстовые поля с типами text / int / float."""

from typing import Any, Literal, Optional, Tuple

import pygame
import string

InputType = Literal["text", "int", "float"]

ALLOWED_INPUT_CHARS = set("0123456789.,-")
ALLOWED_INT_CHARS = set("0123456789-")
ALLOWED_NAME_CHARS = set(string.ascii_letters + string.digits + string.whitespace + "._-()")

KEYPAD_MAP = {
    pygame.K_KP0: "0",
    pygame.K_KP1: "1",
    pygame.K_KP2: "2",
    pygame.K_KP3: "3",
    pygame.K_KP4: "4",
    pygame.K_KP5: "5",
    pygame.K_KP6: "6",
    pygame.K_KP7: "7",
    pygame.K_KP8: "8",
    pygame.K_KP9: "9",
    pygame.K_KP_PERIOD: ".",
    pygame.K_KP_MINUS: "-",
    pygame.K_MINUS: "-",
    pygame.K_PERIOD: ".",
    pygame.K_COMMA: ",",
}


def can_add_char(input_type: InputType, current: str, ch: str) -> bool:
    if not ch:
        return False
    if input_type == "text":
        return ch in ALLOWED_NAME_CHARS or (ord(ch) >= 0x20 and ch not in "\x00\r\n")
    if input_type == "int":
        if ch == "-":
            return not current or current == "-"
        return ch in "0123456789"
    if input_type == "float":
        if ch == "-":
            return not current or current == "-"
        if ch in ".,":
            return "." not in current.replace("-", "")
        return ch in "0123456789"
    return False


def filter_chars_for_paste(input_type: InputType, text: str) -> str:
    if input_type == "text":
        return "".join(c for c in text if c in ALLOWED_NAME_CHARS or (ord(c) >= 0x20 and c not in "\x00\r\n"))
    if input_type == "int":
        out = []
        for c in text:
            if c in "0123456789":
                out.append(c)
            elif c == "-" and not out:
                out.append(c)
        return "".join(out)
    if input_type == "float":
        out = []
        seen_dot = False
        for c in text:
            if c in "0123456789":
                out.append(c)
            elif c == "-" and not out:
                out.append(c)
            elif c in ".," and not seen_dot:
                out.append(".")
                seen_dot = True
        return "".join(out)
    return ""


def parse_input_value(
    input_type: InputType,
    raw: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> Tuple[bool, Any]:
    raw = raw.strip().replace(",", ".")
    if not raw or raw == "-":
        return False, None
    try:
        if input_type == "int":
            value = int(float(raw))
            if min_val is not None:
                value = max(int(min_val), value)
            if max_val is not None:
                value = min(int(max_val), value)
            return True, value
        if input_type == "float":
            value = float(raw)
            if min_val is not None:
                value = max(min_val, value)
            if max_val is not None:
                value = min(max_val, value)
            return True, value
        return True, raw.strip()
    except ValueError:
        return False, None


def get_active_input_type(editor) -> InputType:
    return getattr(editor, "_active_text_input_type", "text")


def _paste_into_editor_buffer(editor, name: str) -> None:
    try:
        if not pygame.scrap.get_init():
            pygame.scrap.init()
    except Exception:
        return
    try:
        data = pygame.scrap.get(pygame.SCRAP_TEXT)
        if not data:
            return
        text = data.decode("utf-8", errors="replace")
        input_type = get_active_input_type(editor)
        filtered = filter_chars_for_paste(input_type, text)
        if filtered:
            editor._text_input_buffers[name] = editor._text_input_buffers.get(name, "") + filtered
    except Exception:
        pass


def _copy_editor_buffer_to_clipboard(editor, name: str) -> None:
    try:
        if not pygame.scrap.get_init():
            pygame.scrap.init()
    except Exception:
        return
    try:
        text = editor._text_input_buffers.get(name, "")
        if text:
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
    except Exception:
        pass


def handle_text_input_keydown(editor, event: pygame.event.Event) -> bool:
    """Обработка KEYDOWN при активном текстовом поле. Возвращает True если событие обработано."""
    name = editor._active_text_input
    if name is None:
        return False

    mod = event.mod & (pygame.KMOD_CTRL | pygame.KMOD_META)
    if mod:
        if event.key == pygame.K_v:
            _paste_into_editor_buffer(editor, name)
            return True
        if event.key == pygame.K_c:
            _copy_editor_buffer_to_clipboard(editor, name)
            return True

    if event.key == pygame.K_RETURN:
        editor._deactivate_text_input(apply=True)
        return True
    if event.key == pygame.K_ESCAPE:
        editor._deactivate_text_input(apply=False)
        return True
    if event.key == pygame.K_BACKSPACE:
        editor._text_input_buffers[name] = editor._text_input_buffers[name][:-1]
        return True

    input_type = get_active_input_type(editor)
    if input_type == "int":
        keypad_no_dot = {k: v for k, v in KEYPAD_MAP.items() if v not in ".,"}
        if event.key in keypad_no_dot and not (event.unicode or ""):
            ch = keypad_no_dot[event.key]
            buf = editor._text_input_buffers.get(name, "")
            if can_add_char(input_type, buf, ch):
                editor._text_input_buffers[name] = buf + ch
            return True
    elif event.key in KEYPAD_MAP and not (event.unicode or ""):
        ch = KEYPAD_MAP[event.key]
        buf = editor._text_input_buffers.get(name, "")
        if can_add_char(input_type, buf, ch):
            editor._text_input_buffers[name] = buf + ch
        return True
    return True


def handle_text_input_text(editor, event: pygame.event.Event) -> bool:
    """Обработка TEXTINPUT при активном текстовом поле."""
    name = editor._active_text_input
    if name is None:
        return False
    input_type = get_active_input_type(editor)
    buf = editor._text_input_buffers.get(name, "")
    added = ""
    for c in (event.text or ""):
        if can_add_char(input_type, buf + added, c):
            added += c
    if added:
        editor._text_input_buffers[name] = buf + added
    return True
