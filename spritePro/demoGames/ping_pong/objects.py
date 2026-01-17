import random
import time

import spritePro as s
from config import BALL_SPEED, PADDLE_SPEED


class Paddle(s.Sprite):
    def __init__(self, pos, color, up_key, down_key, scene=None):
        super().__init__("", (18, 110), pos, speed=PADDLE_SPEED, scene=scene)
        self.set_color(color)
        self.set_image(s.utils.round_corners(self.image, 18))
        self.up_key = up_key
        self.down_key = down_key

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
        self.last_hit_at = 0.0
        self.paddles = []
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
        self.direction = self._random_direction(serve_dir)

    def _random_direction(self, serve_dir: int) -> s.Vector2:
        y = random.uniform(-0.7, 0.7)
        direction = s.Vector2(serve_dir, y)
        if direction.length_squared() == 0:
            direction = s.Vector2(serve_dir, 0.2)
        return direction.normalize()

    def update(self, screen=None):
        self.bounced = False
        self.velocity = self.direction * self.speed * s.dt
        super().update(screen)

        if self.rect.top <= 0:
            self.rect.top = 0
            self.direction.y = abs(self.direction.y)
            self.bounced = True
        elif self.rect.bottom >= s.WH.y:
            self.rect.bottom = int(s.WH.y)
            self.direction.y = -abs(self.direction.y)
            self.bounced = True

        now = time.monotonic()
        if now - self.last_hit_at > 0.05:
            for paddle in self.paddles:
                if self.rect.colliderect(paddle.rect):
                    self.last_hit_at = now
                    offset = (self.rect.centery - paddle.rect.centery) / (
                        paddle.rect.height / 2
                    )
                    self.direction.x *= -1
                    self.direction.y = max(-0.9, min(0.9, offset))
                    if self.direction.length_squared() == 0:
                        self.direction = s.Vector2(1, 0)
                    self.direction = self.direction.normalize()
                    if self.direction.x > 0:
                        self.rect.left = paddle.rect.right + 2
                    else:
                        self.rect.right = paddle.rect.left - 2
                    self.position = self.rect.center
                    break

    def _emit_trail(self) -> None:
        particles = self._trail_emitter.emit()
        if self.scene is not None:
            for particle in particles:
                particle.scene = self.scene
