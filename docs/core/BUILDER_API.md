# 🏗 Builder API — Fluent API для спрайтов и частиц

**Полное руководство по Builder Pattern в SpritePro v3.4.0**

---

## 🎯 Обзор

Builder API позволяет создавать спрайты и частицы с помощью **Fluent Interface** (потоковый интерфейс), что делает код читаемым и выразительным:

```python
# Вместо этого (старый стиль):
sprite = Sprite("player.png", (50, 50), s.WH_C)
sprite.set_position(100, 200)
sprite.set_scale(1.5)
sprite.set_color(255, 0, 0)

# Используем Builder API:
sprite = s.sprite("player.png").position(100, 200).scale(1.5).color(255, 0, 0).build()
```

---

## 📦 SpriteBuilder — создание спрайтов

### Базовое использование

```python
import spritePro as s

# Простой спрайт с позицией и размером
sprite = s.sprite("player.png").position(100, 200).size((50, 50)).build()

# Спрайт с цветом и прозрачностью
sprite = s.sprite("enemy.png") \
    .position(300, 400) \
    .color(255, 100, 50) \
    .alpha(0.7) \
    .build()

# Спрайт с масштабированием
sprite = s.sprite("boss.png") \
    .position(s.WH_C) \
    .scale(2.0) \
    .build()
```

### Методы Builder API

#### 1. Позиционирование
```python
# Установить позицию
sprite = s.sprite().position(x, y).build()

# Относительная позиция (от центра экрана)
sprite = s.sprite().center(s.WH_C).build()

# Привязка к краям экрана
sprite = s.sprite().top_left((100, 50)).build()
sprite = s.sprite().bottom_right((700, 550)).build()
```

#### 2. Размер и масштаб
```python
# Установить размер (ширина, высота)
sprite = s.sprite().size(50, 100).build()

# Масштабирование (float или tuple)
sprite = s.sprite().scale(1.5).build()           # Равномерный масштаб
sprite = s.sprite().scale((2.0, 0.5)).build()    # Разный масштаб по осям

# Комбинация размера и масштаба
sprite = s.sprite().size(50, 50).scale(2.0).build()
```

#### 3. Цвет и прозрачность
```python
# RGB цвет (0-255)
sprite = s.sprite().color(255, 0, 0).build()     # Красный
sprite = s.sprite().color((100, 200, 50)).build()

# Прозрачность (alpha) 0.0-1.0
sprite = s.sprite().alpha(0.5).build()           # Полупрозрачный

# Комбинация цвета и прозрачности
sprite = s.sprite().color(255, 255, 255).alpha(0.8).build()
```

#### 4. Обрезка изображения (crop)
```python
# Обрезать часть изображения
sprite = s.sprite("character.png") \
    .crop(left=10, top=20, width=50, height=30) \
    .position(100, 200) \
    .build()

# Обрезка для спрайтовых анимаций
sprite = s.sprite("sheet.png") \
    .crop(0, 0, 64, 64)  # Первый кадр 64x64
    .position(100, 200) \
    .build()
```

#### 5. Скругление углов (border radius)
```python
# Скруглить все углы
sprite = s.sprite("box.png") \
    .border_radius(10) \
    .position(100, 200) \
    .build()

# Разное скругление для каждого угла
sprite = s.sprite("panel.png") \
    .border_radius(top_left=5, top_right=10, bottom_left=10, bottom_right=5) \
    .position(100, 200) \
    .build()
```

#### 6. Маска коллизий (collision mask)
```python
# Создать спрайт с маской для физики
sprite = s.sprite("player.png") \
    .position(100, 200) \
    .mask()  # Автоматически создаёт маску по контуру изображения
    .build()

# Маска с заданным радиусом (для круглых объектов)
sprite = s.sprite("orb.png") \
    .position(300, 400) \
    .mask(radius=25)  # Радиус маски
    .build()
```

#### 7. Сцена и родитель
```python
# Добавить в сцену при создании
sprite = s.sprite("player.png") \
    .position(100, 200) \
    .scene(main_scene) \
    .build()

# Установить родителя (для иерархии спрайтов)
parent = s.Sprite("", (50, 50), s.WH_C, scene=scene)
child = s.sprite("enemy.png") \
    .position(100, 100) \
    .parent(parent) \
    .build()
```

