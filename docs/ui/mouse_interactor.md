# MouseInteractor (Взаимодействие с мышью)

Компонент для добавления обработки мыши к спрайтам.

## Конструктор

```python
MouseInteractor(sprite, on_click=None, on_mouse_down=None, on_mouse_up=None, on_hover_enter=None, on_hover_exit=None)
```

| Параметр | Тип | Описание |
|----------|-----|----------|
| `sprite` | Sprite | Спрайт для прикрепления |
| `on_click` | callable | При клике на спрайт |
| `on_mouse_down` | callable | При нажатии |
| `on_mouse_up` | callable | При отпускании |
| `on_hover_enter` | callable | При входе мыши |
| `on_hover_exit` | callable | При выходе мыши |

## Свойства

```python
mouse_handler.is_hovered  # bool - мышь над спрайтом
mouse_handler.is_pressed  # bool - кнопка нажата на спрайте
```

## Методы

```python
mouse_handler.update()  # Обновить состояние (в игровом цикле)
```

## Примеры

```python
import spritePro as s

sprite = s.Sprite("button.png", pos=(400, 300))

mouse_handler = s.MouseInteractor(
    sprite=sprite,
    on_click=lambda: print("Клик!"),
    on_hover_enter=lambda: sprite.set_color((150, 200, 255)),
    on_hover_exit=lambda: sprite.set_color((255, 255, 255)),
    on_mouse_down=lambda: sprite.set_scale(0.95),
    on_mouse_up=lambda: sprite.set_scale(1.0),
)

# В игровом цикле
while True:
    s.update()
    mouse_handler.update()
```

## Интерактивная кнопка

```python
class InteractiveButton(s.Sprite):
    def __init__(self, image_path, pos, on_click_callback):
        super().__init__(image_path, pos=pos)
        self.interactor = s.MouseInteractor(
            sprite=self,
            on_click=on_click_callback,
            on_hover_enter=self.on_hover,
            on_hover_exit=self.on_hover_exit,
        )
        
    def on_hover(self):
        self.scale = 1.1
        
    def on_hover_exit(self):
        self.scale = 1.0
```

## Несколько спрайтов

```python
sprites = []
interactors = []

for i in range(5):
    sprite = s.Sprite(f"item_{i}.png", pos=(100 + i * 150, 300))
    interactor = s.MouseInteractor(
        sprite=sprite,
        on_click=lambda idx=i: print(f"Кликнут элемент {idx}"),
    )
    sprites.append(sprite)
    interactors.append(interactor)
```

## Примечание

Button и ToggleButton уже используют MouseInteractor внутри, создавать его отдельно не нужно.

## См. также

- [Button](button.md)
- [Sprite](sprite.md)
