# Audio (Звук и музыка)

Централизованное управление звуковыми эффектами и музыкой.

## Быстрый старт

```python
import spritePro as s

audio = s.audio_manager

# Загрузка звука
jump_sound = audio.load_sound("jump", "sounds/jump.mp3")

# Воспроизведение
jump_sound.play()
audio.play_sound("sounds/jump.mp3")  # Прямо по пути
```

## Звуки

```python
audio.load_sound("bounce", "sounds/bounce.mp3")
audio.play_sound("bounce")
audio.play_sound("sounds/explosion.mp3", volume=0.8)
```

## Музыка

```python
audio.play_music("music/background.mp3")           # Зацикленная
audio.play_music("music/intro.mp3", loop=False)    # Одна
audio.play_music("music/intro.mp3", volume=0.5)    # С громкостью

audio.stop_music()
audio.pause_music()
audio.unpause_music()
```

## Громкость

```python
audio.set_music_volume(0.3)  # 30%
audio.set_sfx_volume(0.8)    # 80%
audio.set_music_enabled(False)  # Выключить музыку
audio.set_sfx_enabled(False)   # Выключить звуки
```

## Sound (обёртка)

```python
bounce = audio.load_sound("bounce", "sounds/bounce.mp3")
bounce.play()              # С настройками AudioManager
bounce.play(volume=0.5)   # С переопределением громкости
```

## Полный пример

```python
import spritePro as s

audio = s.audio_manager
audio.set_music_volume(0.4)
audio.set_sfx_volume(1.0)

jump_sound = audio.load_sound("jump", "sounds/jump.mp3")
coin_sound = audio.load_sound("coin", "sounds/coin.wav")

audio.play_music("music/background.mp3")

# В игре
if s.input.was_pressed(pygame.K_SPACE):
    jump_sound.play()
```

## Поддерживаемые форматы

- **Звуки**: WAV, OGG, MP3
- **Музыка**: MP3, OGG, MID, MOD, WAV

## Рекомендации

- Загружайте звуки один раз при инициализации
- Для звуков используйте WAV или OGG
- Для музыки — MP3 или OGG

## ToggleButton для звука

```python
music_toggle = s.ToggleButton(
    "", (150, 40), (100, 50),
    text_on="Music: ON", text_off="Music: OFF",
    on_toggle=lambda is_on: audio.set_music_enabled(is_on)
)
```