---

## 🎆 ParticleBuilder — создание частиц

### Базовое использование

```python
import spritePro as s

# Простой эмиттер частиц
emitter = s.particles() \
    .amount(50) \
    .lifetime(1.0) \
    .speed(100, 200) \
    .position(s.WH_C) \
    .build()

# Частицы с гравитацией
emitter = s.particles() \
    .amount(100) \
    .lifetime(2.0) \
    .speed(50, 150) \
    .gravity(0, 300)  # Гравитация вниз
    .position(s.WH_C) \
    .build()
```

### Методы Builder API

#### 1. Количество частиц
```python
# Установить количество
emitter = s.particles().amount(50).build()

# Динамическое изменение количества
emitter.set_amount(100)  # Увеличить до 100 частиц
```

#### 2. Время жизни
```python
# В секундах
emitter = s.particles().lifetime(1.5).build()

# В миллисекундах (автоматическое преобразование)
emitter = s.particles().lifetime(1500).build()  # 1500ms = 1.5s

# Диапазон времени жизни (случайное значение)
emitter = s.particles().lifetime_range(0.5, 2.0).build()
```

#### 3. Скорость вылета
```python
# Минимальная и максимальная скорость
emitter = s.particles().speed(100, 300).build()

# Вектор скорости (x, y)
emitter = s.particles().velocity((50, -100)).build()

# Диапазон скоростей
emitter = s.particles().speed_range(50, 200).build()
```

#### 4. Гравитация
```python
# Стандартная гравитация вниз
emitter = s.particles().gravity(0, 300).build()

# Гравитация в другую сторону (вверх)
emitter = s.particles().gravity(0, -200).build()

# Наклонная гравитация
emitter = s.particles().gravity((100, 150)).build()
```

#### 5. Угол вылета
```python
# Во все стороны (360°)
emitter = s.particles().angle_range(0, 360).build()

# В одну сторону (конус)
emitter = s.particles().angle_range(-45, 45).build()

# Точный угол
emitter = s.particles().angle(90).build()  # 90°
```

#### 6. Размер частиц
```python
# Фиксированный размер
emitter = s.particles().size(10).build()

# Диапазон размеров
emitter = s.particles().size_range(5, 20).build()

# Изменение размера со временем (scale over lifetime)
emitter = s.particles().size_over_lifetime((1.0, 0.0)).build()
```

#### 7. Цвет частиц
```python
# Фиксированный цвет
emitter = s.particles().color(255, 255, 0).build()

# Диапазон цветов (HSL)
emitter = s.particles().hue_range(0, 360).build()

# Градиент цвета
emitter = s.particles().color_over_lifetime((255, 0, 0), (0, 0, 255)).build()
```

#### 8. Автоэмиссия
```python
# Автоматически выпускать частицы при создании
emitter = s.particles() \
    .amount(100) \
    .lifetime(1.0) \
    .auto_emit()  # Эмиттирует сразу после build()
    .build()

# Автоэмиссия с задержкой
emitter = s.particles() \
    .amount(50) \
    .lifetime(2.0) \
    .auto_emit(delay=0.5)  # Задержка 0.5 сек перед эмиссией
    .build()
```

---

## 🎨 Готовые шаблоны (Templates)

### Шаблоны частиц

```python
import spritePro as s

# Искры
spark_emitter = s.particles(template_sparks) \
    .position(s.WH_C) \
    .build()

# Дым
smoke_emitter = s.particles(template_smoke) \
    .position(400, 300) \
    .build()

# Огонь
fire_emitter = s.particles(template_fire) \
    .position(s.WH_C) \
    .build()

# Снег
snow_emitter = s.particles(template_snowfall) \
    .position(s.WH_C) \
    .build()

# Круговой взрыв
circular_burst = s.particles(template_circular_burst) \
    .amount(100) \
    .speed_range(200, 400) \
    .position(s.WH_C) \
    .build()

# След (trail)
trail_emitter = s.particles(template_trail) \
    .lifetime(0.5) \
    .size_range(3, 8) \
    .position(player_pos) \
    .auto_emit() \
    .build()
```

