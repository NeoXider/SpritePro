# AudioManager - Управление звуком и музыкой

`AudioManager` предоставляет централизованное управление звуковыми эффектами и музыкой в SpritePro. Он автоматически создается при импорте библиотеки и доступен через `spritePro.audio_manager`.

## Быстрый старт

```python
import spritePro as s

# Получаем глобальный AudioManager
audio = s.audio_manager

# Загружаем звук
# Загружаем звук и сразу получаем объект Sound
bounce_sound = audio.load_sound("bounce", "sounds/bounce.mp3")

# Воспроизводим звук напрямую
audio.play_sound("bounce")

# Или используем объект Sound
bounce_sound.play()  # Воспроизвести с настройками AudioManager

# Воспроизводим музыку
audio.play_music("music/background.mp3")
```

## Основные методы

### Загрузка и воспроизведение звуков

#### `load_sound(name: str, path: str) -> Sound`

Загружает звуковой эффект и возвращает объект `Sound` для удобного использования.

**Параметры:**
- `name` (str): Имя звука для последующего использования
- `path` (str): Путь к файлу звука

**Возвращает:**
- `Sound`: Объект Sound для воспроизведения

**Пример:**
```python
# Сохраняем объект Sound при загрузке
jump_sound = audio.load_sound("jump", "sounds/jump.mp3")
coin_sound = audio.load_sound("coin", "sounds/coin.wav")

# Можно сразу использовать
jump_sound.play()

# Или в одну строку для быстрого воспроизведения
audio.load_sound("explosion", "sounds/explosion.mp3").play()
```

#### `play_sound(name_or_path: str, volume: float = None) -> None`

Воспроизводит звуковой эффект. Может воспроизвести звук по имени (если он был загружен) или напрямую по пути к файлу (автоматически загрузит и воспроизведет).

**Параметры:**
- `name_or_path` (str): Имя звука (загруженного через `load_sound()`) или путь к файлу звука
- `volume` (float, optional): Громкость (0.0 - 1.0). Если `None`, используется `sfx_volume`

**Пример:**
```python
# Воспроизведение загруженного звука
audio.load_sound("bounce", "sounds/bounce.mp3")
audio.play_sound("bounce")

# Прямое воспроизведение по пути (без предварительной загрузки!)
audio.play_sound("sounds/jump.mp3")
audio.play_sound("sounds/coin.wav", volume=0.8)
```

### Управление музыкой

#### `play_music(path: str, loop: bool = True, volume: float = None) -> None`

Воспроизводит музыку из файла.

**Параметры:**
- `path` (str): Путь к файлу музыки
- `loop` (bool): Зациклить ли музыку. По умолчанию `True`
- `volume` (float, optional): Громкость (0.0 - 1.0). Если `None`, используется `music_volume`

**Пример:**
```python
audio.play_music("music/background.mp3")  # Зацикленная музыка
audio.play_music("music/intro.mp3", loop=False, volume=0.7)  # С указанной громкостью
audio.play_music("music/background.mp3", volume=0.5)  # Сразу с нужной громкостью!
```

#### `stop_music() -> None`

Останавливает воспроизведение музыки.

**Пример:**
```python
audio.stop_music()
```

#### `pause_music() -> None`

Приостанавливает воспроизведение музыки.

**Пример:**
```python
audio.pause_music()
```

#### `unpause_music() -> None`

Возобновляет воспроизведение музыки.

**Пример:**
```python
audio.unpause_music()
```

### Управление громкостью

#### `set_music_volume(volume: float) -> None`

Устанавливает громкость музыки (0.0 - 1.0).

**Параметры:**
- `volume` (float): Громкость (автоматически ограничивается диапазоном 0.0 - 1.0)

**Пример:**
```python
audio.set_music_volume(0.3)  # 30% громкости
audio.set_music_volume(1.0)  # 100% громкости
```

#### `set_sfx_volume(volume: float) -> None`

Устанавливает громкость звуковых эффектов (0.0 - 1.0).

**Параметры:**
- `volume` (float): Громкость (автоматически ограничивается диапазоном 0.0 - 1.0)

**Пример:**
```python
audio.set_sfx_volume(0.8)  # 80% громкости
```

**Примечание:** Изменение `sfx_volume` автоматически обновляет громкость всех загруженных звуков.

### Включение/выключение звука

#### `set_music_enabled(enabled: bool) -> None`

Включает или выключает музыку.

**Параметры:**
- `enabled` (bool): `True` для включения, `False` для выключения

**Пример:**
```python
audio.set_music_enabled(False)  # Выключить музыку
audio.set_music_enabled(True)   # Включить музыку
```

#### `set_sfx_enabled(enabled: bool) -> None`

Включает или выключает звуковые эффекты.

**Параметры:**
- `enabled` (bool): `True` для включения, `False` для выключения

**Пример:**
```python
audio.set_sfx_enabled(False)  # Выключить звуки
```

#### `get_sound(name: str) -> Sound | None`

Получает обертку `Sound` для удобного использования звука.

**Параметры:**
- `name` (str): Имя звука, загруженного через `load_sound()`

**Возвращает:**
- `Sound | None`: Обертка над звуком или `None`, если звук не найден

**Пример:**
```python
bounce_sound = audio.load_sound("bounce", "sounds/bounce.mp3")
bounce_sound.play()  # Воспроизвести с настройками AudioManager
```

## Класс Sound

Обертка над звуком в AudioManager для удобного использования. Позволяет сохранять звуки в переменные и воспроизводить их с автоматическим применением настроек AudioManager.

