"""Пример 2: синхронизация позиции между двумя клиентами.

Каждый клиент двигает своего игрока (WASD), отправляет позицию с троттлингом
и рисует второго игрока по приходящим pos-сообщениям.
"""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.get_screen((800, 600), "Lesson 2 - Sync Positions")
    # Контекст даёт ctx.send(), ctx.poll(), ctx.is_host и т.д.
    ctx = s.multiplayer.init_context(net, role, color)

    # Два спрайта: «я» слева, «другой» справа.
    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))
    # Цвета по роли: хост — красноватый, клиент — синеватый.
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    # Буфер для позиции другого игрока; обновляется из сети, применяется к other.
    remote_pos = list(other.get_world_position())
    speed = 240.0

    while True:
        s.update(fill_color=(20, 20, 25))
        dt = s.dt

        # Управление: оси A/D и W/S, движение с учётом dt.
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # Отправляем pos не чаще чем раз в 0.2 сек — меньше нагрузки на сеть.
        ctx.send_every("pos", {"x": pos.x, "y": pos.y}, 0.2)

        # Читаем входящие сообщения; при pos обновляем remote_pos и двигаем other.
        for m in ctx.poll():
            if m.get("event") == "pos":
                d = m.get("data", {})
                remote_pos[:] = [
                    float(d.get("x", remote_pos[0])),
                    float(d.get("y", remote_pos[1])),
                ]
        other.set_position(remote_pos)


if __name__ == "__main__":
    # Запуск мультиплеера.
    s.networking.run()
