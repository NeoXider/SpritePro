"""Demo: Builder Pattern - Fluent API для создания спрайтов."""

import sys

import pygame
import spritePro as s


class BuilderDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.enable_debug()

        self.sprite = (
            s.sprite(r"C:\Git\SpritePro\spritePro\demoGames\Sprites\amogus.png")
            .size(100,100)
            .border_radius(20)
            .alpha(200)
            .position(0,0)
            .speed(2)
            .build()
        )

        self.hat = (
            s.sprite(r"")
            .size(100,10)
            .border_radius(20)
            .alpha(200)
            .position(0,-40)
            .parent(self.sprite)
            .build()
        )

        self.player = (
            s.sprite("examples/images/player.png")
            .position(100, 300)
            .scale(2.0)
            .color(255, 255, 255)
            .sorting_order(10)
            .build()
        )
        s.debug_log_info("Sprite created via Builder")

        self.enemy = (
            s.sprite("examples/images/enemy.png")
            .position(400, 300)
            .scale(1.5)
            .color(255, 100, 100)
            .crop(0, 0, 48, 48)
            .border_radius(12)
            .mask(True)
            .build()
        )

        self.coin = s.sprite("").position(600, 300).size(32, 32).color(255, 215, 0).build()
        self.coin.set_circle_shape(radius=16, color=(255, 215, 0))

        self.emitter = (
            s.particles()
            .amount(1)
            .lifetime(2.0)
            .speed(100, 300)
            .angle(0, 360)
            .colors([(255, 200, 50), (255, 100, 0), (255, 255, 100)])
            .fade_speed(200)
            .gravity(0, 100)
            .position(400, 400)
            .auto_emit(True)
            .image(r"C:\Git\SpritePro\spritePro\demoGames\Sprites\amogus.png")
            .build()
        )
        #self.emitter.config.image_scale_range = (0.03, 0.08)
        self.emitter.config.angular_velocity_range = (-150, 150)


        s.debug_log_info("All builders demo complete!")

    def update(self, dt: float) -> None:
        self.sprite.handle_keyboard_input()
        self.hat.color = s.utils.ColorEffects.rainbow(3, )
        if s.input.was_pressed(s.pygame.K_r):
            self.sprite.active = not self.sprite.active

        if s.input.was_pressed(pygame.K_SPACE):
            particles = self.emitter.emit()
            for p in particles:
                p.position = (400, 300)
            s.debug_log_info(f"Emitted {len(particles)} particles")


def run_demo(platform: str = "pygame") -> None:
    s.run(
        scene=BuilderDemoScene,
        size=(800, 600),
        title="Builder Demo - Fluent API",
        fill_color=(20, 20, 30),
        platform=platform,
    )


if __name__ == "__main__":
    run_demo("kivy" if "--kivy" in sys.argv else "pygame")
