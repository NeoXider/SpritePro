import time

class Timer:
    """Универсальный таймер для анимаций и задержек."""
    def __init__(self, duration=0):
        self.duration = duration
        self.start_time = None

    def start(self, duration=None):
        self.duration = duration if duration is not None else self.duration
        self.start_time = time.time()

    def done(self):
        if self.start_time is None:
            return False
        return (time.time() - self.start_time) >= self.duration

    def reset(self):
        self.start_time = None 