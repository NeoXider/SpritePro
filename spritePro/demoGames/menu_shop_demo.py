"""Демо: одна сцена, отдельные страницы (Меню, Магазин, Инвентарь, Настройки). Меню → Магазин, из Магазина назад в Меню, Выход."""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402
from spritePro.layout import (
    LayoutAlignMain,
    LayoutAlignCross,
    GridFlow,
    layout_flex_row,
    layout_flex_column,
    layout_grid,
    layout_horizontal,
    layout_vertical,
    layout_circle,
    layout_line,
)
from spritePro.constants import Anchor


W, H = 1000, 660
MARGIN = 24
PAD = 16
GAP = 14
SIDEBAR_W = 180
CARD_W, CARD_H = 120, 156
GRID_COLS = 4
NAV_H = 52
BTN_H = 42
RADIUS = 12

# Палитра: тёмная тема, один акцент
COLOR_BG = (22, 24, 32)
COLOR_PANEL = (32, 35, 48)
COLOR_CARD = (42, 46, 62)
COLOR_NAV = (28, 31, 42)
COLOR_BTN = (55, 60, 78)
COLOR_BTN_ACCENT = (70, 130, 220)
COLOR_TEXT = (230, 232, 240)
COLOR_TEXT_DIM = (140, 145, 165)
COLOR_PRICE = (100, 200, 120)


def _panel(w, h, color, scene, radius=RADIUS):
    p = s.Sprite("", (w, h), (0, 0), scene=scene)
    p.set_rect_shape(size=(w, h), color=color, width=0, border_radius=radius)
    return p


def _btn(text, scene, callback, w=140, h=BTN_H, accent=False):
    b = s.Button("", size=(w, h), pos=(0, 0), text=text, text_size=15, scene=scene)
    col = COLOR_BTN_ACCENT if accent else COLOR_BTN
    b.set_rect_shape(size=(w, h), color=col, width=0, border_radius=10)
    if callback:
        b.on_click(callback)
    return b


def _nav_bar(scene, title, on_back):
    """Панель сверху страницы: кнопка «Назад» и заголовок. Возвращает (bar, btn_back, lbl)."""
    w = int(s.WH.x) - 2 * MARGIN
    bar = _panel(w, NAV_H, COLOR_NAV, scene, radius=10)
    bar.set_position((MARGIN, MARGIN), anchor=Anchor.TOP_LEFT)
    btn_back = _btn("← Меню", scene, on_back, w=100, h=36, accent=False)
    lbl = s.TextSprite(title, 18, COLOR_TEXT, (0, 0), anchor=Anchor.MID_LEFT, scene=scene)
    layout_flex_row(
        bar,
        [btn_back, lbl],
        gap=GAP,
        padding=(PAD, 0, PAD, 0),
        align_main=LayoutAlignMain.START,
        align_cross=LayoutAlignCross.CENTER,
        use_local=True,
    ).apply()
    return bar, btn_back, lbl


def _card(name, price_str, scene, on_buy):
    cont = s.Sprite("", (CARD_W, CARD_H), (0, 0), scene=scene)
    cont.set_rect_shape(size=(CARD_W, CARD_H), color=COLOR_CARD, width=0, border_radius=10)
    icon = s.Sprite("", (40, 40), (0, 0), scene=scene)
    icon.set_rect_shape(size=(40, 40), color=COLOR_BTN_ACCENT, width=0, border_radius=8)
    lbl_name = s.TextSprite(name, 12, COLOR_TEXT, (0, 0), anchor=Anchor.MID_TOP, scene=scene)
    lbl_price = s.TextSprite(price_str, 12, COLOR_PRICE, (0, 0), anchor=Anchor.MID_TOP, scene=scene)
    buy_btn = s.Button("", size=(70, 24), pos=(0, 0), text="Купить", text_size=11, scene=scene)
    buy_btn.set_rect_shape(size=(70, 24), color=COLOR_BTN_ACCENT, width=0, border_radius=6)
    buy_btn.on_click(on_buy)
    layout_flex_column(
        cont,
        [icon, lbl_name, lbl_price, buy_btn],
        gap=4,
        padding=8,
        align_main=LayoutAlignMain.CENTER,
        align_cross=LayoutAlignCross.CENTER,
        use_local=True,
    ).apply()
    return cont


