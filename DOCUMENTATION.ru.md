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
Базовый класс спрайта с поддержкой движения, анимации и визуальных эффектов.

#### Свойства
- `auto_flip` (bool): Автоматическое отражение спрайта по горизонтали при движении влево/вправо. По умолчанию: True
- `stop_threshold` (float): Пороговое значение расстояния для остановки движения. По умолчанию: 1.0
- `color` (Tuple[int, int, int]): Текущий цвет спрайта. По умолчанию: (255, 255, 255)
- `active` (bool): Активен ли спрайт и должен ли он отображаться. По умолчанию: True

#### Атрибуты экземпляра
- `size` (tuple): Размеры спрайта (ширина, высота)
- `start_pos` (tuple): Начальная позиция (x, y)
- `velocity` (Vector2): Текущий вектор скорости
- `speed` (float): Базовая скорость движения
- `flipped_h` (bool): Отражен ли спрайт по горизонтали
- `flipped_v` (bool): Отражен ли спрайт по вертикали
- `angle` (float): Текущий угол поворота
- `scale` (float): Текущий масштаб
- `alpha` (int): Текущая прозрачность (0-255)
- `state` (str): Текущее состояние
- `states` (set): Доступные состояния {"idle", "moving", "hit", "attacking", "dead"}
- `sound_file` (str): Путь к текущему звуковому файлу
- `sound` (pygame.mixer.Sound): Текущий звуковой объект

#### Методы
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0)`: Инициализирует новый спрайт
- `set_color(color: Tuple)`: Устанавливает цвет спрайта
- `set_image(image_source: Union[str, Path, pygame.Surface], size: Optional[Tuple[int, int]] = None)`: Устанавливает новое изображение
- `set_native_size()`: Возвращает спрайт к оригинальным размерам изображения
- `update(window: pygame.Surface)`: Обновляет состояние и отрисовывает спрайт
- `set_active(active: bool)`: Устанавливает активное состояние спрайта
- `reset_sprite()`: Сбрасывает спрайт в начальное положение и состояние
- `move(dx: float, dy: float)`: Перемещает спрайт на указанное расстояние
- `move_towards(target_pos: Tuple[float, float], speed: Optional[float] = None)`: Двигает спрайт к целевой позиции
- `set_velocity(vx: float, vy: float)`: Устанавливает скорость спрайта
- `move_up/down/left/right(speed: Optional[float] = None)`: Двигает спрайт в указанном направлении
- `handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT)`: Обрабатывает ввод с клавиатуры
- `stop()`: Останавливает движение спрайта
- `rotate_to(angle: float)`: Поворачивает спрайт на указанный угол
- `rotate_by(angle_change: float)`: Поворачивает спрайт на относительный угол
- `set_scale(scale: float)`: Устанавливает масштаб спрайта
- `set_alpha(alpha: int)`: Устанавливает прозрачность спрайта
- `fade_by(amount: int, min_alpha: int = 0, max_alpha: int = 255)`: Изменяет прозрачность на относительное значение
- `scale_by(amount: float, min_scale: float = 0.0, max_scale: float = 2.0)`: Изменяет масштаб на относительное значение
- `distance_to(other_sprite) -> float`: Вычисляет расстояние до другого спрайта
- `set_state(state: str)`: Устанавливает текущее состояние спрайта
- `is_in_state(state: str) -> bool`: Проверяет, находится ли спрайт в указанном состоянии
- `is_visible_on_screen(screen: pygame.Surface) -> bool`: Проверяет, виден ли спрайт на экране
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Ограничивает движение спрайта в пределах указанных границ
- `play_sound(sound_file: str)`: Воспроизводит звуковой эффект (создает новый объект звука только если файл изменился)

#### Визуальные эффекты
Спрайт поддерживает следующие визуальные эффекты, которые применяются в следующем порядке:
1. Отражение (горизонтальное и вертикальное)
2. Масштабирование
3. Вращение
4. Прозрачность
5. Цветовой оттенок

Пример использования:
```python
# Создание спрайта
sprite = Sprite("player.png", size=(50, 50), pos=(400, 300), speed=5)

