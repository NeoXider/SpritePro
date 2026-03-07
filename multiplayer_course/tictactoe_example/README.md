# Пример: Крестики-нолики (пошаговый мультиплеер)

Полноценная turn-based сетевая игра на SpritePro. Показывает:

- Синхронизацию состояния доски через `ctx.send()` / `ctx.poll()`
- Разделение ролей: хост = X, клиент = O
- Обработку событий `move` и `reset`
- UI на SpritePro: Layout (сетка), Sprite, TextSprite, Button
- Сцены для структуры кода

## Запуск

```bash
# Обычный запуск
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py

# Быстрый запуск для разработки (хост + клиент в двух окнах)
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py --quick

# С указанием хоста и порта
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py --quick --host 127.0.0.1 --port 5050
```

Внутри сам пример уже использует современный scene-based запуск через `s.run(...)`.
Если в своей игре нужен пользовательский вход без quick-режима, можно строить поверх встроенного лобби:

```python
s.networking.run(use_lobby=True)
```

## Управление

- **ЛКМ** — поставить X или O в свободную ячейку (если ваш ход)
- **R** или кнопка «Новая игра» — перезапуск партии
