# Best Practices (Лучшие практики)

## Структура проекта

```
MyGame/
├── main.py              # Точка входа
├── config.py            # Настройки и пути
├── game_events.py       # EventBus события
├── assets/
│   ├── audio/
│   └── images/
├── scenes/
│   ├── main_scene.py
│   └── second_scene.py
└── game/
    ├── domain/
    └── services/
```

## Быстрый старт

```bash
python -m spritePro.cli --create MyGame
```

## Паттерны

### Сцены
```python
class MainScene(s.Scene):
    def on_enter(self, context):
        self.player = s.Sprite("player.png", (64, 64), s.WH_C, speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()
```

### Обработка ввода
```python
if s.input.was_pressed(pygame.K_SPACE):
    player.jump()

# Оси для геймпада
horizontal = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
```

### События
```python
s.events.connect("damage", self.on_damage)
s.events.send("damage", amount=10)
```

## Рекомендации

1. **Используйте сцены** для разделения меню и игры
2. **EventBus** для связи между компонентами
3. **Builder API** для читаемого создания спрайтов
4. **Твины** для анимаций вместо ручных расчётов
5. **Physics** через `s.add_physics()` вместо ручного управления
