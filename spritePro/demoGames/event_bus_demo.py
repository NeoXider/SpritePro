import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class EventBusDemoScene(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.box = s.Sprite("", (70, 70), s.WH_C, scene=self)
        self.box.set_color((120, 200, 255))

        self.title = s.TextSprite("EventBus Demo", 28, (255, 255, 255), (s.WH_C.x, 30), scene=self)
        self.hints = s.TextSprite(
            "1: start timer  |  2: stop timer  |  C: custom event  |  L: local event  |  R: reset counter  |  Mouse: click",
            18,
            (200, 200, 200),
            (s.WH_C.x, 565),
            scene=self,
        )
        self.status = s.TextSprite(
            "События будут появляться здесь...",
            20,
            (220, 220, 220),
            (s.WH_C.x, 520),
            scene=self,
        )

        self.state = {"ticks": 0}
        self.timer = s.Timer(
            1.0,
            callback=lambda: s.events.send("timer_tick"),
            repeat=True,
            autostart=False,
        )
        self.local_event = s.LocalEvent()
        self.local_event.connect(self.on_local_event)

        s.events.connect(s.globalEvents.KEY_DOWN, self.on_key_down)
        s.events.connect(s.globalEvents.KEY_UP, self.on_key_up)
        s.events.connect(s.globalEvents.MOUSE_DOWN, self.on_mouse_down)
        s.events.connect(s.globalEvents.MOUSE_UP, self.on_mouse_up)
        s.events.connect("timer_tick", self.on_timer_tick)
        s.events.connect("custom_event", self.on_custom_event)
        s.events.connect(s.globalEvents.QUIT, self.on_quit)

    def show(self, text: str) -> None:
        self.status.text = text

    def on_key_down(self, key, event) -> None:
        if key == pygame.K_1:
            self.timer.start()
            s.debug_log_info("Timer started")
            self.show("Timer started")
            return
        if key == pygame.K_2:
            self.timer.stop()
            s.debug_log_info("Timer stopped")
            self.show("Timer stopped")
            return
        if key == pygame.K_c:
            s.events.send("custom_event", message="Привет из EventBus!")
            return
        if key == pygame.K_l:
            self.local_event.send(value=self.state["ticks"])
            return
        if key == pygame.K_r:
            self.state["ticks"] = 0
            self.show("Counter reset")
            return
        self.show(f"Key down: {pygame.key.name(key)}")

    def on_key_up(self, key, event) -> None:
        self.show(f"Key up: {pygame.key.name(key)}")

    def on_mouse_down(self, button, pos, event) -> None:
        self.show(f"Mouse down: button={button}, pos={pos}")

    def on_mouse_up(self, button, pos, event) -> None:
        self.show(f"Mouse up: button={button}, pos={pos}")

    def on_timer_tick(self) -> None:
        self.state["ticks"] += 1
        self.show(f"Tick #{self.state['ticks']}")
        if self.state["ticks"] % 2 == 0:
            self.box.set_color((120, 200, 255))
        else:
            self.box.set_color((255, 170, 120))

    def on_custom_event(self, message: str) -> None:
        self.show(f"Custom event: {message}")

    def on_local_event(self, value: int) -> None:
        self.show(f"Local event: value={value}")

    def on_quit(self, event) -> None:
        s.debug_log_info("Quit requested")

    def update(self, dt: float) -> None:
        pass


def main() -> None:
    s.run(
        scene=EventBusDemoScene,
        size=(900, 600),
        title="EventBus Demo",
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    main()