### Кастомизация шаблонов

```python
# Изменить параметры шаблона
custom_fire = s.particles(template_fire) \
    .amount(200)  # Увеличить количество
    .lifetime_range(0.3, 1.5)  # Изменить время жизни
    .speed_range(100, 300)  # Изменить скорость
    .color(255, 150, 50)  # Оранжевый цвет
    .position(s.WH_C) \
    .build()
```

---

## 🔄 Динамическое управление

### Изменение параметров во время runtime

```python
# Создать эмиттер
emitter = s.particles() \
    .amount(50) \
    .lifetime(1.0) \
    .speed(100, 200) \
    .position(s.WH_C) \
    .build()

# Изменить количество частиц
emitter.set_amount(100)

# Изменить время жизни
emitter.set_lifetime(2.0)

# Изменить скорость
emitter.set_speed_range(50, 300)

# Изменить гравитацию
emitter.set_gravity((0, 400))

# Переместить позицию эмиссии
emitter.set_position(new_x, new_y)
```

### Остановка и перезапуск

```python
# Остановить эмиттер
emitter.stop()

# Перезапустить с новыми параметрами
emitter.restart(amount=100, lifetime=2.0)

# Полностью очистить частицы
emitter.clear()
```

---

## 🎯 Примеры использования

### 1. Эффект взрыва
```python
import spritePro as s

class ExplosionScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Создать эмиттер для взрыва
        self.explosion = s.particles() \
            .amount(100) \
            .lifetime_range(0.5, 1.5) \
            .speed_range(200, 400) \
            .angle_range(0, 360) \
            .gravity((0, 200)) \
            .color_range(255, 200, 50) \
            .position(s.WH_C) \
            .build()
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            # Взрыв в центре экрана
            self.explosion.emit(s.WH_C)

s.run(scene=ExplosionScene, size=(800, 600))
```

### 2. Частицы следа (trail)
```python
import spritePro as s

class TrailScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        self.player = s.Sprite("", (50, 50), s.WH_C, scene=self)
        
        # След за игроком
        self.trail = s.particles() \
            .amount(20) \
            .lifetime_range(0.3, 0.8) \
            .speed_range(10, 50) \
            .size_range(3, 8) \
            .color(255, 255, 255) \
            .auto_emit() \
            .build()
    
    def update(self, dt):
        self.player.handle_keyboard_input()
        
        # Обновлять позицию следа
        if self.player.velocity.length() > 10:
            pos = self.player.get_world_position()
            self.trail.set_position(pos)

s.run(scene=TrailScene, size=(800, 600))
```

### 3. Дождь
```python
import spritePro as s

class RainScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Дождь
        self.rain = s.particles(template_snowfall) \
            .amount(500) \
            .lifetime_range(2.0, 4.0) \
            .speed_range(100, 300) \
            .angle_range(85, 95)  # Небольшой наклон
            .color(150, 150, 200) \
            .size(2) \
            .position(s.WH_C) \
            .auto_emit() \
            .build()
    
    def update(self, dt):
        # Интенсивность дождя от времени
        intensity = (s.get_time() % 10) / 10
        self.rain.set_amount(int(200 + intensity * 300))

s.run(scene=RainScene, size=(800, 600), fill_color=(50, 50, 80))
```

### 4. Огонь камина
```python
import spritePro as s

class FirePlaceScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Основной огонь
        self.fire = s.particles(template_fire) \
            .amount(50) \
            .lifetime_range(0.5, 1.5) \
            .speed_range(50, 150) \
            .angle_range(-30, 30)  # Вверх
            .color_range(255, 150, 50) \
            .position(s.WH_C) \
            .auto_emit() \
            .build()
    
    def update(self, dt):
        # Анимация огня (пульсация)
        pulse = 0.8 + 0.2 * s.get_time() % 1
        self.fire.set_amount(int(40 + pulse * 20))

s.run(scene=FirePlaceScene, size=(800, 600), fill_color=(30, 20, 10))
```

---

## 🎨 Продвинутые техники

