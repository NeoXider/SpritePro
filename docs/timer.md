# Компонент Timer

Компонент `Timer` предоставляет точную функциональность таймера для игровых событий, задержек и планирования с поддержкой обратных вызовов, повторения и функций паузы/возобновления.

## Обзор

Компонент Timer необходим для управления событиями, основанными на времени в играх, такими как перезарядка, задержки, анимации и запланированные действия. Он предоставляет независимую от частоты кадров систему времени с гибкой поддержкой обратных вызовов.

## Основные возможности

- **Точное время**: Система времени, независимая от частоты кадров
- **Поддержка обратных вызовов**: Выполнение функций при завершении таймера
- **Функциональность повторения**: Однократные или повторяющиеся таймеры
- **Пауза/Возобновление**: Полный контроль над состоянием таймера
- **Отслеживание прогресса**: Мониторинг прогресса таймера и оставшегося времени
- **Множественные таймеры**: Управление несколькими одновременными таймерами

## Параметры конструктора

- `duration` (float): Длительность таймера в секундах
- `callback` (callable, optional): Функция для вызова при завершении таймера. По умолчанию: None
- `args` (Tuple, optional): Позиционные аргументы для обратного вызова. По умолчанию: ()
- `kwargs` (Dict, optional): Именованные аргументы для обратного вызова. По умолчанию: {}
- `repeat` (bool): Должен ли таймер повторяться. По умолчанию: False
- `autostart` (bool): Запустить таймер сразу при создании. По умолчанию: False

## Свойства

- `duration` (float): Интервал таймера в секундах
- `active` (bool): True, если таймер запущен и не на паузе
- `done` (bool): True, если таймер завершен (и не повторяется)
- `repeat` (bool): Повторяется ли таймер
- `callback` (Callable | None): Функция обратного вызова
- `args` (Tuple): Позиционные аргументы для обратного вызова
- `kwargs` (Dict): Именованные аргументы для обратного вызова

## Управление таймером

### Базовые операции с таймером
```python
# Создать таймер
timer = s.Timer(duration=5.0)

# Запустить таймер (можно указать новую длительность)
timer.start()  # Запустить с текущей длительностью
timer.start(duration=10.0)  # Запустить с новой длительностью

# Поставить таймер на паузу
timer.pause()

# Возобновить таймер
timer.resume()

# Остановить таймер
timer.stop()

# Сбросить таймер
timer.reset()
```

### Проверка состояния таймера
```python
# Проверить состояние таймера
if timer.active:
    print("Таймер активен")

if timer.done:
    print("Таймер завершен")

# Получить информацию о таймере
time_left = timer.time_left()  # Оставшееся время в секундах
elapsed_time = timer.elapsed()  # Прошедшее время в секундах
progress = timer.progress()  # Прогресс от 0.0 до 1.0

print(f"Прогресс: {progress:.2f}")  # 0.0 до 1.0
print(f"Осталось: {time_left:.2f} секунд")
print(f"Прошло: {elapsed_time:.2f} секунд")
```

## Система обратных вызовов

### Простые обратные вызовы
```python
def explosion_timer():
    print("Бум!")
    create_explosion()

timer = s.Timer(3.0, explosion_timer)
timer.start()
```

### Обратные вызовы с параметрами
```python
def damage_player(damage_amount, damage_type="normal"):
    player.take_damage(damage_amount, damage_type)

# Использовать args и kwargs
timer = s.Timer(
    2.0,
    damage_player,
    args=(25,),  # Позиционные аргументы
    kwargs={"damage_type": "fire"}  # Именованные аргументы
)
timer.start()

# Или использовать lambda
timer = s.Timer(2.0, lambda: damage_player(25, "fire"))
timer.start()

# Или использовать functools.partial
from functools import partial
timer = s.Timer(2.0, partial(damage_player, 25, damage_type="fire"))
timer.start()
```

### Множественные обратные вызовы
```python
def callback1():
    print("Первый обратный вызов")

def callback2():
    print("Второй обратный вызов")

# Цепочка обратных вызовов
timer = s.Timer(1.0, lambda: [callback1(), callback2()])
timer.start()
```

## Повторяющиеся таймеры

### Базовый повторяющийся таймер
```python
def spawn_enemy():
    enemies.append(Enemy())

# Создавать врага каждые 5 секунд
spawn_timer = s.Timer(
    duration=5.0,
    callback=spawn_enemy,
    repeat=True
)
spawn_timer.start()
```

