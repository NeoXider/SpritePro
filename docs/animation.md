# Модуль Анимации

Модуль Animation предоставляет продвинутые возможности анимации для спрайтов в фреймворке SpritePro.

## Обзор

Класс Animation - это мощный компонент, который обеспечивает покадровую анимацию, плавные переходы и параллельные анимации для спрайтов. Он поддерживает различные состояния анимации, обратные вызовы и эффекты твининга.

## Основные возможности

- Покадровая анимация с настраиваемой длительностью кадра
- Управление состояниями для различных состояний анимации
- Плавные переходы с использованием твининга
- Поддержка параллельных анимаций
- Система обратных вызовов для событий анимации
- Режимы циклической и однократной анимации
- Привязка к сцене: обновление идет только в активной сцене

## Класс: Animation

### Конструктор
```python
Animation(
    owner_sprite,
    frames: Optional[List[pygame.Surface]] = None,
    frame_duration: float = 0.1,
    loop: bool = True,
    on_complete: Optional[Callable] = None,
    on_frame: Optional[Callable] = None,
    scene: Optional[Scene | str] = None
)
```

**Параметры:**
- `owner_sprite`: Спрайт-владелец анимации
- `frames` (Optional[List[pygame.Surface]]): Список кадров анимации. По умолчанию: None
- `frame_duration` (float): Длительность каждого кадра в секундах. По умолчанию: 0.1 (100 миллисекунд)
- `loop` (bool): Должна ли анимация зацикливаться. По умолчанию: True
- `on_complete` (Optional[Callable]): Функция обратного вызова, вызываемая при завершении анимации. По умолчанию: None
- `on_frame` (Optional[Callable]): Функция обратного вызова, вызываемая при смене кадра. По умолчанию: None
- `scene` (Scene | str, optional): Сцена для анимации. По умолчанию: берется из `owner_sprite.scene`

### Свойства

- `owner`: Спрайт-владелец этой анимации
- `frames`: Список кадров анимации (List[pygame.Surface])
- `frame_duration`: Длительность каждого кадра в секундах (float, хранится внутренне в миллисекундах)
- `loop`: Должна ли анимация зацикливаться (bool)
- `current_frame`: Индекс текущего кадра (int)
- `is_playing`: Воспроизводится ли анимация в данный момент (bool)
- `is_paused`: Находится ли анимация на паузе (bool)
- `states`: Словарь состояний анимации (Dict[str, List[pygame.Surface]])
- `current_state`: Имя текущего состояния (str | None)
- `parallel_animations`: Список параллельных анимаций (List[Animation])
- `tween_manager`: Экземпляр TweenManager для плавных переходов
- `on_complete`: Функция обратного вызова, вызываемая при завершении анимации (Optional[Callable])
- `on_frame`: Функция обратного вызова, вызываемая при смене кадра (Optional[Callable])

### Методы

#### Управление состояниями
- `add_state(name: str, frames: List[pygame.Surface])`: Добавить новое состояние анимации
- `set_state(name: str)`: Переключиться на другое состояние анимации

#### Управление воспроизведением
- `play()`: Начать воспроизведение анимации
- `pause()`: Поставить анимацию на паузу
- `resume()`: Возобновить приостановленную анимацию
- `stop()`: Остановить анимацию
- `reset()`: Сбросить анимацию в начальное состояние

#### Твининг
- `add_tween(name: str, start_value: float, end_value: float, duration: float, easing: EasingType = EasingType.LINEAR, on_complete: Optional[Callable] = None, loop: bool = False, yoyo: bool = False, delay: float = 0, on_update: Optional[Callable[[float], None]] = None)`: Добавить плавный переход
- `update_tween(name: str, dt: Optional[float] = None) -> Optional[float]`: Обновить конкретный переход и получить текущее значение

**Параметры add_tween:**
- `name` (str): Имя перехода
- `start_value` (float): Начальное значение
- `end_value` (float): Конечное значение
- `duration` (float): Длительность в секундах
- `easing` (EasingType): Тип плавности (из EasingType). По умолчанию: EasingType.LINEAR
- `on_complete` (Optional[Callable]): Функция обратного вызова при завершении. По умолчанию: None
- `loop` (bool): Зациклить ли переход. По умолчанию: False
- `yoyo` (bool): Обратить ли переход (туда-обратно). По умолчанию: False
- `delay` (float): Задержка перед началом в секундах. По умолчанию: 0
- `on_update` (Optional[Callable[[float], None]]): Функция обратного вызова при каждом обновлении. По умолчанию: None

#### Параллельные анимации
- `add_parallel_animation(animation: Animation)`: Добавить анимацию для параллельного выполнения

