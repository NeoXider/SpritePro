"""Логика чата: модель сообщений и обработка сетевых событий.

События: chat_message, chat_history, chat_request_history.
Не содержит UI — только данные и разбор входящих сообщений.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List


def _msg(sender_id: int, nick: str, text: str, time_ts: float | None = None) -> dict:
    if time_ts is None:
        time_ts = time.time()
    return {"sender_id": sender_id, "nick": nick, "text": text, "time": time_ts}


class ChatLogic:
    """Хранит список сообщений и обрабатывает сетевые события (без UI)."""

    def __init__(self) -> None:
        self.messages: List[Dict[str, Any]] = []

    def add_message(
        self,
        sender_id: int,
        nick: str,
        text: str,
        time_ts: float | None = None,
    ) -> Dict[str, Any]:
        """Добавляет сообщение и возвращает его запись."""
        msg = _msg(sender_id, nick, text, time_ts)
        self.messages.append(msg)
        return msg

    def set_messages_from_history(self, messages: List[Dict[str, Any]]) -> None:
        """Подменяет список сообщений (после получения истории)."""
        self.messages = [m for m in messages if isinstance(m, dict)]

    def get_messages(self) -> List[Dict[str, Any]]:
        return self.messages.copy()

    def process_network_message(
        self,
        event: str,
        data: Dict[str, Any],
    ) -> tuple[str, Any] | None:
        """Обрабатывает одно входящее сообщение. Возвращает (action, payload) или None.
        action: 'add' — payload = dict сообщения; 'rebuild' — payload не используется.
        """
        if event == "chat_message":
            msg = self.add_message(
                data.get("sender_id", 0),
                data.get("nick", "?"),
                data.get("text", ""),
                data.get("time"),
            )
            return ("add", msg)
        if event == "chat_history":
            msgs = data.get("messages", [])
            if isinstance(msgs, list):
                self.set_messages_from_history(msgs)
                return ("rebuild", None)
        return None