### Методы

#### `play(volume: float = None) -> None`

Воспроизводит звук через AudioManager с применением текущих настроек.

**Параметры:**
- `volume` (float, optional): Громкость (0.0 - 1.0). Если `None`, используется `sfx_volume` из AudioManager

**Пример:**
```python
bounce_sound = audio.load_sound("bounce", "sounds/bounce.mp3")
bounce_sound.play()  # С настройками AudioManager
bounce_sound.play(volume=0.5)  # С переопределенной громкостью
```

### Свойства

#### `name: str`
Имя звука в AudioManager.

#### `sound: pygame.mixer.Sound | None`
Прямой доступ к `pygame.mixer.Sound` (если нужен для расширенного использования).

## Атрибуты

### `music_volume: float`
Громкость музыки (0.0 - 1.0). По умолчанию `0.5`.

### `sfx_volume: float`
Громкость звуковых эффектов (0.0 - 1.0). По умолчанию `1.0`.

### `music_enabled: bool`
Включена ли музыка. По умолчанию `True`.

### `sfx_enabled: bool`
Включены ли звуковые эффекты. По умолчанию `True`.

### `sounds: dict[str, pygame.mixer.Sound]`
Словарь загруженных звуков. Не рекомендуется изменять напрямую.

### `current_music: str | None`
Путь к текущей музыке или `None`, если музыка не воспроизводится.

## Полный пример

```python
import spritePro as s

# Инициализация
screen = s.get_screen((800, 600), "Audio Demo")

# Получаем AudioManager
audio = s.audio_manager

# Настраиваем громкость
audio.set_music_volume(0.4)
audio.set_sfx_volume(1.0)

# Загружаем звуки и сразу получаем объекты Sound
jump_sound = audio.load_sound("jump", "sounds/jump.mp3")
coin_sound = audio.load_sound("coin", "sounds/coin.wav")
bounce_sound = audio.load_sound("bounce", "sounds/bounce.mp3")

# Воспроизводим музыку
audio.play_music("music/background.mp3")

# Создаем кнопки для управления
music_toggle = s.ToggleButton(
    "",
    size=(150, 40),
    pos=(100, 50),
    text_on="Music: ON",
    text_off="Music: OFF",
    on_toggle=lambda is_on: audio.set_music_enabled(is_on)
)

sfx_toggle = s.ToggleButton(
    "",
    size=(150, 40),
    pos=(100, 100),
    text_on="SFX: ON",
    text_off="SFX: OFF",
    on_toggle=lambda is_on: audio.set_sfx_enabled(is_on)
)

# Игровой цикл
while True:
    s.update(fill_color=(20, 20, 30))
    
    # Воспроизводим звуки при нажатии клавиш
    for event in s.events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                audio.play_sound("jump")
            elif event.key == pygame.K_c:
                audio.play_sound("coin")
```

## Пример из ping_pong.py

```python
import spritePro as s

# Получаем AudioManager
audio = s.audio_manager

# Инициализация звуков
def create_music():
    global bounce_sound
    audio.set_music_volume(0.4)
    audio.set_sfx_volume(1.0)
    audio.play_music(str(path / "Audio" / "fon_musik.mp3"))
    # Загружаем звук и сразу получаем объект Sound
    bounce_sound = audio.load_sound("bounce", str(path / "Audio" / "baunch.mp3"))

# Воспроизведение звука при столкновении
def ball_bounch():
    if ball.rect.top <= 0:
        bounce_sound.play()  # Используем обертку Sound
        ball.dir_y = 1

# Переключение музыки
def music_toggle(is_on: bool):
    audio.set_music_enabled(is_on)
    bounce_sound.play()  # Звук подтверждения

# Переключение звуков
def audio_toggle(is_on: bool):
    audio.set_sfx_enabled(is_on)
    bounce_sound.play()  # Звук подтверждения
```

## Поддерживаемые форматы

AudioManager использует `pygame.mixer`, который поддерживает следующие форматы:
- **Звуки**: WAV, OGG, MP3 (зависит от системы)
- **Музыка**: MP3, OGG, MID, MOD, WAV (зависит от системы)

**Рекомендация:** Для звуковых эффектов используйте WAV или OGG для лучшей производительности. Для музыки - MP3 или OGG.

## Обработка ошибок

AudioManager автоматически обрабатывает ошибки загрузки файлов и выводит предупреждения в консоль:

```python
# Если файл не найден, будет выведено предупреждение
audio.load_sound("missing", "nonexistent.mp3")
# Output: Error loading sound 'missing' from 'nonexistent.mp3': ...

# Если звук не загружен, будет выведено предупреждение
audio.play_sound("not_loaded")
# Output: Sound 'not_loaded' not found. Load it first with load_sound().
```

## Советы по использованию

1. **Загружайте звуки один раз** при инициализации игры, а не каждый кадр
2. **Используйте имена звуков** вместо прямых путей для удобства
3. **Настраивайте громкость** в зависимости от типа звука (музыка обычно тише)
4. **Проверяйте включение звука** перед воспроизведением (AudioManager делает это автоматически)
5. **Используйте переключатели** для удобного управления звуком в настройках игры

## Интеграция с ToggleButton

AudioManager отлично работает с `ToggleButton` для создания переключателей звука:

```python
music_toggle = s.ToggleButton(
    "",
    size=(150, 40),
    pos=(100, 50),
    text_on="Music: ON",
    text_off="Music: OFF",
    on_toggle=lambda is_on: s.audio_manager.set_music_enabled(is_on)
)
```

