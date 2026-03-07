import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class ParticlesAutoEmitScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.title = s.TextSprite("Particles Auto Emit Demo", 28, (255, 255, 255), (s.WH_C.x, 30), scene=self)
        self.hints = s.TextSprite(
            "Слева: по времени  |  Синий квадрат: по расстоянию (только при движении)",
            18,
            (200, 200, 200),
            (s.WH_C.x, 565),
            scene=self,
        )

        self.mover = s.Sprite("", (40, 40), (650, 300), speed=320, scene=self)
        self.mover.set_color((120, 200, 255))

        self.interval_emitter = s.ParticleEmitter(
            s.template_trail(),
            auto_emit=True,
            emit_interval=(0.05, 0.15),
            auto_register=True,
        )
        self.interval_emitter.set_position((200, 300))

        self.step_emitter = s.ParticleEmitter(
            s.template_sparks(),
            auto_emit=True,
            emit_step=50,
            emit_interval=0,
            auto_register=True,
        )

    def update(self, dt: float) -> None:
        axis_x = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
        axis_y = s.input.get_axis(pygame.K_UP, pygame.K_DOWN)
        self.mover.velocity.x = axis_x * self.mover.speed * s.dt
        self.mover.velocity.y = axis_y * self.mover.speed * s.dt

        self.step_emitter.set_position(self.mover.rect.center)

        if s.input.was_pressed(pygame.K_SPACE):
            if self.interval_emitter.auto_emit:
                self.interval_emitter.stop_auto_emit()
                self.hints.text = "Слева: выкл  |  Синий квадрат: по расстоянию"
            else:
                self.interval_emitter.start_auto_emit()
                self.hints.text = "Слева: по времени  |  Синий квадрат: по расстоянию"


def main(platform: str = "pygame"):
    s.run(
        scene=ParticlesAutoEmitScene,
        size=(900, 600),
        title="Particles Auto Emit Demo",
        fill_color=(20, 20, 30),
        platform=platform,
    )


if __name__ == "__main__":
    main()