# Управление движением
sprite.move_up()  # Движение вверх
sprite.move_right()  # Движение вправо

# Визуальные эффекты
sprite.set_scale(1.5)  # Увеличение размера
sprite.rotate_by(45)  # Поворот на 45 градусов
sprite.fade_by(-50)  # Уменьшение прозрачности
sprite.set_color((255, 0, 0))  # Красный оттенок

# Звуковые эффекты
sprite.play_sound("jump.wav")  # Воспроизведение звука

# В игровом цикле
while True:
    # Обработка ввода
    sprite.handle_keyboard_input()
    
    # Обновление и отрисовка
    sprite.update(screen)
```

### GameSprite
Расширяет базовый класс Sprite для игровых объектов с управлением здоровьем и обработкой столкновений.

#### Свойства
- `collision_step` (int): Шаг разрешения столкновений (по умолчанию: 1)
- `health_component` (HealthComponent): Управляет функциональностью здоровья
- `on_collision` (Optional[Callable]): Обработчик событий столкновения
- `_user_on_death_callback` (Optional[Callable]): Пользовательский обработчик смерти
- `_last_obstacles_hash` (Optional[int]): Хеш последних препятствий для оптимизации
- `_last_obstacles_rects` (Optional[List[pygame.Rect]]): Список прямоугольников последних препятствий

#### Методы
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, max_health: int = 100, current_health: Optional[int] = None)`: Инициализирует игровой спрайт с управлением здоровьем
- `_handle_damage_state(amount: float)`: Внутренний обработчик событий получения урона
- `_handle_death_event(dead_sprite: Sprite)`: Внутренний обработчик событий смерти
- `on_collision_event(callback: Callable)`: Устанавливает обработчик событий столкновения
- `on_death_event(callback: Callable[["GameSprite"], None])`: Устанавливает обработчик событий смерти
- `collide_with(other_sprite) -> bool`: Проверяет столкновение с другим спрайтом с использованием пиксельно-точных масок
- `collide_with_group(group: pygame.sprite.Group) -> List`: Проверяет столкновение с группой спрайтов
- `collide_with_tag(group: pygame.sprite.Group, tag: str) -> List`: Проверяет столкновение с помеченными спрайтами
- `_get_collision_side(prev_x: float, prev_y: float, rect: pygame.Rect) -> str`: Определяет сторону столкновения ('top', 'bottom', 'left', 'right', 'inside')
- `resolve_collisions(*obstacles) -> List[Tuple[pygame.Rect, str]]`: Разрешает столкновения с препятствиями и останавливает движение

#### Управление здоровьем
Класс GameSprite включает систему здоровья со следующими возможностями:
- Отслеживание максимального и текущего здоровья
- Функциональность получения урона и лечения
- Обработка событий смерти
- Управление состоянием при получении урона/смерти

Пример использования:
```python
# Создание игрового спрайта с здоровьем
player = GameSprite(
    "player.png",
    size=(50, 50),
    pos=(100, 100),
    speed=5,
    max_health=100,
    current_health=80  # Начальное здоровье меньше максимального
)

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

# Проверка столкновений с группой
colliding_sprites = player.collide_with_group(enemy_group)

# Проверка столкновений с помеченными спрайтами
tagged_collisions = player.collide_with_tag(enemy_group, "boss")

# Разрешение столкновений с препятствиями
collisions = player.resolve_collisions(obstacle1, obstacle2)
for obstacle, side in collisions:
    print(f"Столкновение с {obstacle} со стороны {side}")
```

### PhysicalSprite
Спрайт с поддержкой физики, включая гравитацию, отскок и обработку столкновений. Расширяет GameSprite возможностями физической симуляции.

