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


def _display_name_with_map(pid: int, name_by_id: Optional[dict[int, str]] = None) -> str:
    """Отображаемое имя игрока: берём из словаря, иначе fallback по id."""
    if name_by_id is not None:
        name = name_by_id.get(pid)
        if name:
            return name
    return _display_name(pid)


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
    """Сцена лобби: хранит всё состояние и UI, обновляется через update().

    Работает как в pygame-режиме (через обычный цикл s.update),
    так и в Kivy-режиме (через s.update_embedded и run_kivy_app).
    """

    def __init__(
        self,
        on_start_game: Callable[[s.NetClient, str], None],
        window_size: tuple[int, int],
        title: str,
    ) -> None:
        super().__init__()
        self._lobby_sprites: List = []
        self._on_start_game = on_start_game
        self._window_size = window_size
        self._title = title

        # Состояние соединения
        self.is_host: bool = True
        self.connected: bool = False
        self.net: Optional[NetClient] = None
        self.role: str = "host"
        self.server: Optional[NetServer] = None
        self.player_ids: set[int] = set()
        self.player_names: dict[int, str] = {}
        self.roster: list[int] = []
        self.joined: bool = False
        self.error_msg: str = ""
        self.status_msg: str = ""

        W, H = int(s.WH.x), int(s.WH.y)
        cx = W // 2
        inner_w = W - 2 * PAD
        inner_h = H - 2 * PAD

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
        ]
        layout_setup = layout_flex_column(
            container=(PAD, PAD, inner_w, inner_h - 60),
            children=setup_children,
            gap=GAP,
            padding=0,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.CENTER,
            auto_apply=True,
        )

        # Нижняя панель статуса/ошибки отдельно, чтобы не пересекаться с кнопками
        layout_status = layout_flex_column(
            container=(PAD, H - PAD - 60, inner_w, 60),
            children=[status_text, error_text],
            gap=4,
            padding=0,
            align_main=LayoutAlignMain.END,
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
            layout_status,
            title_label,
            name_label,
            role_label,
            role_display,
            role_row,
            port_label,
            ip_label,
            lobby_title,
            me_label,
            roster_text,
        ]
        lobby_sprites = _collect_sprites_with_children(buttons_and_inputs, other_sprites)
        self.set_lobby_sprites(lobby_sprites)

        # Сохраняем ссылки на элементы UI для update()
        self._name_input = name_input
        self._role_display = role_display
        self._btn_host = btn_host
        self._btn_client = btn_client
        self._btn_start_server = btn_start_server
        self._btn_connect = btn_connect
        self._btn_start_game = btn_start_game
        self._btn_back = btn_back
        self._port_input = port_input
        self._ip_input = ip_input
        self._status_text = status_text
        self._error_text = error_text
        self._layout_setup = layout_setup
        self._setup_children = setup_children
        self._lobby_title = lobby_title
        self._me_label = me_label
        self._roster_text = roster_text

        self._apply_host_ui(True)
        btn_start_server.on_click(self._do_connect_host)
        btn_connect.on_click(self._do_connect_client)
        btn_host.on_click(lambda: self._apply_host_ui(True))
        btn_client.on_click(lambda: self._apply_host_ui(False))

    def set_lobby_sprites(self, sprites: List) -> None:
        self._lobby_sprites = list(sprites)

    def on_exit(self) -> None:
        for sp in self._lobby_sprites:
            try:
                s.unregister_sprite(sp)
            except Exception:
                pass
        self._lobby_sprites.clear()

    def _apply_host_ui(self, is_host: bool) -> None:
        self.is_host = is_host
        self._role_display.set_text("Режим: Хост" if self.is_host else "Режим: Клиент")
        self._role_display.set_rect_shape(
            size=(140, 28),
            color=(50, 70, 90) if self.is_host else (60, 60, 68),
            width=0,
            border_radius=4,
        )
        self._role_display.set_color(COLOR_ACTIVE if self.is_host else COLOR_LABEL)
        self._btn_host.set_all_colors(
            COLOR_ACTIVE if self.is_host else COLOR_INACTIVE,
            (50, 110, 170) if self.is_host else (50, 50, 58),
            (90, 150, 210) if self.is_host else (80, 80, 90),
        )
        self._btn_host.text_sprite.set_color((255, 255, 255) if self.is_host else (180, 180, 180))
        self._btn_client.set_all_colors(
            COLOR_ACTIVE if not self.is_host else COLOR_INACTIVE,
            (50, 110, 170) if not self.is_host else (50, 50, 58),
            (90, 150, 210) if not self.is_host else (80, 80, 90),
        )
        self._btn_client.text_sprite.set_color((255, 255, 255) if not self.is_host else (180, 180, 180))
        self._btn_start_server.set_active(self.is_host)
        self._btn_connect.set_active(not self.is_host)
        self._ip_input.set_active(not self.is_host)

    def _do_connect_host(self) -> None:
        try:
            port = int(self._port_input.value or self._port_input.placeholder or str(DEFAULT_PORT))
        except ValueError:
            self.error_msg = "Неверный порт"
            self.status_msg = ""
            return
        self.error_msg = ""
        self.status_msg = "Подключение..."
        self._status_text.set_text(self.status_msg)
        self._status_text.set_active(True)
        self._error_text.set_active(False)
        try:
            self.server = NetServer(host="0.0.0.0", port=port, debug=False)
            self.server.start()
            time.sleep(0.4)
            self.net = NetClient("127.0.0.1", port, debug=False)
            self.net.connect()
            self.role = "host"
            s.multiplayer.init_context(self.net, self.role)
            self.connected = True
            self.status_msg = ""
            self._show_lobby()
        except Exception as e:
            self.error_msg = str(e)[:50]
            self.status_msg = ""
            self._status_text.set_active(False)
            self._error_text.set_text(self.error_msg)
            self._error_text.set_active(True)
            self.server = None

    def _do_connect_client(self) -> None:
        try:
            port = int(self._port_input.value or self._port_input.placeholder or str(DEFAULT_PORT))
        except ValueError:
            self.error_msg = "Неверный порт"
            self.status_msg = ""
            return
        ip = (self._ip_input.value or self._ip_input.placeholder or DEFAULT_IP).strip()
        self.error_msg = ""
        self.status_msg = "Подключение..."
        self._status_text.set_text(self.status_msg)
        self._status_text.set_active(True)
        self._error_text.set_active(False)
        try:
            self.net = NetClient(ip, port, debug=False)
            self.net.connect()
            self.role = "client"
            s.multiplayer.init_context(self.net, self.role)
            self.connected = True
            self.status_msg = ""
            self._show_lobby()
        except Exception as e:
            self.error_msg = str(e)[:50]
            self.status_msg = ""
            self._status_text.set_active(False)
            self._error_text.set_text(self.error_msg)
            self._error_text.set_active(True)

    def _go_back(self) -> None:
        try:
            if self.server is not None:
                self.server.stop()
                self.server = None
        except Exception:
            pass
        try:
            if self.net is not None:
                self.net.close()
                self.net = None
        except Exception:
            pass
        self.connected = False
        self.joined = False
        self.player_ids.clear()
        self.player_names.clear()
        self.roster = []
        self._layout_setup.set_active(True)
        for sp in self._setup_children:
            sp.set_active(True)
        self._lobby_title.set_active(False)
        self._me_label.set_active(False)
        self._roster_text.set_active(False)
        self._btn_start_game.set_active(False)
        self._btn_back.set_active(False)

    def _show_lobby(self) -> None:
        for sp in self._setup_children:
            sp.set_active(False)
        self._layout_setup.set_active(False)
        self._status_text.set_active(False)
        self._error_text.set_active(False)
        self._lobby_title.set_active(True)
        self._me_label.set_active(True)
        self._roster_text.set_active(True)
        self._btn_back.set_active(True)
        self._btn_start_game.set_active(True)

        def _go_game() -> None:
            log_dir = os.environ.get("SPRITEPRO_LOG_DIR", "spritepro_logs")
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError:
                pass
            tag = "host" if self.role == "host" else "client"
            s.set_debug_log_file(path=os.path.join(log_dir, f"debug_{tag}.log"), enabled=True)
            if s.multiplayer_ctx is not None and s.multiplayer_ctx.is_host:
                s.multiplayer_ctx.send(EVENT_START_GAME)
            self.on_exit()
            self._on_start_game(self.net, self.role)

        self._btn_start_game.on_click(_go_game)
        self._btn_back.on_click(self._go_back)

    def update(self, _dt: float) -> None:
        if not self.connected:
            if self.error_msg:
                self._error_text.set_text(self.error_msg)
                self._error_text.set_active(True)
            else:
                self._error_text.set_active(False)
            if self.status_msg:
                self._status_text.set_text(self.status_msg)
                self._status_text.set_active(True)
            return

        ctx_ref = s.multiplayer_ctx
        self._me_label.set_text(
            f"Вы: {self._name_input.value or 'Игрок'} | {ctx_ref.role} (ID: {ctx_ref.client_id})"
        )

        if ctx_ref.id_assigned and not self.joined:
            self.joined = True
            my_name = self._name_input.value or "Игрок"
            ctx_ref.send("join", {"name": my_name})
            self.player_ids.add(ctx_ref.client_id)
            self.player_names[ctx_ref.client_id] = my_name

            # Хосту нужно сразу заполнить roster (он не получает собственный join обратно).
            if ctx_ref.is_host:
                self.roster = sorted(self.player_ids)
                payload_players = {pid: self.player_names.get(pid, _display_name(pid)) for pid in self.roster}
                ctx_ref.send("roster", {"players": payload_players})

        for msg in ctx_ref.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == EVENT_START_GAME:
                self.on_exit()
                self._on_start_game(self.net, self.role)
                return
            if event == "join":
                pid = data.get("sender_id")
                if pid is not None:
                    pid_int = int(pid)
                    self.player_ids.add(pid_int)
                    join_name = data.get("name")
                    if isinstance(join_name, str) and join_name:
                        self.player_names[pid_int] = join_name
                if ctx_ref.is_host:
                    self.roster = sorted(self.player_ids)
                    payload_players = {p: self.player_names.get(p, _display_name(p)) for p in self.roster}
                    ctx_ref.send("roster", {"players": payload_players})
            elif event == "roster":
                roster_players = data.get("players", [])
                if isinstance(roster_players, dict):
                    # dict: id -> ({"name": ...} | "name")
                    parsed: dict[int, str] = {}
                    for k, v in roster_players.items():
                        try:
                            pid_int = int(k)
                        except (TypeError, ValueError):
                            continue
                        if isinstance(v, dict):
                            name = v.get("name")
                            if isinstance(name, str) and name:
                                parsed[pid_int] = name
                            else:
                                parsed[pid_int] = _display_name(pid_int)
                        else:
                            name_str = str(v) if v is not None else ""
                            parsed[pid_int] = name_str or _display_name(pid_int)
                    self.player_names = parsed
                    self.roster = sorted(parsed.keys())
                else:
                    # старый формат: список id
                    self.roster = [int(x) for x in list(roster_players)]
                    for pid_int in self.roster:
                        self.player_names.setdefault(pid_int, _display_name(pid_int))

        self._roster_text.set_text(
            "Игроки:\n" + "\n".join(_display_name_with_map(pid, self.player_names) for pid in self.roster)
        )
        self._btn_back.set_active(True)
        self._btn_start_game.set_active(True)