#### Управление кадрами
- `update(dt: Optional[float] = None)`: Обновить состояние анимации
- `get_current_frame() -> Optional[pygame.Surface]`: Получить текущий кадр анимации
- `set_frame_duration(duration: float)`: Установить длительность кадра в секундах
- `set_loop(loop: bool)`: Установить, должна ли анимация зацикливаться

## Примеры использования

### Базовая анимация
```python
import spritePro as s
import pygame

# Создать спрайт
sprite = s.Sprite("", size=(100, 100), pos=(400, 300))

# Создать кадры анимации
frames = []
for i in range(8):
    frame = pygame.Surface((100, 100), pygame.SRCALPHA)
    # Нарисовать что-то на кадре
    pygame.draw.circle(frame, (255, 0, 0), (50, 50), 30 + i * 5)
    frames.append(frame)

# Создать и запустить анимацию
animation = s.Animation(sprite, frames=frames, frame_duration=0.1)  # 0.1 секунды = 100 мс
animation.play()

# Анимация автоматически регистрируется при создании (auto_register=True по умолчанию)
# В игровом цикле - вариант 1: автоматическое обновление (по умолчанию)
animation = s.Animation(sprite, frames=frames, frame_duration=0.1)  # Автоматически регистрируется
while True:
    s.update()  # Анимация обновится автоматически с dt

# В игровом цикле - вариант 2: без автоматической регистрации
animation = s.Animation(sprite, frames=frames, frame_duration=0.1, auto_register=False)
while True:
    s.update()
    animation.update()  # dt автоматически берется из spritePro.dt, если не указан
```

### Анимация на основе состояний
```python
# Создать анимацию с состояниями
animation = s.Animation(sprite)
animation.add_state("idle", idle_frames)
animation.add_state("walk", walk_frames)
animation.add_state("jump", jump_frames)

# Переключить состояние
animation.set_state("walk")
animation.play()
```

### Анимация с твинингом
```python
# Добавить твининг масштаба
animation.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    easing=s.EasingType.EASE_IN_OUT,
    loop=True,
    yoyo=True
)

# В игровом цикле обновлять твининг - вариант 1: автоматическое обновление
s.register_update_object(animation)
while True:
    s.update()  # Анимация обновится автоматически
    
    # Применить значение твининга к спрайту
    scale_value = animation.update_tween("scale")

# В игровом цикле обновлять твининг - вариант 2: ручное обновление
while True:
    s.update()
    animation.update()  # dt автоматически берется из spritePro.dt
    
    # Применить значение твининга к спрайту
    scale_value = animation.update_tween("scale")
    if scale_value is not None:
        sprite.scale = scale_value
```

### Параллельные анимации
```python
# Создать основную анимацию
main_animation = s.Animation(sprite, frames=walk_frames)

# Создать дополнительную анимацию (например, для эффекта)
effect_animation = s.Animation(sprite, frames=effect_frames)

# Добавить параллельную анимацию
main_animation.add_parallel_animation(effect_animation)

# Обе анимации будут обновляться вместе
main_animation.play()
```

### Обратные вызовы
```python
def on_animation_complete():
    print("Анимация завершена!")
    sprite.set_state("idle")

def on_frame_change(frame_index):
    print(f"Текущий кадр: {frame_index}")

animation = s.Animation(
    sprite,
    frames=frames,
    on_complete=on_animation_complete,
    on_frame=on_frame_change
)
animation.play()
```

## Лучшие практики

### 1. Управление кадрами
- Сохраняйте размеры кадров одинаковыми
- Используйте подходящую длительность кадров
- Учитывайте использование памяти при больших наборах кадров

### 2. Управление состояниями
- Используйте осмысленные имена состояний
- Предзагружайте все состояния при инициализации
- Обрабатывайте переходы между состояниями плавно

### 3. Производительность
- Используйте подходящее количество кадров
- Рассмотрите использование спрайт-листов для сложных анимаций
- Следите за использованием памяти при большом количестве анимаций

### 4. Твининг
- Используйте подходящие типы плавности
- Учитывайте влияние на производительность при большом количестве твинов
- Используйте эффект yoyo для плавных переходов

## Интеграция с другими компонентами

Animation разработан для бесшовной работы с другими компонентами spritePro:

- **Sprite**: Анимация автоматически обновляет изображение спрайта
- **Tween**: Использует TweenManager для плавных переходов
- **Timer**: Может использоваться для синхронизации анимаций

Для более подробной информации см.:
- [Документация по спрайтам](sprite.md)
- [Документация по твинингу](tween.md)