#### Свойства
- `jump_force` (float): Сила прыжка в м/с (по умолчанию: 7)
- `MAX_STEPS` (int): Максимальное количество шагов физики за кадр (по умолчанию: 8)
- `mass` (float): Масса в кг
- `gravity` (float): Сила гравитации в м/с²
- `bounce_enabled` (bool): Включен ли отскок
- `is_grounded` (bool): Касается ли спрайт земли
- `ground_friction` (float): Коэффициент трения при касании земли (по умолчанию: 0.8)
- `min_velocity_threshold` (float): Минимальный порог скорости для остановки (по умолчанию: 0.01)
- `position` (Vector2): Позиция в метрах
- `velocity` (Vector2): Скорость в м/с
- `force` (Vector2): Текущий вектор силы
- `acceleration` (Vector2): Текущий вектор ускорения
- `_x_controlled_this_frame` (bool): Флаг управления по X в текущем кадре

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
Класс PhysicalSprite реализует физическую систему со следующими возможностями:
- Реальные единицы измерения (метры, м/с, м/с²)
- Гравитация и определение касания земли
- Применение сил и ускорение
- Механика отскока
- Трение о землю
- Разрешение столкновений

Пример использования:
```python
# Создаем спрайт с поддержкой физики
player = PhysicalSprite(
    "player.png",
    size=(50, 50),
    pos=(100, 100),
    speed=5,
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# В игровом цикле:
while True:
    # Обработка ввода
    player.handle_keyboard_input(
        left_key=pygame.K_a,
        right_key=pygame.K_d,
        up_key=pygame.K_w
    )
    
    # Обновление физики
    player.update_physics(60)  # 60 FPS
    
    # Применение сил
    player.apply_force(pygame.math.Vector2(0, -9.8))  # Гравитация
    
    # Прыжок
    if player.is_grounded:
        player.jump(7)  # Прыжок с силой 7 м/с
    
    # Ограничение движения в пределах экрана
    player.limit_movement(screen.get_rect())
    
    # Разрешение столкновений
    collisions = player.resolve_collisions(
        obstacle1,
        obstacle2,
        fps=60,
        limit_top=True,
        limit_bottom=True,
        limit_left=True,
        limit_right=True
    )
    
    # Отрисовка
    player.update(screen)
```

## Компоненты

### TextSprite
Спрайт для отображения текста с поддержкой всех базовых механик Sprite. Расширяет базовый класс Sprite для обработки отображения текста, сохраняя все основные функции спрайта, такие как движение, вращение, масштабирование, прозрачность и определение столкновений. Автоматически перерисовывает изображение спрайта при обновлении текста, цвета или шрифта.

#### Свойства
- `text` (str): Отображаемый текст
- `color` (Tuple[int, int, int]): Цвет текста в формате RGB. По умолчанию: (255, 255, 255)
- `font_size` (int): Размер шрифта в пунктах. По умолчанию: 24
- `font_path` (Optional[Union[str, Path]]): Путь к файлу шрифта .ttf или None для системного шрифта
- `font` (pygame.font.Font): Текущий объект шрифта
- `auto_flip` (bool): Всегда False для текстовых спрайтов

#### Методы
- `__init__(text: str, font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255), pos: Tuple[int, int] = (0, 0), font_name: Optional[Union[str, Path]] = None, speed: float = 0, **sprite_kwargs)`: Инициализирует текстовый спрайт
- `input(k_delete: pygame.key = pygame.K_ESCAPE) -> str`: Обрабатывает ввод текста с клавиатуры
- `set_text(new_text: str = None)`: Обновляет текст спрайта и перерисовывает изображение
- `set_color(new_color: Tuple[int, int, int])`: Обновляет цвет текста и перерисовывает изображение
- `set_font(font_name: Optional[Union[str, Path]], font_size: int)`: Устанавливает шрифт и размер, затем отрисовывает текст на новой поверхности

