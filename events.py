
"""
Observer -> Наблюдатель

Подписчик (случатель) воспроизведение звук
connect     
Собтие (информация) нажатие на кнопку

"""
from spritePro.utils.logger import log_info
from blinker import signal


class Event:
    subscribers = []

    def subscribe(self, subsctiber):
        self.subscribers.append(subsctiber)

    def invoke(self):
        for i in self.subscribers:
            i()


# def play_audio(fsdf):
#     log_info("Воспроизводим звук")

# damage = Event()
# damage.subscribe(play_audio)
# damage.invoke()

# damage.invoke()

def on_damage(sender, damage):
    log_info("получили урон:", damage)

damage = signal("damage player")

damage.connect(on_damage)

damage.send("player", damage=10)

damage.send("player", damage=20)




