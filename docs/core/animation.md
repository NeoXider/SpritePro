# Animation (Анимация)

Покадровая анимация для спрайтов с поддержкой состояний и твининга.

## Конструктор

```python
Animation(owner_sprite, frames=None, frame_duration=0.1, loop=True, on_complete=None, on_frame=None)
```

| Параметр | Тип | Описание |
|----------|-----|---------|
| `owner_sprite` | Sprite | Спрайт-владелец |
| `frames` | List[Surface] | Список кадров |
| `frame_duration` | float | Длительность кадра (сек) |
| `loop` | bool | Зациклить |
| `on_complete` | Callable | При завершении |
| `on_frame` | Callable | При смене кадра |

## Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `current_frame` | int | Индекс текущего кадра |
| `is_playing` | bool | Воспроизводится |
| `is_paused` | bool | На паузе |
| `states` | Dict | Состояния анимации |
| `current_state` | str | Текущее состояние |

## Методы

### Управление воспроизведением

```python
animation.play()
animation.pause()
animation.resume()
animation.stop()
animation.reset()
```

### Состояния

```python
animation.add_state("idle", idle_frames)
animation.add_state("walk", walk_frames)
animation.set_state("walk")
```

### Твининг

```python
animation.add_tween("scale", 1.0, 1.5, 1.0, easing=s.EasingType.EASE_IN_OUT, loop=True, yoyo=True)
scale_value = animation.update_tween("scale")
```

## Примеры

```python
import spritePro as s
import pygame

sprite = s.Sprite("", size=(100, 100), pos=(400, 300))

frames = [pygame.Surface((100, 100), pygame.SRCALPHA) for _ in range(8)]
for i, frame in enumerate(frames):
    pygame.draw.circle(frame, (255, 0, 0), (50, 50), 30 + i * 5)

animation = s.Animation(sprite, frames=frames, frame_duration=0.1)
animation.play()
```

### Состояния

```python
animation = s.Animation(sprite)
animation.add_state("idle", idle_frames)
animation.add_state("walk", walk_frames)
animation.set_state("walk")
animation.play()
```

### Параллельные анимации

```python
main_animation = s.Animation(sprite, frames=walk_frames)
effect_animation = s.Animation(sprite, frames=effect_frames)
main_animation.add_parallel_animation(effect_animation)
main_animation.play()
```

### Обратные вызовы

```python
def on_complete():
    sprite.set_state("idle")

animation = s.Animation(sprite, frames=frames, on_complete=on_complete)
animation.play()
```

## Автообновление

```python
# Вариант 1: автоматически (по умолчанию)
animation = s.Animation(sprite, frames=frames)
while True:
    s.update()  # Анимация обновится автоматически

# Вариант 2: ручное обновление
animation = s.Animation(sprite, frames=frames, auto_register=False)
while True:
    s.update()
    animation.update()
```

## См. также

- [Tween System](tween_system.md)
- [Sprite](sprite.md)
