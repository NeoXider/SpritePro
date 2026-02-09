"""Практика 1: ping/pong через NetServer и NetClient.

Что нужно сделать:
- Прочитайте TODO и реализуйте недостающий функционал.
"""

import time

import spritePro as s


def main() -> None:
    # Локальный сервер для обработки сообщений.
    server = s.NetServer(host="0.0.0.0", port=5050)
    server.start()

    # Локальный клиент.
    client = s.NetClient("127.0.0.1", 5050)
    client.connect()

    # Таймер отправки ping и счетчик pong.
    last_ping_time = 0.0
    pong_count = 0

    while True:
        now = time.time()

        if now - last_ping_time >= 0.5:
            last_ping_time = now
            # TODO: отправьте "ping" с полем tick (увеличивайте счетчик).
            pass

        # Сервер читает входящие сообщения.
        for msg in server.poll():
            if msg.get("event") == "ping":
                # TODO: ответьте клиентам "pong" и верните tick.
                pass

        # Клиент читает ответы.
        for msg in client.poll():
            if msg.get("event") == "pong":
                pong_count += 1
                print("pong:", pong_count, msg.get("data"))

        # Пауза, чтобы не перегружать CPU.
        time.sleep(0.05)


if __name__ == "__main__":
    # Запуск практики.
    main()
