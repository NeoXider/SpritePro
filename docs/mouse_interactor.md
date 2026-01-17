# Компонент MouseInteractor

Компонент `MouseInteractor` предоставляет комплексную обработку взаимодействия с мышью для спрайтов, включая обнаружение наведения, события клика и управление состоянием.

## Обзор

MouseInteractor - это компонент, который можно прикрепить к любому спрайту для добавления возможностей взаимодействия с мышью. Он обрабатывает состояния наведения, обнаружение клика и предоставляет обратные вызовы для различных событий мыши.

## Основные возможности

- **Обнаружение наведения**: Автоматическое отслеживание состояния наведения мыши
- **Обработка клика**: Поддержка левой, правой и средней кнопок мыши
- **Управление состоянием**: Отслеживание состояния нажатия, отпускания и удержания
- **Обратные вызовы событий**: Настраиваемые обработчики событий
- **Обнаружение столкновений**: Обнаружение на основе прямоугольника (rect)

## Параметры конструктора

- `sprite` (pygame.sprite.Sprite): Спрайт для прикрепления взаимодействия мыши
- `on_click` (Optional[Callable[[], None]]): Вызывается при отпускании кнопки мыши над спрайтом. По умолчанию: None
- `on_mouse_down` (Optional[Callable[[], None]]): Вызывается при нажатии кнопки мыши над спрайтом. По умолчанию: None
- `on_mouse_up` (Optional[Callable[[], None]]): Вызывается при отпускании кнопки мыши (независимо от позиции). По умолчанию: None
- `on_hover_enter` (Optional[Callable[[], None]]): Вызывается, когда мышь впервые входит в область спрайта. По умолчанию: None
- `on_hover_exit` (Optional[Callable[[], None]]): Вызывается, когда мышь покидает область спрайта. По умолчанию: None

## Свойства

- `is_hovered` (bool): Находится ли мышь в данный момент над спрайтом
- `is_pressed` (bool): Нажата ли кнопка мыши в данный момент над спрайтом

## Методы

- `update(events: Optional[List[pygame.event.Event]] = None)`: Обновить состояние взаимодействия на основе событий мыши. Если `events` не указан, использует `spritePro.pygame_events`

## Обработка событий

### Проверка состояния

```python
# Проверить состояние взаимодействия мыши
if mouse_handler.is_hovered:
    print("Мышь над спрайтом")

if mouse_handler.is_pressed:
    print("Кнопка мыши нажата на спрайте")

# Обновить обработчик мыши (вызывать в игровом цикле)
mouse_handler.update()  # Использует spritePro.pygame_events автоматически
# или
mouse_handler.update(pygame.event.get())  # Передать события вручную
```

### Обратные вызовы событий

```python
def on_click():
    print("Клик!")

def on_mouse_down():
    print("Кнопка нажата")

def on_mouse_up():
    print("Кнопка отпущена")

def on_hover_enter():
    print("Мышь вошла в область")

def on_hover_exit():
    print("Мышь покинула область")

mouse_handler = s.MouseInteractor(
    sprite=sprite,
    on_click=on_click,
    on_mouse_down=on_mouse_down,
    on_mouse_up=on_mouse_up,
    on_hover_enter=on_hover_enter,
    on_hover_exit=on_hover_exit
)
```

## Примеры интеграции

### Интерактивная кнопка

```python
class InteractiveButton(s.Sprite):
    def __init__(self, image_path, pos, on_click_callback):
        super().__init__(image_path, pos=pos)
        
        # Создать обработчик мыши
        self.interactor = s.MouseInteractor(
            sprite=self,
            on_click=on_click_callback,
            on_hover_enter=self.on_hover,
            on_hover_exit=self.on_hover_exit
        )
        
    def on_hover(self):
        self.scale = 1.1  # Увеличить при наведении
        
    def on_hover_exit(self):
        self.scale = 1.0  # Вернуть нормальный размер
        
    def update(self, screen=None):
        super().update(screen)
        self.interactor.update()  # Обновить взаимодействие
```

### Кнопка с визуальной обратной связью

```python
button = s.Sprite("button.png", pos=(400, 300))
button.base_color = (100, 150, 255)

interactor = s.MouseInteractor(
    sprite=button,
    on_click=lambda: print("Кнопка нажата!"),
    on_hover_enter=lambda: button.set_color((150, 200, 255)),
    on_hover_exit=lambda: button.set_color(button.base_color),
    on_mouse_down=lambda: button.set_color((50, 100, 200)),
    on_mouse_up=lambda: button.set_color((150, 200, 255))
)

# В игровом цикле
while True:
    s.update()
    interactor.update()
```

### Множественные спрайты с взаимодействием

