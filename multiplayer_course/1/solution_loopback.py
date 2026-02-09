"""Решение 1: ping/pong через NetServer и NetClient."""

import time

import spritePro as s


def main() -> None:
    # Запускаем локальный сервер.
    server = s.NetServer(host="0.0.0.0", port=5050)
    server.start()

    # Подключаем клиента.
    client = s.NetClient("127.0.0.1", 5050)
    client.connect()

    # Таймеры и счетчики.
    last_ping_time = 0.0
    tick = 0
    pong_count = 0

    while True:
        now = time.time()

        if now - last_ping_time >= 0.5:
            last_ping_time = now
            tick += 1
            # Отправляем ping с текущим tick.
            client.send("ping", {"tick": tick})

        # Сервер отвечает pong с тем же tick.
        for msg in server.poll():
            if msg.get("event") == "ping":
                data = msg.get("data", {})
                server.broadcast("pong", {"tick": data.get("tick")})

        # Клиент считает pong.
        for msg in client.poll():
            if msg.get("event") == "pong":
                pong_count += 1
                print("pong:", pong_count, msg.get("data"))

        # Небольшая пауза.
        time.sleep(0.05)


if __name__ == "__main__":
    # Запуск решения.
    main()
