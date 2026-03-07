"""Демо: Events + Multiplayer (камень/ножницы/бумага).

Запуск:
1) Быстрый режим (хост + второй клиент):
   python spritePro/demoGames/events_rps_demo.py --quick --host 127.0.0.1 --port 5050
2) Хост-режим:
   python spritePro/demoGames/events_rps_demo.py --host_mode --host 0.0.0.0 --port 5050
3) Только сервер:
   python spritePro/demoGames/events_rps_demo.py --server --host 0.0.0.0 --port 5050
4) Клиент:
   python spritePro/demoGames/events_rps_demo.py --host IP_СЕРВЕРА --port 5050
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame  # noqa: E402

import spritePro as s  # noqa: E402


CHOICES = {
    pygame.K_1: "rock",
    pygame.K_2: "paper",
    pygame.K_3: "scissors",
}


def _resolve_winner(left: str, right: str) -> int:
    if left == right:
        return 0
    if (left, right) in (
        ("rock", "scissors"),
        ("scissors", "paper"),
        ("paper", "rock"),
    ):
        return 1
    return -1


class EventsRpsScene(s.Scene):
    def __init__(self, net: s.NetClient, role: str) -> None:
        super().__init__()
        s.multiplayer.init_context(net, role)
        self.ctx = s.multiplayer_ctx
        self.title = s.TextSprite("Rock / Paper / Scissors", 30, (255, 255, 255), (400, 40), scene=self)
        self.hint = s.TextSprite("1=Rock  2=Paper  3=Scissors", 20, (200, 200, 200), (400, 80), scene=self)
        self.status = s.TextSprite("Make your choice...", 20, (220, 220, 220), (400, 120), scene=self)
        self.my_info = s.TextSprite("You (ID: ?)", 20, (120, 200, 255), (200, 220), scene=self)
        self.other_info = s.TextSprite("Other (ID: ?)", 20, (255, 200, 120), (600, 220), scene=self)
        self.my_choice_text = s.TextSprite("?", 36, (120, 200, 255), (200, 270), scene=self)
        self.other_choice_text = s.TextSprite("?", 36, (255, 200, 120), (600, 270), scene=self)
        self.score_text = s.TextSprite("Score: 0 - 0", 22, (255, 255, 255), (400, 360), scene=self)

        self.my_choice: str | None = None
        self.other_choice: str | None = None
        self.my_score = 0
        self.other_score = 0
        self.other_id: int | None = None
        self.last_result_at: float | None = None
        self.result_delay = 1.0
        s.events.connect("rps_choice", self.on_choice)

    def on_choice(self, choice: str, sender_id: int | None = None) -> None:
        if self.last_result_at is not None:
            return

        if sender_id == self.ctx.client_id or sender_id is None:
            self.my_choice = choice
        else:
            self.other_choice = choice
            self.other_id = sender_id

        if self.my_choice and self.other_choice:
            result = _resolve_winner(self.my_choice, self.other_choice)
            if result > 0:
                self.my_score += 1
                self.status.set_text("You win this round!")
            elif result < 0:
                self.other_score += 1
                self.status.set_text("You lose this round!")
            else:
                self.status.set_text("Draw.")
            self.last_result_at = s.time_since_start

    def update(self, dt: float) -> None:
        if self.last_result_at is None:
            for key, choice in CHOICES.items():
                if s.input.was_pressed(key):
                    s.events.send(
                        "rps_choice",
                        route="all",
                        net=self.ctx,
                        choice=choice,
                        sender_id=self.ctx.client_id,
                    )

        for msg in self.ctx.poll():
            if msg.get("event") == "rps_choice":
                s.events.send("rps_choice", **msg.get("data", {}))

        self.my_info.set_text(f"You (ID: {self.ctx.client_id})")
        other_id_label = "?" if self.other_id is None else str(self.other_id)
        self.other_info.set_text(f"Other (ID: {other_id_label})")

        if self.last_result_at is not None and s.time_since_start - self.last_result_at >= self.result_delay:
            self.last_result_at = None
            self.my_choice = None
            self.other_choice = None
            self.status.set_text("Make your choice...")

        self.my_choice_text.set_text(self.my_choice or "?")
        self.other_choice_text.set_text(self.other_choice or "?")
        self.score_text.set_text(f"Score: {self.my_score} - {self.other_score}")


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.run(
        scene=lambda: EventsRpsScene(net, role),
        size=(800, 520),
        title="Events RPS Demo",
        fps=60,
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    s.networking.run()
