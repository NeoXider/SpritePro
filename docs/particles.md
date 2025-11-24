# Система частиц

SpritePro включает легковесную систему частиц, разработанную для быстрых вспышек и простых эффектов, с гибкой конфигурацией для визуализации, движения, порядка отрисовки и времени жизни.

## Обзор

Система частиц SpritePro предоставляет гибкую и производительную систему для создания визуальных эффектов. Каждая частица является полноценным спрайтом, что обеспечивает полную интеграцию с камерой, иерархией спрайтов и системой отрисовки.

## Основные возможности

- **Гибкая конфигурация**: Настройка всех параметров через ParticleConfig
- **Изображения и цвета**: Поддержка как изображений, так и цветных кругов
- **Движение и физика**: Скорость, углы, гравитация и вращение
- **Время жизни**: Настраиваемое время жизни с затуханием
- **Порядок отрисовки**: Интеграция с системой sorting_order
- **Экранное пространство**: Поддержка UI-частиц

## ParticleConfig

### Параметры конструктора

Основные параметры:
- `amount` (int): Количество частиц для создания при каждом emit. По умолчанию: 30
- `size_range` (tuple[int, int]): Размер для частиц по умолчанию (круги). По умолчанию: (4, 6)
- `speed_range` (tuple[float, float]): Диапазон начальной скорости. По умолчанию: (120.0, 260.0)
- `angle_range` (tuple[float, float]): Диапазон угла выброса в градусах (0 = вправо, 90 = вниз). По умолчанию: (0.0, 360.0)

Время жизни:
- `lifetime` (float | None): Фиксированное время жизни в секундах. По умолчанию: None
- `lifetime_range` (tuple[float, float] | None): Диапазон времени жизни в секундах. По умолчанию: (0.6, 1.2)
- `fade_speed` (float): Скорость затухания альфа-канала в секунду. По умолчанию: 220.0

Движение:
- `gravity` (Vector2): Вектор ускорения, применяемый каждый кадр. По умолчанию: Vector2(0, 0)
- `screen_space` (bool): Игнорировать камеру, если True. По умолчанию: False

Визуализация:
- `colors` (Sequence[Color]): Палитра цветов для частиц по умолчанию (круги). По умолчанию: [(255, 255, 255)]
- `image` (pygame.Surface | Path | None): Использовать эту поверхность для каждой частицы. По умолчанию: None
- `image_factory` (Callable[[int], Surface] | None): Фабрика для создания изображения для каждой частицы. По умолчанию: None
- `image_scale_range` (tuple[float, float] | None): Диапазон случайного равномерного масштаба для изображения. По умолчанию: None

Вращение:
- `align_rotation_to_velocity` (bool): Поворачивать изображение в направлении скорости. По умолчанию: False
- `image_rotation_range` (tuple[float, float] | None): Диапазон случайного начального поворота в градусах. По умолчанию: None
- `angular_velocity_range` (tuple[float, float] | None): Диапазон непрерывного вращения (град/сек). По умолчанию: None

Масштабирование:
- `scale_velocity_range` (tuple[float, float] | None): Диапазон скорости изменения масштаба (коэффициент в секунду). По умолчанию: None

Порядок отрисовки:
- `sorting_order` (int | None): Слой для порядка отрисовки (больше = спереди). По умолчанию: None

Область появления:
- `spawn_rect` (pygame.Rect | None): Прямоугольная область появления относительно позиции emit. По умолчанию: None
- `spawn_circle_radius` (float | None): Радиус круглой области появления относительно позиции emit. По умолчанию: None

Расширенные параметры:
- `particle_class` (type[Particle] | None): Пользовательский подкласс Particle. По умолчанию: None
- `particle_template` (Particle | None): Готовый экземпляр Particle как шаблон. Копируются свойства шаблона (масштаб, угол, цвет, дополнительные атрибуты), но позиция, скорость и время жизни берутся из конфига. Полезно для создания интерактивных частиц (например, огнемет с уроном). По умолчанию: None
- `custom_factory` (Callable[[Particle, int], None] | None): Хук для изменения частицы после создания. По умолчанию: None
- `factory` (Callable[[Vector2, Vector2, int, ParticleConfig, int], Particle] | None): Полная переопределение фабрики создания частиц. По умолчанию: None

## ParticleEmitter

### Методы

- `emit(position: Optional[Tuple[float, float] | Vector2] = None, overrides: Optional[ParticleConfig] = None) -> Sequence[Particle]`: Выпустить частицы. Если `position` не указан, используется позиция, установленная через `set_position()`
- `set_position(position: Tuple[float, float] | Vector2, anchor: str | Anchor = Anchor.CENTER)`: Установить позицию эмиттера для последующих вызовов `emit()` без аргументов
- `get_position() -> Optional[Tuple[float, float] | Vector2]`: Получить текущую позицию эмиттера
- `update_config(**kwargs)`: Обновить конфигурацию эмиттера с заданными значениями

## Particle

Наследуется от `spritePro.Sprite`.

### Атрибуты

