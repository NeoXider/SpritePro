# TextInput

Поле ввода текста на базе Button. Наследует от Button, при клике переходит в режим ввода (focus); поддерживает `pygame.TEXTINPUT`, Enter (подтверждение) и Escape (сброс фокуса).

## Обзор

- **Наследование**: `TextInput(Button)` — кнопка без анимаций, при клике активирует ввод.
- **События**: **on_change** — при каждом изменении текста (ввод/удаление символа); **on_submit** — при нажатии Enter (применение/подтверждение).
- **Обработка в цикле**: обрабатывает клик (фокус/сброс), `KEYDOWN` (Enter, Escape, Backspace, цифровая клавиатура), `TEXTINPUT` (символы); события берутся из `spritePro.pygame_events` в `update()`.

## Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `size` | (int, int) | (200, 36) | Размер поля |
| `pos` | (int, int) | (100, 100) | Позиция |
| `placeholder` | str | "" | Текст-подсказка при пустом значении |
| `value` | str | "" | Начальное значение |
| `max_length` | int | 128 | Максимальная длина |
| `on_change` | Callable[[str], None] | None | Вызывается при каждом изменении текста (ввод/удаление символа) |
| `on_submit` | Callable[[str], None] | None | Вызывается при нажатии Enter (применение/подтверждение) |
| `text_color` | (int,int,int) | (200,200,200) | Цвет текста |
| `bg_color` | (int,int,int) | (45,45,52) | Цвет фона |
| `active_bg_color` | (int,int,int) | (55,55,62) | Цвет фона при фокусе |
| `font_size` | int | 18 | Размер шрифта |
| `sorting_order` | int | 1000 | Слой отрисовки |
| `scene` | Scene \| str \| None | None | Сцена |

## Пример

```python
import spritePro as s

class FormScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.input = s.TextInput(
            size=(280, 36),
            pos=(s.WH_C.x, 200),
            placeholder="Введите имя...",
            value="",
            max_length=32,
            on_change=self._on_change,
            on_submit=self._on_submit,
            scene=self,
        )

    def _on_change(self, value: str) -> None:
        print("Текст:", value)

    def _on_submit(self, value: str) -> None:
        print("Отправлено:", value)
```

## События: изменение и применение

- **on_change(value)** — вызывается при любом изменении текста (добавление символа, Backspace). Подходит для валидации или подсказок в реальном времени.
- **on_submit(value)** — вызывается при нажатии Enter; поле теряет фокус, передаётся итоговое значение. Подходит для «применить» / «готово».

## Управление

- **Клик по полю** — активация ввода (фокус), курсор «|».
- **Клик вне поля** — сброс фокуса (если обрабатываете клики снаружи).
- **Enter** — сброс фокуса и вызов `on_submit(value)`.
- **Escape** — сброс фокуса без вызова `on_submit`.
- **Backspace** — удаление последнего символа.
- **TEXTINPUT** и цифровая клавиатура — добавление символов (с учётом `max_length`).

## Методы

- **set_value(value)** — установить текст (обрезается по `max_length`), обновляет отображение и вызывает `on_change`.
- **activate()** — включить режим ввода (фокус).
- **deactivate()** — выключить режим ввода.
- **handle_event(event)** — обработать событие pygame; возвращает `True`, если событие потреблено. В сцене вызывается автоматически из `update()` через `pygame_events`.

## Связанное

- [Button](button.md) — базовая кнопка.
- [Slider](slider.md) — слайдер.
- [Input](input.md) — состояние клавиш и мыши.
