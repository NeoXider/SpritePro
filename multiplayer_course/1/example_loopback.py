"""Пример 1: базовый обмен сообщениями (loopback).

Один процесс поднимает сервер и клиента: клиент шлёт hello,
сервер рассылает welcome всем — демонстрация очереди сообщений без мультиплеера.
"""

import time

import spritePro as s


def main() -> None:
    # Сервер слушает на всех интерфейсах (0.0.0.0) на порту 5050.
    server = s.NetServer(host="0.0.0.0", port=5050, debug=False)
    server.start()

    # Клиент подключается к локальной машине (127.0.0.1 — loopback).
    client = s.NetClient("127.0.0.1", 5050)
    client.connect()

    # Клиент отправляет событие hello с данными — сервер получит его в poll().
    client.send("hello", {"name": "player"})

    start = time.time()
    while time.time() - start < 5.0:
        # Сервер забирает входящие сообщения и на hello отвечает broadcast welcome.
        for msg in server.poll():
            if msg.get("event") == "hello":
                server.broadcast("welcome", {"text": "hi"})

        # Клиент забирает ответы; broadcast не доставляет отправителю копию (exclude).
        for msg in client.poll():
            if msg.get("event") == "welcome":
                print("welcome:", msg.get("data"))

        time.sleep(0.05)


if __name__ == "__main__":
    # Запуск примера.
    main()
