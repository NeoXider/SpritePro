"""Готовая сцена/экран лобби для мультиплеера.

Экран 1 — настройка: имя, хост/клиент, порт (и IP для клиента), «Запустить сервер» / «Подключиться».
Экран 2 — в лобби: список игроков (roster). У обоих: кнопки «Назад» и «В игру».
По нажатию «В игру» хост рассылает start_game остальным; любой участник (хост или клиент) может нажать «В игру» и войти в игру (в т.ч. клиент — после того как хост уже запустил игру).
«Назад» — отключение и возврат к экрану настройки.

Использование через run():
    s.networking.run(use_lobby=True)

Или вручную: вызвать run_multiplayer_lobby(on_start_game) после get_screen().
"""

from __future__ import annotations

import os
import time
from typing import Callable, List, Optional

import spritePro as s
from spritePro.networking import NetServer, NetClient
from spritePro.layout import layout_flex_column, layout_flex_row
from spritePro.layout import LayoutAlignMain, LayoutAlignCross

DEFAULT_PORT = 5050
DEFAULT_IP = "127.0.0.1"
PAD = 28
GAP = 12
COLOR_BG = (22, 22, 28)
COLOR_TEXT = (240, 240, 240)
COLOR_LABEL = (200, 200, 200)
COLOR_ERROR = (255, 100, 100)
COLOR_STATUS = (150, 220, 150)
COLOR_ACTIVE = (70, 130, 180)
COLOR_INACTIVE = (60, 60, 68)

EVENT_START_GAME = "start_game"


def _display_name(pid: int) -> str:
    return "Host" if pid == 0 else f"Player {pid}"


def _collect_sprites_with_children(
    buttons_and_inputs: List,
    other_sprites: List,
) -> List:
    """Собирает все спрайты лобби, включая text_sprite у кнопок и полей ввода."""
    out: List = list(other_sprites)
    for x in buttons_and_inputs:
        out.append(x)
        if hasattr(x, "text_sprite") and getattr(x, "text_sprite", None) is not None:
            out.append(x.text_sprite)
    return out


class MultiplayerLobbyScene(s.Scene):
    """Сцена лобби: при on_exit снимает с регистрации все свои спрайты."""

    def __init__(self) -> None:
        super().__init__()
        self._lobby_sprites: List = []

    def set_lobby_sprites(self, sprites: List) -> None:
        self._lobby_sprites = list(sprites)

    def on_exit(self) -> None:
        for sp in self._lobby_sprites:
            try:
                s.unregister_sprite(sp)
            except Exception:
                pass
        self._lobby_sprites.clear()


