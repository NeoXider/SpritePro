# Компонент здоровья

`HealthComponent` предоставляет комплексное управление здоровьем для игровых спрайтов, включая урон, лечение, регенерацию и обработку смерти.

## Обзор

HealthComponent — это модульная система, которую можно прикрепить к любому спрайту для добавления функциональности здоровья. Она поддерживает обратные вызовы урона, события смерти и лечение.

## Основные возможности

- **Управление здоровьем**: Отслеживание текущего и максимального здоровья
- **Система урона**: Получение урона с настраиваемыми обратными вызовами
- **Система лечения**: Восстановление здоровья с ограничениями и обратными вызовами
- **Обработка смерти**: Автоматическое обнаружение смерти и обратные вызовы
- **Перегрузка операторов**: Использование операторов +, -, ==, <, > для операций со здоровьем

## Параметры конструктора

- `max_health` (int): Максимальные очки здоровья. По умолчанию: 100
- `current_health` (int, опционально): Начальное здоровье. По умолчанию: max_health

## Операции со здоровьем

### Базовое управление здоровьем
```python
# Установить значения здоровья
health.current_health = 75
health.max_health = 150

# Получить информацию о здоровье
current = health.current_health
maximum = health.max_health
is_alive = health.is_alive

# Проверить статус
is_alive = health.is_alive
is_full_health = (health.current_health == health.max_health)
```

### Система урона
```python
# Получить урон
health.take_damage(30)

# Получить урон с информацией об источнике
health.take_damage(20, damage_source="fire")

# Проверить, был ли урон действительно применен
damage_applied = health.take_damage(50)
if damage_applied:
    print("Урон был применен")
```

### Система лечения
```python
# Вылечить урон
health.heal(25)

# Вылечить с максимальным ограничением
health.heal(100)  # Не превысит max_health

# Проверить, было ли лечение применено
healing_applied = health.heal(30)
if healing_applied:
    print("Лечение было применено")
```

## Обратные вызовы и события

### Обратные вызовы урона
```python
def on_damage(health_component, damage_amount, new_health):
    print(f"Получено {damage_amount} урона! Здоровье: {new_health}")
    
    # Визуальная обратная связь
    sprite.set_color((255, 100, 100))  # Красная вспышка
    
    # Звуковой эффект
    play_sound("hit.wav")

health.set_damage_callback(on_damage)
```

### Обратные вызовы смерти
```python
def on_death(health_component):
    print("Сущность умерла!")
    
    # Анимация смерти
    sprite.play_animation("death")
    
    # Удалить из игры
    sprite.set_active(False)

health.set_death_callback(on_death)
```

### Обратные вызовы лечения
```python
def on_heal(health_component, heal_amount, new_health):
    print(f"Вылечено {heal_amount} HP! Здоровье: {new_health}")
    
    # Визуальная обратная связь
    sprite.set_color((100, 255, 100))  # Зеленая вспышка

health.set_heal_callback(on_heal)
```

## Система регенерации

### Базовая регенерация
```python
# Включить регенерацию здоровья
health.enable_regeneration(
    regen_rate=2,        # 2 HP в секунду
    regen_delay=3.0,     # Ждать 3 секунды после урона
    max_regen_health=80  # Регенерировать только до 80% от максимального здоровья
)

# Выключить регенерацию
health.disable_regeneration()

# Проверить статус регенерации
if health.is_regenerating():
    print("В настоящее время регенерируется здоровье")
```

### Продвинутая регенерация
```python
# Регенерация с пользовательскими условиями
def can_regenerate():
    return not player.in_combat and player.is_resting

health.set_regeneration_condition(can_regenerate)

# Обратные вызовы регенерации
def on_regen_start():
    print("Началась регенерация здоровья")

def on_regen_stop():
    print("Остановлена регенерация здоровья")

health.set_regen_start_callback(on_regen_start)
health.set_regen_stop_callback(on_regen_stop)
```

## Система неуязвимости

### Базовая неуязвимость
```python
# Сделать неуязвимым на 2 секунды
health.set_invincible(duration=2.0)

# Проверить статус неуязвимости
if health.is_invincible():
    print("В настоящее время неуязвим")

# Получить оставшееся время неуязвимости
time_left = health.get_invincibility_time_left()
```

### Неуязвимость с визуальными эффектами
```python
def apply_invincibility_effect():
    if health.is_invincible():
        # Эффект мигания
        alpha = 128 if (time.time() * 10) % 2 < 1 else 255
        sprite.set_alpha(alpha)
    else:
        sprite.set_alpha(255)

# Вызвать в цикле обновления
apply_invincibility_effect()
```

