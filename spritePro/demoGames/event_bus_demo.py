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
        "1: start timer  |  2: stop timer  |  C: custom event  |  L: local event  |  R: reset counter  |  Mouse: click",
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
        if key == pygame.K_l:
            local_event.send(value=state["ticks"])
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

    def on_timer_tick() -> None:
        state["ticks"] += 1
        show(f"Tick #{state['ticks']}")
        if state["ticks"] % 2 == 0:
            box.set_color((120, 200, 255))
        else:
            box.set_color((255, 170, 120))

    def on_custom_event(message: str) -> None:
        show(f"Custom event: {message}")

    def on_local_event(value: int) -> None:
        show(f"Local event: value={value}")

    def on_quit(event) -> None:
        s.debug_log_info("Quit requested")

    timer = s.Timer(
        1.0,
        callback=lambda: s.events.send("timer_tick"),
        repeat=True,
        autostart=False,
    )
    local_event = s.LocalEvent()
    local_event.connect(on_local_event)

    s.events.connect(s.globalEvents.KEY_DOWN, on_key_down)
    s.events.connect(s.globalEvents.KEY_UP, on_key_up)
    s.events.connect(s.globalEvents.MOUSE_DOWN, on_mouse_down)
    s.events.connect(s.globalEvents.MOUSE_UP, on_mouse_up)
    s.events.connect("timer_tick", on_timer_tick)
    s.events.connect("custom_event", on_custom_event)
    s.events.connect(s.globalEvents.QUIT, on_quit)

    _ = (title, hints, status)

    running = True
    while running:
        s.update(fill_color=(20, 20, 30))

        if s.input.was_pressed(pygame.K_ESCAPE):
            running = False

        for key in (
            pygame.K_1,
            pygame.K_2,
            pygame.K_c,
            pygame.K_l,
            pygame.K_r,
        ):
            if s.input.was_pressed(key):
                s.events.send(s.globalEvents.KEY_DOWN, key=key, event=None)
            if s.input.was_released(key):
                s.events.send(s.globalEvents.KEY_UP, key=key, event=None)

        if s.input.was_mouse_pressed(1):
            s.events.send(
                s.globalEvents.MOUSE_DOWN, button=1, pos=s.input.mouse_pos, event=None
            )
        if s.input.was_mouse_released(1):
            s.events.send(
                s.globalEvents.MOUSE_UP, button=1, pos=s.input.mouse_pos, event=None
            )


if __name__ == "__main__":
    main()
