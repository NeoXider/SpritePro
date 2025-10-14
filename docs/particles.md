# Particles

SpritePro includes a lightweight particle system designed for quick bursts and simple effects, with flexible configuration for visuals, motion, sorting order, and lifetimes.

## Quick Start

```python
import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig
from pygame.math import Vector2

s.init()
s.get_screen((900, 600), "Particles Quick Start")

cfg = ParticleConfig(
    amount=40,
    lifetime_range_s=(0.6, 1.5),       # lifetime in seconds
    speed_range=(140.0, 280.0),
    angle_range=(0.0, 360.0),
    fade_speed=260.0,                  # alpha per second
    gravity=Vector2(0, 240.0),
)

emitter = ParticleEmitter(cfg)
emitter.emit((450, 300))

while True:
    s.update(fps=60, update_display=True, fill_color=(18, 22, 28))
```

## Using Images

You can use a ready `pygame.Surface` or generate one per particle via a factory.

```python
star_img = pygame.image.load("assets/star.png").convert_alpha()

cfg = ParticleConfig(
    amount=30,
    image=star_img,                    # use this surface for each particle
    image_scale_range=(0.5, 1.4),      # random uniform scale per particle
)

# Or dynamic images per index
def image_factory(i: int) -> pygame.Surface:
    size = 8 + (i % 6)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 80), (size//2, size//2), size//2)
    return surf

cfg2 = ParticleConfig(amount=50, image_factory=image_factory)
```

## Rotation

- `align_rotation_to_velocity=True` rotates the image towards the travel direction.
- `image_rotation_range=(min_deg, max_deg)` sets a random initial rotation.
- `angular_velocity_range=(min_deg_s, max_deg_s)` adds continuous spin.

```python
cfg = ParticleConfig(
    amount=25,
    align_rotation_to_velocity=True,
    angular_velocity_range=(-180.0, 180.0),
)
```

## Sorting Order

Particles integrate with the global layered draw order:

- Lower `sorting_order` draws behind; higher draws in front.

```python
cfg_back = ParticleConfig(sorting_order=-100)
cfg_ui = ParticleConfig(sorting_order=1200)
```

## Lifetimes and Fading

You can specify lifetime in seconds or milliseconds. Seconds take priority:

- `lifetime_s`: fixed lifetime (seconds)
- `lifetime_range_s`: range (seconds)
- `lifetime_ms`: fixed lifetime (milliseconds)
- `lifetime_range`: range (milliseconds)

Alpha fades out each frame by `fade_speed * dt`.

## Motion

- `speed_range` with `angle_range` defines initial velocity.
- `gravity` is added to velocity each frame.
- Positions update in world space unless `screen_space=True`.

## Custom Particle Class

Provide a custom subclass or a full factory:

```python
from spritePro.particles import Particle

class MyParticle(Particle):
    def update(self, screen=None):
        super().update(screen)
        # glow, trail, etc.

cfg = ParticleConfig(particle_class=MyParticle)

def build(pos, vel, life, cfg, idx) -> Particle:
    return MyParticle(
        image=star_img.copy(), pos=pos, velocity=vel, lifetime_ms=life,
        fade_speed=cfg.fade_speed, gravity=cfg.gravity,
        screen_space=cfg.screen_space, sorting_order=cfg.sorting_order,
    )

cfg2 = ParticleConfig(factory=build)
```

## API Reference

### ParticleConfig

- `amount: int` — number of particles to spawn per emit
- `size_range: tuple[int, int]` — size for default circle particles
- `speed_range: tuple[float, float]` — initial speed magnitude
- `angle_range: tuple[float, float]` — emission angle (deg)
- `lifetime_ms: int | None` — fixed lifetime in ms
- `lifetime_range: tuple[int, int]` — lifetime range in ms
- `lifetime_s: float | None` — fixed lifetime in seconds (priority)
- `lifetime_range_s: tuple[float, float] | None` — range in seconds (priority)
- `fade_speed: float` — alpha fade speed per second
- `gravity: Vector2` — acceleration each frame
- `screen_space: bool` — ignore camera if True
- `sorting_order: int | None` — layer for draw order
- `colors: Sequence[Color]` — palette for default circles
- `image: pygame.Surface | None` — use this surface for each particle
- `image_factory: Callable[[int], Surface] | None` — build per-particle image
- `image_scale_range: tuple[float, float] | None` — random scale per particle
- `align_rotation_to_velocity: bool` — face along velocity
- `image_rotation_range: tuple[float, float] | None` — random initial rotation
- `angular_velocity_range: tuple[float, float] | None` — spin (deg/sec)
- `particle_class: type[Particle] | None` — custom particle subtype
- `custom_factory: Callable[[Particle, int], None] | None` — post-create hook
- `factory: Callable[[Vector2, Vector2, int, ParticleConfig, int], Particle] | None` — full override

### Particle

Inherits from `spritePro.Sprite`.

Attributes:
- `velocity: Vector2`
- `spawn_time: int` (ms)
- `lifetime: int` (ms)
- `fade_speed: float`
- `gravity: Vector2`
- `screen_space: bool`
- `angular_velocity: float` (deg/sec)

Behavior:
- Position integrates velocity and gravity
- Alpha fades by `fade_speed * dt`
- Auto-kills when lifetime expires or fully transparent
- Applies rotation if `angular_velocity != 0`

## Demos

- `spritePro/demoGames/particle_demo.py` — basic particles
- `spritePro/demoGames/particles_images_demo.py` — particles using images, scaling, rotation


