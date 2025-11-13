# Модуль Tween

## Обзор

Модуль tween предоставляет мощную систему для создания плавных анимаций и переходов между значениями. Он поддерживает различные функции плавности, зацикливание и обратные вызовы для сложных последовательностей анимации.

## Основные компоненты

### TweenManager

Основной класс для управления несколькими твинами одновременно.

```python
import spritePro as s

tween_manager = s.TweenManager()
```

#### Методы

- `add_tween(name: str, start_value: float, end_value: float, duration: float, easing: EasingType = EasingType.LINEAR, on_complete: Optional[Callable] = None, loop: bool = False, yoyo: bool = False, delay: float = 0, on_update: Optional[Callable[[float], None]] = None)`: Добавить новый твин
- `update(dt: Optional[float] = None)`: Обновить все активные твины
- `pause_all()`: Поставить на паузу все твины
- `resume_all()`: Возобновить все твины
- `stop_all()`: Остановить и удалить все твины
- `get_tween(name: str) -> Optional[Tween]`: Получить конкретный твин
- `remove_tween(name: str)`: Удалить конкретный твин

### Tween

Базовый класс для отдельных твинов.

#### Параметры конструктора

- `start_value` (float): Начальное значение
- `end_value` (float): Конечное значение
- `duration` (float): Длительность анимации в секундах
- `easing` (EasingType): Тип функции плавности. По умолчанию: EasingType.LINEAR
- `loop` (bool): Зациклить ли анимацию. По умолчанию: False
- `yoyo` (bool): Обратить ли направление при зацикливании. По умолчанию: False
- `on_update` (Optional[Callable[[float], None]]): Обратный вызов для обновлений значения. По умолчанию: None
- `on_complete` (Optional[Callable]): Обратный вызов при завершении анимации. По умолчанию: None
- `delay` (float): Задержка перед началом в секундах. По умолчанию: 0

#### Методы Tween

- `update(dt: Optional[float] = None) -> Optional[float]`: Обновить твин и получить текущее значение
- `pause()`: Поставить твин на паузу
- `resume()`: Возобновить твин
- `stop()`: Остановить твин
- `reset()`: Сбросить твин в начальное состояние
- `get_progress() -> float`: Получить прогресс от 0.0 до 1.0

## Функции плавности

Модуль предоставляет различные функции плавности через перечисление `EasingType`:

```python
from spritePro.components.tween import EasingType
```

### Базовые функции плавности

- `LINEAR`: Постоянная скорость
- `EASE_IN`: Медленное начало, быстрое окончание
- `EASE_OUT`: Быстрое начало, медленное окончание
- `EASE_IN_OUT`: Медленное начало и окончание, быстрое середину

### Продвинутые функции плавности

- `SINE`: Плавная плавность на основе синуса
- `QUAD`: Квадратичная плавность
- `CUBIC`: Кубическая плавность
- `QUART`: Четвертая степень плавности
- `QUINT`: Пятая степень плавности
- `EXPO`: Экспоненциальная плавность
- `CIRC`: Круговая плавность
- `BACK`: Плавность с перелетом
- `BOUNCE`: Отскакивающая плавность
- `ELASTIC`: Эластичная плавность

## Примеры использования

### Базовое движение

```python
import spritePro as s

# Создать твин для горизонтального движения
tween_manager = s.TweenManager()

tween_manager.add_tween(
    "move_x",
    start_value=0,
    end_value=100,
    duration=2.0,
    easing=s.EasingType.EASE_IN_OUT,
    on_update=lambda x: setattr(sprite, 'x', x)
)

# В игровом цикле
while True:
    s.update()
    tween_manager.update()  # Обновить все твины
```

### Переход цвета

```python
# Создать твин для изменения цвета
def lerp_color(color1, color2, t):
    return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))

red = (255, 0, 0)
blue = (0, 0, 255)

tween_manager.add_tween(
    "color",
    start_value=0,
    end_value=1,
    duration=1.5,
    easing=s.EasingType.SINE,
    on_update=lambda t: sprite.set_color(lerp_color(red, blue, t))
)
```

### Зацикленная анимация

```python
# Создать зацикленный твин с эффектом yoyo
tween_manager.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    easing=s.EasingType.EASE_IN_OUT,
    loop=True,
    yoyo=True,
    on_update=lambda s: setattr(sprite, 'scale', s)
)
```

### Несколько твинов

```python
# Создать несколько твинов для сложной анимации
tween_manager.add_tween("move_x", start_value=0, end_value=100, duration=2.0)
tween_manager.add_tween("move_y", start_value=0, end_value=50, duration=1.5)
tween_manager.add_tween("angle", start_value=0, end_value=360, duration=3.0)

# Обновить все твины
tween_manager.update()
```

### Твин с задержкой

```python
# Твин с задержкой перед началом
tween_manager.add_tween(
    "fade",
    start_value=255,
    end_value=0,
    duration=1.0,
    delay=2.0,  # Начнется через 2 секунды
    on_update=lambda alpha: sprite.set_alpha(int(alpha))
)
```

### Управление отдельным твином

```python
# Создать твин напрямую
tween = s.Tween(
    start_value=0,
    end_value=100,
    duration=2.0,
    easing=s.EasingType.EASE_IN_OUT
)

# Управление
tween.pause()
tween.resume()
tween.stop()
tween.reset()

# Обновление и получение значения
current_value = tween.update(dt=s.dt)
if current_value is not None:
    sprite.x = current_value
```

### Обратные вызовы

```python
def on_complete():
    print("Анимация завершена!")

def on_update(value):
    sprite.scale = value
    print(f"Текущий масштаб: {value}")

tween_manager.add_tween(
    "scale",
    start_value=1.0,
    end_value=2.0,
    duration=2.0,
    on_update=on_update,
    on_complete=on_complete
)
```

## Лучшие практики

1. **Всегда обновляйте твины в игровом цикле** используя `tween_manager.update(dt)` или `tween.update(dt)`
2. **Используйте уникальные идентификаторы** для каждого твина
3. **Очищайте твины**, когда они больше не нужны, используя `remove_tween()` или `stop_all()`
4. **Используйте подходящие функции плавности** для разных типов анимаций
5. **Рассмотрите использование обратных вызовов** для сложных анимаций
6. **Используйте `dt` (delta time)** для независимой от частоты кадров анимации

## Соображения производительности

- Твины легковесны и эффективны
- Количество активных твинов должно контролироваться
- Сложные функции плавности могут иметь более высокое использование CPU
- Рассмотрите использование более простых функций плавности для мобильных устройств

## Интеграция с другими компонентами

### С системой спрайтов

```python
# Анимация позиции спрайта
tween_manager.add_tween(
    "position_x",
    start_value=sprite.x,
    end_value=500,
    duration=2.0,
    on_update=lambda x: setattr(sprite, 'x', x)
)

# Анимация масштаба
tween_manager.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    loop=True,
    yoyo=True,
    on_update=lambda s: setattr(sprite, 'scale', s)
)
```

### С системой анимации

```python
# Использование твинов в Animation компоненте
animation.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    easing=s.EasingType.EASE_IN_OUT
)
```

Для более подробной информации о связанных компонентах см.:
- [Документация по анимации](animation.md) - Использование твинов в анимациях
- [Документация по спрайтам](sprite.md) - Анимация свойств спрайтов
