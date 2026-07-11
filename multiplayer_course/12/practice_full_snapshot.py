"""Практика 12: полный снапшот мира + авторитет хоста.

Заготовка: игроки уже двигаются и видят друг друга. Ваша задача — добавить
монеты по правилу «один владелец у каждого объекта»:

TODO(1): монеты создаёт и рассылает ТОЛЬКО авторитет (хост):
         снапшот world = {"coins": [...], "scores": {...}} каждые 0.5 с.
TODO(2): подбор монеты: локально убрать сразу; хост засчитывает сам,
         клиент шлёт take_coin и ждёт подтверждение coin_taken.
TODO(3): apply_snapshot на клиенте: добавить недостающие монеты,
         убрать исчезнувшие, обновить scores.
TODO(4)*: защита от гонки — не «воскрешать» из снапшота монету,
          взятую менее 1 секунды назад (см. recently_taken).

Проверка: запустите --quick, соберите монеты в обоих окнах — счёт и монеты
должны совпадать. Затем подключите третье окно (--host 127.0.0.1) в середине
игры — оно должно получить актуальный мир без спец-логики.
"""

import random
import time

import pygame
import spritePro as s

COIN_COUNT = 10
SNAPSHOT_INTERVAL = 0.5
POS_INTERVAL = 1.0 / 30.0
RECENT_TTL = 1.0

PALETTE = [(220, 70, 70), (70, 120, 220), (70, 220, 120), (220, 180, 70)]


def _color_for(client_id: int) -> tuple[int, int, int]:
    return PALETTE[client_id % len(PALETTE)]


def multiplayer_main() -> None:
    s.get_screen((800, 600), "Lesson 12 - Practice")
    ctx = s.multiplayer_ctx
    is_authority = ctx.is_host

    me = s.Sprite("", (40, 40), (400, 300))
    others: dict[int, s.Sprite] = {}

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

    # TODO(1): напишите world_snapshot() -> dict с монетами и счётом.

    # TODO(3): напишите apply_snapshot(data) — сверку монет со снапшотом.
    #          TODO(4)*: внутри не добавляйте монеты из recently_taken (< RECENT_TTL).

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

        # TODO(2): подбор монеты (me.rect.colliderect(coin.rect)):
        #   - remove_coin(cid) локально сразу;
        #   - авторитет: scores[...] += 1, spawn_coin(), ctx.send("coin_taken", ...);
        #   - клиент: ctx.send("take_coin", {"coin_id": cid}) и ждать подтверждение.

        if is_authority:
            snapshot_timer += dt
            if snapshot_timer >= SNAPSHOT_INTERVAL:
                snapshot_timer = 0.0
                # TODO(1): ctx.send("world", world_snapshot())

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

            # TODO(2): elif event == "take_coin" and is_authority:
            #   подтверждать ТОЛЬКО если remove_coin(...) вернул True
            #   (иначе двое заберут одну монету).

            # TODO(2): elif event == "coin_taken": remove_coin(...)

            # TODO(3): elif event == "world" and not is_authority: apply_snapshot(data)

        my_score = scores.get(ctx.client_id, 0)
        table = "  ".join(f"P{k}:{v}" for k, v in sorted(scores.items()))
        hud.set_text(f"Me: {my_score}   [{table}]   coins: {len(coins)}")


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main)
