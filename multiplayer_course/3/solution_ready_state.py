"""Решение 3: ready и старт от хоста.

Как в example_ready_state: надпись «Start» в центре, задержка перед автостартом,
локальное обновление ready_map при отправке ready.
"""

import pygame
import spritePro as s

START_DELAY = 1.0


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "Lesson 3 - Solution")
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
                game_started = True
                state.set_text("State: game")
                start_label.set_active(False)

        both_ready = all(ready_map.values())
        if both_ready and not game_started:
            both_ready_timer += dt
            start_label.set_active(True)
        else:
            both_ready_timer = 0.0
            start_label.set_active(False)

        if (
            ctx.is_host
            and not game_started
            and both_ready
            and both_ready_timer >= START_DELAY
        ):
            ctx.send("start", {})
            game_started = True
            state.set_text("State: game")
            start_label.set_active(False)

        info.set_text(
            f"Ready: {is_ready} | host={ready_map['host']} client={ready_map['client']}"
        )


if __name__ == "__main__":
    # Запуск решения.
    s.networking.run()
