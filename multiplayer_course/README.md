# Курс по мультиплееру на SpritePro 3.8

Курс из 10 уроков: от базового сетевого обмена до полноценной мультиплеерной мини-игры с лобби, счётом и результатами.

Обновлён под **SpritePro 3.8.0**: рекомендуемый запуск через `s.run(..., multiplayer=True)`.

## Как проходить

1. Идите по порядку: папки `1` → `10`.
2. В каждом уроке сначала прочитайте `lesson.md`.
3. Запустите `example_*.py` — увидите эталонный пример.
4. Выполните задания в `practice_*.py`.
5. Сверяйтесь с `solution_*.py` только после попытки.

## Что внутри каждого урока

| Файл | Назначение |
|------|-----------|
| `lesson.md` | Теория, примеры кода, задания |
| `example_*.py` | Рабочий пример по теме |
| `practice_*.py` | Практика с `TODO` для самостоятельной работы |
| `solution_*.py` | Эталонное решение |

## Запуск примеров

```bash
python multiplayer_course/2/example_sync_positions.py
```

SpritePro автоматически запустит 2 окна (хост + клиент). Для 3+ окон:

```python
s.run(multiplayer=True, multiplayer_entry=main, multiplayer_clients=3)
```

С отладочным логом сети:
```bash
python multiplayer_course/2/example_sync_positions.py --net_debug
```

## Два уровня уроков

| Уровень | Что изучается | Уроки |
|---------|-------------|-------|
| **Low-level** | `NetServer`, `NetClient`, `ctx.send()`, `poll()`, JSON | 1–4 |
| **App-level** | `Scene`, `Button`, `s.run()`, архитектура проекта | 5–10 |

Ручной цикл `while True: s.update(...)` допустим в учебных low-level примерах. Для полноценных игр используйте `s.run(...)`.

## Структура курса

| # | Тема | Ключевой навык |
|---|------|---------------|
| **1** | Сетевой слой: сообщения и очередь | `NetServer`, `NetClient`, `send()`, `poll()` |
| **2** | Синхронизация позиций | `send_every()`, троттлинг, «свой» vs «чужой» |
| **3** | Готовность и старт | Флаги `ready_map`, authority хоста |
| **4** | Лобби и список игроков | `join`, `roster`, `client_id` |
| **5** | Сцены и UI | `Scene`, `Button`, синхронный переход |
| **6** | Зона захвата и счёт | Authority счёта, кулдаун, валидация |
| **7** | Результаты и перезапуск | Передача данных между сценами, `recreate=True` |
| **8** | Структура проекта | `game_config.py`, модули, хелперы |
| **9** | Финальный мини-экзамен | Всё вместе: лобби → игра → результат |
| **10** | Продвинутые темы | LERP, роутинг, снапшоты, dedicated server |

## Ключевые API

```python
import spritePro as s

# Запуск мультиплеера (app-level)
s.run(multiplayer=True, setup=setup_scenes)

# Или с учебной entry-функцией (low-level)
s.run(multiplayer=True, multiplayer_entry=multiplayer_main)

# Контекст мультиплеера
ctx = s.multiplayer_ctx
ctx.is_host      # bool — я хост?
ctx.client_id    # int — мой ID
ctx.id_assigned  # bool — ID получен?
ctx.send(event, data)              # Отправить сообщение
ctx.poll()                         # Получить входящие
ctx.send_every(event, data, 0.1)   # С троттлингом
```

## Полный пример: Крестики-нолики

В папке [tictactoe_example/](tictactoe_example/) — готовая пошаговая сетевая игра:
- Turn-based логика (хост = X, клиент = O)
- Синхронизация доски, перезапуск
- UI: Layout, Sprite, Button, TextSprite, Scene

```bash
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py --quick
```

## Встроенное лобби

Для продакшен-проектов используйте готовое лобби SpritePro:

```python
s.run(
    scene=GameScene,
    multiplayer=True,
    use_lobby=True,      # Готовый UI лобби
    title="My Game",
)
```

## Ссылки

- [Документация по мультиплееру](../docs/systems/networking_guide.md)
- [API Reference](../docs/API_REFERENCE.md)
- [CHANGELOG](../CHANGELOG.md)
