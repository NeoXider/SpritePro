# reactive_example.py
# Расширенный пример с различными возможностями RxPy

import rx
import rx.operators as ops
import time
from rx.subject import Subject, BehaviorSubject, ReplaySubject
from rx.disposable import CompositeDisposable

# --- Пример 1: BehaviorSubject для хранения состояния (как в прошлый раз) ---
print("--- Пример 1: BehaviorSubject (Состояние) ---")

class Player:
    def __init__(self, name, initial_hp):
        self.name = name
        self.hp = BehaviorSubject(initial_hp)

    def take_damage(self, amount):
        new_hp = self.hp.value - amount
        self.hp.on_next(new_hp)

player = Player("Рыцарь", 100)
player.hp.subscribe(lambda hp: print(f"[HP] Текущее здоровье: {hp}"))
player.take_damage(30)

# Новый подписчик сразу получит последнее значение (70)
player.hp.subscribe(lambda hp: print(f"[Новый подписчик] Узнал, что HP = {hp}"))
player.hp.on_completed()
print("\n" + "-"*40 + "\n")


# --- Пример 2: Subject для простых событий без состояния ---
print("--- Пример 2: Subject (События) ---")

# Событие "уровень повышен"
level_up_event = Subject()

level_up_event.subscribe(lambda level: print(f"Поздравляем с {level}-м уровнем! Награда выдана."))

print("Игрок выполнил квест...")
level_up_event.on_next(5) # Подписчик сработает

# Если подписаться сейчас, ничего не произойдет, т.к. Subject не хранит старые значения
level_up_event.subscribe(lambda level: print(f"[Опоздавший подписчик] Уровень повышен до {level}"))

print("Игрок выполнил еще один квест...")
level_up_event.on_next(6) # Теперь сработают оба подписчика
level_up_event.on_completed()
print("\n" + "-"*40 + "\n")


# --- Пример 3: ReplaySubject для событий с историей ---
print("--- Пример 3: ReplaySubject (История) ---")

# Создаем чат, который хранит 3 последних сообщения
chat_log = ReplaySubject(buffer_size=3)

chat_log.on_next("Рыцарь: Привет всем!")
chat_log.on_next("Маг: И тебе привет.")
chat_log.on_next("Разбойник: Что тут происходит?")
chat_log.on_next("Рыцарь: Готовимся к походу.") # "Привет всем!" будет вытеснено из буфера

print("Целитель входит в чат и видит последние сообщения:")
# Новый подписчик получит весь буфер (последние 3 сообщения)
chat_log.subscribe(lambda msg: print(f"  - {msg}"))

chat_log.on_next("Целитель: Я с вами!") # Сработает у подписчика
chat_log.on_completed()
print("\n" + "-"*40 + "\n")


# --- Пример 4: Потоки из интервалов и управление подписками ---
print("--- Пример 4: Interval и Disposables ---")

# Создаем "игровой движок", который генерирует события (тики) каждые 0.5 секунды
game_tick = rx.interval(0.5).pipe(
    ops.map(lambda i: f"Тик #{i}")
)

# Создаем "монстра", который будет получать урон каждую секунду
monster_ai_stream = rx.interval(1).pipe(
    ops.map(lambda i: 10 * (i + 1)) # 10, 20, 30...
)

# Используем CompositeDisposable для управления всеми подписками
disposables = CompositeDisposable()

print("Запускаем игровой мир... (подождите 3 секунды)")

disposables.add(
    game_tick.subscribe(lambda tick: print(f"[Движок] {tick}"))
)
disposables.add(
    monster_ai_stream.subscribe(lambda damage: print(f"[Монстр] получил {damage} урона от яда."))
)

# Даем поработать 3 секунды
time.sleep(3)

# Теперь "убиваем" все подписки одним махом. Потоки остановятся.
print("Выходим из игры, все подписки уничтожены.")
disposables.dispose()

# Проверяем, что больше ничего не происходит
time.sleep(1)
print("Конец.")
