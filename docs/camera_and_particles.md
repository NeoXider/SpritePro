# Камера и система частиц SpritePro

## 🔭 Управление камерой

SpritePro автоматически создаёт `SpriteProGame` с глобальной камерой. Основные функции доступны через `spritePro`:

- `s.process_camera_input(speed=250.0, keys=None, mouse_drag=False)` — обрабатывает клавиатуру/мышь и смещает камеру.
- `s.set_camera_position(x, y)` и `s.move_camera(dx, dy)` — прямое управление.
- `s.set_camera_follow(sprite, offset=(0, 0))` — режим слежения за спрайтом (например, за игроком). Смещение задаётся в мировых координатах.
- `s.clear_camera_follow()` — возвращает ручное управление.
- `s.get_camera_position()` — текущая позиция камеры.

Вызов `s.update(...)` внутри игрового цикла автоматически обновляет время, события, камеру и все зарегистрированные спрайты, поэтому ручных вызовов `get_game().update(...)` больше не требуется.

## 🌟 Частицы

Модуль `spritePro.particles` содержит простую систему частиц:

```python
from spritePro.particles import ParticleEmitter, ParticleConfig

config = ParticleConfig(
    amount=80,
    size_range=(4, 7),
    speed_range=(80, 200),
    lifetime_range=(500, 900),
    colors=[(255, 200, 40), (255, 120, 200)],
)
emitter = ParticleEmitter(config)

# В любой момент:
emitter.emit((player.rect.centerx, player.rect.centery))
```

`ParticleConfig` управляет всеми параметрами: количеством частиц, размерами, скоростью, временем жизни, гравитацией, списком цветов и т.д. При необходимости можно задать `custom_factory`, чтобы программно модифицировать каждую частицу.

Каждая частица — полноценный `Sprite`, поэтому она учитывает камеру. Для HUD-частиц можно установить `screen_space=True`.

## 📌 Закрепление и позиционирование UI

Все спрайты поддерживают метод `set_screen_space(True)`, который фиксирует объект к экрану. Для позиционирования добавлен `Sprite.set_position(...)` с поддержкой якорей (`center`, `topleft`, `midbottom` и т.д.).

По умолчанию спрайты мировые (`screen_space=False`), а `Button` и `TextSprite` автоматически закрепляются на экране, что облегчает создание интерфейсов.

## 🧱 Иерархия спрайтов

- Используйте `sprite.set_parent(parent)` чтобы прикрепить один спрайт к другому.
- Параметр `keep_world_position` позволяет сохранить мировые координаты или принять локальные.
- При перемещении родителя его дети автоматически следуют за ним; локальный сдвиг хранится в `local_offset`.
- `set_screen_space(True)` у родителя фиксирует всех его детей на экране.
- Для точного позиционирования применяйте `set_position(position, anchor=spritePro.Anchor.TOP_LEFT)` и другие якоря из `spritePro.Anchor`.
