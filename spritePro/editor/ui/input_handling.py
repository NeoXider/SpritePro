"""Обработка ввода: текстовые поля, маппинг клавиш."""

import pygame
import string

# Символы, допустимые в числовых полях (zoom, grid, свойства)
ALLOWED_INPUT_CHARS = set("0123456789.,-")
# Для поля Name — буквы, цифры, пробел и типичные символы
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


def is_allowed_input_char(ch: str) -> bool:
    return ch in ALLOWED_INPUT_CHARS


def is_allowed_char_for_input(editor, ch: str) -> bool:
    if editor._active_text_input == "prop_input_name":
        return ch in ALLOWED_NAME_CHARS or (ch and ord(ch) >= 0x20 and ch not in "\x00\r\n")
    return ch in ALLOWED_INPUT_CHARS


def handle_text_input_keydown(editor, event: pygame.event.Event) -> bool:
    """Обработка KEYDOWN при активном текстовом поле. Возвращает True если событие обработано."""
    name = editor._active_text_input
    if name is None:
        return False

    if event.key == pygame.K_RETURN:
        editor._deactivate_text_input(apply=True)
        return True
    if event.key == pygame.K_ESCAPE:
        editor._deactivate_text_input(apply=False)
        return True
    if event.key == pygame.K_BACKSPACE:
        editor._text_input_buffers[name] = editor._text_input_buffers[name][:-1]
        return True

    if name == "prop_input_name":
        return True
    ch = event.unicode
    if ch and is_allowed_char_for_input(editor, ch):
        editor._text_input_buffers[name] += ch
        return True
    if event.key in KEYPAD_MAP:
        editor._text_input_buffers[name] += KEYPAD_MAP[event.key]
        return True
    return True


def handle_text_input_text(editor, event: pygame.event.Event) -> bool:
    """Обработка TEXTINPUT при активном текстовом поле."""
    name = editor._active_text_input
    if name is None:
        return False
    text = event.text or ""
    if name == "prop_input_name":
        filtered = "".join(c for c in text if (c in ALLOWED_NAME_CHARS or (ord(c) >= 0x20 and c not in "\r\n")))
    else:
        filtered = "".join(c for c in text if is_allowed_input_char(c))
    if filtered:
        editor._text_input_buffers[name] += filtered
    return True
