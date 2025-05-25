### Tween System
The tween system provides smooth transitions between values with various easing functions. For detailed documentation, see [tween.md](docs/tween.md).

```python
# Create a tween manager
tween_manager = TweenManager()

# Add a tween for smooth movement
tween_manager.add_tween(
    "move_x",           # Unique identifier
    start_value=0,      # Start position
    end_value=100,      # End position
    duration=2.0,       # Duration in seconds
    easing=EasingType.EASE_IN_OUT,  # Easing function
    loop=True,          # Enable looping
    yoyo=True,          # Reverse direction when looping
    on_update=lambda x: sprite.rect.x = x  # Update callback
)

# Update tweens in game loop
tween_manager.update(dt)

# Control tweens
tween_manager.pause_all()    # Pause all tweens
tween_manager.resume_all()   # Resume all tweens
tween_manager.stop_all()     # Stop all tweens
```

Available easing types:
- `LINEAR`: Linear interpolation
- `EASE_IN`: Slow start, fast end
- `EASE_OUT`: Fast start, slow end
- `EASE_IN_OUT`: Slow start and end, fast middle
- `SINE`: Smooth sine-based easing
- `QUAD`: Quadratic easing
- `CUBIC`: Cubic easing
- `QUART`: Quartic easing
- `QUINT`: Quintic easing
- `EXPO`: Exponential easing
- `CIRC`: Circular easing
- `BACK`: Overshooting easing
- `BOUNCE`: Bouncing easing
- `ELASTIC`: Elastic easing

### Система Твинов
Система твинов обеспечивает плавные переходы между значениями с различными функциями плавности. Подробная документация доступна в [tween_ru.md](docs/tween_ru.md).

```python
# Создание менеджера твинов
tween_manager = TweenManager()

# Добавление твина для плавного движения
tween_manager.add_tween(
    "move_x",           # Уникальный идентификатор
    start_value=0,      # Начальная позиция
    end_value=100,      # Конечная позиция
    duration=2.0,       # Длительность в секундах
    easing=EasingType.EASE_IN_OUT,  # Функция плавности
    loop=True,          # Включить зацикливание
    yoyo=True,          # Обратное направление при зацикливании
    on_update=lambda x: sprite.rect.x = x  # Функция обновления
)

# Обновление твинов в игровом цикле
tween_manager.update(dt)

# Управление твинами
tween_manager.pause_all()    # Пауза всех твинов
tween_manager.resume_all()   # Возобновление всех твинов
tween_manager.stop_all()     # Остановка всех твинов
```

Доступные типы плавности:
- `LINEAR`: Линейная интерполяция
- `EASE_IN`: Медленное начало, быстрое окончание
- `EASE_OUT`: Быстрое начало, медленное окончание
- `EASE_IN_OUT`: Медленное начало и окончание, быстрое в середине
- `SINE`: Плавная синусоидальная интерполяция
- `QUAD`: Квадратичная интерполяция
- `CUBIC`: Кубическая интерполяция
- `QUART`: Интерполяция четвертой степени
- `QUINT`: Интерполяция пятой степени
- `EXPO`: Экспоненциальная интерполяция
- `CIRC`: Круговая интерполяция
- `BACK`: Интерполяция с перелетом
- `BOUNCE`: Интерполяция с отскоком
- `ELASTIC`: Эластичная интерполяция 