"""Demo: Builder Pattern - Fluent API для создания спрайтов."""
import pygame
import spritePro as sp


def run_demo():
    sp.init()
    screen = sp.get_screen((800, 600), "Builder Demo - Fluent API")

    sp.enable_debug()

    player = (
        sp.sprite("examples/images/player.png")
        .position(100, 300)
        .scale(2.0)
        .color(255, 255, 255)
        .sorting_order(10)
        .build()
    )
    sp.debug_log_info("Sprite created via Builder")

    enemy = (
        sp.sprite("examples/images/enemy.png")
        .position(400, 300)
        .scale(1.5)
        .color(255, 100, 100)
        .crop(0, 0, 48, 48)
        .border_radius(12)
        .mask(True)
        .build()
    )

    coin = (
        sp.sprite("")
        .position(600, 300)
        .size(32, 32)
        .color(255, 215, 0)
        .build()
    )
    coin.set_circle_shape(radius=16, color=(255, 215, 0))

    emitter = (
        sp.particles()
        .amount(30)
        .lifetime(1.0)
        .speed(100, 300)
        .angle(0, 360)
        .colors([(255, 200, 50), (255, 100, 0), (255, 255, 100)])
        .fade_speed(200)
        .gravity(0, 100)
        .position(400, 400)
        .auto_emit(True)
        .build()
    )

    sp.debug_log_info("All builders demo complete!")

    while True:
        sp.update(fill_color=(20, 20, 30))

        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    particles = emitter.emit()
                    for p in particles:
                        p.position = (400, 300)
                    sp.debug_log_info(f"Emitted {len(particles)} particles")


if __name__ == "__main__":
    run_demo()
