# Tween System (Анимации)

Плавные переходы между значениями с поддержкой функций плавности, зацикливания и обратных вызовов.

## TweenManager

```python
tween_manager = s.TweenManager()
```

### Методы

| Метод | Описание |
|-------|----------|
| `add_tween(...)` | Добавить твин |
| `update()` | Обновить все твины |
| `pause_all()` | Пауза всем |
| `resume_all()` | Возобновить |
| `stop_all()` | Остановить все |
| `start_tween(name)` | Запустить по имени |
| `remove_tween(name)` | Удалить твин |

## Tween

```python
tween = s.Tween(start_value, end_value, duration, easing=EasingType.LINEAR)
```

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `start_value` | Начальное значение | — |
| `end_value` | Конечное значение | — |
| `duration` | Длительность (сек) | — |
| `easing` | Тип плавности | LINEAR |
| `loop` | Зациклить | False |
| `yoyo` | Туда-обратно | False |
| `on_update` | Колбэк обновления | None |
| `on_complete` | Колбэк завершения | None |
| `delay` | Задержка (сек) | 0 |
| `auto_start` | Автозапуск | True |

### Методы

```python
tween.start()
tween.pause()
tween.resume()
tween.stop()
tween.reset()
current_value = tween.update()
tween.get_progress()  # 0.0 - 1.0
```

## Функции плавности (EasingType)

- `LINEAR` — постоянная скорость
- `EASE_IN` / `EASE_OUT` / `EASE_IN_OUT`
- `SINE`, `QUAD`, `CUBIC`, `QUART`, `QUINT`
- `EXPO`, `CIRC`
- `BACK` — с перелетом
- `BOUNCE` — отскок
- `ELASTIC` — эластичность

## Fluent API (Do-твины)

Методы возвращают `TweenHandle`:

```python
player.DoMove((500, 300), 1.2)  # По умолчанию Ease.OutQuad

# Конфигурация хэндла
handle = player.DoMove((200, 500), 1)\
    .SetEase(s.Ease.OutCubic)\
    .SetDelay(0.3)\
    .OnComplete(lambda: print("Done"))

player.DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)
```

### TweenHandle методы

| Метод | Описание |
|-------|----------|
| `SetEase(ease)` | Плавность |
| `SetDelay(sec)` | Задержка |
| `OnComplete(cb)` | При завершении |
| `SetLoops(n)` | Проходы (-1 = бесконечно) |
| `SetYoyo(True)` | Туда-обратно |
| `Restart()` | Перезапуск |
| `Kill(complete=False)` | Остановить |

### Do-методы спрайта

| Метод | Описание |
|-------|----------|
| `DoMove(to, dur)` | Движение к позиции |
| `DoMoveBy(delta, dur)` | Смещение |
| `DoScale(to, dur)` | Масштаб |
| `DoScaleBy(delta, dur)` | Изменение масштаба |
| `DoRotate(to, dur)` | Поворот к углу |
| `DoRotateBy(delta, dur)` | Поворот на угол |
| `DoColor(to, dur)` | Цвет |
| `DoAlpha(to, dur)` | Прозрачность |
| `DoFadeIn(dur)` | Появление |
| `DoFadeOut(dur)` | Исчезновение |
| `DoSize(to, dur)` | Размер |
| `DoPunchScale(s, dur)` | Удар масштаба |
| `DoShakePosition(s, dur)` | Дрожание позиции |
| `DoBezier(end, c1, c2, dur)` | Движение по Безье |
| `DoKill()` | Остановить все твины |

## Примеры

```python
# Простое движение
s.tween_position(sprite, to=(500, 300), duration=0.8, easing=s.EasingType.EASE_OUT)

# Fluent API
player.DoMove((500, 300), 1.2).SetEase(s.Ease.OutQuad)

# Зацикленный yoyo-масштаб
player.DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)

# Векторное значение
from pygame.math import Vector2
tween_manager.add_tween("move", Vector2(100, 100), Vector2(500, 300), 1.2,
    on_update=lambda v: setattr(sprite, "pos", v), value_type="vector2")
```

## Демо

```bash
python -m spritePro.demoGames.fluent_tween_demo
```

## См. также

- [Animation](animation.md)
- [Sprite](sprite.md)
