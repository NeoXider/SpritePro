"""Demo: Object Pool - пул объектов для оптимизации."""
import pygame
import spritePro as sp
from spritePro.utils.pool import ObjectPool
from pygame.math import Vector2
import random


def run_demo():
    sp.get_screen((800, 600), "Object Pool Demo")
    sp.enable_debug()

    pool_size_text = sp.TextSprite("Pool size: 0", color=(255, 255, 0), pos=(20, 50))
    pool_size_text.set_position((20, 50), anchor="topleft")
    pool_size_text.set_screen_space(True)

    active_text = sp.TextSprite("Active: 0", color=(0, 255, 255), pos=(20, 75))
    active_text.set_position((20, 75), anchor="topleft")
    active_text.set_screen_space(True)

    info_text = sp.TextSprite("SPACE: emit | UP/DOWN: adjust amount", color=(200, 200, 200), pos=(20, 100))
    info_text.set_position((20, 100), anchor="topleft")
    info_text.set_screen_space(True)

    pool = ObjectPool(
        factory=lambda: sp.Sprite("", size=(20, 20)),
        max_size=200,
    )

    current_amount = 30

    class PooledEmitter:
        def __init__(self):
            self.pool = pool
            self.released_this_frame = []

        def emit_burst(self, count):
            particles = []
            for _ in range(count):
                sprite = self.pool.acquire()
                if sprite not in sp.get_game().all_sprites:
                    sp.register_sprite(sprite)
                sprite.set_circle_shape(radius=7, color=(255, 200, 50))
                sprite.rect.center = (400, 300)
                sprite.position = (400, 300)
                angle = pygame.time.get_ticks() % 360 * random.randint(0, 360)
                v = pygame.math.Vector2(1, 0).rotate(angle) * 4
                sprite.velocity = Vector2(v.x, v.y)
                sprite.active = True
                particles.append(sprite)

            for p in particles:
                p.update = self._make_update(p)
            return particles

        def _make_update(self, sprite):
            original_update = sprite.update

            def updated(screen=None):
                result = original_update(screen)
                if hasattr(sprite, "rect"):
                    if sprite.rect.y > 650 or sprite.rect.x < -50 or sprite.rect.x > 850:
                        sp.unregister_sprite(sprite)
                        self.pool.release(sprite)
                        self.released_this_frame.append(sprite)
                return result

            return updated

    emitter = PooledEmitter()
    active_particles = []

    sp.debug_log_info("Object Pool Demo started!")

    while True:
        emitter.released_this_frame.clear()
        sp.update(fill_color=(20, 20, 35))

        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    new_particles = emitter.emit_burst(current_amount)
                    active_particles.extend(new_particles)
                    sp.debug_log_info(f"Emitted {len(new_particles)} particles")
                if event.key == pygame.K_UP:
                    current_amount = min(100, current_amount + 5)
                if event.key == pygame.K_DOWN:
                    current_amount = max(5, current_amount - 5)

        pool_size_text.set_text(f"Pool size: {pool.size} / {pool.max_size}")
        active_text.set_text(f"Active particles: {len(active_particles)}")

        for p in list(active_particles):
            p.update()

        active_particles = [p for p in active_particles if p not in emitter.released_this_frame]


if __name__ == "__main__":
    run_demo()