### Автозапуск таймера
```python
# Таймер запустится автоматически при создании
timer = s.Timer(
    duration=2.0,
    callback=lambda: print("Тик"),
    repeat=True,
    autostart=True  # Автоматический запуск
)
```

## Продвинутые возможности

### Таймер с изменением длительности
```python
# Можно изменить длительность при запуске
timer = s.Timer(duration=5.0)
timer.start(duration=10.0)  # Запустить с новой длительностью
```

### Таймер с отслеживанием прогресса
```python
def update_progress_bar(progress):
    progress_bar.width = int(200 * progress)

class ProgressTimer(s.Timer):
    def __init__(self, duration, callback, progress_callback=None):
        super().__init__(duration, callback)
        self.progress_callback = progress_callback
        
    def update(self):
        super().update()
        
        if self.progress_callback and self.active:
            progress = self.progress()
            self.progress_callback(progress)

# Таймер с обновлениями прогресса
timer = ProgressTimer(10.0, game_over, update_progress_bar)
timer.start()
```

### Условные таймеры
```python
class ConditionalTimer(s.Timer):
    def __init__(self, duration, callback, condition):
        super().__init__(duration, callback)
        self.condition = condition
        
    def update(self):
        if self.condition():
            super().update()
        else:
            self.pause()

# Таймер, который работает только когда игрок жив
def player_alive():
    return player.health > 0

conditional_timer = ConditionalTimer(
    5.0, 
    regenerate_health, 
    player_alive
)
conditional_timer.start()
```

### Цепочки таймеров
```python
class TimerChain:
    def __init__(self, timer_configs):
        self.timers = []
        self.current_index = 0
        
        for i, (duration, callback) in enumerate(timer_configs):
            if i == len(timer_configs) - 1:
                # Последний таймер
                timer = s.Timer(duration, callback)
            else:
                # Связать со следующим таймером
                next_callback = timer_configs[i + 1][1]
                timer = s.Timer(duration, lambda: self.next_timer())
            self.timers.append(timer)
            
    def start(self):
        if self.timers:
            self.current_index = 0
            self.timers[0].start()
            
    def next_timer(self):
        self.current_index += 1
        if self.current_index < len(self.timers):
            self.timers[self.current_index].start()
            
    def update(self):
        if self.current_index < len(self.timers):
            self.timers[self.current_index].update()

# Создать последовательность таймеров
sequence = TimerChain([
    (2.0, lambda: print("Фаза 1")),
    (3.0, lambda: print("Фаза 2")),
    (1.0, lambda: print("Фаза 3 завершена"))
])
sequence.start()
```

## Примеры интеграции в игру

### Система перезарядки
```python
class Weapon:
    def __init__(self, cooldown_time):
        self.cooldown_time = cooldown_time
        self.cooldown_timer = s.Timer(cooldown_time)
        self.can_fire = True
        
    def fire(self):
        if self.can_fire:
            # Выстрелить
            self.shoot_projectile()
            
            # Начать перезарядку
            self.can_fire = False
            self.cooldown_timer.reset()
            self.cooldown_timer.start()
            
    def update(self):
        self.cooldown_timer.update()
        
        # Проверить завершение перезарядки
        if self.cooldown_timer.done:
            self.can_fire = True
            
    def get_cooldown_progress(self):
        return self.cooldown_timer.progress()
```

### Длительность усиления
```python
class PowerUp:
    def __init__(self, duration):
        self.active = False
        self.timer = s.Timer(duration, self.deactivate)
        
    def activate(self):
        if not self.active:
            self.active = True
            self.apply_effect()
            self.timer.start()
            
    def deactivate(self):
        self.active = False
        self.remove_effect()
        
    def apply_effect(self):
        player.speed *= 2  # Удвоить скорость
        
    def remove_effect(self):
        player.speed /= 2  # Вернуть к нормальной
        
    def update(self):
        self.timer.update()
```

### Тайминг анимации
```python
class AnimatedSprite(s.Sprite):
    def __init__(self, frames, frame_duration):
        super().__init__(frames[0], size=frames[0].get_size())
        self.frames = frames
        self.current_frame = 0
        
        # Таймер для смены кадров
        self.frame_timer = s.Timer(
            frame_duration,
            self.next_frame,
            repeat=True,
            autostart=True
        )
        
    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.set_image(self.frames[self.current_frame])
        
    def update(self, screen=None):
        super().update(screen)
        self.frame_timer.update()
```

