## Blinker — современный сигнальный механизм (pub/sub) для Python

Blinker — лёгкая и быстрая библиотека, реализующая паттерн «сигнал/слот» (издатель/подписчик). С помощью сигналов независимые части приложения обмениваются уведомлениями без жёстких зависимостей и прямых импортов.

- **Где применяют**: веб-приложения (Flask использует Blinker для внутренних сигналов), плагинные системы, микросервисы, интеграции и любая событийная логика.
- **Ключевая идея**: код «отправляет» событие через `Signal`, а произвольное число «получателей» (обработчиков) реагируют на него.

---

## Установка

```bash
pip install blinker
```

---

## Быстрый старт (TL;DR)

```python
from blinker import signal

# 1) Создаём именованный сигнал (попадает в глобальное пространство имён)
user_logged_in = signal('user_logged_in')

# 2) Подписываемся (получатель обязан принимать аргумент sender)
def on_login(sender, user_id):
    print(f"login: sender={sender}, user_id={user_id}")

user_logged_in.connect(on_login)

# 3) Отправляем событие; вернётся список пар (receiver, return_value)
result = user_logged_in.send(sender='auth-service', user_id=42)
```

---

## Базовые понятия

- **Signal**: объект события, через который выполняется рассылка уведомлений.
- **Receiver**: функция/метод-обработчик, подписанный на сигнал (`connect`).
- **Sender**: объект или маркер, указывающий, кто инициировал событие; передаётся первым позиционным аргументом при `send`.
- **ANY**: специальный маркер, означающий «любой отправитель». 
- **Namespace**: отдельное пространство имён для изолированной регистрации сигналов.
- **Слабые ссылки**: по умолчанию подписки на методы удерживаются через weakref, чтобы не мешать сборке мусора.

---

## Получение сигналов

Способы создать/получить сигнал:

```python
from blinker import signal, Namespace

# Глобальное именованное пространство
task_done = signal('task_done')              # NamedSignal

# Локальное пространство имён (рекомендуется для библиотек/пакетов)
ns = Namespace()
order_paid = ns.signal('order_paid')         # Signal в отдельном Namespace

# Анонимный сигнал (без реестра имён)
from blinker import Signal
custom = Signal()                            # вручную созданный сигнал
```

---

## Подписка на сигнал

1) Через `connect`:

```python
from blinker import ANY

def receiver(sender, **payload):
    print('got', sender, payload)

# Подписка на любых отправителей
task_done.connect(receiver)                  # по умолчанию sender=ANY

# Подписка только на конкретного отправителя
class Worker: ...
worker = Worker()
task_done.connect(receiver, sender=worker)

# Сильная ссылка на метод (не по умолчанию)
task_done.connect(worker.handle, weak=False)
```

2) Через декоратор `connect_via` (удобно для фильтрации по отправителю):

```python
@task_done.connect_via(worker)
def on_task_done(sender, **kw):
    ...
```

Отписка:

```python
task_done.disconnect(receiver)               # от любых отправителей
task_done.disconnect(receiver, sender=worker)
```

---

## Отправка сигнала

```python
result = task_done.send(sender=worker, task_id='T-100', status='ok')
# result: list[tuple[callable, Any]] — пары (получатель, возвращённое_значение)
```

Замечания:
- Исключения в получателях по умолчанию «пробрасываются» и прерывают рассылку. Если нужно изолировать ошибки — оборачивайте обработчики в try/except.
- `has_receivers_for(sender)` быстро отвечает, есть ли подписчики для конкретного отправителя; полезно, если формирование полезной нагрузки дорого.

```python
if task_done.has_receivers_for(worker):
    # подготовим полезную нагрузку только при наличии слушателей
    payload = make_payload()
    task_done.send(worker, **payload)
```

Итерация по реальным получателям для данного отправителя:

```python
for recv in task_done.receivers_for(worker):
    # можно вызвать вручную или проинспектировать
    ...
```

---

