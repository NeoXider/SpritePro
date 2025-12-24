# Модуль Button

Класс `Button` предоставляет простую в использовании интерактивную UI-кнопку с эффектами наведения, анимациями и настраиваемым внешним видом.

## Обзор

Button объединяет класс Sprite с TextSprite и MouseInteractor для создания полного интерактивного решения для кнопок. Он автоматически обрабатывает события мыши, визуальную обратную связь и отображение текста.

## Основные возможности

- **Интерактивный UI**: Обнаружение наведения и клика с визуальной обратной связью
- **Настраиваемый внешний вид**: Цвета, шрифты, размеры и анимации
- **Обработка событий**: Обратные вызовы клика и управление состоянием
- **Плавные анимации**: Анимации наведения и нажатия с настраиваемой скоростью
- **Интеграция текста**: Встроенная отрисовка текста с поддержкой шрифтов

## Параметры конструктора

- `sprite` (str): Путь к фоновому изображению. По умолчанию: "" (сплошной цвет)
- `size` (tuple): Размеры кнопки (ширина, высота). По умолчанию: (250, 70)
- `pos` (tuple): Позиция кнопки. По умолчанию: (300, 200)
- `text` (str): Текст метки кнопки. По умолчанию: "Button"
- `text_size` (int): Размер шрифта. По умолчанию: 24
- `text_color` (tuple): Цвет текста RGB. По умолчанию: (0, 0, 0)
- `font_name` (str/Path): Путь к файлу шрифта. По умолчанию: None (системный шрифт)
- `on_click` (callable): Обработчик события клика. По умолчанию: None
- `sorting_order` (int): Порядок слоя отрисовки для кнопки и её метки. По умолчанию: 1000
- `hover_scale_delta` (float): Изменение масштаба при наведении. По умолчанию: 0.05
- `press_scale_delta` (float): Изменение масштаба при нажатии. По умолчанию: -0.08
- `hover_color` (tuple): Цвет фона при наведении. По умолчанию: (230, 230, 230)
- `press_color` (tuple): Цвет фона при нажатии. По умолчанию: (180, 180, 180)
- `base_color` (tuple): Цвет фона по умолчанию. По умолчанию: (255, 255, 255)
- `anim_speed` (float): Множитель скорости анимации. По умолчанию: 0.2
- `animated` (bool): Включить ли анимации. По умолчанию: True
- `use_scale_fx` (bool): Включить/выключить эффект масштабирования при наведении и нажатии. По умолчанию: True
- `use_color_fx` (bool): Включить/выключить эффект изменения цвета при наведении и нажатии. По умолчанию: True
- `anchor` (str | Anchor): Якорь для позиционирования. По умолчанию: Anchor.CENTER

**Пример использования якоря:**
```python
# Кнопка внизу по центру экрана
button = s.Button("", (200, 50), (s.WH_C.x, s.WH.y - 20), "Menu", anchor=s.Anchor.MID_BOTTOM)

# Кнопка в правом верхнем углу
close_btn = s.Button("", (50, 50), (s.WH.x - 10, 10), "X", anchor=s.Anchor.TOP_RIGHT)
```

## Визуальная настройка

### Цвета
```python
button = s.Button(
    text="Стилизованная кнопка",
    base_color=(100, 150, 255),      # Обычное состояние
    hover_color=(120, 170, 255),     # Наведение мыши
    press_color=(80, 130, 235),      # Нажатие мыши
    text_color=(255, 255, 255)       # Белый текст
)
```

### Настройки анимации
```python
button = s.Button(
    text="Анимированная кнопка",
    hover_scale_delta=0.1,    # Увеличить на 10% при наведении
    press_scale_delta=-0.05,  # Уменьшить на 5% при нажатии
    anim_speed=0.3,          # Скорость анимации
    animated=True            # Включить анимации
)
```

### Пользовательские шрифты
```python
button = s.Button(
    text="Пользовательский шрифт",
    font_name="assets/fonts/custom.ttf",
    text_size=28
)
```

### Управление цветами и масштабами
```python
# Установить базовый цвет
button.set_base_color((100, 150, 255))

# Установить все цвета сразу
button.set_all_colors(
    base_color=(255, 255, 255),    # Обычное состояние
    hover_color=(230, 230, 230),    # При наведении
    press_color=(180, 180, 180)    # При нажатии
)

# Установить все масштабы сразу
button.set_all_scales(
    base_scale=1.0,    # Обычный масштаб
    hover_scale=1.1,   # При наведении
    press_scale=0.95  # При нажатии
)

# Отключить эффекты масштабирования или цвета
button.use_scale_fx = False  # Отключить масштабирование
button.use_color_fx = False  # Отключить изменение цвета
```

## Обработка событий

### События клика
```python
def button_clicked():
    print("Кнопка была нажата!")
    # Добавьте вашу логику кнопки здесь

button = s.Button(
    text="Кнопка действия",
    on_click=button_clicked
)
```

### Продвинутая обработка событий
```python
def hover_handler():
    print("Мышь наведена на кнопку")

button = s.Button(text="Кнопка наведения")
button.on_hover(hover_handler)

# Или установить обработчик клика после создания
def click_handler():
    print("Кнопка нажата!")
    
button.on_click(click_handler)
```