### Тайминг состояний игры
```python
class GameStateManager:
    def __init__(self):
        self.state = "menu"
        self.state_timer = s.Timer(0)
        
    def change_state(self, new_state, duration=None):
        self.state = new_state
        
        if duration:
            self.state_timer = s.Timer(
                duration,
                lambda: self.change_state("menu")
            )
            self.state_timer.start()
            
    def show_game_over(self):
        self.change_state("game_over", 5.0)  # Вернуться в меню через 5 секунд
        
    def update(self):
        self.state_timer.update()
```

## Менеджер таймеров

### Управление несколькими таймерами
```python
class TimerManager:
    def __init__(self):
        self.timers = []
        
    def add_timer(self, timer):
        self.timers.append(timer)
        
    def remove_timer(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)
            
    def update_all(self):
        # Обновить все таймеры
        for timer in self.timers[:]:  # Копия списка для избежания проблем с изменением
            timer.update()
            
            # Удалить завершенные неповторяющиеся таймеры
            if timer.done and not timer.repeat:
                self.timers.remove(timer)
                
    def pause_all(self):
        for timer in self.timers:
            timer.pause()
            
    def resume_all(self):
        for timer in self.timers:
            timer.resume()
            
    def clear_all(self):
        for timer in self.timers:
            timer.stop()
        self.timers.clear()

# Глобальный менеджер таймеров
timer_manager = TimerManager()

# Добавить таймеры
timer_manager.add_timer(spawn_timer)
timer_manager.add_timer(powerup_timer)

# Обновить все таймеры в игровом цикле
timer_manager.update_all()
```

## Соображения производительности

- Таймеры легковесны и эффективны
- Используйте менеджер таймеров для лучшей организации
- Удаляйте завершенные таймеры для предотвращения утечек памяти
- Рассмотрите пул таймеров для часто создаваемых/удаляемых таймеров

## Интеграция с другими компонентами

### С системой анимации
```python
# Временные последовательности анимации
def create_explosion_sequence():
    # Начать анимацию взрыва
    explosion.play_animation("explode")
    
    # Удалить взрыв после анимации
    cleanup_timer = s.Timer(2.0, lambda: explosion.kill())
    cleanup_timer.start()
```

### С системой здоровья
```python
# Таймер регенерации здоровья
def setup_health_regen():
    regen_timer = s.Timer(
        1.0,  # Каждую секунду
        lambda: player.heal(5),
        repeat=True,
        autostart=True
    )
```

## Методы

### Управление
- `start(duration: Optional[float] = None)`: Запустить таймер (можно указать новую длительность)
- `pause()`: Поставить таймер на паузу, сохраняя оставшееся время
- `resume()`: Возобновить таймер с паузы, продолжая с оставшегося времени
- `stop()`: Остановить таймер и пометить как завершенный
- `reset()`: Сбросить состояние таймера
- `update()`: Обновить состояние таймера (вызывать каждый кадр)

### Получение информации
- `time_left() -> float`: Получить оставшееся время до срабатывания (>=0), исключая паузы
- `elapsed() -> float`: Получить прошедшее время с последнего запуска, исключая паузы
- `progress() -> float`: Получить прогресс завершения от 0.0 до 1.0

## Важные нюансы

1. **Независимость от частоты кадров**: Таймер использует `time.monotonic()` для точного времени, независимого от FPS
2. **Пауза сохраняет время**: При паузе сохраняется оставшееся время, которое восстанавливается при возобновлении
3. **Повторение**: При `repeat=True` таймер автоматически перезапускается после срабатывания
4. **Обратные вызовы**: Callback вызывается с аргументами `args` и `kwargs`, переданными в конструктор
5. **Изменение длительности**: Можно изменить длительность при вызове `start(duration=...)`

## Базовое использование

```python
import spritePro as s

# Создать простой таймер
def timer_finished():
    print("Таймер завершен!")

timer = s.Timer(
    duration=3.0,  # 3 секунды
    callback=timer_finished
)

# Запустить таймер
timer.start()

# Обновлять в игровом цикле
timer.update()
```

Для более подробной информации о связанных компонентах см.:
- [Документация по здоровью](health.md) - Тайминг регенерации здоровья
- [Документация по анимации](animation.md) - Тайминг кадров анимации
- [Документация по твинингу](tween.md) - Плавный тайминг анимации
