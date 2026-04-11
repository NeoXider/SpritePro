# Build (Сборка)

## Что выбрать

| Цель | Инструмент |
|------|-----------|
| Desktop | `python main.py` или PyInstaller |
| Web | `pygbag` / `spritepro --webgl` |
| Android | `Kivy` + `Buildozer` |

## Сборка библиотеки

```bash
pip install --upgrade build
python -m build  # Результат в dist/
```

## Desktop

```python
s.run(scene=MainScene, platform="pygame")
```

### Сборка .exe

```bash
pip install pyinstaller
pyinstaller --windowed main.py  # Папка с проектом
```

## Web

### Установка

```bash
pip install pygbag
```

### Сборка

```bash
python -m pygbag . --build
```

Или через SpritePro:

```bash
pip install "spritepro[web]"
spritepro --webgl . --archive  # ZIP в build/web.zip
```

### Проверка

```bash
python -m pygbag .
# Открыть http://localhost:8000
```

## Mobile (Kivy)

### Установка

```bash
pip install "spritepro[kivy]"
```

### Локальная проверка

```bash
s.run(scene=MainScene, platform="kivy")
```

### Preview разных экранов

```bash
python -m spritePro.cli --preview main.py --platform kivy --screen phone-portrait
python -m spritePro.cli --preview main.py --platform kivy --screen tablet-landscape
python -m spritePro.cli --list-screen-presets
```

### Android сборка

Быстрый путь:

```bash
python -m spritePro.cli --android .
```

Ручной путь:

```bash
pip install buildozer "cython==0.29.33"
buildozer init
# Отредактировать buildozer.spec
buildozer android debug
```

### Проверенная конфигурация buildozer.spec

```ini
requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,pygame,pymunk,spritepro
android.archs = arm64-v8a
```

### Опции CLI

```bash
python -m spritePro.cli --android . --android-mode release
python -m spritePro.cli --android . --android-mode aab
python -m spritePro.cli --android . --android-orientation portrait
python -m spritePro.cli --android . --android-permission INTERNET
```

## Проверка APK

```bash
adb install -r bin/<apk>.apk
adb shell am start -n org.example.mygame/org.kivy.android.PythonActivity
adb logcat -d
```

## Важно для mobile

- Делайте UI и hitbox крупнее, чем на desktop
- Используйте `Path(__file__)` для путей к ассетам
- Проверяйте на реальном устройстве
- Для мультиплеера добавьте `android.permissions = INTERNET`

## Демо

```bash
python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
python -m spritePro.demoGames.kivy_hybrid_demo
```
