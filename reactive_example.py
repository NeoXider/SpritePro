# reactive_example.py
# Расширенный пример с различными возможностями RxPy

import rx
import rx.operators as ops
import time
from rx.subject import Subject, BehaviorSubject, ReplaySubject
from rx.disposable import CompositeDisposable
from spritePro.utils.logger import log_info

# --- Пример 1: BehaviorSubject для хранения состояния (как в прошлый раз) ---
log_info("--- Пример 1: BehaviorSubject (Состояние) ---")

class Player:
    def __init__(self, name, initial_hp):
        self.name = name
        self.hp = BehaviorSubject(initial_hp)

    def take_damage(self, amount):
        new_hp = self.hp.value - amount
        self.hp.on_next(new_hp)

player = Player("Рыцарь", 100)
player.hp.subscribe(lambda hp: log_info(f"[HP] Текущее здоровье: {hp}"))
player.take_damage(30)

# Новый подписчик сразу получит последнее значение (70)
player.hp.subscribe(lambda hp: log_info(f"[Новый подписчик] Узнал, что HP = {hp}"))
player.hp.on_completed()
log_info("\n" + "-"*40 + "\n")


# --- Пример 2: Subject для простых событий без состояния ---
log_info("--- Пример 2: Subject (События) ---")

# Событие "уровень повышен"
level_up_event = Subject()

level_up_event.subscribe(lambda level: log_info(f"Поздравляем с {level}-м уровнем! Награда выдана."))

log_info("Игрок выполнил квест...")
level_up_event.on_next(5) # Подписчик сработает

# Если подписаться сейчас, ничего не произойдет, т.к. Subject не хранит старые значения
level_up_event.subscribe(lambda level: log_info(f"[Опоздавший подписчик] Уровень повышен до {level}"))

log_info("Игрок выполнил еще один квест...")
level_up_event.on_next(6) # Теперь сработают оба подписчика
level_up_event.on_completed()
log_info("\n" + "-"*40 + "\n")


# --- Пример 3: ReplaySubject для событий с историей ---
log_info("--- Пример 3: ReplaySubject (История) ---")

# Создаем чат, который хранит 3 последних сообщения
chat_log = ReplaySubject(buffer_size=3)

chat_log.on_next("Рыцарь: Привет всем!")
chat_log.on_next("Маг: И тебе привет.")
chat_log.on_next("Разбойник: Что тут происходит?")
chat_log.on_next("Рыцарь: Готовимся к походу.") # "Привет всем!" будет вытеснено из буфера

log_info("Целитель входит в чат и видит последние сообщения:")
# Новый подписчик получит весь буфер (последние 3 сообщения)
chat_log.subscribe(lambda msg: log_info(f"  - {msg}"))

chat_log.on_next("Целитель: Я с вами!") # Сработает у подписчика
chat_log.on_completed()
log_info("\n" + "-"*40 + "\n")


# --- Пример 4: Потоки из интервалов и управление подписками ---
log_info("--- Пример 4: Interval и Disposables ---")

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

log_info("Запускаем игровой мир... (подождите 3 секунды)")

disposables.add(
    game_tick.subscribe(lambda tick: log_info(f"[Движок] {tick}"))
)
disposables.add(
    monster_ai_stream.subscribe(lambda damage: log_info(f"[Монстр] получил {damage} урона от яда."))
)

# Даем поработать 3 секунды
time.sleep(3)

# Теперь "убиваем" все подписки одним махом. Потоки остановятся.
log_info("Выходим из игры, все подписки уничтожены.")
disposables.dispose()

# Проверяем, что больше ничего не происходит
time.sleep(1)
log_info("Конец.")

log_info("\n" + "=" * 40 + "\n")

# --- Пример 5: Blinker (сигналы) ---
log_info("--- Пример 5: Blinker (Сигналы) ---")

try:
    from blinker import signal
except Exception as exc:
    log_info(f"Blinker не установлен: {exc}")
else:
    on_damage = signal("player_damage")
    on_level_up = signal("player_level_up")

    class BlinkerPlayer:
        def __init__(self, name: str, hp: int):
            self.name = name
            self.hp = hp
            self.level = 1

        def take_damage(self, amount: int) -> None:
            self.hp = max(0, self.hp - amount)
            on_damage.send(self, amount=amount, hp=self.hp)

        def level_up(self) -> None:
            self.level += 1
            on_level_up.send(self, level=self.level)

    def on_damage_handler(sender, amount: int, hp: int) -> None:
        log_info(f"[Blinker] {sender.name} получил {amount} урона, HP={hp}")

    def on_level_up_handler(sender, level: int) -> None:
        log_info(f"[Blinker] {sender.name} повысил уровень до {level}")

    on_damage.connect(on_damage_handler)
    on_level_up.connect(on_level_up_handler)

    blinker_player = BlinkerPlayer("Лучник", 120)
    blinker_player.take_damage(25)
    blinker_player.level_up()
