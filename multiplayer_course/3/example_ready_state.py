"""Пример 3: готовность игроков и старт игры.

Синхронизация флагов ready между хостом и клиентом; при готовности обоих
появляется надпись «Start» в центре; хост отправляет start и игра начинается.
"""

import pygame
import spritePro as s

START_DELAY = 1.0  # сколько секунд показывать «Start» перед автостартом


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 600), "Lesson 3 - Ready State")
    ctx = s.multiplayer.init_context(net, role)

    is_ready = False
    game_started = False
    ready_map = {"host": False, "client": False}
    player_key = "host" if ctx.is_host else "client"
    both_ready_timer = 0.0  # накапливаем время, пока оба готовы

    info = s.TextSprite("Space: ready", 28, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    state = s.TextSprite("State: lobby", 28, (240, 240, 240), (20, 60), anchor=s.Anchor.TOP_LEFT)
    start_label = s.TextSprite("Start", 48, (120, 255, 120), s.WH_C, anchor=s.Anchor.CENTER)
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

        # Хост шлёт start только после задержки — надпись «Start» успевает отобразиться.
        if ctx.is_host and not game_started and both_ready and both_ready_timer >= START_DELAY:
            ctx.send("start", {})
            game_started = True
            state.set_text("State: game")
            start_label.set_active(False)

        info.set_text(f"Ready: {is_ready} | host={ready_map['host']} client={ready_map['client']}")


if __name__ == "__main__":
    s.networking.run()
