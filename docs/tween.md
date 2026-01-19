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

- `add_tween(name: str, start_value: float, end_value: float, duration: float, easing: EasingType = EasingType.LINEAR, on_complete: Optional[Callable] = None, loop: bool = False, yoyo: bool = False, delay: float = 0, on_update: Optional[Callable[[float], None]] = None, auto_start: bool = True)`: Добавить новый твин (твины в менеджере не регистрируются отдельно, обновляются через менеджер)
- `update(dt: Optional[float] = None)`: Обновить все активные твины (dt автоматически берется из spritePro.dt, если не указан)
- `pause_all()`: Поставить на паузу все твины
- `resume_all()`: Возобновить все твины
- `stop_all(apply_end: bool = True)`: Остановить и удалить все твины (можно применить конечные значения)
- `reset_all(apply_end: bool = False)`: Сбросить все твины (можно применить конечные значения перед сбросом)
- `start_all(apply_end: bool = False)`: Запустить все твины (можно применить конечные значения перед стартом)
- `start_tween(name: str)`: Запустить конкретный твин по имени
- `get_tween(name: str) -> Optional[Tween]`: Получить конкретный твин
- `remove_tween(name: str, apply_end: bool = True)`: Удалить конкретный твин (можно применить конечное значение)

### Tween

Базовый класс для отдельных твинов.

#### Параметры конструктора

- `start_value` (Any): Начальное значение (float, Vector2, tuple/list)
- `end_value` (Any): Конечное значение
- `duration` (float): Длительность анимации в секундах
- `easing` (EasingType): Тип функции плавности. По умолчанию: EasingType.LINEAR
- `loop` (bool): Зациклить ли анимацию. По умолчанию: False
- `yoyo` (bool): Обратить ли направление при зацикливании. По умолчанию: False
- `on_update` (Optional[Callable[[Any], None]]): Обратный вызов для обновлений значения. По умолчанию: None
- `on_complete` (Optional[Callable]): Обратный вызов при завершении анимации. По умолчанию: None
- `delay` (float): Задержка перед началом в секундах. По умолчанию: 0
- `auto_start` (bool): Автоматически запускать твин при создании. По умолчанию: True
- `auto_register` (bool): Автоматически регистрировать твин для обновления в spritePro.update(). По умолчанию: True
- `value_type` (Optional[str]): "vector2", "vector3", "color" или None (авто). По умолчанию: None

#### Методы Tween

- `start()`: Запустить твин (если был создан с auto_start=False)
- `update(dt: Optional[float] = None) -> Optional[Any]`: Обновить твин и получить текущее значение (dt автоматически берется из spritePro.dt, если не указан)
- `pause()`: Поставить твин на паузу
- `resume()`: Возобновить твин
- `stop(apply_end: bool = True)`: Остановить твин (можно применить конечное значение)
- `reset(apply_end: bool = False)`: Сбросить твин (можно применить конечное значение перед сбросом)
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

### Готовые твины для спрайтов

SpritePro предоставляет набор готовых твинов для типовых свойств спрайта:

- `tween_position`, `tween_move_by`
- `tween_scale`, `tween_scale_by`
- `tween_rotate`, `tween_rotate_by`
- `tween_color`, `tween_alpha`, `tween_size`

Полная документация: [Tween Presets](tween_presets.md)

```python
import spritePro as s

sprite = s.Sprite("", (60, 60), (200, 200))
sprite.set_color((120, 200, 255))

s.tween_position(sprite, to=(500, 300), duration=0.8, easing=s.EasingType.EASE_OUT)
s.tween_scale(sprite, to=1.4, duration=0.5, yoyo=True, loop=True)
s.tween_color(sprite, to=(255, 120, 120), duration=1.0)
```

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

# TweenManager автоматически регистрируется при создании (auto_register=True по умолчанию)
# В игровом цикле - вариант 1: автоматическое обновление (по умолчанию)
tween_manager = s.TweenManager()  # Автоматически регистрируется
while True:
    s.update()  # Автоматически обновит твины с dt

