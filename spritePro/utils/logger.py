"""Лёгкий логгер с попыткой использовать SpritePro debug-логи."""

from __future__ import annotations

import logging
from typing import Callable


def _get_spritepro_logger(method_name: str) -> Callable[[str], None] | None:
    try:
        import spritePro as s

        return getattr(s, method_name)
    except Exception:
        return None


def log_info(*message: object) -> None:
    """Логирует информационное сообщение."""
    text = " ".join(str(part) for part in message)
    handler = _get_spritepro_logger("debug_log_info")
    if handler:
        handler(text)
        return
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info(text)


def log_warning(*message: object) -> None:
    """Логирует предупреждение."""
    text = " ".join(str(part) for part in message)
    handler = _get_spritepro_logger("debug_log_warning")
    if handler:
        handler(text)
        return
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.warning(text)


def log_error(*message: object) -> None:
    """Логирует ошибку."""
    text = " ".join(str(part) for part in message)
    handler = _get_spritepro_logger("debug_log_error")
    if handler:
        handler(text)
        return
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.error(text)