```python
# Создать несколько интерактивных спрайтов
sprites = []
interactors = []

for i in range(5):
    sprite = s.Sprite(f"item_{i}.png", pos=(100 + i * 150, 300))
    interactor = s.MouseInteractor(
        sprite=sprite,
        on_click=lambda idx=i: print(f"Кликнут элемент {idx}")
    )
    sprites.append(sprite)
    interactors.append(interactor)

# Обновить все в игровом цикле
while True:
    s.update()
    for interactor in interactors:
        interactor.update()
```

### Условное взаимодействие

```python
class ConditionalInteractor:
    def __init__(self, sprite, condition_func):
        self.sprite = sprite
        self.condition = condition_func
        self.interactor = s.MouseInteractor(
            sprite=sprite,
            on_click=self.on_click
        )
        
    def on_click(self):
        if self.condition():
            print("Клик обработан")
        else:
            print("Клик проигнорирован")
            
    def update(self):
        self.interactor.update()

# Использование
def can_interact():
    return player.health > 0

interactor = ConditionalInteractor(sprite, can_interact)
```

## Интеграция с другими компонентами

### С компонентом Button

Класс `Button` уже использует `MouseInteractor` внутри, поэтому вам не нужно создавать его отдельно:

```python
button = s.Button(
    text="Нажми меня",
    on_click=lambda: print("Кнопка нажата")
)
# MouseInteractor уже создан внутри Button
```

### С компонентом ToggleButton

`ToggleButton` также использует `MouseInteractor`:

```python
toggle = s.ToggleButton(
    text="Переключатель",
    on_toggle=lambda state: print(f"Состояние: {state}")
)
```

## Важные нюансы

1. **Обновление в игровом цикле**: Всегда вызывайте `update()` в игровом цикле для правильной работы
2. **События**: Если не передаете события в `update()`, компонент автоматически использует `spritePro.pygame_events`
3. **Обнаружение столкновений**: Используется прямоугольное обнаружение столкновений (`rect.collidepoint`)
4. **Состояния**: `is_hovered` и `is_pressed` - это свойства, а не методы
5. **Обратные вызовы**: Все обратные вызовы вызываются без параметров

## Производительность

- MouseInteractor легковесен и эффективен
- Обнаружение столкновений основано на прямоугольниках для максимальной производительности
- Для большого количества интерактивных спрайтов рассмотрите использование пространственного разбиения

## Примеры использования

### Меню с наведением

```python
menu_items = []
menu_interactors = []

def create_menu_item(text, pos, action):
    sprite = s.Sprite("", size=(200, 50), pos=pos)
    sprite.set_color((100, 100, 100))
    
    interactor = s.MouseInteractor(
        sprite=sprite,
        on_click=action,
        on_hover_enter=lambda: sprite.set_color((150, 150, 150)),
        on_hover_exit=lambda: sprite.set_color((100, 100, 100))
    )
    
    menu_items.append(sprite)
    menu_interactors.append(interactor)
    return sprite, interactor

# Создать элементы меню
create_menu_item("Начать игру", (400, 200), start_game)
create_menu_item("Настройки", (400, 260), open_settings)
create_menu_item("Выход", (400, 320), exit_game)

# Обновить все в игровом цикле
while True:
    s.update()
    for interactor in menu_interactors:
        interactor.update()
```

### Инвентарь с перетаскиванием

```python
class DraggableItem:
    def __init__(self, sprite, pos):
        self.sprite = sprite
        self.sprite.position = pos
        self.dragging = False
        self.offset = (0, 0)
        
        self.interactor = s.MouseInteractor(
            sprite=sprite,
            on_mouse_down=self.start_drag,
            on_mouse_up=self.stop_drag
        )
        
    def start_drag(self):
        mouse_pos = pygame.mouse.get_pos()
        self.dragging = True
        self.offset = (
            mouse_pos[0] - self.sprite.x,
            mouse_pos[1] - self.sprite.y
        )
        
    def stop_drag(self):
        self.dragging = False
        
    def update(self):
        self.interactor.update()
        if self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            self.sprite.position = (
                mouse_pos[0] - self.offset[0],
                mouse_pos[1] - self.offset[1]
            )
```

## Базовое использование

```python
import spritePro as s

# Создать спрайт с взаимодействием мыши
sprite = s.Sprite("button.png", pos=(400, 300))

# Добавить взаимодействие мыши
mouse_handler = s.MouseInteractor(
    sprite=sprite,
    on_click=lambda: print("Спрайт кликнут!")
)

# Обновлять в игровом цикле
mouse_handler.update()
```

Для более подробной информации о связанных компонентах см.:
- [Документация по кнопкам](button.md) - Использование MouseInteractor в кнопках
- [Документация по спрайтам](sprite.md) - Базовые спрайты
