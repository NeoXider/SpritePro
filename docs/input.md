# Ввод и события

## InputState (как в Unity)

SpritePro предоставляет `s.input` для получения состояния клавиш каждый кадр:

```python
import pygame
import spritePro as s

s.get_screen((800, 600), "Input Example")

while True:
    s.update()

    if s.input.was_pressed(pygame.K_SPACE):
        print("Space pressed")

    if s.input.is_pressed(pygame.K_a):
        print("A is held")

    if s.input.was_released(pygame.K_ESCAPE):
        print("Escape released")

    horizontal = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
```

Также доступны состояния мыши:
- `s.input.is_mouse_pressed(button)`
- `s.input.was_mouse_pressed(button)`
- `s.input.was_mouse_released(button)`
- `s.input.mouse_pos`, `s.input.mouse_rel`, `s.input.mouse_wheel`

## EventBus

Для подписки на события используйте `s.events`:

```python
import spritePro as s

def on_quit(event):
    print("Quit requested")

def on_key_down(key, event):
    print("Key down:", key)

s.events.on("quit", on_quit)
s.events.on("key_down", on_key_down)
```

Доступные события:
- `quit`
- `key_down`, `key_up`
- `mouse_down`, `mouse_up`

## Сырые события pygame

Если нужен прямой доступ к событиям pygame, используйте `s.pygame_events`.
