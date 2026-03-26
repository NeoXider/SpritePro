# Particles (Частицы)

Легковесная система частиц. Каждая частица — полноценный спрайт.

## ParticleConfig

```python
from spritePro.particles import ParticleEmitter, ParticleConfig
from pygame.math import Vector2

cfg = ParticleConfig(
    amount=40,
    size_range=(4, 6),
    speed_range=(120.0, 260.0),
    angle_range=(0.0, 360.0),
    lifetime_range=(0.6, 1.2),
    fade_speed=260.0,
    gravity=Vector2(0, 240.0),
    colors=[(255, 100, 100), (100, 255, 100)],
)
```

| Параметр | Описание |
|----------|----------|
| `amount` | Количество частиц при emit |
| `size_range` | Диапазон размера (круги) |
| `speed_range` | Диапазон скорости |
| `angle_range` | Диапазон угла выброса (°) |
| `lifetime_range` | Время жизни (сек) |
| `fade_speed` | Скорость затухания |
| `gravity` | Гравитация |
| `colors` | Палитра цветов |
| `image` | Изображение частицы |
| `sorting_order` | Слой отрисовки |
| `screen_space` | Экранное пространство |

## ParticleEmitter

```python
emitter = ParticleEmitter(cfg)
emitter.emit((450, 300))

# Или с авто-эмиссией
emitter = s.ParticleEmitter(
    s.template_trail(),
    auto_emit=True,
    emit_interval=(0.05, 0.15),
)
```

### Методы

| Метод | Описание |
|-------|----------|
| `emit(pos)` | Выпустить частицы |
| `set_position(pos)` | Установить позицию |
| `start_auto_emit()` | Включить авто-эмиссию |
| `stop_auto_emit()` | Выключить |

### Параметры авто-эмиссии

```python
ParticleEmitter(
    auto_emit=True,
    emit_interval=(0.05, 0.15),  # Случайный интервал
    emit_step=20,                 # По дистанции
    auto_register=True,
)
```

## Изображения

```python
star_img = pygame.image.load("star.png").convert_alpha()
cfg = ParticleConfig(
    image=star_img,
    image_scale_range=(0.5, 1.4),
)
```

## Вращение

```python
cfg = ParticleConfig(
    align_rotation_to_velocity=True,
    angular_velocity_range=(-180.0, 180.0),
)
```

## Область появления

```python
cfg = ParticleConfig(spawn_rect=pygame.Rect(-50, -50, 100, 100))
cfg = ParticleConfig(spawn_circle_radius=50.0)
```

## Интерактивные частицы

```python
class FireParticle(s.Particle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage = 10
        self.has_hit = False
        
fire_template = FireParticle(image=surf, pos=(0, 0), ...)
fire_template.set_color((255, 100, 0))
fire_config = ParticleConfig(particle_template=fire_template, ...)
```

## Полный пример

```python
import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig
from pygame.math import Vector2

s.init()
s.get_screen((900, 600))

cfg = ParticleConfig(
    amount=40,
    lifetime_range=(0.6, 1.5),
    speed_range=(140.0, 280.0),
    gravity=Vector2(0, 240.0),
)

emitter = ParticleEmitter(cfg)
emitter.emit((450, 300))

while True:
    s.update(fps=60, update_display=True, fill_color=(18, 22, 28))
```

## Демо

```bash
python -m spritePro.demoGames.particle_demo
python -m spritePro.demoGames.fireworks_demo
```

## См. также

- [Sprite](sprite.md)