INV_SLOT_W, INV_SLOT_H = 100, 56


def _inv_slot(scene, name):
    """Слот инвентаря: иконка + название купленного предмета."""
    slot = s.Sprite("", (INV_SLOT_W, INV_SLOT_H), (0, 0), scene=scene)
    slot.set_rect_shape(size=(INV_SLOT_W, INV_SLOT_H), color=COLOR_CARD, width=0, border_radius=8)
    icon = s.Sprite("", (32, 32), (0, 0), scene=scene)
    icon.set_rect_shape(size=(32, 32), color=COLOR_BTN_ACCENT, width=0, border_radius=6)
    lbl = s.TextSprite(name, 11, COLOR_TEXT, (0, 0), anchor=Anchor.MID_LEFT, scene=scene)
    layout_flex_row(
        slot,
        [icon, lbl],
        gap=6,
        padding=6,
        align_main=LayoutAlignMain.CENTER,
        align_cross=LayoutAlignCross.CENTER,
        use_local=True,
    ).apply()
    return slot


# Имена страниц
PAGE_MENU = "MENU"
PAGE_SHOP = "SHOP"
PAGE_INVENTORY = "INVENTORY"
PAGE_SETTINGS = "SETTINGS"


class MenuPage(s.Page):
    """Главное меню: лейаут по центру экрана, флекс, выравнивание по центру."""

    def __init__(self, scene, pm):
        super().__init__(PAGE_MENU, scene=scene)
        self.pm = pm
        w, h = int(s.WH.x), int(s.WH.y)
        content_top = MARGIN + 80
        content_h = h - content_top - 60
        content_w = w - 2 * MARGIN
        cx, cy = w // 2, content_top + content_h // 2

        root = s.Sprite("", (content_w, content_h), (cx, cy), scene=scene)
        root.set_rect_shape(size=(content_w, content_h), color=(0, 0, 0, 0), width=0)

        panel_w = min(400, content_w - 2 * MARGIN)
        panel_h = min(380, content_h - 2 * MARGIN)
        panel = _panel(panel_w, panel_h, COLOR_PANEL, scene)

        layout_flex_column(
            root,
            [panel],
            gap=0,
            padding=0,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()

        title = s.TextSprite("Меню", 26, COLOR_TEXT, (0, 0), anchor=Anchor.MID_TOP, scene=scene)
        btn_shop = _btn("Магазин", scene, lambda: pm.set_active_page(PAGE_SHOP), w=200, accent=True)
        btn_inv = _btn("Инвентарь", scene, lambda: pm.set_active_page(PAGE_INVENTORY), w=200)
        btn_settings = _btn("Настройки", scene, lambda: pm.set_active_page(PAGE_SETTINGS), w=200)
        btn_exit = _btn("Выход", scene, self._on_exit, w=200)

        layout_flex_column(
            panel,
            [title, btn_shop, btn_inv, btn_settings, btn_exit],
            gap=20,
            padding=PAD * 2,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()
        self.add_sprite(root)

    def _on_exit(self):
        raise SystemExit(0)


class ShopPage(s.Page):
    """Страница магазина: назад в меню, категории, сетка товаров."""

    def __init__(self, scene, pm, status_cb):
        super().__init__(PAGE_SHOP, scene=scene)
        self.pm = pm
        w, h = int(s.WH.x), int(s.WH.y)
        content_top = MARGIN + NAV_H + GAP
        content_h = h - content_top - 50
        content_w = w - 2 * MARGIN

        bar, btn_back, nav_lbl = _nav_bar(scene, "Магазин", lambda: pm.set_active_page(PAGE_MENU))
        self.add_sprite(bar)

        main = _panel(content_w, content_h, COLOR_PANEL, scene)
        main.set_position((MARGIN, content_top), anchor=Anchor.TOP_LEFT)

        inner_w = content_w - 2 * PAD
        inner_h = content_h - 2 * PAD
        inner = s.Sprite("", (inner_w, inner_h), (0, 0), scene=scene)
        inner.set_rect_shape(size=(inner_w, inner_h), color=(0, 0, 0, 0), width=0)
        inner.set_parent(main, keep_world_position=False)
        inner.local_position = (0, 0)

        sidebar = _panel(SIDEBAR_W, inner_h, COLOR_CARD, scene, radius=8)
        grid_w = inner_w - SIDEBAR_W - GAP
        grid_panel = s.Sprite("", (grid_w, inner_h), (0, 0), scene=scene)
        grid_panel.set_rect_shape(size=(grid_w, inner_h), color=(0, 0, 0, 0), width=0)
        layout_flex_row(
            inner,
            [sidebar, grid_panel],
            gap=GAP,
            padding=0,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.START,
            use_local=True,
        ).apply()

        cat_names = ["Всё", "Оружие", "Броня", "Зелья", "Квесты"]
        cat_btns = [
            _btn(n, scene, lambda n=n: status_cb(f"Категория: {n}"), w=SIDEBAR_W - 2 * PAD, h=36)
            for n in cat_names
        ]
        for b in cat_btns:
            b.set_rect_shape(
                size=(SIDEBAR_W - 2 * PAD, 36), color=COLOR_BTN, width=0, border_radius=8
            )
        layout_flex_column(
            sidebar,
            cat_btns,
            gap=6,
            padding=PAD,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()

        items = [
            ("Меч", "100 G"),
            ("Щит", "80 G"),
            ("Зелье HP", "25 G"),
            ("Шлем", "120 G"),
            ("Лук", "90 G"),
            ("Кольчуга", "150 G"),
            ("Кинжал", "45 G"),
            ("Сапоги", "60 G"),
            ("Перчатки", "55 G"),
            ("Пояс", "40 G"),
            ("Амулет", "200 G"),
            ("Кольцо", "180 G"),
        ]

        def on_buy(name):
            scene.inventory.append(name)
            status_cb(f"В инвентарь: {name}")

        cards = [_card(n, p, scene, on_buy=lambda n=n: on_buy(n)) for n, p in items]
        layout_grid(
            grid_panel,
            cards,
            cols=GRID_COLS,
            gap_x=10,
            gap_y=10,
            padding=8,
            flow=GridFlow.ROW,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()
        self.add_sprite(main)


class InventoryPage(s.Page):
    """Страница инвентаря: флекс с купленными предметами, обновляется при открытии."""

    def __init__(self, scene, pm, status_cb):
        super().__init__(PAGE_INVENTORY, scene=scene)
        self.pm = pm
        self._status_cb = status_cb
        w, h = int(s.WH.x), int(s.WH.y)
        content_top = MARGIN + NAV_H + GAP
        content_h = h - content_top - 50
        content_w = w - 2 * MARGIN

        bar, _, _ = _nav_bar(scene, "Инвентарь", lambda: pm.set_active_page(PAGE_MENU))
        self.add_sprite(bar)

        main = _panel(content_w, content_h, COLOR_PANEL, scene)
        main.set_position((MARGIN, content_top), anchor=Anchor.TOP_LEFT)

        inv_inner_w = content_w - 2 * PAD
        inv_inner_h = content_h - 2 * PAD - BTN_H - GAP
        self._inv_slots = s.Sprite("", (inv_inner_w, inv_inner_h), (0, 0), scene=scene)
        self._inv_slots.set_rect_shape(size=(inv_inner_w, inv_inner_h), color=(0, 0, 0, 0), width=0)

        btn = _btn(
            "Обновить",
            scene,
            lambda: (self._refresh_slots(), status_cb("Инвентарь обновлён")),
            w=120,
            h=38,
        )
        layout_flex_column(
            main,
            [self._inv_slots, btn],
            gap=GAP,
            padding=PAD,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()
        self.add_sprite(main)

    def _refresh_slots(self):
        for child in list(self._inv_slots.children):
            child.set_parent(None)
            if hasattr(child, "kill"):
                child.kill()
        inv = getattr(self.scene, "inventory", [])
        if not inv:
            hint = s.TextSprite(
                "Пусто. Купленные товары появятся здесь.",
                16,
                COLOR_TEXT_DIM,
                (0, 0),
                anchor=Anchor.CENTER,
                scene=self.scene,
            )
            hint.set_parent(self._inv_slots, keep_world_position=False)
            hint.local_position = (0, 0)
        else:
            for name in inv:
                slot = _inv_slot(self.scene, name)
                slot.set_parent(self._inv_slots, keep_world_position=False)
        layout_flex_row(
            self._inv_slots,
            list(self._inv_slots.children),
            gap=GAP,
            padding=PAD,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        ).apply()

    def on_activate(self):
        self._refresh_slots()
        self._inv_slots.set_active(True)
        for child in list(self._inv_slots.children):
            child.set_active(True)

    def on_deactivate(self):
        self._inv_slots.set_active(False)
        for child in list(self._inv_slots.children):
            child.set_active(False)


class SettingsPage(s.Page):
    """Страница настроек: назад в меню."""

    def __init__(self, scene, pm):
        super().__init__(PAGE_SETTINGS, scene=scene)
        self.pm = pm
        w, h = int(s.WH.x), int(s.WH.y)
        content_top = MARGIN + NAV_H + GAP
        content_h = h - content_top - 50
        content_w = min(400, w - 2 * MARGIN)
        cx = w // 2
        cy = content_top + content_h // 2

        bar, _, _ = _nav_bar(scene, "Настройки", lambda: pm.set_active_page(PAGE_MENU))
        self.add_sprite(bar)

        panel = _panel(content_w, content_h, COLOR_PANEL, scene)
        panel.set_position((cx, cy), anchor=Anchor.CENTER)

        lbl = s.TextSprite(
            "Здесь могут быть настройки.",
            16,
            COLOR_TEXT_DIM,
            (0, 0),
            anchor=Anchor.CENTER,
            scene=scene,
        )
        lbl.set_parent(panel, keep_world_position=False)
        lbl.local_position = (0, 0)
        self.add_sprite(panel)


class MenuShopScene(s.Scene):
    """Одна сцена с PageManager: переключение Меню ↔ Магазин ↔ Инвентарь ↔ Настройки."""

    def __init__(self):
        super().__init__()
        w, h = int(s.WH.x), int(s.WH.y)

        bg = s.Sprite("", (w, h), (w // 2, h // 2), scene=self, sorting_order=-10)
        bg.set_rect_shape(size=(w, h), color=COLOR_BG, width=0)
        bg.set_position((0, 0), anchor=Anchor.TOP_LEFT)

        self._status_text = s.TextSprite(
            "Меню → Магазин / Инвентарь / Настройки. Из любой страницы: ← Меню. Выход — из главного меню.",
            13,
            COLOR_TEXT_DIM,
            (w // 2, h - 20),
            anchor=Anchor.MID_BOTTOM,
            scene=self,
        )
        self._status_text.sorting_order = 300
        self.inventory = []

        def status(msg):
            self._status_text.text = msg

        self.pm = s.PageManager(scene=self)
        self.pm.add_page(MenuPage(self, self.pm))
        self.pm.add_page(ShopPage(self, self.pm, status))
        self.pm.add_page(InventoryPage(self, self.pm, status))
        self.pm.add_page(SettingsPage(self, self.pm))
        self.pm.set_active_page(PAGE_MENU)

    def update(self, dt: float) -> None:
        self.pm.update()


def main():
    s.get_screen((W, H), "Меню и Инвентарь")
    scene = MenuShopScene()
    s.set_scene(scene)
    while True:
        s.update(fill_color=COLOR_BG)


if __name__ == "__main__":
    main()
