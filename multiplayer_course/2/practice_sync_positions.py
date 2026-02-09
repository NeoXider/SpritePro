"""Практика 2: синхронизация позиции с TODO.

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал.
"""

import pygame
import spritePro as s


def multiplayer_main(net: s.NetClient, role: str) -> None:
    # Окно и базовая сцена.
    s.get_screen((800, 600), "Lesson 2 - Practice")

    # Глобальный контекст мультиплеера.
    ctx = s.multiplayer.init_context(net, role)

    # Создаем спрайты игроков.
    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))

    # Настраиваем цвета.
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    other_color = (70, 120, 220) if ctx.is_host else (220, 70, 70)
    me.set_color(my_color)
    other.set_color(other_color)

    # Буфер позиции.
    remote_pos = [other.get_world_position().x, other.get_world_position().y]
    speed = 240.0

    while True:
        # Игровой тик.
        s.update(fill_color=(20, 20, 25))
        dt = s.dt

        # Движение локального игрока.
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # Отправка позиции с лимитом.
        # TODO: используйте ctx.send_every("pos", {"x": pos.x, "y": pos.y}, 0.05).
        pass

        # Прием сетевых сообщений.
        for msg in ctx.poll():
            if msg.get("event") == "pos":
                # TODO: прочитайте координаты и обновите remote_pos.
                pass

        # Применяем позицию удаленного игрока.
        other.set_position(remote_pos)


if __name__ == "__main__":
    # Запуск практики.
    s.networking.run()