## Состояния кнопки

## Активация

Вызов `button.set_active(False)` теперь также передает неактивное состояние встроенной текстовой метке и любым другим дочерним элементам, прикрепленным к кнопке. Повторно включите с помощью `button.set_active(True)`, чтобы вернуть и тело кнопки, и её метку в систему спрайтов.

### Управление состоянием
```python
# Масштабировать кнопку
button.set_scale(1.2, update=True)  # Сделать кнопку на 20% больше и обновить базовый масштаб
button.set_scale(1.2, update=False)  # Временно изменить масштаб без обновления базового

# Доступ к свойствам кнопки
current_scale = button.scale
button_rect = button.rect
button_text = button.text_sprite.text

# Доступ к внутренним компонентам
text_sprite = button.text_sprite  # TextSprite для текста
interactor = button.interactor    # MouseInteractor для мыши
```

## Иерархия спрайтов

Кнопки автоматически делают свою внутреннюю метку `TextSprite` дочерним элементом спрайта кнопки. Это сохраняет метку выровненной с преобразованиями и гарантирует, что вызов `button.kill()` также удаляет метку из сцены. Если вам нужно повторно использовать метку в другом месте, сначала отсоедините её с помощью `button.text_sprite.set_parent(None)` перед удалением кнопки.

## Продвинутые возможности

### Многострочный текст
```python
button = s.Button(
    text="Строка 1\nСтрока 2\nСтрока 3",
    size=(300, 120),
    text_size=20
)
```

### Динамические обновления кнопки
```python
# Обновить кнопку на основе состояния игры
def update_button():
    if player.health > 50:
        button.text_sprite.set_text("Здоров")
        button.set_color((100, 255, 100))
    else:
        button.text_sprite.set_text("Ранен")
        button.set_color((255, 100, 100))

# Вызвать в игровом цикле
update_button()
```

### Переключатели
Для кнопок, которым нужно переключаться между состояниями, используйте ToggleButton:
```python
# Создать переключатель
toggle = s.ToggleButton(
    pos=(400, 300),
    text_on="Звук ВКЛ",
    text_off="Звук ВЫКЛ",
    color_on=(50, 200, 50),
    color_off=(200, 50, 50),
    is_on=True,
    on_toggle=lambda state: print(f"Звук {'включен' if state else 'выключен'}")
)
```

См. [Документацию ToggleButton](toggle_button.md) для подробной информации.

### Группы кнопок
```python
# Создать несколько кнопок
buttons = []

for i, text in enumerate(["Старт", "Настройки", "Выход"]):
    button = s.Button(
        text=text,
        pos=(400, 200 + i * 80),
        on_click=lambda t=text: handle_menu_click(t)
    )
    buttons.append(button)

def handle_menu_click(button_text):
    if button_text == "Старт":
        start_game()
    elif button_text == "Настройки":
        show_options()
    elif button_text == "Выход":
        quit_game()
```

## Примеры стилизации

### Кнопка игрового меню
```python
menu_button = s.Button(
    text="ИГРАТЬ",
    size=(200, 60),
    pos=(400, 300),
    text_size=32,
    text_color=(255, 255, 255),
    base_color=(50, 50, 150),
    hover_color=(70, 70, 170),
    press_color=(30, 30, 130),
    hover_scale_delta=0.05,
    anim_speed=0.2
)
```

### Кнопка слота инвентаря
```python
slot_button = s.Button(
    sprite="slot_background.png",
    size=(64, 64),
    pos=(100, 100),
    text="",  # Нет текста для слотов предметов
    on_click=lambda: use_item(slot_index)
)
```



## Базовое использование

```python
import spritePro as s

# Создать простую кнопку
button = s.Button(
    text="Нажми меня!",
    pos=(400, 300),
    on_click=lambda: print("Кнопка нажата!")
)

# Обновить в игровом цикле
button.update()
```

## Интеграция с другими компонентами

### С системой анимации
```python
# Анимировать внешний вид кнопки
button.add_component(s.Animation([
    "button_frame1.png",
    "button_frame2.png",
    "button_frame3.png"
], frame_duration=0.2))
```

### С системой таймеров
```python
# Кнопка с перезарядкой
class CooldownButton(s.Button):
    def __init__(self, cooldown_time=3.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldown_time = cooldown_time
        self.cooldown_timer = None
        
    def on_click(self):
        if self.cooldown_timer is None:
            # Выполнить действие кнопки
            self.execute_action()
            
            # Начать перезарядку
            self.set_active(False)
            self.cooldown_timer = s.Timer(
                self.cooldown_time,
                self.cooldown_finished
            )
            self.cooldown_timer.start()
            
    def cooldown_finished(self):
        self.set_active(True)
        self.cooldown_timer = None
```

## Советы по производительности

- Используйте группы кнопок для лучшей организации
- Отключайте неиспользуемые кнопки для экономии обработки
- Рассмотрите использование спрайт-листов для фонов кнопок
- Кэшируйте объекты шрифтов для лучшей производительности

Для получения дополнительной информации о связанных компонентах см.:
- [Документация компонента Text](text.md)
- [Документация MouseInteractor](mouse_interactor.md)
- [Документация компонента Animation](animation.md)
