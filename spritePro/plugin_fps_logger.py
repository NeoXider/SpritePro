"""
Встроенный плагин: периодический вывод FPS в debug-лог.

Подключается при импорте. Чтобы включить: импортируйте модуль до get_screen/update.
Чтобы отключить: pm = get_plugin_manager(); pm.disable_plugin("fps_logger").
"""

from __future__ import annotations

import time

from .plugins import register_plugin, hook

_INTERVAL = 2.0
_last_log_time: float = time.monotonic()


@register_plugin("fps_logger", "1.0.0", "SpritePro")
@hook("game_update")
def _on_game_update(dt: float) -> None:
    import spritePro as s

    global _last_log_time
    now = time.monotonic()
    if now - _last_log_time >= _INTERVAL:
        _last_log_time = now
        clock = getattr(s, "clock", None)
        fps_val = clock.get_fps() if clock is not None else 0.0
        s.debug_log_info(f"[fps_logger] FPS: {fps_val:.1f} dt={dt:.4f}")
