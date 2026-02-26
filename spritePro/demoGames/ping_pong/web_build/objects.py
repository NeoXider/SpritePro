import random

import spritePro as s
from spritePro.physics import add_physics, add_static_physics, PhysicsConfig
from config import BALL_SPEED, PADDLE_SPEED


class Paddle(s.Sprite):
    def __init__(self, pos, color, up_key, down_key, scene=None):
        super().__init__("", (18, 110), pos, speed=PADDLE_SPEED, scene=scene)
        self.set_color(color)
        self.set_image(s.utils.round_corners(self.image, 18))
        self.up_key = up_key
        self.down_key = down_key
        self._body = add_static_physics(self)
        s.physics.add(self._body)

    def update(self, screen=None):
        axis = s.input.get_axis(self.up_key, self.down_key)
        self.velocity.y = axis * self.speed * s.dt
        super().update(screen)
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > s.WH.y:
            self.rect.bottom = int(s.WH.y)
        self.position = self.rect.center


class Ball(s.Sprite):
    def __init__(self, pos, scene=None):
        super().__init__("", (26, 26), pos, speed=BALL_SPEED, scene=scene)
        self.set_color((250, 240, 200))
        self.set_image(s.utils.round_corners(self.image, 100))
        self.direction = s.Vector2(1, 0)
        self.bounced = False
        self.paddles = []
        config = PhysicsConfig(mass=1.0, gravity=0.0, bounce=1.0, friction=1.0)
        self._body = add_physics(self, config)
        s.physics.add(self._body)
        self._trail_config = s.template_trail()
        self._trail_emitter = s.ParticleEmitter(self._trail_config)
        self._trail_emitter.set_parent(self)
        self._trail_timer = s.Timer(0.05, callback=self._emit_trail, repeat=True)
        self._trail_timer.pause()

    def set_trail_config(self, config: s.ParticleConfig) -> None:
        self._trail_config = config
        self._trail_emitter.set_config(config)

    def start_trail(self) -> None:
        self._trail_timer.start()

    def stop_trail(self) -> None:
        self._trail_timer.pause()

    def reset(self, serve_dir: int = 1):
        self.position = (int(s.WH_C.x), int(s.WH_C.y))
        self.rect.center = self.position
        self.direction = self._random_direction(serve_dir)
        vx = self.direction.x * BALL_SPEED
        vy = self.direction.y * BALL_SPEED
        self._body.set_velocity(vx, vy)

    def _random_direction(self, serve_dir: int) -> s.Vector2:
        y = random.uniform(-0.7, 0.7)
        if -0.25 < y < 0.25:
            y = 0.25 if random.random() >= 0.5 else -0.25
        direction = s.Vector2(serve_dir, y)
        return direction.normalize()

    def update(self, screen=None):
        self.bounced = False
        super().update(screen)

    def _emit_trail(self) -> None:
        particles = self._trail_emitter.emit()
        if self.scene is not None:
            for particle in particles:
                particle.scene = self.scene
