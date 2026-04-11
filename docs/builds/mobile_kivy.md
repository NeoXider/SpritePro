# Mobile (Мобильная разработка)

## Главная идея

Одна и та же игра запускается на desktop и mobile:

```python
s.run(scene=MyScene, platform="pygame")   # Desktop
s.run(scene=MyScene, platform="kivy")     # Mobile
```

## Установка

```bash
pip install "spritepro[kivy]"
```

## Минимальный пример

```python
import spritePro as s

class MyScene(s.Scene):
    def __init__(self):
        super().__init__()
        player = s.Sprite("", (80, 80), (200, 200), scene=self)
        player.set_rect_shape((80, 80), (80, 220, 255), border_radius=24)

s.run(scene=MyScene, title="My Game", fill_color=(20, 20, 30), platform="kivy")
```

## Полноэкранный запуск

```python
s.run(scene=MyScene, platform="kivy")
```

## Hybrid: Kivy UI + игра

Если нужен верхний бар, кнопка Back, меню:

```python
s.run_kivy_hybrid(scene=MyScene, root_builder=build_root, ...)
```

Подробнее: [kivy_hybrid.md](kivy_hybrid.md)

## Пути к ассетам

Используйте `Path(__file__)` для корректных путей:

```python
from pathlib import Path
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
player = s.Sprite(str(ASSETS_DIR / "player.png"), (96, 96), s.WH_C, scene=self)
```

## Preview на разных экранах

```bash
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --list-screen-presets
```

## Android сборка

```bash
python -m spritePro.cli --android .
```

Или вручную:

```bash
pip install buildozer "cython==0.29.33"
buildozer init
buildozer android debug
```

### buildozer.spec

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
orientation = landscape
```

## Демо

```bash
python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
python spritePro/demoGames/kivy_hybrid_demo.py
```
