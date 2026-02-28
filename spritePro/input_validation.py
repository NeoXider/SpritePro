"""Валидация и парсинг полей ввода: типы text / int / float.

Используется компонентом TextInput и редактором сцен.
"""

from typing import Any, Literal, Optional, Set, Tuple

InputType = Literal["text", "int", "float"]


def can_add_char(
    input_type: InputType,
    current: str,
    ch: str,
    allowed_text_chars: Optional[Set[str]] = None,
) -> bool:
    """Можно ли добавить символ ch в текущую строку current для данного типа поля."""
    if not ch:
        return False
    if input_type == "text":
        if allowed_text_chars is not None:
            return ch in allowed_text_chars or (ord(ch) >= 0x20 and ch not in "\x00\r\n")
        return ch.isprintable() or ch in " \t"
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


def filter_chars_for_paste(
    input_type: InputType,
    text: str,
    allowed_text_chars: Optional[Set[str]] = None,
) -> str:
    """Оставляет в text только допустимые для типа поля символы (для вставки из буфера)."""
    if input_type == "text":
        if allowed_text_chars is not None:
            return "".join(
                c for c in text
                if c in allowed_text_chars or (ord(c) >= 0x20 and c not in "\x00\r\n")
            )
        return "".join(c for c in text if c.isprintable() or c in " \t")
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
    """Парсит строку в значение по типу поля. Возвращает (ok, value)."""
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
