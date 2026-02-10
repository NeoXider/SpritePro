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


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 520), "Events RPS Demo")
    _ = s.multiplayer.init_context(net, role)
    ctx = s.multiplayer_ctx

    title = s.TextSprite("Rock / Paper / Scissors", 30, (255, 255, 255), (400, 40))
    hint = s.TextSprite("1=Rock  2=Paper  3=Scissors", 20, (200, 200, 200), (400, 80))
    status = s.TextSprite("Make your choice...", 20, (220, 220, 220), (400, 120))

    my_info = s.TextSprite("You (ID: ?)", 20, (120, 200, 255), (200, 220))
    other_info = s.TextSprite("Other (ID: ?)", 20, (255, 200, 120), (600, 220))
    my_choice_text = s.TextSprite("?", 36, (120, 200, 255), (200, 270))
    other_choice_text = s.TextSprite("?", 36, (255, 200, 120), (600, 270))
    score_text = s.TextSprite("Score: 0 - 0", 22, (255, 255, 255), (400, 360))

    _ = (title, hint)

    # Текущие выборы игрока и соперника.
    my_choice: str | None = None
    other_choice: str | None = None
    my_score = 0
    other_score = 0
    other_id: int | None = None
    # Пауза после результата, чтобы было видно победителя.
    last_result_at: float | None = None
    result_delay = 1.0

    def on_choice(choice: str, sender_id: int | None = None) -> None:
        nonlocal my_choice, other_choice, my_score, other_score, other_id, last_result_at
        # Не принимаем новые ходы, пока показываем результат.
        if last_result_at is not None:
            return

        if sender_id == ctx.client_id or sender_id is None:
            my_choice = choice
        else:
            other_choice = choice
            other_id = sender_id

        # Оба выбора готовы — считаем результат и запускаем паузу.
        if my_choice and other_choice:
            result = _resolve_winner(my_choice, other_choice)
            if result > 0:
                my_score += 1
                status.set_text("You win this round!")
            elif result < 0:
                other_score += 1
                status.set_text("You lose this round!")
            else:
                status.set_text("Draw.")
            last_result_at = s.time_since_start

    s.events.connect("rps_choice", on_choice)

    while True:
        s.update(fps=60, fill_color=(20, 20, 30))

        # Во время паузы после результата ввод блокируется.
        if last_result_at is None:
            for key, choice in CHOICES.items():
                if s.input.was_pressed(key):
                    s.events.send(
                        "rps_choice",
                        route="all",
                        net=ctx,
                        choice=choice,
                        sender_id=ctx.client_id,
                    )

        for msg in ctx.poll():
            if msg.get("event") == "rps_choice":
                s.events.send("rps_choice", **msg.get("data", {}))

        my_info.set_text(f"You (ID: {ctx.client_id})")
        other_id_label = "?" if other_id is None else str(other_id)
        other_info.set_text(f"Other (ID: {other_id_label})")

        # Сброс после задержки и ожидание нового раунда.
        if last_result_at is not None:
            if s.time_since_start - last_result_at >= result_delay:
                last_result_at = None
                my_choice = None
                other_choice = None
                status.set_text("Make your choice...")

        my_choice_text.set_text(my_choice or "?")
        other_choice_text.set_text(other_choice or "?")
        score_text.set_text(f"Score: {my_score} - {other_score}")


if __name__ == "__main__":
    s.networking.run()
