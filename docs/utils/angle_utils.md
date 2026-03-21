# Angle Utils (Утилиты для работы с углами)

Модуль `angle_utils` предоставляет функции для работы с углами, включая нормализацию, конвертацию и вычисления.

## Доступные функции

### `normalize_angle(angle)`
Нормализует угол в диапазоне 0-360 градусов.

```python
from spritePro.utils.angle import normalize_angle

angle = normalize_angle(450)  # Вернёт 90
angle = normalize_angle(-90)   # Вернёт 270
```

### `deg_to_rad(degrees)`
Конвертирует градусы в радианы.

```python
from spritePro.utils.angle import deg_to_rad

radians = deg_to_rad(180)  # Вернёт π (3.14159...)
```

### `rad_to_deg(radians)`
Конвертирует радианы в градусы.

```python
from spritePro.utils.angle import rad_to_deg

degrees = rad_to_deg(3.14159)  # Вернёт ~180
```

### `angle_diff(angle1, angle2)`
Вычисляет разницу между двумя углами (кратчайший путь).

```python
from spritePro.utils.angle import angle_diff

diff = angle_diff(10, 350)  # Вернёт -20 (кратчайший путь)
```

### `lerp_angle(start, end, t)`
Линейная интерполяция между двумя углами.

```python
from spritePro.utils.angle import lerp_angle

angle = lerp_angle(0, 180, 0.5)  # Вернёт 90
```

## Примеры использования

### Вращение спрайта
```python
import spritePro as s
from spritePro.utils.angle import deg_to_rad

# Повернуть спрайт на 45 градусов
sprite.set_rotation(deg_to_rad(45))
```

### Следование за целью
```python
import spritePro as s
from spritePro.utils.angle import angle_diff

# Вычислить угол до цели
dx = target.x - sprite.x
dy = target.y - sprite.y
angle = math.atan2(dy, dx)

# Повернуть спрайт
sprite.set_rotation(angle)
```
