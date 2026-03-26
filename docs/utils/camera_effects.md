# Эффекты камеры

Визуальные эффекты: shake, zoom, fade, flash.

## CameraEffects

```python
from spritePro.camera_effects import CameraEffects

effects = CameraEffects(camera)
```

## Методы

| Метод | Описание |
|-------|----------|
| `shake(intensity, duration)` | Тряска камеры |
| `zoom(target, duration)` | Масштабирование |
| `fade_in(duration, color)` | Появление |
| `fade_out(duration, color)` | Затемнение |
| `slide(pos, duration)` | Плавное перемещение |
| `flash(intensity, color)` | Вспышка |
| `pulse(scale, duration)` | Пульсация |
| `roll(angle, duration)` | Вращение |

## Параметры

```python
effects.shake(intensity=0.5, duration=0.5)   # 0.0-1.0
effects.zoom(2.0, duration=1.0)             # Увеличить в 2 раза
effects.fade_in(duration=1.0)                # Появление за 1 сек
effects.fade_out(duration=0.5, color=(255, 0, 0))  # Красное затемнение
effects.slide((100, 200), duration=0.5)
effects.flash(intensity=0.8)                 # Белая вспышка
effects.pulse(scale=1.2, duration=0.3)
effects.roll(45)                             # Повернуть на 45°
```

## Пример: урон игроку

```python
def on_player_hit(self):
    self.camera_effects.shake(intensity=0.8, duration=0.3)
    self.camera_effects.flash(color=(255, 0, 0))
```

## Пример: переход между сценами

```python
def transition_to_scene(self, name):
    self.camera_effects.fade_out(duration=0.5)
    # ... загрузка сцены ...
    self.camera_effects.fade_in(duration=0.5)
```

## Пример: взрыв

```python
def on_explosion(self):
    self.camera_effects.shake(intensity=1.0, duration=0.5)
    self.camera_effects.flash(intensity=1.0, color=(255, 100, 0))
    self.camera_effects.pulse(scale=1.3, duration=0.3)
```

## Свойства

```python
effects.is_active          # Есть ли активные эффекты
effects.current_effects   # Список активных
effects.stop_all()       # Остановить все
```

## Рекомендации

- Не злоупотребляйте эффектами
- Используйте для обратной связи (урон, победа)
- Предоставляйте опцию отключения для доступности

## См. также

- [Camera](sprite.md)