# В игровом цикле - вариант 2: без автоматической регистрации
tween_manager = s.TweenManager(auto_register=False)
while True:
    s.update()
    tween_manager.update()  # dt автоматически берется из spritePro.dt
```

### Переход цвета

```python
import spritePro as s

tween_manager.add_tween(
    "color",
    start_value=(255, 0, 0),
    end_value=(0, 255, 0),
    duration=1.5,
    easing=s.EasingType.SINE,
    on_update=lambda c: sprite.set_color(c),
    value_type="color"
)
```

### Вектор2 (позиция)

```python
from pygame.math import Vector2
import spritePro as s

tween_manager.add_tween(
    "move",
    start_value=Vector2(100, 100),
    end_value=Vector2(500, 300),
    duration=1.2,
    on_update=lambda v: setattr(sprite, "pos", v),
    value_type="vector2"
)
```

### Вектор3 (кастомные данные)

```python
import spritePro as s

tween_manager.add_tween(
    "data",
    start_value=(0.0, 1.0, 0.0),
    end_value=(1.0, 0.0, 2.0),
    duration=2.0,
    on_update=lambda v: print(v),
    value_type="vector3"
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
# Создать твин напрямую (автоматически запускается)
tween = s.Tween(
    start_value=0,
    end_value=100,
    duration=2.0,
    easing=s.EasingType.EASE_IN_OUT
)

# Создать твин без автоматического запуска
tween = s.Tween(
    start_value=0,
    end_value=100,
    duration=2.0,
    auto_start=False  # Не запускается автоматически
)
tween.start()  # Запустить вручную

# Управление
tween.pause()
tween.resume()
tween.stop()
tween.reset()
tween.start()  # Запустить заново

# Обновление и получение значения
current_value = tween.update()  # dt автоматически берется из spritePro.dt
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

### Создание твина без автоматического запуска

```python
# Создать твин, который не запускается автоматически
tween_manager.add_tween(
    "fade_in",
    start_value=0,
    end_value=255,
    duration=1.0,
    auto_start=False  # Не запускается при создании
)

# Запустить в нужный момент
def show_sprite():
    tween_manager.start_tween("fade_in")
    sprite.active = True
```

### Сброс всех твинов

```python
# Сбросить все твины в начальное состояние
tween_manager.reset_all()

# Полезно при перезапуске уровня или сцены
def restart_level():
    tween_manager.reset_all()  # Все твины вернутся к начальным значениям
```

## Автоматическое обновление

По умолчанию все компоненты (TweenManager, Animation, Timer, Tween) автоматически регистрируются для обновления при создании:

```python
import spritePro as s

# Все эти объекты автоматически регистрируются при создании
tween_manager = s.TweenManager()  # auto_register=True по умолчанию
animation = s.Animation(...)  # auto_register=True по умолчанию
timer = s.Timer(...)  # auto_register=True по умолчанию, autostart=True по умолчанию

# В игровом цикле - все зарегистрированные объекты обновятся автоматически с dt
while True:
    s.update()  # Автоматически обновит все зарегистрированные объекты

# Если нужно отключить автоматическую регистрацию
tween_manager = s.TweenManager(auto_register=False)
animation = s.Animation(..., auto_register=False)
timer = s.Timer(..., auto_register=False)

# Или отменить регистрацию вручную
s.unregister_update_object(tween_manager)
```

## Лучшие практики

1. **Используйте автоматическое обновление** - передавайте твины, анимации и таймеры в `spritePro.update()` или регистрируйте через `register_update_object()`
2. **Параметр `dt` необязателен** - он автоматически берется из `spritePro.dt`, если не указан явно
3. **Используйте `auto_start=False`** для твинов, которые нужно запускать вручную в определенный момент
4. **Используйте уникальные идентификаторы** для каждого твина
5. **Очищайте твины**, когда они больше не нужны, используя `remove_tween()` или `stop_all()`
6. **Используйте `reset_all()`** для сброса всех твинов в начальное состояние
7. **Используйте подходящие функции плавности** для разных типов анимаций
8. **Рассмотрите использование обратных вызовов** для сложных анимаций

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
