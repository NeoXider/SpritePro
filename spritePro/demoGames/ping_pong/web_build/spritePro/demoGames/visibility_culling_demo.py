"""Demo: Visibility Culling — проверка is_visible_on_screen().

Спрайты движутся и отскакивают от границ области. Счётчики показывают,
сколько из них попадают в текущий вид камеры (Visible) и сколько вне (Offscreen).
Двигайте камеру WASD — числа меняются. Спрайты не исчезают, они всегда в области и периодически заходят в кадр.
"""
import pygame
import spritePro as sp

WORLD_LEFT = -80
WORLD_RIGHT = 880
WORLD_TOP = -80
WORLD_BOTTOM = 680


def run_demo():
    sp.init()
    sp.get_screen((800, 600), "Visibility Culling Demo")
    sp.enable_debug()
    sp.debug_log_info("Visibility Culling: WASD — камера, спрайты отскакивают в области")

    sprites = []
    num_sprites = 60

    for i in range(num_sprites):
        x = 100 + (i % 10) * 70
        y = 100 + (i // 10) * 80
        sprite = sp.Sprite("", pos=(x, y), size=(36, 36))
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
        sprite.set_circle_shape(radius=18, color=colors[i % 4])
        angle_deg = i * 37
        v = pygame.math.Vector2(1, 0).rotate(angle_deg) * 90
        sprite.velocity = pygame.math.Vector2(v.x, v.y)
        sprites.append(sprite)

    visible_text = sp.TextSprite("Visible: 0", color=(0, 255, 0), pos=(20, 30))
    visible_text.set_position((20, 30), anchor="topleft")
    visible_text.set_screen_space(True)
    offscreen_text = sp.TextSprite("Offscreen: 0", color=(255, 150, 150), pos=(20, 52))
    offscreen_text.set_position((20, 52), anchor="topleft")
    offscreen_text.set_screen_space(True)
    hint = sp.TextSprite("WASD: move camera — visible count changes", color=(200, 200, 200), pos=(20, 78))
    hint.set_position((20, 78), anchor="topleft")
    hint.set_screen_space(True)

    while True:
        sp.update(fill_color=(20, 20, 35))

        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        if sp.input.is_pressed(pygame.K_a):
            sp.move_camera(-280 * sp.dt, 0)
        if sp.input.is_pressed(pygame.K_d):
            sp.move_camera(280 * sp.dt, 0)
        if sp.input.is_pressed(pygame.K_w):
            sp.move_camera(0, -280 * sp.dt)
        if sp.input.is_pressed(pygame.K_s):
            sp.move_camera(0, 280 * sp.dt)

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
