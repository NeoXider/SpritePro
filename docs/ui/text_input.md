# TextInput (Поле ввода текста)

Поле ввода текста на базе Button. Наследует от Button, при клике переходит в режим ввода (focus); поддерживает типы **text** / **int** / **float**, `pygame.TEXTINPUT`, Enter (подтверждение), Escape (сброс фокуса), **Ctrl+V** (вставка) и **Ctrl+C** (копирование содержимого поля).

## Обзор

- **Наследование**: `TextInput(Button)` — кнопка без анимаций, при клике активирует ввод.
- **Тип поля**: `input_type`: **"text"** (любой печатный текст), **"int"** (целые числа), **"float"** (дробные). Для int/float некорректные символы не вводятся и отфильтровываются при вставке; при необходимости задают границы `min_val` / `max_val`.
- **События**: **on_change** — при каждом изменении текста; **on_submit** — при нажатии Enter.
- **Обработка в цикле**: обрабатывает клик, `KEYDOWN` (Enter, Escape, Backspace, Ctrl+V/Ctrl+C, цифровая клавиатура), `TEXTINPUT`; события из `spritePro.pygame_events` в `update()`.

## Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `size` | (int, int) | (200, 36) | Размер поля |
| `pos` | (int, int) | (100, 100) | Позиция |
| `placeholder` | str | "" | Текст-подсказка при пустом значении |
| `value` | str | "" | Начальное значение |
| `max_length` | int | 128 | Максимальная длина |
| `input_type` | "text" \| "int" \| "float" | "text" | Тип поля: текст, целое или дробное число |
| `min_val` | float \| None | None | Нижняя граница для int/float (при парсинге) |
| `max_val` | float \| None | None | Верхняя граница для int/float (при парсинге) |
| `on_change` | Callable[[str], None] | None | Вызывается при каждом изменении текста |
| `on_submit` | Callable[[str], None] | None | Вызывается при нажатии Enter |
| `text_color` | (int,int,int) | (200,200,200) | Цвет текста |
| `bg_color` | (int,int,int) | (45,45,52) | Цвет фона |
| `active_bg_color` | (int,int,int) | (55,55,62) | Цвет фона при фокусе |
| `font_size` | int | 18 | Размер шрифта |
| `sorting_order` | int | 1000 | Слой отрисовки |
| `scene` | Scene \| str \| None | None | Сцена |

## Типы поля (input_type)

- **text** — допускаются любые печатные символы, пробел и табуляция. Подходит для имён, сообщений.
- **int** — только цифры и один минус в начале. Точка и запятая не вводятся; при вставке из буфера лишние символы отфильтровываются.
- **float** — цифры, один минус в начале, одна десятичная точка (запятая при вставке заменяется на точку).

Для числовых полей при применении (например в `on_submit`) удобно парсить значение через модуль **spritePro.input_validation**: `parse_input_value(input_type, raw, min_val, max_val)` возвращает `(ok, value)`.

## Пример

```python
import spritePro as s
from spritePro.input_validation import parse_input_value

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
        self.num_input = s.TextInput(
            pos=(s.WH_C.x, 260),
            value="0",
            input_type="int",
            min_val=0,
            max_val=100,
            on_submit=self._on_number_submit,
            scene=self,
        )

    def _on_change(self, value: str) -> None:
        print("Текст:", value)

    def _on_submit(self, value: str) -> None:
        print("Отправлено:", value)

    def _on_number_submit(self, value: str) -> None:
        ok, num = parse_input_value("int", value, 0, 100)
        if ok and num is not None:
            print("Число:", num)
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
- **Ctrl+V** (Cmd+V на Mac) — вставка из буфера обмена; для int/float вставляются только допустимые символы.
- **Ctrl+C** (Cmd+C на Mac) — копирование содержимого поля в буфер обмена.
- **TEXTINPUT** и цифровая клавиатура — добавление символов (для int/float только допустимые, с учётом `max_length`).

## Методы

- **set_value(value)** — установить текст (обрезается по `max_length`), обновляет отображение и вызывает `on_change`.
- **activate()** — включить режим ввода (фокус).
- **deactivate()** — выключить режим ввода.
- **handle_event(event)** — обработать событие pygame; возвращает `True`, если событие потреблено. В сцене вызывается автоматически из `update()` через `pygame_events`.

## Связанное

- [Button](button.md) — базовая кнопка.
- [Slider](slider.md) — слайдер.
- [Input](input.md) — состояние клавиш и мыши.
- Модуль **spritePro.input_validation** — `InputType`, `can_add_char`, `filter_chars_for_paste`, `parse_input_value` для типизированного ввода и парсинга (используется TextInput и редактором сцен).
