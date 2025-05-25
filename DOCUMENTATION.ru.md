# Документация spritePro

[English version](DOCUMENTATION.md)

## Содержание
1. [Инициализация и настройка](#инициализация-и-настройка)
2. [Основные классы](#основные-классы)
3. [Компоненты](#компоненты)
4. [Утилиты](#утилиты)
5. [Лучшие практики](#лучшие-практики)

## Инициализация и настройка

### Инициализация
```python
import spritePro

# Инициализация библиотеки
spritePro.init()

# Создание окна
spritePro.get_screen((800, 600), "Моя игра")
```

### Основные константы
- `spritePro.WH_CENTER`: Координаты центра экрана
- `spritePro.screen`: Основная поверхность окна
- `spritePro.clock`: Объект для контроля FPS

## Основные классы

### Sprite
Базовый класс для всех спрайтов.

#### Свойства
- `auto_flip` (bool): Автоматически отражать спрайт по горизонтали при движении влево/вправо
- `stop_threshold` (float): Порог расстояния для остановки движения
- `color` (Tuple[int, int, int]): Текущий цветовой оттенок
- `active` (bool): Активен ли спрайт и должен ли отображаться
- `size` (tuple): Размеры спрайта (ширина, высота)
- `start_pos` (tuple): Начальная позиция (x, y)
- `velocity` (Vector2): Текущий вектор скорости
- `speed` (float): Базовая скорость движения
- `flipped_h` (bool): Отражен ли спрайт по горизонтали
- `flipped_v` (bool): Отражен ли спрайт по вертикали
- `angle` (float): Текущий угол поворота
- `scale` (float): Текущий масштаб
- `alpha` (int): Текущая прозрачность (0-255)
- `state` (str): Текущее состояние ("idle", "moving", "hit", "attacking", "dead")
- `states` (set): Доступные состояния
- `mask` (pygame.mask.Mask): Маска коллизии

#### Методы
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0)`: Инициализация нового спрайта
- `set_color(color: Tuple)`: Установка цветового оттенка
- `set_image(image_source: Union[str, Path, pygame.Surface], size: Optional[Tuple[int, int]] = None)`: Установка нового изображения
- `set_native_size()`: Сброс спрайта к оригинальным размерам изображения
- `update(window: pygame.Surface)`: Обновление состояния и отрисовка спрайта
- `_update_image()`: Обновление изображения спрайта со всеми визуальными эффектами
- `set_active(active: bool)`: Установка активного состояния спрайта
- `reset_sprite()`: Сброс спрайта в начальную позицию и состояние
- `move(dx: float, dy: float)`: Перемещение спрайта на указанное расстояние
- `move_towards(target_pos: Tuple[float, float], speed: Optional[float] = None)`: Движение к цели
- `set_velocity(vx: float, vy: float)`: Прямая установка скорости
- `move_up(speed: Optional[float] = None)`: Движение вверх
- `move_down(speed: Optional[float] = None)`: Движение вниз
- `move_left(speed: Optional[float] = None)`: Движение влево
- `move_right(speed: Optional[float] = None)`: Движение вправо
- `handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT)`: Обработка ввода с клавиатуры
- `stop()`: Остановка движения
- `rotate_to(angle: float)`: Поворот на указанный угол
- `rotate_by(angle_change: float)`: Поворот на относительный угол
- `set_scale(scale: float)`: Установка масштаба
- `set_alpha(alpha: int)`: Установка прозрачности
- `fade_by(amount: int, min_alpha: int = 0, max_alpha: int = 255)`: Изменение прозрачности на указанную величину
- `scale_by(amount: float, min_scale: float = 0.0, max_scale: float = 2.0)`: Изменение масштаба на указанную величину
- `distance_to(other_sprite) -> float`: Расчет расстояния до другого спрайта
- `set_state(state: str)`: Установка текущего состояния
- `is_in_state(state: str) -> bool`: Проверка текущего состояния
- `is_visible_on_screen(screen: pygame.Surface) -> bool`: Проверка видимости на экране
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Ограничение движения в пределах границ
- `play_sound(sound_file: str)`: Воспроизведение звукового эффекта

Пример использования:
```python
# Создание спрайта
sprite = Sprite("sprite.png", size=(100, 100), pos=(400, 300), speed=5)

# Установка цветового оттенка
sprite.set_color((255, 0, 0))  # Красный оттенок

# Движение
sprite.move_towards((500, 400))  # Движение к точке
sprite.set_velocity(2, 0)  # Движение вправо со скоростью 2

# Визуальные эффекты
sprite.set_scale(1.5)  # Увеличение на 50%
sprite.set_alpha(128)  # Прозрачность 50%
sprite.rotate_by(45)  # Поворот на 45 градусов

# Управление состоянием
sprite.set_state("moving")
if sprite.is_in_state("moving"):
    print("Спрайт движется")

# Ограничение движения
sprite.limit_movement(screen.get_rect(), padding=10)  # Держаться в 10px от краев экрана
```

### GameSprite
Расширяет базовый класс Sprite для игровых объектов с управлением здоровьем и обработкой столкновений.

#### Свойства
- `collision_step` (int): Шаг разрешения столкновений (по умолчанию: 1)
- `health_component` (HealthComponent): Управляет функциональностью здоровья
- `on_collision` (Optional[Callable]): Обработчик событий столкновения
- `_user_on_death_callback` (Optional[Callable]): Пользовательский обработчик смерти

#### Методы
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, max_health: int = 100, current_health: Optional[int] = None)`: Инициализация игрового спрайта с управлением здоровьем
- `_handle_damage_state(amount: float)`: Внутренний обработчик событий получения урона
- `_handle_death_event(dead_sprite: Sprite)`: Внутренний обработчик событий смерти
- `on_collision_event(callback: Callable)`: Установка обработчика событий столкновения
- `on_death_event(callback: Callable[["GameSprite"], None])`: Установка обработчика событий смерти
- `collide_with(other_sprite) -> bool`: Проверка столкновения с другим спрайтом с использованием пиксельно-точных масок
- `collide_with_group(group: pygame.sprite.Group) -> List`: Проверка столкновения с группой спрайтов
- `collide_with_tag(group: pygame.sprite.Group, tag: str) -> List`: Проверка столкновения с помеченными спрайтами
- `_get_collision_side(prev_x: float, prev_y: float, rect: pygame.Rect) -> str`: Определение стороны столкновения
- `resolve_collisions(*obstacles) -> List[Tuple[pygame.Rect, str]]`: Разрешение столкновений с препятствиями

#### Управление здоровьем
Класс GameSprite включает систему здоровья со следующими возможностями:
- Отслеживание максимального и текущего здоровья
- Функциональность получения урона и лечения
- Обработка событий смерти
- Управление состоянием при получении урона/смерти

Пример использования:
```python
# Создание игрового спрайта с здоровьем
player = GameSprite("player.png", max_health=100)

def on_death(sprite):
    print(f"{sprite} умер!")

def on_collision():
    print("Обнаружено столкновение!")

# Настройка обработчиков
player.on_death_event(on_death)
player.on_collision_event(on_collision)

# Управление здоровьем
player.health_component.take_damage(50)  # Уменьшить здоровье на 50
player.health_component.heal(20)  # Восстановить 20 здоровья

# Обнаружение столкновений
if player.collide_with(enemy):
    print("Попал по врагу!")

# Разрешение столкновений
player.resolve_collisions(obstacles)
```

### PhysicSprite
Спрайт с поддержкой физики, включая гравитацию, отскок и обработку столкновений. Расширяет GameSprite возможностями физической симуляции.

#### Свойства
- `jump_force` (float): Сила прыжка в м/с (по умолчанию: 7)
- `MAX_STEPS` (int): Максимальное количество шагов физики за кадр (по умолчанию: 8)
- `mass` (float): Масса в кг
- `gravity` (float): Сила гравитации в м/с²
- `bounce_enabled` (bool): Включен ли отскок
- `is_grounded` (bool): Касается ли спрайт земли
- `ground_friction` (float): Коэффициент трения при касании земли
- `min_velocity_threshold` (float): Минимальный порог скорости для остановки
- `position` (Vector2): Позиция в метрах
- `velocity` (Vector2): Скорость в м/с
- `force` (Vector2): Текущий вектор силы
- `acceleration` (Vector2): Текущий вектор ускорения

#### Методы
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 5, health: int = 100, mass: float = 1.0, gravity: float = 9.8, bounce_enabled: bool = False)`: Инициализирует спрайт с поддержкой физики
- `apply_force(force: pygame.math.Vector2)`: Применяет вектор силы к спрайту
- `bounce(normal: pygame.math.Vector2)`: Обрабатывает отскок от поверхности
- `update_physics(fps: float, collisions_enabled: bool = True)`: Обновляет физику спрайта
- `update(window: pygame.Surface)`: Отрисовывает спрайт без обновления физики
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Ограничивает движение в пределах границ с поддержкой отскока
- `handle_keyboard_input(keys=None, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT, up_key=pygame.K_UP)`: Обрабатывает ввод с клавиатуры для движения на основе физики
- `jump(jump_force: float)`: Применяет силу прыжка, если спрайт на земле
- `force_in_direction(direction: pygame.math.Vector2, force: float)`: Применяет силу в указанном направлении
- `_check_grounded(rects)`: Внутренний метод для проверки касания земли
- `resolve_collisions(*obstacles, fps=60, limit_top=True, limit_bottom=True, limit_left=True, limit_right=True)`: Разрешает столкновения с препятствиями

#### Физическая система
Класс PhysicSprite реализует физическую систему со следующими возможностями:
- Реальные единицы измерения (метры, м/с, м/с²)
- Гравитация и определение касания земли
- Применение сил и ускорение
- Механика отскока
- Трение о землю
- Разрешение столкновений

Пример использования:
```python
# Создаем спрайт с поддержкой физики
player = PhysicSprite(
    "player.png",
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# В игровом цикле:
while True:
    # Обработка ввода
    player.handle_keyboard_input()
    
    # Обновление физики
    player.update_physics(60)  # 60 FPS
    
    # Ограничение движения в пределах экрана
    player.limit_movement(screen.get_rect())
    
    # Отрисовка
    player.update(screen)
    
    # Применение сил
    player.apply_force(pygame.math.Vector2(0, -9.8))  # Гравитация
    
    # Прыжок
    if player.is_grounded:
        player.jump(7)  # Прыжок с силой 7 м/с
```

## Компоненты

### Text
Спрайт для отображения текста со всеми базовыми механиками Sprite. Расширяет базовый функционал Sprite для работы с текстом, сохраняя основные возможности спрайта.

#### Свойства
- `text` (str): Отображаемый текст
- `color` (Tuple[int, int, int]): Цвет текста в формате RGB
- `font_size` (int): Размер шрифта в пунктах
- `font_path` (Optional[Union[str, Path]]): Путь к файлу шрифта .ttf или None для системного шрифта

#### Методы
- `__init__(text: str, font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255), pos: Tuple[int, int] = (0, 0), font_name: Optional[Union[str, Path]] = None, speed: float = 0, **sprite_kwargs)`: Инициализирует текстовый спрайт
- `input(k_delete: pygame.key = pygame.K_ESCAPE) -> str`: Обрабатывает ввод текста с клавиатуры
- `set_text(new_text: str = None)`: Обновляет текст спрайта и перерисовывает изображение
- `set_color(new_color: Tuple[int, int, int])`: Обновляет цвет текста и перерисовывает изображение
- `set_font(font_name: Optional[Union[str, Path]], font_size: int)`: Устанавливает шрифт и размер, затем отрисовывает текст

Пример использования:
```python
# Создание текстового спрайта
text = TextSprite(
    text="Привет мир",
    font_size=32,
    color=(255, 255, 255),
    pos=(400, 300)
)

# Обновление текста
text.text = "Новый текст"

# Изменение цвета
text.set_color((255, 0, 0))

# Обработка ввода с клавиатуры
text.input()  # Позволяет вводить текст с backspace и escape для очистки
```

### Button
Интерактивная кнопка пользовательского интерфейса.

#### Свойства
- `text` (str): Текст кнопки
- `pos` (Tuple[int, int]): Позиция (x, y)
- `size` (Tuple[int, int]): Размер (ширина, высота)
- `is_hovered` (bool): Наведена ли мышь
- `is_pressed` (bool): Нажата ли кнопка
- `color` (Tuple[int, int, int]): Цвет кнопки
- `hover_color` (Tuple[int, int, int]): Цвет при наведении
- `press_color` (Tuple[int, int, int]): Цвет при нажатии
- `text_color` (Tuple[int, int, int]): Цвет текста
- `font_size` (int): Размер шрифта
- `border_radius` (int): Радиус скругления углов
- `padding` (int): Внутренний отступ

#### Методы
- `__init__(text: str, pos: Tuple[int, int], size: Tuple[int, int], color: Tuple[int, int, int] = (100, 100, 100), hover_color: Tuple[int, int, int] = (150, 150, 150), press_color: Tuple[int, int, int] = (50, 50, 50), text_color: Tuple[int, int, int] = (255, 255, 255), font_size: int = 24, border_radius: int = 10, padding: int = 10)`: Инициализирует кнопку
- `on_click(callback: Callable)`: Устанавливает обработчик клика
- `on_hover(callback: Callable)`: Устанавливает обработчик наведения
- `on_press(callback: Callable)`: Устанавливает обработчик нажатия
- `on_release(callback: Callable)`: Устанавливает обработчик отпускания
- `update()`: Обновляет состояние кнопки
- `draw(surface: pygame.Surface)`: Отрисовывает кнопку на поверхности

Пример:
```python
button = spritePro.Button(
    text="Нажми меня",
    pos=(400, 300),
    size=(200, 50),
    color=(100, 100, 100),
    hover_color=(150, 150, 150),
    press_color=(50, 50, 50),
    text_color=(255, 255, 255),
    font_size=24,
    border_radius=10,
    padding=10
)

def on_click():
    print("Кнопка нажата!")

button.on_click(on_click)
```

### Timer
Универсальный таймер на основе системного времени. Обеспечивает точный контроль времени с поддержкой обратных вызовов и различными функциями тайминга.

#### Свойства
- `duration` (float): Интервал таймера в секундах
- `active` (bool): True, если таймер работает и не на паузе
- `done` (bool): True, если таймер завершен (и не повторяется)
- `callback` (Optional[Callable]): Функция, вызываемая при срабатывании таймера
- `repeat` (bool): Автоматически ли перезапускается таймер после срабатывания

#### Методы
- `__init__(duration: float, callback: Optional[Callable] = None, args: Tuple = (), kwargs: Dict = None, repeat: bool = False, autostart: bool = False)`: Инициализирует таймер с указанной длительностью и опциональным обратным вызовом
- `start(duration: Optional[float] = None)`: (Пере)запускает таймер
- `pause()`: Ставит таймер на паузу, сохраняя оставшееся время
- `resume()`: Возобновляет таймер с паузы
- `stop()`: Останавливает таймер и помечает его как завершенный
- `reset()`: Сбрасывает состояние таймера
- `update()`: Обновляет состояние таймера, должен вызываться каждый кадр
- `time_left() -> float`: Получает оставшееся время до срабатывания
- `elapsed() -> float`: Получает прошедшее время с последнего (пере)запуска
- `progress() -> float`: Получает прогресс завершения от 0.0 до 1.0

Пример использования:
```python
# Создание одноразового таймера
def on_timer_complete():
    print("Таймер завершен!")

timer = Timer(
    duration=3.0,
    callback=on_timer_complete,
    autostart=True
)

# Создание повторяющегося таймера
def tick():
    print("Тик!")

repeating_timer = Timer(
    duration=1.0,
    callback=tick,
    repeat=True,
    autostart=True
)

# В игровом цикле:
timer.update()
repeating_timer.update()

# Проверка прогресса
progress = timer.progress()  # от 0.0 до 1.0
time_left = timer.time_left()  # оставшиеся секунды
```

### Health
Комплексная система управления здоровьем для спрайтов. Обеспечивает отслеживание здоровья, механику получения урона/лечения и обратные вызовы событий.

#### Свойства
- `max_health` (float): Максимальное значение здоровья
- `current_health` (float): Текущее значение здоровья
- `is_alive` (bool): Жив ли спрайт (здоровье > 0)
- `owner_sprite` (Optional[Sprite]): Ссылка на спрайт, которому принадлежит этот компонент здоровья

#### Методы
- `__init__(max_health: float, current_health: Optional[float] = None, owner_sprite: Optional[Sprite] = None, on_hp_change: Optional[Union[HpChangeCallback, List[HpChangeCallback]]] = None, on_damage: Optional[Union[DamageCallback, List[DamageCallback]]] = None, on_heal: Optional[Union[HealCallback, List[HealCallback]]] = None, on_death: Optional[Union[DeathCallback, List[DeathCallback]]] = None)`: Инициализирует компонент здоровья
- `take_damage(amount: float, damage_type: Optional[str] = None)`: Применяет урон к спрайту
- `heal(amount: float, heal_type: Optional[str] = None)`: Лечит спрайт
- `resurrect(heal_to_max: bool = True)`: Воскрешает мертвый спрайт
- `add_on_hp_change_callback(callback: HpChangeCallback)`: Добавляет обратный вызов для изменений здоровья
- `add_on_damage_callback(callback: DamageCallback)`: Добавляет обратный вызов для событий получения урона
- `add_on_heal_callback(callback: HealCallback)`: Добавляет обратный вызов для событий лечения
- `add_on_death_callback(callback: DeathCallback)`: Добавляет обратный вызов для событий смерти

Пример использования:
```python
def on_hp_change(new_hp, diff):
    print(f"Здоровье изменилось на {diff}, новое значение: {new_hp}")

def on_death(sprite):
    print(f"{sprite} умер!")

health = HealthComponent(
    max_health=100,
    current_health=100,
    on_hp_change=on_hp_change,
    on_death=on_death
)

# Получение урона
health.take_damage(20)  # Уменьшает здоровье на 20

# Лечение
health.heal(10)  # Увеличивает здоровье на 10

# Проверка состояния
if health.is_alive:
    print(f"Текущее здоровье: {health.current_health}/{health.max_health}")

# Воскрешение, если мертв
if not health.is_alive:
    health.resurrect()
```

### MouseInteractor
Компонент для обработки взаимодействия с мышью для спрайтов.

#### Свойства
- `is_hovered` (bool): Наведена ли мышь на спрайт
- `is_pressed` (bool): Нажата ли кнопка мыши на спрайте
- `is_clicked` (bool): Был ли клик по спрайту
- `mouse_pos` (Tuple[int, int]): Текущая позиция мыши
- `mouse_buttons` (Tuple[bool, bool, bool]): Текущее состояние кнопок мыши

#### Методы
- `__init__(sprite: Sprite)`: Инициализирует взаимодействие с мышью для спрайта
- `on_hover(callback: Callable)`: Устанавливает обработчик наведения
- `on_press(callback: Callable)`: Устанавливает обработчик нажатия
- `on_release(callback: Callable)`: Устанавливает обработчик отпускания
- `on_click(callback: Callable)`: Устанавливает обработчик клика
- `update()`: Обновляет состояние взаимодействия

Пример:
```python
sprite = spritePro.Sprite("sprite.png")
interactor = spritePro.MouseInteractor(sprite)

def on_hover():
    print("Мышь наведена на спрайт")

def on_click():
    print("Спрайт был кликнут")

interactor.on_hover(on_hover)
interactor.on_click(on_click)

# В игровом цикле
while True:
    interactor.update()
```

## Утилиты

### Surface
Функции для работы с поверхностями.

#### Функции
- `round_corners(surface, radius)`: Создание поверхности с закругленными углами
- `set_mask(surface, mask)`: Применение маски к поверхности

## Лучшие практики

### Управление ресурсами
- Используйте `set_image()` для загрузки изображений
- Освобождайте ресурсы при завершении
- Используйте кэширование для часто используемых ресурсов

### Оптимизация производительности
- Минимизируйте количество спрайтов
- Используйте группы спрайтов для эффективного обновления
- Применяйте ограничения движения для предотвращения выхода за границы

### Обработка событий
- Используйте callback-функции для обработки событий
- Избегайте блокирующих операций в обработчиках
- Правильно обрабатывайте исключения

### Физика
- Используйте реальные единицы измерения
- Настраивайте параметры физики под конкретную игру
- Обрабатывайте столкновения эффективно

### UI компоненты
- Создавайте переиспользуемые компоненты
- Используйте стили для единообразия
- Обрабатывайте все состояния компонентов 

### Глобальные переменные
- `spritePro.events`: Список текущих событий pygame
- `spritePro.screen`: Основная поверхность окна
- `spritePro.screen_rect`: Прямоугольник основного окна
- `spritePro.clock`: Объект для контроля FPS
- `spritePro.dt`: Дельта времени между кадрами
- `spritePro.FPS`: Стандартное количество кадров в секунду (60)
- `spritePro.WH`: Кортеж размеров окна
- `spritePro.WH_CENTER`: Кортеж координат центра экрана

### Физические константы
- `PIXELS_PER_METER`: Коэффициент перевода из пикселей в метры (50 пикселей = 1 метр)
- `SKIN`: Ширина коллизионной оболочки для определения земли (2 пикселя)

### Значения по умолчанию для кнопок
- `hover_scale_delta`: Изменение масштаба при наведении (0.05)
- `press_scale_delta`: Изменение масштаба при нажатии (-0.08)
- `hover_color`: Цвет фона при наведении ((230, 230, 230))
- `press_color`: Цвет фона при нажатии ((180, 180, 180))
- `base_color`: Стандартный цвет фона ((255, 255, 255))
- `anim_speed`: Множитель скорости анимации (0.2)
- `animated`: Включены ли анимации (True)

### Значения по умолчанию для спрайтов
- `auto_flip`: Автоматически отражать спрайт по горизонтали при движении влево/вправо (True)
- `stop_threshold`: Порог расстояния для остановки движения (1.0)
- `color`: Стандартный цветовой оттенок ((255, 255, 255))
- `active`: Активен ли спрайт и должен ли отображаться (True)
- `states`: Стандартные состояния спрайта ({"idle", "moving", "hit", "attacking", "dead"})

### Значения по умолчанию для физических спрайтов
- `jump_force`: Стандартная сила прыжка в м/с (7)
- `MAX_STEPS`: Максимальное количество шагов физики за кадр (8)
- `mass`: Стандартная масса в кг (1.0)
- `gravity`: Стандартная сила гравитации в м/с² (9.8)
- `bounce_enabled`: Включен ли отскок по умолчанию (False)
- `ground_friction`: Стандартный коэффициент трения о землю (0.8)
- `min_velocity_threshold`: Минимальный порог скорости для остановки (0.01) 