Пример использования:
```python
# Создание текстового спрайта
text = TextSprite(
    text="Привет, мир!",
    font_size=32,
    color=(255, 0, 0),
    pos=(400, 300)
)

# Обновление текста
text.set_text("Новый текст")

# Изменение цвета
text.set_color((0, 255, 0))

# Изменение шрифта
text.set_font("arial.ttf", 48)

# Обработка ввода с клавиатуры
text.input()  # ESC для очистки, Backspace для удаления

# В игровом цикле
while True:
    # Обновление и отрисовка
    text.update(screen)
```

### Button
Удобная кнопка на основе Sprite + TextSprite + MouseInteractor. Объединяет функциональность спрайта с отображением текста и взаимодействием с мышью для создания интерактивной кнопки с анимациями при наведении и нажатии.

#### Свойства
- `text_sprite` (TextSprite): Спрайт для отображения текста
- `interactor` (MouseInteractor): Обработчик взаимодействия с мышью
- `hover_color` (Tuple[int, int, int]): Цвет фона при наведении. По умолчанию: (230, 230, 230)
- `press_color` (Tuple[int, int, int]): Цвет фона при нажатии. По умолчанию: (180, 180, 180)
- `current_color` (Tuple[int, int, int]): Текущий цвет фона
- `hover_scale_delta` (float): Изменение масштаба при наведении. По умолчанию: 0.05
- `press_scale_delta` (float): Изменение масштаба при нажатии. По умолчанию: -0.08
- `start_scale` (float): Начальный масштаб
- `_target_scale` (float): Целевой масштаб для анимации
- `anim_speed` (float): Скорость анимации. По умолчанию: 0.2
- `animated` (bool): Включены ли анимации. По умолчанию: True

#### Методы
- `__init__(sprite: str = "", size: Tuple[int, int] = (250, 70), pos: Tuple[int, int] = (300, 200), text: str = "Button", text_size: int = 24, text_color: Tuple[int, int, int] = (0, 0, 0), font_name: Optional[Union[str, Path]] = None, on_click: Optional[Callable[[], None]] = None, hover_scale_delta: float = 0.05, press_scale_delta: float = -0.08, hover_color: Tuple[int, int, int] = (230, 230, 230), press_color: Tuple[int, int, int] = (180, 180, 180), base_color: Tuple[int, int, int] = (255, 255, 255), anim_speed: float = 0.2, animated: bool = True)`: Инициализирует кнопку
- `update(screen: pygame.Surface)`: Обновляет состояние кнопки и отрисовывает её
- `set_scale(scale: float, update: bool = True)`: Устанавливает масштаб кнопки

Пример использования:
```python
# Создание кнопки
button = Button(
    text="Нажми меня",
    pos=(400, 300),
    on_click=lambda: print("Кнопка нажата!")
)

# В игровом цикле
while True:
    # Обновление и отрисовка
    button.update(screen)
```

### Timer
Универсальный таймер на основе системного времени. Обеспечивает точный контроль времени с поддержкой обратных вызовов и различными функциями тайминга.

#### Свойства
- `duration` (float): Интервал таймера в секундах
- `active` (bool): True, если таймер работает и не на паузе
- `done` (bool): True, если таймер завершен (и не повторяется)
- `callback` (Optional[Callable]): Функция, вызываемая при срабатывании таймера
- `args` (Tuple): Позиционные аргументы для callback
- `kwargs` (Dict): Именованные аргументы для callback
- `repeat` (bool): Автоматически ли перезапускается таймер после срабатывания
- `_start_time` (Optional[float]): Время последнего запуска
- `_next_fire` (Optional[float]): Время следующего срабатывания

