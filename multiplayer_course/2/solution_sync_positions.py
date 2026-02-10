"""Решение 2: синхронизация позиции между клиентами."""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    # Создаем окно.
    s.get_screen((800, 600), "Lesson 2 - Solution")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role)

    # Локальный и удаленный игроки.
    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))

    # Цвета по роли.
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    # Буфер удаленной позиции.
    remote_pos = [other.get_world_position().x, other.get_world_position().y]
    speed = 240.0

    while True:
        # Тик обновления.
        s.update(fill_color=(20, 20, 25))
        dt = s.dt

        # Локальное движение.
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # Отправка позиции 20 раз/сек.
        ctx.send_every("pos", {"pos": list(pos)}, 0.05)

        # Прием позиции удаленного игрока.
        for msg in ctx.poll():
            if msg.get("event") == "pos":
                d = msg.get("data", {})
                remote_pos[:] = d.get("pos", [0, 0])

        # Применяем удаленную позицию.
        other.set_position(remote_pos)


if __name__ == "__main__":
    # Запуск решения.
    s.networking.run()