- `velocity` (Vector2): Текущая скорость в пикселях в секунду
- `spawn_time` (int): Время создания в миллисекундах (pygame ticks)
- `lifetime` (int): Время жизни в миллисекундах; частица умирает после этого
- `fade_speed` (float): Скорость затухания альфа-канала в секунду
- `gravity` (Vector2): Вектор ускорения, применяемый каждый кадр
- `screen_space` (bool): Игнорировать камеру, если True
- `angular_velocity` (float): Скорость вращения в градусах в секунду
- `scale_velocity` (float): Скорость изменения масштаба (коэффициент в секунду)

### Поведение

- Позиция интегрирует скорость и гравитацию
- Альфа-канал затухает на `fade_speed * dt`
- Автоматически удаляется при истечении времени жизни или полной прозрачности
- Применяет вращение, если `angular_velocity != 0`
- Применяет масштабирование, если `scale_velocity != 0`

## Использование изображений

Вы можете использовать готовую `pygame.Surface` или генерировать её для каждой частицы через фабрику.

```python
star_img = pygame.image.load("assets/star.png").convert_alpha()

cfg = ParticleConfig(
    amount=30,
    image=star_img,                    # использовать эту поверхность для каждой частицы
    image_scale_range=(0.5, 1.4),      # случайный равномерный масштаб для каждой частицы
)

# Или динамические изображения для каждого индекса
def image_factory(i: int) -> pygame.Surface:
    size = 8 + (i % 6)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 80), (size//2, size//2), size//2)
    return surf

cfg2 = ParticleConfig(amount=50, image_factory=image_factory)
```

## Вращение

- `align_rotation_to_velocity=True` поворачивает изображение в направлении движения.
- `image_rotation_range=(min_deg, max_deg)` устанавливает случайный начальный поворот.
- `angular_velocity_range=(min_deg_s, max_deg_s)` добавляет непрерывное вращение.

```python
cfg = ParticleConfig(
    amount=25,
    image=star_img,
    align_rotation_to_velocity=True,
    angular_velocity_range=(-180.0, 180.0),
)
```

## Порядок отрисовки

Частицы интегрируются с глобальным порядком отрисовки по слоям:

- Меньший `sorting_order` рисуется сзади; больший спереди.

```python
cfg_back = ParticleConfig(sorting_order=-100)  # Сзади
cfg_ui = ParticleConfig(sorting_order=1200)    # Спереди (UI)
```

## Время жизни и затухание

Вы можете указать время жизни в секундах или миллисекундах. Секунды имеют приоритет:

- `lifetime`: фиксированное время жизни (секунды)
- `lifetime_range`: диапазон времени жизни (секунды)
- `fade_speed`: скорость затухания альфа-канала в секунду

Альфа-канал затухает каждый кадр на `fade_speed * dt`.

## Движение

- `speed_range` с `angle_range` определяет начальную скорость.
- `gravity` добавляется к скорости каждый кадр.
- Позиции обновляются в мировом пространстве, если только `screen_space=True`.

```python
cfg = ParticleConfig(
    amount=50,
    speed_range=(100.0, 200.0),      # Диапазон скорости
    angle_range=(0.0, 360.0),        # Диапазон угла выброса
    gravity=Vector2(0, 300.0),       # Гравитация вниз
    screen_space=False                # В мировом пространстве
)
```

## Область появления

Вы можете указать область появления частиц:

```python
# Прямоугольная область
cfg = ParticleConfig(
    amount=30,
    spawn_rect=pygame.Rect(-50, -50, 100, 100)  # Относительно позиции emit
)

# Круглая область
cfg = ParticleConfig(
    amount=30,
    spawn_circle_radius=50.0  # Радиус круга относительно позиции emit
)
```

## Масштабирование

Частицы могут масштабироваться со временем:

```python
cfg = ParticleConfig(
    amount=30,
    image=star_img,
    scale_velocity_range=(-0.5, -1.0)  # Уменьшение масштаба в секунду
)
```

## Пользовательский класс частиц

Предоставьте пользовательский подкласс или полную фабрику:

```python
from spritePro.particles import Particle

class MyParticle(Particle):
    def update(self, screen=None):
        super().update(screen)
        # Свечение, след и т.д.

cfg = ParticleConfig(particle_class=MyParticle)

# Или полная фабрика
def build(pos, vel, life, cfg, idx) -> Particle:
    return MyParticle(
        image=star_img.copy(),
        pos=pos,
        velocity=vel,
        lifetime_ms=life,
        fade_speed=cfg.fade_speed,
        gravity=cfg.gravity,
        screen_space=cfg.screen_space,
        sorting_order=cfg.sorting_order,
    )

cfg2 = ParticleConfig(factory=build)
```


## Быстрый старт

```python
import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig
from pygame.math import Vector2

s.init()
s.get_screen((900, 600), "Система частиц")

cfg = ParticleConfig(
    amount=40,
    lifetime_range=(0.6, 1.5),       # время жизни в секундах
    speed_range=(140.0, 280.0),
    angle_range=(0.0, 360.0),
    fade_speed=260.0,                  # альфа в секунду
    gravity=Vector2(0, 240.0),
)

emitter = ParticleEmitter(cfg)
emitter.emit((450, 300))

while True:
    s.update(fps=60, update_display=True, fill_color=(18, 22, 28))
```