#### Методы
- `__init__(duration: float, callback: Optional[Callable] = None, args: Tuple = (), kwargs: Dict = None, repeat: bool = False, autostart: bool = False)`: Инициализирует таймер с указанной длительностью и опциональным обратным вызовом
- `start(duration: Optional[float] = None)`: (Пере)запускает таймер, опционально устанавливая новую длительность
- `pause()`: Ставит таймер на паузу, сохраняя оставшееся время
- `resume()`: Возобновляет таймер с паузы, продолжая с оставшегося времени
- `stop()`: Останавливает таймер и помечает его как завершенный
- `reset()`: Сбрасывает состояние таймера. Если активен, сбрасывает прошедшее время и устанавливает следующее срабатывание через duration секунд. Если неактивен, просто очищает флаг done
- `update()`: Обновляет состояние таймера, должен вызываться каждый кадр. Если активен и текущее время >= next_fire, выполняет callback и либо останавливает таймер (если не повторяется), либо перезапускает его (если повторяется)
- `time_left() -> float`: Возвращает оставшееся время до срабатывания (>=0), исключая паузы
- `elapsed() -> float`: Возвращает прошедшее время с последнего (пере)запуска, исключая паузы
- `progress() -> float`: Возвращает прогресс выполнения от 0.0 до 1.0

Пример использования:
```python
# Создаем одноразовый таймер
def on_timer_complete():
    print("Таймер завершен!")

timer = Timer(
    duration=3.0,
    callback=on_timer_complete,
    autostart=True
)

# Создаем повторяющийся таймер
def tick():
    print("Тик!")

repeating_timer = Timer(
    duration=1.0,
    callback=tick,
    repeat=True,
    autostart=True
)

# В игровом цикле:
while True:
    # Обновление таймеров
    timer.update()
    repeating_timer.update()
    
    # Проверка прогресса
    progress = timer.progress()  # от 0.0 до 1.0
    time_left = timer.time_left()  # оставшиеся секунды
    
    # Управление таймером
    if some_condition:
        timer.pause()
    elif other_condition:
        timer.resume()
    elif reset_condition:
        timer.reset()
```

### Health
Компонент для управления здоровьем спрайта. Предоставляет функционал для отслеживания текущего и максимального здоровья, получения урона, лечения, а также вызывает пользовательские функции (колбэки) при различных событиях. Поддерживает сравнение и изменение здоровья с использованием операторов.

#### Свойства
- `max_health` (float): Максимальное количество здоровья
- `current_health` (float): Текущее количество здоровья
- `is_alive` (bool): True, если спрайт жив (текущее здоровье > 0)
- `owner_sprite` (Optional[Sprite]): Ссылка на спрайт-владелец для колбэков

#### Методы
- `__init__(max_health: float, current_health: Optional[float] = None, owner_sprite: Optional[Sprite] = None, on_hp_change: Optional[Union[HpChangeCallback, List[HpChangeCallback]]] = None, on_damage: Optional[Union[DamageCallback, List[DamageCallback]]] = None, on_heal: Optional[Union[HealCallback, List[HealCallback]]] = None, on_death: Optional[Union[DeathCallback, List[DeathCallback]]] = None)`: Инициализирует компонент здоровья
- `take_damage(amount: float, damage_type: Optional[str] = None)`: Применяет урон к спрайту
- `heal(amount: float, heal_type: Optional[str] = None)`: Лечит спрайт
- `resurrect(heal_to_max: bool = True)`: Воскрешает мертвый спрайт
- `add_on_hp_change_callback(callback: HpChangeCallback)`: Добавляет колбэк для изменения здоровья
- `add_on_damage_callback(callback: DamageCallback)`: Добавляет колбэк для получения урона
- `add_on_heal_callback(callback: HealCallback)`: Добавляет колбэк для лечения
- `add_on_death_callback(callback: DeathCallback)`: Добавляет колбэк для смерти

#### Операторы
Компонент поддерживает следующие операторы сравнения:
- `<`, `<=`, `>`, `>=`: Сравнение текущего здоровья с числом или другим компонентом здоровья
- `==`, `!=`: При сравнении с числом сравнивается текущее здоровье, при сравнении с bool сравнивается состояние живости

