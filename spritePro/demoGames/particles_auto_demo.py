import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def main():
    s.get_screen((900, 600), "Particles Auto Emit Demo")

    title = s.TextSprite(
        "Particles Auto Emit Demo", 28, (255, 255, 255), (s.WH_C.x, 30)
    )
    hints = s.TextSprite(
        "Слева: по времени  |  Синий квадрат: по расстоянию (только при движении)",
        18,
        (200, 200, 200),
        (s.WH_C.x, 565),
    )

    mover = s.Sprite("", (40, 40), (650, 300), speed=320)
    mover.set_color((120, 200, 255))

    interval_emitter = s.ParticleEmitter(
        s.template_trail(),
        auto_emit=True,
        emit_interval=(0.05, 0.15),
        auto_register=True,
    )
    interval_emitter.set_position((200, 300))

    step_emitter = s.ParticleEmitter(
        s.template_sparks(),
        auto_emit=True,
        emit_step=50,
        emit_interval=0,
        auto_register=True,
    )

    _ = (title, hints)

    while True:
        s.update(fill_color=(20, 20, 30))

        axis_x = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
        axis_y = s.input.get_axis(pygame.K_UP, pygame.K_DOWN)
        mover.velocity.x = axis_x * mover.speed * s.dt
        mover.velocity.y = axis_y * mover.speed * s.dt

        step_emitter.set_position(mover.rect.center)

        if s.input.was_pressed(pygame.K_SPACE):
            if interval_emitter.auto_emit:
                interval_emitter.stop_auto_emit()
                hints.text = "Слева: выкл  |  Синий квадрат: по расстоянию"
            else:
                interval_emitter.start_auto_emit()
                hints.text = "Слева: по времени  |  Синий квадрат: по расстоянию"


if __name__ == "__main__":
    main()
