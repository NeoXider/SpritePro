# Mobile With SpritePro

`SpritePro` сам управляет кадром и сам отрисовывает игру, поэтому для `Kivy` важнее не переписать игру, а просто дать движку другой render target и другой host loop. Теперь это встроено в API.

## Главная идея

Одна и та же игра может запускаться так:

```python
s.run(scene=MyScene, platform="pygame")
s.run(scene=MyScene, platform="kivy")
```

То есть `Kivy` стал способом запуска, а не отдельной ручной интеграцией.

## Новый простой API

- `spritePro.run(...)` — единая точка входа для desktop и `Kivy`
- `spritePro.run_kivy(...)` — короткий алиас для `Kivy`
- `spritePro.run_kivy_hybrid(...)` — high-level запуск hybrid-приложения: Kivy UI + встроенная область игры
- `spritePro.create_kivy_widget(...)` — создать SpritePro как обычный `Kivy`-виджет
- `spritePro.attach_surface(surface)` — подключение внешней поверхности
- `spritePro.update_embedded(...)` — один кадр без `pygame.display.update()`
- `spritePro.mobile.run_kivy_app(...)` — низкоуровневый запуск, если нужна ручная настройка host-приложения

## Full-screen по умолчанию

Сейчас режим по умолчанию для `Kivy` остаётся простым:

```python
s.run(scene=MyScene, platform="kivy")
```

То есть вся игра занимает приложение целиком.

## Hybrid режим: Kivy UI + встроенная игра

Если нужен верхний бар, кнопка `Back`, меню на `Kivy` и отдельная игровая область, используйте:

```python
s.run_kivy_hybrid(...)
```

или:

```python
game_widget = s.create_kivy_widget(...)
```

Подробная документация и примеры:

- [kivy_hybrid.md](kivy_hybrid.md)

## Минимум строк для Scene-игры

```python
import spritePro as s


class MyScene(s.Scene):
    def __init__(self):
        super().__init__()
        player = s.Sprite("", (80, 80), (200, 200), scene=self)
        player.set_rect_shape((80, 80), (80, 220, 255), border_radius=24)


s.run(
    scene=MyScene,
    title="My SpritePro Game",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

## Минимум строк для setup-игры без Scene

```python
import spritePro as s


def setup():
    player = s.Sprite("", (90, 90), s.WH_C)
    player.set_rect_shape((90, 90), (255, 180, 80), border_radius=24)


s.run(
    setup,
    title="My SpritePro Game",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

## Как перевести старую игру

Было:

```python
s.get_screen((800, 600), "Game")
s.set_scene(MyScene())

while True:
    s.update(fill_color=(20, 20, 30))
```

Стало:

```python
s.run(
    scene=MyScene,
    size=(800, 600),
    title="Game",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

Для desktop достаточно заменить `platform="kivy"` на `platform="pygame"` или просто не указывать его.

## Мобильное управление

Самый простой вариант — экранные `Button` в `screen_space`:

```python
left = s.Button("", (110, 110), (110, s.WH.y - 110), text="LEFT", scene=self)
left.set_screen_space(True)

if left.rect.collidepoint(s.input.mouse_pos) and s.input.is_mouse_pressed(1):
    player.rect.x -= 6
```

Это работает и мышью на desktop, и касанием внутри `Kivy`.

## Готовое демо

```bash
python -m spritePro.demoGames.mobile_orb_collector_demo --pygame
python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
python spritePro/demoGames/kivy_hybrid_demo.py
```

## Демо с `--kivy`

Сейчас в репозитории уже можно запускать через `Kivy` как минимум эти demo:

- `spritePro.demoGames.mobile_orb_collector_demo`
- `spritePro.demoGames.drag_drop_demo`
- `spritePro.demoGames.slider_textinput_demo`
- `spritePro.demoGames.pages_demo`
- `spritePro.demoGames.builder_demo`
- `spritePro.demoGames.particle_pool_demo`
- `spritePro.demoGames.three_clients_move_demo`

Для отдельного hybrid-сценария с внешним `Kivy` UI смотрите:

- `spritePro.demoGames.kivy_hybrid_demo`
