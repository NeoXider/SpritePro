# Эффекты камеры

Модуль `camera_effects.py` предоставляет визуальные эффекты для камеры, включая shake (тряску), zoom, fade и другие эффекты, которые могут улучшить игровой опыт.

## Обзор

Система эффектов камеры позволяет применять различные визуальные эффекты к камере сцены, создавая кинематографические переходы и обратную связь для игрока.

## Основные компоненты

### CameraEffects

```python
from spritePro.camera_effects import CameraEffects

effects = CameraEffects(camera)
```

### Методы класса

#### `shake(intensity=1.0, duration=0.3)`

Создает эффект тряски камеры.

**Параметры:**
- `intensity` (float) — интенсивность тряски (0.0-1.0)
- `duration` (float) — продолжительность в секундах

**Пример:**
```python
effects.shake(intensity=0.5, duration=0.5)
```

#### `zoom(target_zoom, duration=0.5, easing='ease_out')`

Плавное масштабирование камеры.

**Параметры:**
- `target_zoom` (float) — целевой уровень масштаба (1.0 = нормальный)
- `duration` (float) — продолжительность анимации
- `easing` (str) — тип сглаживания

```python
effects.zoom(2.0, duration=1.0)  # Увеличить в 2 раза
effects.zoom(0.5, duration=0.5)  # Уменьшить в 2 раза
```

#### `fade_in(duration=0.5, color=(0, 0, 0))`

Плавное появление (убирание черного экрана).

**Параметры:**
- `duration` (float) — продолжительность
- `color` (tuple) — цвет затемнения

```python
effects.fade_in(duration=1.0)  # Появление за 1 секунду
effects.fade_out(duration=0.5, color=(255, 0, 0))  # Затемнение красным
```

#### `fade_out(duration=0.5, color=(0, 0, 0))`

Плавное затемнение (появление черного экрана).

```python
effects.fade_out(duration=0.5)
```

#### `slide(target_position, duration=0.5, easing='ease_in_out')`

Плавное перемещение камеры к целевой позиции.

**Параметры:**
- `target_position` (tuple) — координаты (x, y)
- `duration` (float) — продолжительность
- `easing` (str) — тип сглаживания

```python
effects.slide((100, 200), duration=0.5)
```

#### `flash(intensity=1.0, color=(255, 255, 255))`

Мгновенная вспышка экрана.

**Параметры:**
- `intensity` (float) — интенсивность вспышки
- `color` (tuple) — цвет вспышки

```python
effects.flash(intensity=0.8)  # Белая вспышка
effects.flash(intensity=1.0, color=(255, 0, 0))  # Красная вспышка
```

#### `pulse(scale=1.1, duration=0.3)`

Эффект пульсации (приближение и отдаление).

**Параметры:**
- `scale` (float) — максимальный масштаб
- `duration` (float) — продолжительность

```python
effects.pulse(scale=1.2, duration=0.2)
```

#### `roll(angle, duration=0.5)`

Вращение камеры вокруг точки фокуса.

```python
effects.roll(45)  # Повернуть на 45 градусов
```

#### `update(delta_time)`

Обновление активных эффектов. Вызывается автоматически в игровом цикле.

#### `stop()`

Остановка всех активных эффектов.

#### `stop_all()`

Немедленная остановка всех эффектов и сброс камеры.

```python
effects.stop_all()
```

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `is_active` | bool | Есть ли активные эффекты |
| `current_effects` | list | Список активных эффектов |

## Практические примеры

### Эффект при получении урона

```python
from spritePro import SpritePro
from spritePro.camera_effects import CameraEffects

class Game(SpritePro):
    def on_ready(self):
        self.camera_effects = CameraEffects(self.camera)
        
    def on_player_hit(self):
        self.camera_effects.shake(intensity=0.8, duration=0.3)
        self.camera_effects.flash(color=(255, 0, 0))
```

### Переход между сценами

```python
def transition_to_scene(self, scene_name):
    self.camera_effects.fade_out(duration=0.5, color=(0, 0, 0))
    
    def after_fade():
        self.load_scene(scene_name)
        self.camera_effects.fade_in(duration=0.5)
        
    self.timer(0.5, after_fade)
```

###焦距变化

```python
def on_zoom_in(self):
    self.camera_effects.zoom(2.0, duration=0.5, easing='ease_out')
    
def on_zoom_out(self):
    self.camera_effects.zoom(1.0, duration=0.5, easing='ease_out')
```

### Кинематографический момент

```python
def play_cutscene(self):
    self.camera_effects.fade_out(duration=1.0)
    
    def show_title():
        self.camera_effects.fade_in(duration=1.0)
        self.camera_effects.zoom(1.5, duration=2.0)
        self.camera_effects.slide((400, 300), duration=2.0)
        
    self.timer(1.0, show_title)
```

### Взрывной эффект

```python
def on_explosion(self, position):
    self.camera_effects.shake(intensity=1.0, duration=0.5)
    self.camera_effects.flash(intensity=1.0, color=(255, 100, 0))
    self.camera_effects.pulse(scale=1.3, duration=0.3)
```

### Эффект при победе

```python
def on_victory(self):
    self.camera_effects.fade_out(duration=0.5, color=(255, 215, 0))
    
    def celebrate():
        self.camera_effects.zoom(1.5, duration=1.0)
        self.camera_effects.flash(color=(255, 215, 0))
        
    self.timer(0.5, celebrate)
```

## Комбинирование эффектов

```python
def dramatic_effect(self):
    self.camera_effects.fade_out(duration=0.3)
    
    def phase_two():
        self.camera_effects.shake(intensity=0.6, duration=0.4)
        self.camera_effects.flash()
        self.camera_effects.fade_in(duration=0.5)
        self.camera_effects.zoom(1.2, duration=0.5)
        
    self.timer(0.3, phase_two)
```

## Настройки по умолчанию

```python
effects = CameraEffects(
    camera,
    default_duration=0.5,
    default_easing='ease_in_out',
    shake_decay=0.9
)
```

## Лучшие практики

1. **Не злоупотребляйте эффектами** — частые тряски и вспышки могут утомить игрока
2. **Используйте для обратной связи** — эффекты лучше работают как реакция на события
3. **Комбинируйте умеренно** — слишком много эффектов одновременно выглядят хаотично
4. **Учитывайте настройки доступности** — предоставляйте опцию отключения эффектов
