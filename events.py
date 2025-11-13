
"""
Observer -> Наблюдатель

Подписчик (случатель) воспроизведение звук
connect     
Собтие (информация) нажатие на кнопку

"""


class Event:
    subscribers = []

    def subscribe(self, subsctiber):
        self.subscribers.append(subsctiber)

    def invoke(self):
        for i in self.subscribers:
            i()


# def play_audio(fsdf):
#     print("Воспроизводим звук")

# damage = Event()
# damage.subscribe(play_audio)
# damage.invoke()

# damage.invoke()

from blinker import signal

def on_damage(sender, damage):
    print("получили урон:", damage)

damage = signal("damage player")

damage.connect(on_damage)

damage.send("player", damage=10)

damage.send("player", damage=20)