### 1. Пул частиц (Particle Pool)
```python
import spritePro as s

class ParticlePoolScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Создать пул эмиттеров
        self.emitters = []
        for i in range(10):
            emitter = s.particles() \
                .amount(30) \
                .lifetime_range(0.5, 1.0) \
                .speed_range(100, 200) \
                .position((i * 80 + 40, 300)) \
                .build()
            self.emitters.append(emitter)
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            # Эмитировать все частицы
            for emitter in self.emitters:
                emitter.emit()

s.run(scene=ParticlePoolScene, size=(800, 600))
```

### 2. Частицы с физикой
```python
import spritePro as s

class PhysicsParticlesScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        # Частицы с гравитацией и отскоком
        self.particles = s.particles() \
            .amount(100) \
            .lifetime_range(2.0, 4.0) \
            .speed_range(50, 150) \
            .gravity((0, 300))  # Гравитация
            .bounce(0.7)  # Отскок 70%
            .position(s.WH_C) \
            .build()
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            self.particles.emit()

s.run(scene=PhysicsParticlesScene, size=(800, 600))
```

### 3. Цветовые эффекты на частицах
```python
import spritePro as s
import colorsys

class RainbowParticlesScene(s.Scene):
    def __init__(self):
        super().__init__()
        
        self.particles = s.particles() \
            .amount(100) \
            .lifetime_range(1.0, 2.0) \
            .speed_range(100, 300) \
            .position(s.WH_C) \
            .build()
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            # Радужный цвет
            hue = (s.get_time() * 0.1) % 1
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            self.particles.set_color(int(r*255), int(g*255), int(b*255))
        
        # Эмитировать частицы
        if s.input.is_pressed(s.pygame.K_lshift):
            self.particles.emit()

s.run(scene=RainbowParticlesScene, size=(800, 600))
```

---

## 📊 Производительность и оптимизация

### Object Pooling для частиц
```python
import spritePro as s
from spritePro.utils.pool import ObjectPool

class OptimizedParticlesScene(s.Scene):
    def __init__(self):
        super().__init()
        
        # Пул эмиттеров для эффективности
        self.emitter_pool = ObjectPool(
            factory=lambda: s.particles() \
                .amount(50) \
                .lifetime_range(0.5, 1.5) \
                .build(),
            pool_size=20
        )
    
    def update(self, dt):
        if s.input.was_pressed(s.pygame.K_SPACE):
            # Получить эмиттер из пула
            emitter = self.emitter_pool.get()
            emitter.emit()
            
            # Вернуть в пул после завершения
            emitter.on_complete(lambda: self.emitter_pool.put(emitter))

s.run(scene=OptimizedParticlesScene, size=(800, 600))
```

### Оптимизация количества частиц
```python
# Ограничить максимальное количество активных частиц
emitter = s.particles() \
    .amount(100) \
    .max_active_particles(50)  # Максимум 50 одновременно
    .build()

# Использовать пул для повторного использования
emitter.use_pool(True).build()
```

---

## 🎯 Best Practices

### ✅ Делать:
- Использовать шаблоны для стандартных эффектов (искры, дым, огонь)
- Ограничивать количество частиц для производительности
- Использовать Object Pooling для частых эмиссий
- Применять `lifetime_range` для естественного разнообразия
- Комбинировать гравитацию и скорость для реалистичных эффектов

### ❌ Избегать:
- Слишком большого количества частиц (>500 на экран)
- Длительного времени жизни (>5 сек) без оптимизации
- Частых изменений параметров во время runtime
- Создания новых эмиттеров каждый кадр (использовать пулы)

---

## 🔍 Поиск по документации

| Фича | Документация |
|------|--------------|
| Базовое создание спрайтов | [SpriteBuilder](#spritebuilder---создание-спрайтов) |
| Создание частиц | [ParticleBuilder](#particlebuilder---создание-частиц) |
| Готовые шаблоны | [Templates](#готовые-шаблоны-templates) |
| Динамическое управление | [Runtime Management](#динамическое-управление) |
| Примеры эффектов | [Examples](#примеры-использования) |
| Оптимизация | [Performance](#производительность-и-оптимизация) |

---

<div align="center">

**🎮 Готовы к практике?**  
Запустите [builder_demo.py](../spritePro/demoGames/builder_demo.py) для просмотра примеров!

</div>
