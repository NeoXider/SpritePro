"""Решение 6: счет за зону и синхронизация."""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    # Окно и игроки.
    s.get_screen((800, 600), "Lesson 6 - Solution")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role)

    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    # Целевая зона для очков.
    target = s.Sprite("", (60, 60), (400, 300))
    target.set_color((80, 200, 120))

    # Счет и UI.
    scores = {"host": 0, "client": 0}
    score_text = s.TextSprite("", 26, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)

    # Сетевые параметры.
    remote_pos = [other.get_world_position().x, other.get_world_position().y]
    score_cooldown = 0.0
    speed = 240.0

    while True:
        # Игровой тик.
        s.update(fill_color=(16, 16, 22))
        dt = s.dt

        # Движение локального игрока.
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # Отправка позиции.
        ctx.send_every("pos", {"pos": list(pos)}, 0.05)

        # Начисление очков по зоне.
        score_cooldown = max(0.0, score_cooldown - dt)
        dx_t = pos.x - 400
        dy_t = pos.y - 300
        if score_cooldown <= 0.0 and (dx_t * dx_t + dy_t * dy_t) <= 30 * 30:
            score_cooldown = 0.5
            player_key = "host" if ctx.is_host else "client"
            ctx.send("score", {"id": player_key})

        # Обработка сетевых событий.
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "pos":
                remote_pos[:] = data.get("pos", remote_pos)
            elif event == "score" and ctx.is_host:
                player_id = data.get("id")
                if player_id in scores:
                    scores[player_id] += 1
                    ctx.send("score_update", {"scores": scores})
            elif event == "score_update":
                scores = dict(data.get("scores", scores))

        # Обновляем отображение.
        other.set_position(remote_pos)
        score_text.set_text(f"Score  host={scores['host']}  client={scores['client']}")


if __name__ == "__main__":
    # Запуск решения.
    s.networking.run()
