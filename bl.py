from blinker import signal, Namespace

def inf(sender):
    print("info", sender)

s1 = signal("event")
s1.connect(inf)

s1.send("any")

localNameSpace = Namespace()
s2 = localNameSpace.signal("event")
s2.send("localNameSpace")

s3 = signal("event")
s3.send("new signal event")


print("\n--- HP Example ---")

# 1. Сигнал, который будет отправляться при получении урона
player_took_damage = signal("player-took-damage")

# 2. Обработчик для логирования события
# Получатель должен принимать отправителя (player) и любые доп. аргументы
def log_damage_event(player, **kwargs):
    """Просто записывает информацию в консоль."""
    damage_amount = kwargs.get('damage_amount', 0)
    print(f"[LOG] Игрок {player.name} получил {damage_amount} урона. Осталось HP: {player.hp}")

# 3. Обработчик, имитирующий обновление интерфейса
def ui_health_bar_update(player, **kwargs):
    """Имитирует обновление полоски здоровья в UI."""
    print(f"[UI] Обновляем хит-бар для {player.name}! Новое значение: {player.hp}")
    if player.hp <= 0:
        print(f"[UI] Игрок {player.name} побежден!")

# 4. Подключаем оба обработчика к сигналу
player_took_damage.connect(log_damage_event)
player_took_damage.connect(ui_health_bar_update)


# 5. Класс игрока
class Player:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp

    def take_damage(self, amount):
        """Метод для получения урона."""
        if self.hp > 0:
            self.hp -= amount
            if self.hp < 0:
                self.hp = 0
            print(f"\n*Игрок {self.name} получает {amount} урона*")
            # Отправляем сигнал!
            # В качестве отправителя (sender) передаем сам объект игрока.
            # В качестве полезной нагрузки - количество урона.
            player_took_damage.send(self, damage_amount=amount)

# --- Демонстрация ---
player1 = Player("Герой", 100)

player1.take_damage(25)
player1.take_damage(40)
player1.take_damage(50) # Этот удар должен "убить" игрока