## Продвинутые возможности

### Модификаторы здоровья
```python
# Временные модификаторы здоровья
class HealthModifier:
    def __init__(self, multiplier, duration):
        self.multiplier = multiplier
        self.duration = duration
        self.start_time = time.time()
    
    def is_active(self):
        return time.time() - self.start_time < self.duration
    
    def apply_damage(self, damage):
        return damage * self.multiplier

# Добавить сопротивление урону
resistance_modifier = HealthModifier(0.5, 10.0)  # 50% урона на 10 секунд
health.add_modifier(resistance_modifier)
```

### Зоны здоровья
```python
# Разное поведение в зависимости от процента здоровья
def update_health_effects():
    health_percent = health.get_health_percentage()
    
    if health_percent > 0.75:
        # Высокое здоровье - нормальное состояние
        sprite.set_color(None)
    elif health_percent > 0.25:
        # Среднее здоровье - желтая тонировка
        sprite.set_color((255, 255, 100))
    else:
        # Низкое здоровье - красная тонировка и тряска экрана
        sprite.set_color((255, 100, 100))
        screen.shake(intensity=2)
```

### Барьеры здоровья
```python
# Система щита/барьера
class HealthBarrier:
    def __init__(self, barrier_health):
        self.barrier_health = barrier_health
        self.max_barrier = barrier_health
    
    def absorb_damage(self, damage):
        absorbed = min(damage, self.barrier_health)
        self.barrier_health -= absorbed
        return damage - absorbed  # Оставшийся урон

# Добавить барьер к компоненту здоровья
barrier = HealthBarrier(50)
health.add_barrier(barrier)
```

## Примеры интеграции

### Со Sprite
```python
class Player(s.Sprite):
    def __init__(self):
        super().__init__("player.png")
        
        # Добавить компонент здоровья
        self.health_component = s.HealthComponent(max_health=100)
        
        # Настроить обратные вызовы здоровья
        self.health_component.set_damage_callback(self.on_damage)
        self.health_component.set_death_callback(self.on_death)
        
        # Включить регенерацию
        self.health_component.enable_regeneration(
            regen_rate=1,
            regen_delay=5.0
        )
    
    def on_damage(self, health_comp, damage, new_health):
        # Тряска экрана при уроне
        screen.shake(intensity=damage / 10)
        
        # Кадры неуязвимости
        self.health_component.set_invincible(1.0)
    
    def on_death(self, health_comp):
        # Конец игры
        game.show_game_over_screen()
```

### UI полосы здоровья
```python
class HealthBar:
    def __init__(self, health_component, pos, size):
        self.health_component = health_component
        self.pos = pos
        self.size = size
    
    def draw(self, screen):
        # Фон
        bg_rect = pygame.Rect(self.pos, self.size)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect)
        
        # Полоса здоровья
        health_percent = self.health_component.get_health_percentage()
        health_width = int(self.size[0] * health_percent)
        health_rect = pygame.Rect(self.pos, (health_width, self.size[1]))
        
        # Цвет в зависимости от здоровья
        if health_percent > 0.6:
            color = (100, 255, 100)  # Зеленый
        elif health_percent > 0.3:
            color = (255, 255, 100)  # Желтый
        else:
            color = (255, 100, 100)  # Красный
            
        pygame.draw.rect(screen, color, health_rect)
```

## Соображения производительности

- Компоненты здоровья легковесны и эффективны
- Регенерация использует delta time для независимости от частоты кадров
- Обратные вызовы опциональны и вызываются только при необходимости
- Отслеживание неуязвимости оптимизировано для частых проверок

## Сводка событий

- `on_damage`: Вызывается при получении урона
- `on_heal`: Вызывается при восстановлении здоровья
- `on_death`: Вызывается при достижении здоровья нуля
- `on_regen_start`: Вызывается при начале регенерации
- `on_regen_stop`: Вызывается при окончании регенерации

## Базовое использование

```python
import spritePro as s

# Создать компонент здоровья
health = s.HealthComponent(max_health=100)

# Получить урон
health.take_damage(25)

# Вылечить урон
health.heal(10)

# Проверить статус
if health.is_alive():
    print(f"Здоровье: {health.current_health}/{health.max_health}")
```

Для получения дополнительной информации о связанных системах см.:
- [Документация Sprite](sprite.md) - Интеграция здоровья
- [Компонент таймера](timer.md) - Для тайминга, связанного со здоровьем
- [Компонент анимации](animation.md) - Для анимаций на основе здоровья
