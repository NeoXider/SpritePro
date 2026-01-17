import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def main() -> None:
    s.get_screen((900, 600), "EventBus Demo")

    box = s.Sprite("", (70, 70), s.WH_C)
    box.set_color((120, 200, 255))

    title = s.TextSprite("EventBus Demo", 28, (255, 255, 255), (s.WH_C.x, 30))
    hints = s.TextSprite(
        "1: start timer  |  2: stop timer  |  C: custom event  |  R: reset counter  |  Mouse: click",
        18,
        (200, 200, 200),
        (s.WH_C.x, 565),
    )
    status = s.TextSprite(
        "События будут появляться здесь...", 20, (220, 220, 220), (s.WH_C.x, 520)
    )

    state = {"ticks": 0}

    def show(text: str) -> None:
        status.text = text

    def on_key_down(key, event) -> None:
        if key == pygame.K_1:
            timer.start()
            s.debug_log_info("Timer started")
            show("Timer started")
            return
        if key == pygame.K_2:
            timer.stop()
            s.debug_log_info("Timer stopped")
            show("Timer stopped")
            return
        if key == pygame.K_c:
            s.events.send("custom_event", message="Привет из EventBus!")
            return
        if key == pygame.K_r:
            state["ticks"] = 0
            show("Counter reset")
            return
        show(f"Key down: {pygame.key.name(key)}")

    def on_key_up(key, event) -> None:
        show(f"Key up: {pygame.key.name(key)}")

    def on_mouse_down(button, pos, event) -> None:
        show(f"Mouse down: button={button}, pos={pos}")

    def on_mouse_up(button, pos, event) -> None:
        show(f"Mouse up: button={button}, pos={pos}")

    def on_tick() -> None:
        state["ticks"] += 1
        show(f"Tick #{state['ticks']}")
        if state["ticks"] % 2 == 0:
            box.set_color((120, 200, 255))
        else:
            box.set_color((255, 170, 120))

    def on_custom_event(message: str) -> None:
        show(f"Custom event: {message}")

    def on_quit(event) -> None:
        s.debug_log_info("Quit requested")

    timer = s.Timer(
        1.0, callback=lambda: s.events.send("tick"), repeat=True, autostart=False
    )

    s.events.connect("key_down", on_key_down)
    s.events.connect("key_up", on_key_up)
    s.events.connect("mouse_down", on_mouse_down)
    s.events.connect("mouse_up", on_mouse_up)
    s.events.connect("tick", on_tick)
    s.events.connect("custom_event", on_custom_event)
    s.events.connect("quit", on_quit)

    _ = (title, hints, status)

    while True:
        s.update(fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()
