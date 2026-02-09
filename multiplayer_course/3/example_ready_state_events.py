"""Пример 3 (вариант): готовность и старт через EventBus.

Та же механика, что в example_ready_state.py, но отправка ready/start
через s.events.send(..., route="all"), приём — ctx.poll() с пробросом
в s.events, обработка — s.events.connect. Все места взаимодействия с
событийным автобусом в примере помечены комментариями «EventBus:».
"""

import pygame
import spritePro as s

START_DELAY = 3.0  # сколько секунд показывать «Start» перед автостартом


def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.get_screen((800, 600), "Lesson 3 - Ready State (EventBus)")
    ctx = s.multiplayer.init_context(net, role)

    is_ready = False
    game_started = False
    ready_map = {"host": False, "client": False}
    player_key = "host" if ctx.is_host else "client"
    both_ready_timer = 0.0

    # EventBus: обработчики — функции, которые автобус вызовет при send(имя_события, ...).
    # Аргументы приходят как **payload (id=..., value=... при "ready"; при "start" payload может быть пустым).
    def on_ready(**payload):
        pid = payload.get("id")
        if pid in ready_map:
            ready_map[pid] = bool(payload.get("value", False))

    def on_start(**payload):
        nonlocal game_started
        game_started = True
        state.set_text("State: game")
        start_label.set_active(False)

    # EventBus: подписка — связываем имена событий с обработчиками; любой send("ready", ...) вызовет on_ready и т.д.
    s.events.connect("ready", on_ready)
    s.events.connect("start", on_start)

    info = s.TextSprite("Space: ready", 28, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT)
    state = s.TextSprite("State: lobby", 28, (240, 240, 240), (20, 60), anchor=s.Anchor.TOP_LEFT)
    start_label = s.TextSprite("Start", 48, (120, 255, 120), s.WH_C, anchor=s.Anchor.CENTER)
    start_label.set_active(False)

    while True:
        s.update(fill_color=(15, 15, 20))
        dt = s.dt

        # EventBus: отправка "ready" — send(имя, route="all", net=ctx, ...). route="all" = вызов локальных подписчиков (on_ready) + отправка в сеть через net.
        if s.input.was_pressed(pygame.K_SPACE) and not game_started:
            is_ready = not is_ready
            s.events.send("ready", route="all", net=ctx, id=player_key, value=is_ready)
            ready_map[player_key] = is_ready

        # --- Схема: два подхода к обработке событий ---
        #
        # ПОДХОД A (example_ready_state.py, без EventBus):
        #   Отправка:  ctx.send("ready", {...})  →  только в сеть (себя обновляем вручную: ready_map[key]=...)
        #   Приём:     ctx.poll()  →  for msg: if msg["event"]=="ready": ready_map[...]=...  elif "start": ...
        #   Итого: входящие обрабатываются одним циклом с if/elif по event.
        #
        # ПОДХОД B (здесь, с EventBus):
        #   Отправка:  s.events.send("ready", route="all", ...)  →  локально вызываются on_ready + то же уходит в сеть
        #   Приём:     ctx.poll()  →  приходят только {"event": "ready", "data": {...}}; EventBus сокет не читает.
        #   Если не вызвать s.events.send(ev, **data), обработчики on_ready/on_start не узнают о сообщениях от другого игрока.
        #   Проброс: for msg in ctx.poll(): s.events.send(ev, **data)  →  те же on_ready/on_start вызываются с данными из сети.
        #
        # Сравнение: A — логика приёма в одном месте (цикл poll + if/elif). B — логика в подписчиках (connect);
        #            но входящие с сети нужно вручную «вбросить» в EventBus, иначе подписчики срабатывают только на свои send().
        #
        # EventBus: проброс входящих — из сети приходит только {"event": "ready"|"start", "data": {...}}. Вызов
        # s.events.send(ev, **data) без route/net — доставка только локальным подписчикам (route по умолчанию "local"),
        # т.е. эмулируем «получили событие из сети» и вызываем on_ready/on_start с данными от другого игрока.
        # Варианты отправки при своей инициативе: route="local" | "server" | "clients" | "all" | "net", net=ctx,
        # include_local — см. подробный докстринг s.events.send в event_bus.py.
        # Повторно на отправителе не вызовется: при send(..., route="all") мы уже вызвали обработчик локально, а сервер
        # рассылает сообщение только другим (exclude=отправитель), поэтому в poll() своё сообщение не приходит.
        for msg in ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            s.events.send(ev, **data)

        both_ready = all(ready_map.values())
        if both_ready and not game_started:
            both_ready_timer += dt
            start_label.set_active(True)
        else:
            both_ready_timer = 0.0
            start_label.set_active(False)

        # EventBus: хост отправляет "start" тем же способом — send("start", route="all", net=ctx). Локально сработает on_start, в сеть уйдёт сообщение для клиентов.
        if ctx.is_host and not game_started and both_ready and both_ready_timer >= START_DELAY:
            s.events.send("start", route="all", net=ctx)
            game_started = True
            state.set_text("State: game")
            start_label.set_active(False)

        info.set_text(f"Ready: {is_ready} | host={ready_map['host']} client={ready_map['client']}")


if __name__ == "__main__":
    s.networking.run()
