# Pages

`Page` и `PageManager` — лёгкая система экранов внутри сцены.  
Страница хранит список спрайтов и сама включает/выключает их без лишнего кода.

## Быстрый старт

```python
import spritePro as s

class MenuPage(s.Page):
    def __init__(self, scene=None):
        super().__init__("menu", scene=scene)
        self.add_sprite(s.TextSprite("Menu", 48, pos=(400, 40), scene=scene))
        self.add_sprite(s.Button(text="Start", pos=(400, 300)))

class GamePage(s.Page):
    def __init__(self, scene=None):
        super().__init__("game", scene=scene)
        self.add_sprite(s.TextSprite("Game", 48, pos=(400, 40), scene=scene))

class PagesScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.pages = s.PageManager(scene=self)
        self.pages.add_page(MenuPage(scene=self))
        self.pages.add_page(GamePage(scene=self))
        self.pages.set_active_page("menu")

    def update(self, dt):
        self.pages.update()
```

## API

### Page
- `Page(name, scene=None)` — создаёт страницу.
- `set_active(True/False)` — включает/выключает страницу (спрайты тоже).
- `add_sprite(sprite, use_scene=True)` — добавляет спрайт на страницу.
- `add_sprites(*sprites, use_scene=True)` — добавить несколько спрайтов.
- `remove_sprite(sprite)` — удалить спрайт со страницы.
- `is_active()` — активна ли страница.

### PageManager
- `PageManager(scene=None)` — менеджер страниц.
- `add_page(page)` — добавить страницу.
- `set_active_page(name)` — активировать страницу.
- `get_active_page()` — активная страница.
- `set_scene(scene)` — назначить сцену всем страницам.
- `update()` — обновить активную страницу.

## Примечания
- Если `scene` задана, `add_sprite()` автоматически привяжет спрайт к этой сцене.
- Страницы можно использовать и без сцен — тогда просто управляется активность спрайтов.
