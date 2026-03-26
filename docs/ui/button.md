# Button (Кнопка)

Интерактивная UI-кнопка с эффектами наведения, анимациями и настраиваемым видом.

## Конструктор

```python
Button(sprite="", size=(250, 70), pos=(300, 200), text="Button", text_size=24, text_color=(0, 0, 0), font_name=None, on_click=None, sorting_order=1000, hover_scale_delta=0.05, press_scale_delta=-0.08, hover_color=(230, 230, 230), press_color=(180, 180, 180), base_color=(255, 255, 255), anim_speed=0.2, animated=True, use_scale_fx=True, use_color_fx=True, anchor=Anchor.CENTER, scene=None)
```

| Параметр | Тип | Описание |
|----------|-----|----------|
| `sprite` | str | Путь к фону (пусто = цветной) |
| `size` | tuple | Размер (ширина, высота) |
| `text` | str | Текст кнопки |
| `text_size` | int | Размер шрифта |
| `text_color` | tuple | Цвет текста |
| `on_click` | callable | Обработчик клика |

## Пример

```python
import spritePro as s

button = s.Button(
    text="Нажми меня!",
    pos=(400, 300),
    base_color=(100, 150, 255),
    hover_color=(120, 170, 255),
    on_click=lambda: print("Клик!")
)
```

## Визуальная настройка

```python
button = s.Button(
    text="Стилизованная",
    base_color=(50, 50, 150),
    hover_color=(70, 70, 170),
    press_color=(30, 30, 130),
    text_color=(255, 255, 255),
    hover_scale_delta=0.1,
    anim_speed=0.3,
)
```

## Цвета и масштабы

```python
button.set_base_color((100, 150, 255))
button.set_all_colors(base_color=(255, 255, 255), hover_color=(230, 230, 230), press_color=(180, 180, 180))
button.set_all_scales(base_scale=1.0, hover_scale=1.1, press_scale=0.95)
button.use_scale_fx = False  # Отключить масштабирование
button.use_color_fx = False  # Отключить смену цвета
```

## Обработка событий

```python
def click_handler():
    print("Кнопка нажата!")

button.on_click(click_handler)
button.on_hover(lambda: print("Наведён"))

# Цепочка
button.on_click(click_handler).on_hover(hover_handler).set_base_color((100, 150, 200))
```

## ToggleButton

```python
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

## Многострочный текст

```python
button = s.Button(
    text="Строка 1\nСтрока 2",
    size=(300, 120),
)
```

## Группы кнопок

```python
buttons = []
for i, text in enumerate(["Старт", "Настройки", "Выход"]):
    button = s.Button(
        text=text,
        pos=(400, 200 + i * 80),
        on_click=lambda t=text: handle_menu_click(t)
    )
    buttons.append(button)
```

## Доступ к компонентам

```python
text_sprite = button.text_sprite  # TextSprite
interactor = button.interactor    # MouseInteractor
button.set_scale(1.2, update=True)
button.set_active(False)  # Деактивировать
```

## Рекомендации

- Используйте группы кнопок для организации
- Отключайте неиспользуемые кнопки
- Кэшируйте объекты шрифтов

## См. также

- [ToggleButton](toggle_button.md)
- [Text](text.md)
- [MouseInteractor](mouse_interactor.md)
