"""Практика 3: ready и start с TODO.

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал (при start — обновить game_started/state/start_label; хост — при обоих готовых и задержке отправить start).
- Вариант: тот же сценарий через EventBus; см. example_ready_state_events.py.
"""

import pygame
import spritePro as s

START_DELAY = 1.0


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "Lesson 3 - Practice")
    ctx = s.multiplayer.init_context(net, role, color)

    is_ready = False
    game_started = False
    ready_map = {"host": False, "client": False}
    player_key = "host" if ctx.is_host else "client"
    both_ready_timer = 0.0

    info = s.TextSprite(
        "Space: ready", 28, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT
    )
    state = s.TextSprite(
        "State: lobby", 28, (240, 240, 240), (20, 60), anchor=s.Anchor.TOP_LEFT
    )
    start_label = s.TextSprite(
        "Start", 48, (120, 255, 120), s.WH_C, anchor=s.Anchor.CENTER
    )
    start_label.set_active(False)

    while True:
        s.update(fill_color=(15, 15, 20))
        dt = s.dt

        if s.input.was_pressed(pygame.K_SPACE) and not game_started:
            is_ready = not is_ready
            ctx.send("ready", {"id": player_key, "value": is_ready})
            ready_map[player_key] = is_ready

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "ready":
                pid = data.get("id")
                if pid in ready_map:
                    ready_map[pid] = bool(data.get("value"))
            elif event == "start":
                # TODO: game_started = True, state.set_text("State: game"), start_label.set_active(False)
                pass

        both_ready = all(ready_map.values())
        if both_ready and not game_started:
            both_ready_timer += dt
            start_label.set_active(True)
        else:
            both_ready_timer = 0.0
            start_label.set_active(False)

        if ctx.is_host and not game_started:
            # TODO: если both_ready и both_ready_timer >= START_DELAY — ctx.send("start", {}), game_started = True, state.set_text("State: game"), start_label.set_active(False)
            pass

        info.set_text(
            f"Ready: {is_ready} | host={ready_map['host']} client={ready_map['client']}"
        )


if __name__ == "__main__":
    # Запуск практики.
    s.networking.run()
