"""Решение 12: полный снапшот мира + авторитет хоста.

Все TODO из practice_full_snapshot.py выполнены, включая задание со звёздочкой
(защита recently_taken от «воскрешения» монеты старым снапшотом).
"""

import random
import time

import pygame
import spritePro as s

COIN_COUNT = 10
SNAPSHOT_INTERVAL = 0.5   # полный снапшот мира, 2 раза/с
POS_INTERVAL = 1.0 / 30.0  # своя позиция, 30 раз/с
RECENT_TTL = 1.0           # защита от «воскрешения» монеты старым снапшотом

PALETTE = [(220, 70, 70), (70, 120, 220), (70, 220, 120), (220, 180, 70)]


def _color_for(client_id: int) -> tuple[int, int, int]:
    return PALETTE[client_id % len(PALETTE)]


def multiplayer_main() -> None:
    s.get_screen((800, 600), "Lesson 12 - Solution")
    ctx = s.multiplayer_ctx
    is_authority = ctx.is_host  # в одиночной игре авторитетом был бы сам игрок

    me = s.Sprite("", (40, 40), (400, 300))
    others: dict[int, s.Sprite] = {}

    # Монеты: id -> спрайт. Владелец словаря — хост, у клиента это копия.
    coins: dict[int, s.Sprite] = {}
    next_coin_id = 0
    recently_taken: dict[int, float] = {}
    scores: dict[int, int] = {}

    hud = s.TextSprite("", 22, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    snapshot_timer = 0.0
    speed = 260.0

    def make_coin(coin_id: int, pos: tuple[int, int]) -> None:
        coin = s.Sprite("", (24, 24), pos)
        coin.set_circle_shape(radius=12, color=(240, 210, 80))
        coins[coin_id] = coin

    def spawn_coin() -> None:
        # Только авторитет создаёт новые монеты и выдаёт им id.
        nonlocal next_coin_id
        make_coin(next_coin_id, (random.randint(40, 760), random.randint(60, 560)))
        next_coin_id += 1

    def remove_coin(coin_id: int) -> bool:
        coin = coins.pop(coin_id, None)
        if coin is None:
            return False
        s.disable_sprite(coin)
        recently_taken[coin_id] = time.monotonic()
        return True

    def world_snapshot() -> dict:
        return {
            "coins": [{"id": cid, "pos": list(c.rect.center)} for cid, c in coins.items()],
            "scores": {str(k): v for k, v in scores.items()},
        }

    def apply_snapshot(data: dict) -> None:
        # Сверка с полным снапшотом: добавить новое, убрать исчезнувшее.
        nonlocal scores
        incoming = {int(item["id"]): item for item in data.get("coins", [])}
        for cid in list(coins):
            if cid not in incoming:
                remove_coin(cid)
        for cid, item in incoming.items():
            fresh = time.monotonic() - recently_taken.get(cid, -RECENT_TTL) < RECENT_TTL
            if cid not in coins and not fresh:
                make_coin(cid, tuple(item["pos"]))
        scores = {int(k): v for k, v in data.get("scores", {}).items()}

    def confirm_take(coin_id: int, taker: int) -> None:
        # Авторитет: засчитать, создать замену и разослать подтверждение.
        scores[taker] = scores.get(taker, 0) + 1
        spawn_coin()
        ctx.send("coin_taken", {"coin_id": coin_id, "taker": taker})

    if is_authority:
        for _ in range(COIN_COUNT):
            spawn_coin()

    while True:
        s.update(fill_color=(16, 16, 22))
        dt = s.dt
        me.set_color(_color_for(ctx.client_id))

        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)
        ctx.send_every("pos", {"pos": list(pos)}, POS_INTERVAL)

        # Подбор монеты: убираем сразу, растём по подтверждению.
        for cid, coin in list(coins.items()):
            if me.rect.colliderect(coin.rect):
                remove_coin(cid)
                if is_authority:
                    confirm_take(cid, ctx.client_id)
                else:
                    ctx.send("take_coin", {"coin_id": cid})
                break

        if is_authority:
            snapshot_timer += dt
            if snapshot_timer >= SNAPSHOT_INTERVAL:
                snapshot_timer = 0.0
                ctx.send("world", world_snapshot())

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            sender = data.get("sender_id")

            if event == "pos" and sender is not None:
                if sender not in others:
                    other = s.Sprite("", (40, 40), (0, 0))
                    other.set_color(_color_for(sender))
                    others[sender] = other
                others[sender].set_position(data.get("pos", [0, 0]))

            elif event == "take_coin" and is_authority:
                coin_id = int(data.get("coin_id", -1))
                # Подтверждаем, только если монета ещё существует.
                if remove_coin(coin_id):
                    confirm_take(coin_id, sender)

            elif event == "coin_taken":
                remove_coin(int(data.get("coin_id", -1)))
                taker = data.get("taker")
                if taker is not None:
                    # Рост по подтверждению; снапшот всё равно перезапишет
                    # scores авторитетным значением.
                    scores[taker] = scores.get(taker, 0) + 1

            elif event == "world" and not is_authority:
                apply_snapshot(data)

        my_score = scores.get(ctx.client_id, 0)
        table = "  ".join(f"P{k}:{v}" for k, v in sorted(scores.items()))
        hud.set_text(f"Me: {my_score}   [{table}]   coins: {len(coins)}")


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main)
