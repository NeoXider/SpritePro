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

## Установка mobile-зависимостей

Если вы ставите библиотеку из `pip`:

```bash
pip install "spritepro[kivy]"
```

Если вы работаете из исходников:

```bash
pip install -e ".[kivy]"
```

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

## Пути к ассетам: делайте явно через `Path(__file__)`

Если игра должна одинаково работать в `pygame` и `kivy`, не полагайтесь на текущую рабочую папку и не пишите пути вроде `"spritePro\\demoGames\\Sprites\\hero.png"` или `"assets/player.png"` как "магическую" строку без привязки к файлу.

Правильный и явный вариант:

```python
from pathlib import Path
import spritePro as s


ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "images"


def asset_path(name: str) -> str:
    return str((ASSETS_DIR / name).resolve())


class MyScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite(
            asset_path("player.png"),
            (96, 96),
            s.WH_C,
            scene=self,
        )
```

Почему именно так:

- путь считается от текущего `.py` файла, а не от папки, из которой вы запустили Python
- один и тот же код стабильно работает в `pygame`, `kivy` и в будущей упаковке проекта
- это особенно важно для mobile/hybrid-сценариев, где host-приложение может запускать игру не из той директории, на которую вы рассчитывали

Рекомендуемое правило:

- для изображений, звуков, JSON-сцен и шрифтов используйте `Path(__file__).resolve()`
- передавайте в `SpritePro` уже нормализованный путь через `str(...)`

## Как тестировать на разных экранах

До сборки на телефон полезно прогнать игру на нескольких размерах окна прямо на ПК.

Самый быстрый путь теперь через CLI:

```bash
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen phone-tall
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --preview main.py --platform pygame --size 412x915
python -m spritePro.cli --list-screen-presets
```

Что делает `--preview`:

- запускает указанный `main.py` или папку проекта с `main.py`
- временно подменяет размер окна
- может быстро переключать `pygame` / `kivy` для игр на `s.run(...)`
- добавляет в title подпись вида `[kivy 360x640]`, чтобы не путать окна

Важно:

- переключение платформы через CLI рассчитано на современные игры, которые запускаются через `s.run(...)`
- если проект использует старый ручной цикл с `s.get_screen(...)`, override размера сработает, но автоматическое переключение на `kivy` через CLI не гарантируется

Что происходит при resize в `Kivy`:

- `s.WH` и `s.WH_C` обновляются под новый размер окна/виджета
- но уже созданные спрайты, панели и текст не перестраиваются автоматически только потому, что когда-то были созданы через `s.WH` или `s.WH_C`
- если нужен настоящий adaptive layout, пересчитывайте позиции и размеры от текущих `s.WH` / `s.WH_C` после resize

Минимальный пример:

```python
import spritePro as s


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("", (96, 96), s.WH_C, scene=self)
        self.player.set_rect_shape((96, 96), (90, 210, 255), border_radius=24)


s.run(
    scene=MainScene,
    size=(360, 640),
    title="Mobile Preview",
    fill_color=(20, 20, 30),
    platform="kivy",
)
```

Полезные размеры для быстрой проверки:

- `size=(360, 640)` — маленький portrait
- `size=(412, 915)` — высокий portrait
- `size=(640, 360)` — compact landscape
- `size=(1280, 720)` — большой landscape / tablet preview

Практика:

- сначала прогоните игру в `platform="pygame"`
- потом те же размеры прогоните в `platform="kivy"`
- сравните layout, размер кнопок, позиционирование и touch-friendly UI

Что проверять:

- опирается ли UI на `s.WH` и `s.WH_C` корректно
- не обрезаются ли панели, текст и кнопки
- удобны ли hitbox для пальца
- не выглядят ли ассеты слишком мелкими или слишком крупными
- нормально ли игра переживает portrait/landscape-сценарии
- не осталось ли объектов, которые были один раз выставлены в `__init__` от старого `s.WH_C` и больше не обновляются

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

Для быстрой Android-сборки через CLI и ручного `Buildozer` смотрите:

- [building.md](building.md)
