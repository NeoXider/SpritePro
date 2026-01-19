# Готовые твины (Tween Presets)

Готовые твины — это удобные функции для анимации типовых свойств спрайта без
ручного `on_update`. Все функции возвращают объект `Tween`.

## Импорт

```python
import spritePro as s
```

## Список функций

- `tween_position(sprite, to, duration, easing=..., start=None, anchor=None, ...)`
- `tween_move_by(sprite, delta, duration, easing=..., ...)`
- `tween_scale(sprite, to, duration, easing=..., start=None, ...)`
- `tween_scale_by(sprite, delta, duration, easing=..., ...)`
- `tween_rotate(sprite, to, duration, easing=..., start=None, ...)`
- `tween_rotate_by(sprite, delta, duration, easing=..., ...)`
- `tween_color(sprite, to, duration, easing=..., start=None, ...)`
- `tween_alpha(sprite, to, duration, easing=..., start=None, ...)`
- `tween_size(sprite, to, duration, easing=..., start=None, ...)`
- `tween_punch_scale(sprite, strength=..., duration=..., ...)`
- `tween_shake_position(sprite, strength=..., duration=..., ...)`
- `tween_shake_rotation(sprite, strength=..., duration=..., ...)`
- `tween_fade_in(sprite, duration=..., ...)`
- `tween_fade_out(sprite, duration=..., ...)`
- `tween_color_flash(sprite, flash_color, duration=..., ...)`
- `tween_bezier(sprite, end, control1, control2=None, duration=..., ...)`

## Примеры

### Позиция и масштаб

```python
import spritePro as s

sprite = s.Sprite("", (60, 60), (200, 200))
sprite.set_color((120, 200, 255))

s.tween_position(sprite, to=(500, 300), duration=0.8, easing=s.EasingType.EASE_OUT)
s.tween_scale(sprite, to=1.4, duration=0.5, yoyo=True, loop=True)
```

## Демо

Запуск:

```bash
python spritePro/demoGames/tween_presets_demo.py
```

### Поворот и цвет

```python
s.tween_rotate(sprite, to=360, duration=1.2, easing=s.EasingType.EASE_IN_OUT)
s.tween_color(sprite, to=(255, 120, 120), duration=1.0)
```

### Прозрачность и размер

```python
s.tween_alpha(sprite, to=0, duration=0.6)
s.tween_size(sprite, to=(120, 80), duration=0.7)
```

### Вспышка и дрожание

```python
s.tween_color_flash(sprite, flash_color=(255, 255, 255), duration=0.2)
s.tween_shake_position(sprite, strength=(10, 6), duration=0.35)
s.tween_shake_rotation(sprite, strength=8, duration=0.35)
```

### Безье

```python
s.tween_bezier(
    sprite,
    end=(600, 300),
    control1=(300, 50),
    control2=(450, 550),
    duration=1.0,
)
```