def run_multiplayer_lobby(
    on_start_game: Callable[[s.NetClient, str], None],
    window_size: tuple[int, int] = (480, 540),
    title: str = "Лобби",
    platform: str = "pygame",
) -> None:
    """Запускает лобби до нажатия «В игру»; затем вызывает on_start_game(net, role).

    platform:
        - "pygame" — десктопное окно через get_screen() и цикл s.update().
        - "kivy" — мобильный / гибридный режим через run_kivy_app().
    """
    if "SPRITEPRO_LOG_DIR" not in os.environ:
        os.environ["SPRITEPRO_LOG_DIR"] = os.path.join(os.getcwd(), "spritepro_logs")

    platform_normalized = platform.lower().strip()

    # Если из s.run(...) пришёл размер окна, используем его вместо дефолтного.
    lobby_size_env = os.environ.get("SPRITEPRO_LOBBY_SIZE")
    if lobby_size_env:
        parts = lobby_size_env.split(",")
        if len(parts) == 2:
            try:
                w = int(parts[0].strip())
                h = int(parts[1].strip())
                window_size = (w, h)
            except ValueError:
                pass

    if platform_normalized == "kivy":
        from spritePro.mobile import run_kivy_app

        def bootstrap() -> None:
            os.environ["SPRITEPRO_IN_KIVY_APP"] = "1"
            s.set_scene(MultiplayerLobbyScene(on_start_game, window_size, title))

        run_kivy_app(
            bootstrap,
            title=title,
            fps=60,
            fill_color=COLOR_BG,
            window_size=window_size,
        )
        return

    # pygame / desktop
    s.get_screen(window_size, title)
    s.set_scene(MultiplayerLobbyScene(on_start_game, window_size, title))
    while True:
        s.update(fill_color=COLOR_BG)
        if s.quit_requested():
            return