## Namespace: изоляция сигналов

Используйте `Namespace`, чтобы не «засорять» глобальный реестр имён и избежать коллизий в больших проектах и библиотеках.

```python
events = Namespace()
user_created = events.signal('user_created')
user_deleted = events.signal('user_deleted')
```

---

## Примеры и шаблоны

### Фильтрация по отправителю (класс/экземпляр)

```python
class Repo: ...

repo = Repo()
updated = signal('repo_updated')

def on_repo_updated(sender, branch):
    print('update on', sender, branch)

# Реагируем только на конкретный экземпляр
updated.connect(on_repo_updated, sender=repo)

updated.send(repo, branch='main')   # вызовет on_repo_updated
updated.send('other', branch='dev') # игнор
```

### Методы-обработчики и weakrefs

```python
class Processor:
    def handle(self, sender, **kw):
        ...

p = Processor()
evt = signal('evt')

# Сильная ссылка, чтобы объект не «отвалился» сборщиком мусора
evt.connect(p.handle, weak=False)
```

### Декоратор `connect_via`

```python
build_finished = signal('build_finished')

class Builder: ...
b = Builder()

@build_finished.connect_via(b)
def on_finish(sender, duration_ms):
    print('build finished in', duration_ms)

build_finished.send(b, duration_ms=1200)
```

---

## Интеграция с Flask

Flask рассылает собственные сигналы (например, `template_rendered`, `request_started`, `request_finished`). При наличии установленного `blinker` они становятся активными.

```python
from flask import Flask, template_rendered

app = Flask(__name__)

def on_template(sender, template, context, **extra):
    print('rendered', template.name)

template_rendered.connect(on_template, app)
```

Рекомендации:
- Подключайте обработчики при инициализации приложения/расширений.
- Не выполняйте тяжёлую работу в обработчиках — переносите в очереди/пулы.

---

## Лучшие практики

- **Локализуйте сигналы**: группируйте их в `Namespace` на уровне пакета/модуля.
- **Обрабатывайте ошибки** в подписчиках (исключения не подавляются библиотекой).
- **Не злоупотребляйте сигналами** для обычных вызовов — используйте там, где нужна слабая связность и расширяемость.
- **Именуйте сигнал по домену**: `user.created`, `billing.invoice.paid`.
- **Проверяйте наличие получателей** перед дорогой подготовкой данных (`has_receivers_for`).

---

## Мини-справочник API

- `signal(name: str) -> Signal` — получить/создать именованный сигнал (глобальный реестр).
- `Namespace().signal(name: str) -> Signal` — сигнал в изолированном пространстве имён.
- `Signal.connect(receiver, sender=ANY, weak=True)` — подписка.
- `Signal.connect_via(sender)` — декоратор-подписка для конкретного отправителя.
- `Signal.disconnect(receiver, sender=ANY)` — отписка.
- `Signal.send(sender, **kwargs) -> list[tuple[receiver, return]]` — рассылка.
- `Signal.has_receivers_for(sender) -> bool` — есть ли слушатели.
- `Signal.receivers_for(sender) -> Iterable[receiver]` — итерация по слушателям.
- `ANY` — маркер «любой отправитель».

---

## Частые вопросы

- «Нужно ли всегда передавать `sender`?» — Да, `sender` обязателен и помогает фильтровать подписки.
- «Можно ли подписаться на все события?» — Да, используйте `sender=ANY`.
- «Почему обработчик не вызывается?» — Проверьте, на какого отправителя подписались; сравнение идёт по объекту/ссылке.
- «Как избежать утечек памяти?» — По умолчанию методы держатся как weakref; при необходимости задайте `weak=False` и контролируйте жизненный цикл.

---

## Ссылки

- PyPI: `https://pypi.org/project/blinker/`
- Исходники: `https://github.com/jek/blinker`
- Документация: `https://blinker.readthedocs.io/` (или зеркала `https://pythonhosted.org/blinker/`)