def run_multiplayer_lobby(
    on_start_game: Callable[[s.NetClient, str], None],
    window_size: tuple[int, int] = (480, 540),
    title: str = "Лобби",
) -> None:
    """Запускает цикл лобби до нажатия «В игру»; затем вызывает on_start_game(net, role)."""
    if "SPRITEPRO_LOG_DIR" not in os.environ:
        os.environ["SPRITEPRO_LOG_DIR"] = os.path.join(os.getcwd(), "spritepro_logs")
    s.get_screen(window_size, title)
    W, H = int(s.WH.x), int(s.WH.y)
    cx = W // 2
    inner_w = W - 2 * PAD
    inner_h = H - 2 * PAD

    scene = MultiplayerLobbyScene()

    is_host = True
    connected = False
    net: Optional[NetClient] = None
    role = "host"
    server: Optional[NetServer] = None
    player_ids: set[int] = set()
    roster: list[int] = []
    joined = False
    error_msg = ""
    status_msg = ""

    title_label = s.TextSprite("Мультиплеер", 26, COLOR_TEXT, (0, 0), anchor=s.Anchor.CENTER)
    name_label = s.TextSprite("Имя", 16, COLOR_LABEL, (0, 0), anchor=s.Anchor.TOP_LEFT)
    name_input = s.TextInput(
        size=(inner_w - 20, 32),
        pos=(0, 0),
        placeholder="Игрок",
        value="",
        max_length=32,
        font_size=16,
    )
    role_label = s.TextSprite("Роль", 16, COLOR_LABEL, (0, 0), anchor=s.Anchor.TOP_LEFT)
    role_display = s.TextSprite("Режим: Хост", 16, COLOR_ACTIVE, (0, 0), anchor=s.Anchor.CENTER)
    role_display.set_rect_shape(size=(140, 28), color=(50, 70, 90), width=0, border_radius=4)
    btn_host = s.Button(
        size=(110, 36),
        pos=(0, 0),
        text="Хост",
        text_size=15,
        base_color=COLOR_ACTIVE,
        hover_color=(90, 150, 210),
        press_color=(50, 110, 170),
        text_color=(255, 255, 255),
    )
    btn_client = s.Button(
        size=(110, 36),
        pos=(0, 0),
        text="Клиент",
        text_size=15,
        base_color=COLOR_INACTIVE,
        hover_color=(80, 80, 90),
        press_color=(50, 50, 58),
    )
    port_label = s.TextSprite("Порт", 16, COLOR_LABEL, (0, 0), anchor=s.Anchor.TOP_LEFT)
    port_input = s.TextInput(
        size=(100, 32),
        pos=(0, 0),
        placeholder="5050",
        value=str(DEFAULT_PORT),
        max_length=6,
        font_size=16,
    )
    ip_label = s.TextSprite("IP сервера", 16, COLOR_LABEL, (0, 0), anchor=s.Anchor.TOP_LEFT)
    ip_input = s.TextInput(
        size=(200, 32),
        pos=(0, 0),
        placeholder=DEFAULT_IP,
        value=DEFAULT_IP,
        max_length=40,
        font_size=16,
    )
    btn_start_server = s.Button(
        size=(220, 42),
        pos=(0, 0),
        text="Запустить сервер",
        text_size=17,
    )
    btn_connect = s.Button(
        size=(220, 42),
        pos=(0, 0),
        text="Подключиться",
        text_size=17,
    )
    status_text = s.TextSprite("", 15, COLOR_STATUS, (0, 0), anchor=s.Anchor.CENTER)
    error_text = s.TextSprite("", 14, COLOR_ERROR, (0, 0), anchor=s.Anchor.CENTER)

    def _set_host(h: bool) -> None:
        nonlocal is_host
        is_host = h
        role_display.set_text("Режим: Хост" if is_host else "Режим: Клиент")
        role_display.set_rect_shape(
            size=(140, 28),
            color=(50, 70, 90) if is_host else (60, 60, 68),
            width=0,
            border_radius=4,
        )
        role_display.set_color(COLOR_ACTIVE if is_host else COLOR_LABEL)
        btn_host.set_all_colors(
            COLOR_ACTIVE if is_host else COLOR_INACTIVE,
            (50, 110, 170) if is_host else (50, 50, 58),
            (90, 150, 210) if is_host else (80, 80, 90),
        )
        btn_host.text_sprite.set_color((255, 255, 255) if is_host else (180, 180, 180))
        btn_client.set_all_colors(
            COLOR_ACTIVE if not is_host else COLOR_INACTIVE,
            (50, 110, 170) if not is_host else (50, 50, 58),
            (90, 150, 210) if not is_host else (80, 80, 90),
        )
        btn_client.text_sprite.set_color((255, 255, 255) if not is_host else (180, 180, 180))
        btn_start_server.set_active(is_host)
        btn_connect.set_active(not is_host)
        ip_label.set_active(not is_host)
        ip_input.set_active(not is_host)

    def _do_connect_host() -> None:
        nonlocal server, net, role, connected, error_msg, status_msg
        try:
            port = int(port_input.value or port_input.placeholder or str(DEFAULT_PORT))
        except ValueError:
            error_msg = "Неверный порт"
            status_msg = ""
            return
        error_msg = ""
        status_msg = "Подключение..."
        status_text.set_text(status_msg)
        status_text.set_active(True)
        error_text.set_active(False)
        try:
            server = NetServer(host="0.0.0.0", port=port, debug=False)
            server.start()
            time.sleep(0.4)
            net = NetClient("127.0.0.1", port, debug=False)
            net.connect()
            role = "host"
            s.multiplayer.init_context(net, role)
            connected = True
            status_msg = ""
            _show_lobby()
        except Exception as e:
            error_msg = str(e)[:50]
            status_msg = ""
            status_text.set_active(False)
            error_text.set_text(error_msg)
            error_text.set_active(True)
            server = None

    def _do_connect_client() -> None:
        nonlocal net, role, connected, error_msg, status_msg
        try:
            port = int(port_input.value or port_input.placeholder or str(DEFAULT_PORT))
        except ValueError:
            error_msg = "Неверный порт"
            status_msg = ""
            return
        ip = (ip_input.value or ip_input.placeholder or DEFAULT_IP).strip()
        error_msg = ""
        status_msg = "Подключение..."
        status_text.set_text(status_msg)
        status_text.set_active(True)
        error_text.set_active(False)
        try:
            net = NetClient(ip, port, debug=False)
            net.connect()
            role = "client"
            s.multiplayer.init_context(net, role)
            connected = True
            status_msg = ""
            _show_lobby()
        except Exception as e:
            error_msg = str(e)[:50]
            status_msg = ""
            status_text.set_active(False)
            error_text.set_text(error_msg)
            error_text.set_active(True)

    def _go_back() -> None:
        nonlocal connected, joined, roster, server, net
        try:
            if server is not None:
                server.stop()
                server = None
        except Exception:
            pass
        try:
            if net is not None:
                net.close()
                net = None
        except Exception:
            pass
        connected = False
        joined = False
        player_ids.clear()
        roster = []
        layout_setup.set_active(True)
        for sp in setup_children:
            sp.set_active(True)
        lobby_title.set_active(False)
        me_label.set_active(False)
        roster_text.set_active(False)
        btn_start_game.set_active(False)
        btn_back.set_active(False)

    def _show_lobby() -> None:
        for sp in setup_children:
            sp.set_active(False)
        layout_setup.set_active(False)
        lobby_title.set_active(True)
        me_label.set_active(True)
        roster_text.set_active(True)
        btn_back.set_active(True)
        btn_start_game.set_active(True)

        def _go_game() -> None:
            log_dir = os.environ.get("SPRITEPRO_LOG_DIR", "spritepro_logs")
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError:
                pass
            tag = "host" if role == "host" else "client"
            s.set_debug_log_file(path=os.path.join(log_dir, f"debug_{tag}.log"), enabled=True)
            if s.multiplayer_ctx is not None and s.multiplayer_ctx.is_host:
                s.multiplayer_ctx.send(EVENT_START_GAME)
            scene.on_exit()
            on_start_game(net, role)

        btn_start_game.on_click(_go_game)
        btn_back.on_click(_go_back)

    _set_host(True)
    btn_start_server.on_click(_do_connect_host)
    btn_connect.on_click(_do_connect_client)
    btn_host.on_click(lambda: _set_host(True))
    btn_client.on_click(lambda: _set_host(False))

    role_row = layout_flex_row(
        container=None,
        children=[btn_host, btn_client],
        gap=GAP,
        padding=0,
        align_main=LayoutAlignMain.CENTER,
        align_cross=LayoutAlignCross.CENTER,
        size=(240, 44),
        pos=(cx, 0),
        auto_apply=True,
    )
    setup_children = [
        title_label,
        name_label,
        name_input,
        role_label,
        role_display,
        role_row,
        port_label,
        port_input,
        ip_label,
        ip_input,
        btn_start_server,
        btn_connect,
        status_text,
        error_text,
    ]
    layout_setup = layout_flex_column(
        container=(PAD, PAD, inner_w, inner_h),
        children=setup_children,
        gap=GAP,
        padding=0,
        align_main=LayoutAlignMain.START,
        align_cross=LayoutAlignCross.CENTER,
        auto_apply=True,
    )

    lobby_title = s.TextSprite("В лобби", 24, COLOR_TEXT, (cx, 24), anchor=s.Anchor.CENTER)
    me_label = s.TextSprite("", 18, (170, 220, 255), (20, 54), anchor=s.Anchor.TOP_LEFT)
    roster_text = s.TextSprite("Игроки:", 20, (220, 220, 220), (20, 84), anchor=s.Anchor.TOP_LEFT)
    btn_start_game = s.Button(
        size=(160, 46),
        pos=(cx + 100, H - 70),
        text="В игру",
        text_size=20,
    )
    btn_back = s.Button(
        size=(160, 46),
        pos=(cx - 100, H - 70),
        text="Назад",
        text_size=20,
        base_color=COLOR_INACTIVE,
        hover_color=(80, 80, 90),
        press_color=(50, 50, 58),
        text_color=(180, 180, 180),
    )
    lobby_title.set_active(False)
    me_label.set_active(False)
    roster_text.set_active(False)
    btn_start_game.set_active(False)
    btn_back.set_active(False)

    buttons_and_inputs = [
        btn_host,
        btn_client,
        btn_start_server,
        btn_connect,
        btn_start_game,
        btn_back,
        name_input,
        port_input,
        ip_input,
    ]
    other_sprites = [
        layout_setup,
        title_label,
        name_label,
        role_label,
        role_display,
        role_row,
        port_label,
        ip_label,
        status_text,
        error_text,
        lobby_title,
        me_label,
        roster_text,
    ]
    lobby_sprites = _collect_sprites_with_children(buttons_and_inputs, other_sprites)
    scene.set_lobby_sprites(lobby_sprites)

    while True:
        s.update(fill_color=COLOR_BG)

        if s.quit_requested():
            return

        if not connected:
            if error_msg:
                error_text.set_text(error_msg)
                error_text.set_active(True)
            else:
                error_text.set_active(False)
            if status_msg:
                status_text.set_text(status_msg)
                status_text.set_active(True)
            continue

        ctx_ref = s.multiplayer_ctx
        me_label.set_text(
            f"Вы: {name_input.value or 'Игрок'} | {ctx_ref.role} (ID: {ctx_ref.client_id})"
        )

        if ctx_ref.id_assigned and not joined:
            joined = True
            ctx_ref.send("join")
            player_ids.add(ctx_ref.client_id)

        for msg in ctx_ref.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == EVENT_START_GAME:
                scene.on_exit()
                on_start_game(net, role)
                return
            if event == "join":
                pid = data.get("sender_id")
                if pid is not None:
                    player_ids.add(pid)
                if ctx_ref.is_host:
                    roster = sorted(player_ids)
                    ctx_ref.send("roster", {"players": roster})
            elif event == "roster":
                roster = list(data.get("players", []))

        roster_text.set_text("Игроки:\n" + "\n".join(_display_name(pid) for pid in roster))

        btn_back.set_active(True)
        btn_start_game.set_active(True)
