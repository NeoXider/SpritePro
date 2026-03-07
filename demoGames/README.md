# demoGames — сцена из редактора и физика

Пример запуска игры, сцена которой сделана в **Sprite Editor** (level.json). Показывает, как получать и настраивать физику объектов из сцены в коде.

## Запуск

Из **корня репозитория** SpritePro:

```bash
python demoGames/main.py
```

Либо установить пакет в режиме разработки и запускать из любой папки:

```bash
pip install -e .
python -c "import spritePro; print(spritePro.__file__)"
python demoGames/main.py
```

## Что внутри

- **main.py** — точка входа: запуск через `s.run(...)`, сцена `MainScene`.
- **scenes/main_scene.py** — загрузка сцены через `spawn_scene("scenes/level.json", scene=self)`, получение игрока по имени, настройка физики в коде.
- **scenes/level.json** — сцена, собранная в редакторе (объект `player` с типом физики Dynamic, платформы `rect*` и т.д.).
- **config.py** — размер окна, FPS, скорость и высота прыжка.

## Физика из сцены редактора

1. В редакторе у объекта (например, player) выставляется **Physics: Dynamic** (и при необходимости Mass, Friction, Bounce).
2. При загрузке `spawn_scene` таким объектам автоматически создаётся тело и они добавляются в `s.physics`.
3. В коде тело получаем через **`s.get_physics(sprite)`** и донастраиваем:
   - `body.set_bounce(0)` — без отскока при приземлении (как в Geometry Dash);
   - `body.velocity.x = config.SPEED` — горизонтальная скорость;
   - в `update()` по Space: `body.velocity.y = -config.JUMP` — прыжок.

Подробнее: [docs/physics.md](../docs/physics.md) (раздел «Получение и настройка физики из сцены редактора»).
