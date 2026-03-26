# ToggleButton (Переключатель)

Класс `ToggleButton` расширяет Button, предоставляя переключение между состояниями ВКЛ/ВЫКЛ с разными цветами и текстовыми метками.

## Обзор

ToggleButton идеален для настроек, опций и любых бинарных элементов управления. Автоматически переключается между двумя состояниями с настраиваемым внешним видом.

## Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `sprite` | str | "" | Путь к фоновому изображению |
| `size` | (int, int) | (250, 70) | Размеры (ширина, высота) |
| `pos` | (int, int) | (300, 200) | Позиция |
| `text_on` | str | "ON" | Текст в состоянии ВКЛ |
| `text_off` | str | "OFF" | Текст в состоянии ВЫКЛ |
| `text_size` | int | 24 | Размер шрифта |
| `text_color` | (int,int,int) | (255,255,255) | Цвет текста |
| `font_name` | str | None | Путь к шрифту |
| `on_toggle` | callable | None | Обработчик переключения |
| `is_on` | bool | True | Начальное состояние |
| `color_on` | (int,int,int) | (50,150,50) | Цвет фона ВКЛ (зелёный) |
| `color_off` | (int,int,int) | (150,50,50) | Цвет фона ВЫКЛ (красный) |
| `hover_brightness` | float | 1.2 | Яркость при наведении |
| `press_brightness` | float | 0.8 | Яркость при нажатии |
| `anim_speed` | float | 0.2 | Скорость анимации |
| `animated` | bool | True | Включить анимации |
| `anchor` | Anchor | CENTER | Якорь позиционирования |
| `scene` | Scene | None | Сцена |

## Управление состоянием

```python
# Установить состояние напрямую
toggle.set_state(True)   # ВКЛ
toggle.set_state(False)  # ВЫКЛ

# Переключить программно
toggle.toggle()

# Проверить состояние
if toggle.is_on:
    print("Включено")
```

## Обработчики событий

```python
def handle_toggle(is_on: bool):
    if is_on:
        pygame.mixer.set_volume(1.0)
    else:
        pygame.mixer.set_volume(0.0)

sound_toggle = s.ToggleButton(
    text_on="Звук ВКЛ",
    text_off="Звук ВЫКЛ",
    on_toggle=handle_toggle
)
```

## Визуальная настройка

### Цвета
```python
settings_toggle = s.ToggleButton(
    text_on="Включено",
    text_off="Выключено",
    color_on=(0, 200, 0),     # Зелёный ВКЛ
    color_off=(200, 0, 0),    # Красный ВЫКЛ
    hover_brightness=1.3,
    press_brightness=0.7
)
```

### Динамическое обновление
```python
# Изменить цвета
toggle.set_colors(
    color_on=(255, 165, 0),    # Оранжевый
    color_off=(128, 128, 128)  # Серый
)

# Изменить текст
toggle.set_texts("✓ Активно", "✗ Неактивно")
```

## Пример: Панель настроек

```python
class SettingsPanel:
    def __init__(self):
        self.sound_toggle = s.ToggleButton(
            pos=(400, 200),
            text_on="Звук: ВКЛ",
            text_off="Звук: ВЫКЛ",
            color_on=(50, 200, 50),
            color_off=(200, 50, 50),
            on_toggle=self.on_sound_toggle
        )
        
        self.music_toggle = s.ToggleButton(
            pos=(400, 280),
            text_on="Музыка: ВКЛ",
            text_off="Музыка: ВЫКЛ",
            color_on=(50, 50, 200),
            color_off=(100, 100, 100),
            on_toggle=self.on_music_toggle
        )

    def on_sound_toggle(self, is_on: bool):
        pygame.mixer.set_volume(1.0 if is_on else 0.0)

    def on_music_toggle(self, is_on: bool):
        # Логика музыки
        pass
```

## Пример: Переключатели способностей

```python
# Переключатель силы
power_toggle = s.ToggleButton(
    pos=(100, 50),
    text_on="⚡ СИЛА",
    text_off="⚡ сила",
    size=(120, 40),
    color_on=(255, 255, 0),    # Жёлтый активен
    color_off=(100, 100, 50),
    on_toggle=lambda state: player.set_power_mode(state)
)

# Переключатель щита
shield_toggle = s.ToggleButton(
    pos=(100, 100),
    text_on="🛡️ ЩИТ",
    text_off="🛡️ щит",
    size=(120, 40),
    color_on=(0, 150, 255),    # Синий активен
    color_off=(50, 75, 125),
    on_toggle=lambda state: player.set_shield(state)
)
```

## Базовое использование

```python
import spritePro as s

toggle = s.ToggleButton(
    pos=(400, 300),
    text_on="ВКЛ",
    text_off="ВЫКЛ",
    is_on=True,
    on_toggle=lambda state: print(f"Состояние: {'ВКЛ' if state else 'ВЫКЛ'}")
)
```

## Методы

| Метод | Описание |
|-------|----------|
| `toggle()` | Переключить состояние |
| `set_state(is_on)` | Установить состояние |
| `set_colors(color_on, color_off)` | Изменить цвета |
| `set_texts(text_on, text_off)` | Изменить текст |

## Связанное

- [Button](button.md) — базовый класс
- [Sprite](sprite.md) — базовый класс