Пример использования:
```python
# Создаем компонент здоровья
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
health.take_damage(20)  # -20 HP

# Лечение
health.heal(10)  # +10 HP

# Проверка состояния
if health.is_alive:
    print("Спрайт жив!")

# Сравнение здоровья
if health < 50:
    print("Здоровье меньше 50!")
if health > other_health:
    print("Здоровье больше, чем у другого спрайта!")

# Воскрешение
if not health.is_alive:
    health.resurrect()  # Восстанавливает максимальное здоровье
```

### MouseInteractor
Компонент для обработки взаимодействия с мышью для спрайтов. Добавляет логику определения наведения, нажатия и клика для любого спрайта с атрибутом .rect.

#### Свойства
- `sprite` (pygame.sprite.Sprite): Спрайт, для которого обрабатываются события мыши
- `on_click` (Optional[Callable[[], None]]): Функция, вызываемая при отпускании кнопки мыши над спрайтом
- `on_mouse_down` (Optional[Callable[[], None]]): Функция, вызываемая при нажатии кнопки мыши над спрайтом
- `on_mouse_up` (Optional[Callable[[], None]]): Функция, вызываемая при отпускании кнопки мыши (независимо от позиции)
- `on_hover_enter` (Optional[Callable[[], None]]): Функция, вызываемая при первом наведении мыши на спрайт
- `on_hover_exit` (Optional[Callable[[], None]]): Функция, вызываемая при уходе мыши с области спрайта
- `is_hovered` (bool): True, если мышь находится над спрайтом
- `is_pressed` (bool): True, если кнопка мыши нажата над спрайтом

#### Методы
- `__init__(sprite: pygame.sprite.Sprite, on_click: Optional[Callable[[], None]] = None, on_mouse_down: Optional[Callable[[], None]] = None, on_mouse_up: Optional[Callable[[], None]] = None, on_hover_enter: Optional[Callable[[], None]] = None, on_hover_exit: Optional[Callable[[], None]] = None)`: Инициализирует обработчик мыши для спрайта
- `update(events: Optional[List[pygame.event.Event]] = None)`: Обновляет состояние взаимодействия на основе событий мыши. Должен вызываться каждый кадр перед отрисовкой

Пример использования:
```python
# Создаем спрайт
sprite = pygame.sprite.Sprite()
sprite.image = pygame.Surface((100, 100))
sprite.rect = sprite.image.get_rect()
sprite.rect.center = (400, 300)

# Создаем обработчик мыши
interactor = MouseInteractor(
    sprite=sprite,
    on_hover_enter=lambda: print("Мышь наведена"),
    on_hover_exit=lambda: print("Мышь ушла"),
    on_mouse_down=lambda: print("Кнопка нажата"),
    on_mouse_up=lambda: print("Кнопка отпущена"),
    on_click=lambda: print("Клик!")
)

# В игровом цикле
while True:
    # Обновление состояния взаимодействия
    interactor.update()
    
    # Проверка состояния
    if interactor.is_hovered:
        print("Спрайт под мышью")
    if interactor.is_pressed:
        print("Спрайт нажат")
```

## Утилиты

### Surface
Утилиты для работы с поверхностями pygame.

#### Функции
- `round_corners(surface: pygame.Surface, radius: int = 10) -> pygame.Surface`: Создает новую поверхность с тем же изображением, но со скругленными углами
- `set_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface`: Применяет маску к исходному изображению

Пример использования:
```python
from spritePro.utils.surface import round_corners

# Создаем поверхность со скругленными углами
surface = pygame.Surface((100, 100))
surface.fill((255, 0, 0))  # Красный фон
rounded = round_corners(surface, radius=20)  # Скругление углов радиусом 20 пикселей

# Применяем маску
mask = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (50, 50), 50)  # Круглая маска
masked = set_mask(surface, mask)  # Применяем маску к поверхности
```

## Лучшие практики

### Управление ресурсами
- Используйте `