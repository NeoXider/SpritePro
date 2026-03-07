"""Demo: Visibility Culling — проверка is_visible_on_screen().

Спрайты движутся и отскакивают от границ области. Счётчики показывают,
сколько из них попадают в текущий вид камеры (Visible) и сколько вне (Offscreen).
Двигайте камеру WASD — числа меняются. Спрайты не исчезают, они всегда в области и периодически заходят в кадр.
"""

import pygame
import spritePro as s

WORLD_LEFT = -80
WORLD_RIGHT = 880
WORLD_TOP = -80
WORLD_BOTTOM = 680


def run_demo():
    s.init()
    s.get_screen((800, 600), "Visibility Culling Demo")
    s.enable_debug()
    s.debug_log_info("Visibility Culling: WASD — камера, спрайты отскакивают в области")

    sprites = []
    num_sprites = 60

    for i in range(num_sprites):
        x = 100 + (i % 10) * 70
        y = 100 + (i // 10) * 80
        sprite = s.Sprite("", pos=(x, y), size=(36, 36))
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        sprite.set_circle_shape(radius=18, color=colors[i % 4])
        angle_deg = i * 37
        v = pygame.math.Vector2(1, 0).rotate(angle_deg) * 90
        sprite.velocity = pygame.math.Vector2(v.x, v.y)
        sprites.append(sprite)

    visible_text = s.TextSprite("Visible: 0", color=(0, 255, 0), pos=(20, 30))
    visible_text.set_position((20, 30), anchor="topleft")
    visible_text.set_screen_space(True)
    offscreen_text = s.TextSprite("Offscreen: 0", color=(255, 150, 150), pos=(20, 52))
    offscreen_text.set_position((20, 52), anchor="topleft")
    offscreen_text.set_screen_space(True)
    hint = s.TextSprite(
        "WASD: move camera — visible count changes", color=(200, 200, 200), pos=(20, 78)
    )
    hint.set_position((20, 78), anchor="topleft")
    hint.set_screen_space(True)

    while True:
        s.update(fill_color=(20, 20, 35))

        if s.input.is_pressed(pygame.K_a):
            s.move_camera(-280 * s.dt, 0)
        if s.input.is_pressed(pygame.K_d):
            s.move_camera(280 * s.dt, 0)
        if s.input.is_pressed(pygame.K_w):
            s.move_camera(0, -280 * s.dt)
        if s.input.is_pressed(pygame.K_s):
            s.move_camera(0, 280 * s.dt)

        visible_count = 0
        for sprite in sprites:
            sprite.update()
            if sprite.rect.left < WORLD_LEFT:
                sprite.rect.left = WORLD_LEFT
                sprite.velocity.x = abs(sprite.velocity.x)
            if sprite.rect.right > WORLD_RIGHT:
                sprite.rect.right = WORLD_RIGHT
                sprite.velocity.x = -abs(sprite.velocity.x)
            if sprite.rect.top < WORLD_TOP:
                sprite.rect.top = WORLD_TOP
                sprite.velocity.y = abs(sprite.velocity.y)
            if sprite.rect.bottom > WORLD_BOTTOM:
                sprite.rect.bottom = WORLD_BOTTOM
                sprite.velocity.y = -abs(sprite.velocity.y)

            if sprite.is_visible_on_screen(margin=20):
                visible_count += 1

        offscreen_count = num_sprites - visible_count
        visible_text.set_text(f"Visible: {visible_count}")
        offscreen_text.set_text(f"Offscreen: {offscreen_count}")


if __name__ == "__main__":
    run_demo()