## Примеры использования

### Базовые частицы

```python
cfg = ParticleConfig(
    amount=50,
    colors=[(255, 100, 100), (100, 255, 100), (100, 100, 255)],
    speed_range=(100.0, 200.0),
    angle_range=(0.0, 360.0),
    lifetime_range=(1.0, 2.0),
    fade_speed=200.0
)

emitter = ParticleEmitter(cfg)
emitter.emit((400, 300))
```

### Частицы с гравитацией

```python
cfg = ParticleConfig(
    amount=30,
    speed_range=(50.0, 150.0),
    angle_range=(270.0, 270.0),  # Вниз
    gravity=Vector2(0, 400.0),   # Гравитация вниз
    lifetime_range=(2.0, 3.0)
)

emitter = ParticleEmitter(cfg)
emitter.emit((400, 100))
```

### Частицы с изображениями

```python
star_img = pygame.image.load("star.png").convert_alpha()

cfg = ParticleConfig(
    amount=40,
    image=star_img,
    image_scale_range=(0.3, 1.0),
    speed_range=(100.0, 200.0),
    angular_velocity_range=(-90.0, 90.0)  # Вращение
)

emitter = ParticleEmitter(cfg)
emitter.emit((400, 300))
```

### Частицы в экранном пространстве (UI)

```python
cfg = ParticleConfig(
    amount=20,
    screen_space=True,  # Игнорировать камеру
    sorting_order=1500,  # Рисовать поверх всего
    speed_range=(50.0, 100.0)
)

emitter = ParticleEmitter(cfg)
emitter.set_position((400, 300))
emitter.emit()
```

### Интерактивные частицы (огнемет, урон и т.д.)

Используйте `particle_template` для создания частиц с дополнительной логикой (урон, коллизии и т.д.):

```python
from spritePro.particles import Particle, ParticleConfig, ParticleEmitter

# Создаем пользовательский класс частицы с уроном
class FireParticle(Particle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damage = 10  # Урон от частицы
        self.has_hit = False  # Флаг, чтобы не наносить урон дважды
        
    def check_collision(self, target):
        """Проверка коллизии с целью и нанесение урона."""
        if not self.has_hit and self.rect.colliderect(target.rect):
            target.take_damage(self.damage)
            self.has_hit = True

# Создаем шаблон частицы
fire_template = FireParticle(
    image=pygame.Surface((20, 20), pygame.SRCALPHA),
    pos=(0, 0),  # Позиция будет установлена при создании
    velocity=Vector2(0, 0),  # Скорость будет установлена при создании
    lifetime_ms=1000,
    fade_speed=200.0,
    gravity=Vector2(0, 0),
    screen_space=False,
)
fire_template.set_color((255, 100, 0))  # Оранжевый цвет огня
pygame.draw.circle(fire_template.image, (255, 200, 0), (10, 10), 10)

# Создаем конфигурацию с шаблоном
fire_config = ParticleConfig(
    amount=20,
    particle_template=fire_template,  # Используем шаблон
    speed_range=(200.0, 300.0),
    angle_range=(-30.0, 30.0),  # Огнемет в направлении
    lifetime_range=(0.5, 1.0),
    fade_speed=300.0,
)

# Создаем эмиттер
flamethrower = ParticleEmitter(fire_config)

# В игровом цикле
while True:
    s.update()
    
    # Выпускаем огонь
    fire_particles = flamethrower.emit(player.rect.center)
    
    # Проверяем коллизии с врагами
    for particle in fire_particles:
        for enemy in enemies:
            if isinstance(particle, FireParticle):
                particle.check_collision(enemy)
```

**Преимущества использования `particle_template`:**
- Копируются все свойства шаблона (цвет, масштаб, дополнительные атрибуты)
- Можно создавать интерактивные частицы с логикой (урон, коллизии, эффекты)
- Позиция, скорость и время жизни устанавливаются из конфига для каждой частицы
- Удобно для создания эффектов оружия (огнемет, пули, магия)

### Примеры использования эмиттера

```python
# Создать эмиттер
emitter = ParticleEmitter(cfg)

# Выпустить частицы в конкретной позиции
particles = emitter.emit((400, 300))

# Установить позицию эмиттера
emitter.set_position((400, 300), anchor=s.Anchor.CENTER)

# Выпустить частицы в установленной позиции
particles = emitter.emit()

# Обновить конфигурацию
emitter.update_config(amount=50, speed_range=(200.0, 300.0))
```

## Демо

- `spritePro/demoGames/particle_demo.py` — базовые частицы
- `spritePro/demoGames/particles_images_demo.py` — частицы с использованием изображений, масштабирования и вращения
- `spritePro/demoGames/fireworks_demo.py` — фейерверки с использованием системы частиц

Для более подробной информации о связанных компонентах см.:
- [Документация по камере и частицам](camera_and_particles.md) - Система камеры и генератор частиц
- [Документация по спрайтам](sprite.md) - Базовые спрайты
