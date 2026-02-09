"""Пример 6: очки за зону и синхронизация счета.

Игроки двигаются; при входе в центральную зону отправляется score; хост
ведёт счёт, рассылает score_update; кулдаун ограничивает спам очков.
"""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "Lesson 6 - Score Zone")
    ctx = s.multiplayer.init_context(net, role, color)

    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    # Зелёный квадрат в центре — зона, за вход в которую начисляются очки.
    target = s.Sprite("", (60, 60), (400, 300))
    target.set_color((80, 200, 120))

    scores = {"host": 0, "client": 0}
    score_text = s.TextSprite(
        "", 26, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT
    )

    remote_pos = [other.get_world_position().x, other.get_world_position().y]
    score_cooldown = 0.0
    speed = 240.0

    while True:
        s.update(fill_color=(16, 16, 22))
        dt = s.dt

        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        ctx.send_every("pos", {"x": pos.x, "y": pos.y}, 0.05)

        # Если игрок в радиусе 30 от центра (400,300) и кулдаун истёк — шлём score.
        score_cooldown = max(0.0, score_cooldown - dt)
        dx_t = pos.x - 400
        dy_t = pos.y - 300
        if score_cooldown <= 0.0 and (dx_t * dx_t + dy_t * dy_t) <= 30 * 30:
            score_cooldown = 0.5
            player_key = "host" if ctx.is_host else "client"
            ctx.send("score", {"id": player_key})

        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "pos":
                remote_pos[:] = [
                    float(data.get("x", remote_pos[0])),
                    float(data.get("y", remote_pos[1])),
                ]
            elif event == "score" and ctx.is_host:
                # Хост увеличивает счёт и рассылает актуальный score_update.
                player_id = data.get("id")
                if player_id in scores:
                    scores[player_id] += 1
                    ctx.send("score_update", {"scores": scores})
            elif event == "score_update":
                scores = dict(data.get("scores", scores))

        other.set_position(remote_pos)
        score_text.set_text(f"Score  host={scores['host']}  client={scores['client']}")


if __name__ == "__main__":
    # Запуск примера.
    s.networking.run()
