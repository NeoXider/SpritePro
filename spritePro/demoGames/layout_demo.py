"""Демо всех типов лейаута: FLEX_ROW, FLEX_COLUMN, GRID, HORIZONTAL, VERTICAL, CIRCLE, LINE."""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402
from spritePro.layout import (
    Layout,
    LayoutDirection,
    LayoutAlignMain,
    LayoutAlignCross,
    GridFlow,
    layout_flex_row,
    layout_flex_column,
    layout_horizontal,
    layout_vertical,
    layout_grid,
    layout_circle,
    layout_line,
)


def _make_box(size=(30, 30), color=(255, 200, 100)):
    """Квадрат-спрайт для использования как ребёнок лейаута."""
    sp = s.Sprite("", size, (0, 0))
    sp.set_rect_shape(size=size, color=color, border_radius=4)
    return sp


PAD_TOP = 78
PAD_BOTTOM = 44
PAD_SIDE = 100
MAIN_CONT_COLOR = (40, 40, 52)
MAIN_CONT_BORDER = 2
MAIN_CONT_RADIUS = 12


def _make_zone_container(w, h, scene):
    """Контейнер зоны — спрайт с рамкой, позиция задаётся главным лейаутом."""
    cont = s.Sprite("", (w, h), (0, 0), scene=scene)
    cont.set_rect_shape(size=(w, h), color=(60, 60, 80), width=0, border_radius=8)
    return cont


def _add_zone_label(cont, label_text, scene):
    """Добавляет подпись над контейнером зоны; привязывает к контейнеру, чтобы двигалась с ним."""
    h = cont.rect.height
    lbl = s.TextSprite(
        label_text,
        14,
        (200, 200, 200),
        (0, 0),
        anchor=s.Anchor.MID_BOTTOM,
        scene=scene,
    )
    lbl.set_parent(cont, keep_world_position=False)
    lbl.local_position = (0, -h // 2 - 10)
    return lbl


class LayoutDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        W, H = s.WH.x, s.WH.y
        cx = W // 2

        main_w = W - 2 * PAD_SIDE
        main_h = H - PAD_TOP - PAD_BOTTOM
        main_cont = s.Sprite(
            "",
            (main_w, main_h),
            (PAD_SIDE + main_w / 2, PAD_TOP + main_h / 2),
            scene=self,
            sorting_order=-2,
        )
        main_cont.set_rect_shape(
            size=(main_w, main_h),
            color=MAIN_CONT_COLOR,
            width=MAIN_CONT_BORDER,
            border_radius=MAIN_CONT_RADIUS,
        )
        main_cont.set_position((PAD_SIDE, PAD_TOP), anchor=s.Anchor.TOP_LEFT)
        self._main_cont = main_cont
        self._main_w = main_w
        self._main_h = main_h

        cont_flex_row = _make_zone_container(120, 70, self)
        cont_flex_col = _make_zone_container(70, 120, self)
        cont_grid = _make_zone_container(120, 120, self)
        cont_h = _make_zone_container(100, 50, self)
        cont_v = _make_zone_container(60, 120, self)
        cont_circle = _make_zone_container(120, 120, self)
        cont_line = _make_zone_container(120, 80, self)

        zone_containers = [
            cont_flex_row,
            cont_flex_col,
            cont_grid,
            cont_h,
            cont_v,
            cont_circle,
            cont_line,
        ]
        self.main_layout = Layout(
            main_cont,
            zone_containers,
            direction=LayoutDirection.FLEX_ROW,
            gap=12,
            padding=8,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            wrap=True,
            use_local=True,
        )
        self.main_layout.apply()

        self._zone_labels = []
        lbl_fr = _add_zone_label(cont_flex_row, "FLEX_ROW", self)
        self._zone_labels.append((cont_flex_row, lbl_fr))
        lbl_fc = _add_zone_label(cont_flex_col, "FLEX_COLUMN", self)
        lbl_gr = _add_zone_label(cont_grid, "GRID", self)
        lbl_h = _add_zone_label(cont_h, "HORIZONTAL", self)
        lbl_v = _add_zone_label(cont_v, "VERTICAL", self)
        lbl_c = _add_zone_label(cont_circle, "CIRCLE", self)
        lbl_ln = _add_zone_label(cont_line, "LINE", self)
        self._zone_labels.extend(
            [
                (cont_flex_col, lbl_fc),
                (cont_grid, lbl_gr),
                (cont_h, lbl_h),
                (cont_v, lbl_v),
                (cont_circle, lbl_c),
                (cont_line, lbl_ln),
            ]
        )

        kids_fr = [_make_box((22, 22), (120, 180, 255)) for _ in range(5)]
        for k in kids_fr:
            k.scene = self
        layout_flex_row(
            cont_flex_row,
            kids_fr,
            gap=6,
            padding=6,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        kids_fc = [_make_box((20, 20), (180, 120, 255)) for _ in range(4)]
        for k in kids_fc:
            k.scene = self
        layout_flex_column(
            cont_flex_col,
            kids_fc,
            gap=6,
            padding=6,
            align_main=LayoutAlignMain.START,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        kids_gr = [_make_box((18, 18), (100, 220, 140)) for _ in range(9)]
        for k in kids_gr:
            k.scene = self
        layout_grid(
            cont_grid,
            kids_gr,
            rows=3,
            cols=3,
            gap_x=6,
            gap_y=6,
            padding=8,
            flow=GridFlow.ROW,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        kids_h = [_make_box((18, 18), (255, 160, 100)) for _ in range(4)]
        for k in kids_h:
            k.scene = self
        layout_horizontal(
            cont_h,
            kids_h,
            gap=8,
            padding=4,
            align_main=LayoutAlignMain.SPACE_BETWEEN,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        kids_v = [_make_box((18, 18), (255, 100, 150)) for _ in range(5)]
        for k in kids_v:
            k.scene = self
        layout_vertical(
            cont_v,
            kids_v,
            gap=6,
            padding=4,
            align_main=LayoutAlignMain.SPACE_EVENLY,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        kids_c = [_make_box((16, 16), (200, 255, 200)) for _ in range(8)]
        for k in kids_c:
            k.scene = self
        layout_circle(
            cont_circle,
            kids_c,
            radius=42,
            start_angle=0,
            clockwise=True,
            rotate_children=True,
            offset_angle=0,
            padding=4,
            use_local=True,
        )

        # LINE: точки для расстановки детей — в мировых координатах (лейаут при use_local переведёт в локальные).
        # Визуальная линия — дочерний спрайт контейнера с локальными точками, двигается вместе с зоной.
        w, h = cont_line.rect.width, cont_line.rect.height
        r = cont_line.rect
        points_line_world = [
            (r.left + 10, r.bottom - 12),
            (r.left + 45, r.centery - 5),
            (r.centerx, r.centery + 8),
            (r.right - 15, r.top + 12),
        ]
        points_line_local = [
            (10 - w / 2, h / 2 - 12),
            (45 - w / 2, -5),
            (0, 8),
            (w / 2 - 15, -h / 2 + 12),
        ]
        self._points_line_local = points_line_local
        line_path = s.Sprite("", (1, 1), (0, 0), scene=self, sorting_order=1)
        line_path.set_parent(cont_line, keep_world_position=False)
        line_path.set_polyline(
            points_line_local,
            color=(90, 90, 130),
            width=2,
            world_points=False,
        )
        kids_line = [_make_box((14, 14), (180, 180, 255)) for _ in range(5)]
        for k in kids_line:
            k.scene = self
        layout_line(
            cont_line,
            kids_line,
            points=points_line_world,
            use_local=True,
        )

        self.title = s.TextSprite(
            "Layout Demo",
            26,
            (255, 255, 255),
            (cx, 18),
            anchor=s.Anchor.MID_TOP,
            scene=self,
        )

        self._main_directions = [
            LayoutDirection.FLEX_ROW,
            LayoutDirection.FLEX_COLUMN,
            LayoutDirection.HORIZONTAL,
            LayoutDirection.VERTICAL,
        ]
        self._align_options = [
            LayoutAlignMain.START,
            LayoutAlignMain.CENTER,
            LayoutAlignMain.END,
            LayoutAlignMain.SPACE_BETWEEN,
            LayoutAlignMain.SPACE_AROUND,
            LayoutAlignMain.SPACE_EVENLY,
        ]
        self._direction_index = 0
        self._align_index = 1
        self._moved = False
        self._alt_pos = (PAD_SIDE + 60, PAD_TOP + 25)

        btn_y = 50
        btn_h = 32
        buttons_container = (0, btn_y, W, btn_h)
        self.btn_layout = s.Button(
            "",
            size=(140, btn_h),
            pos=(0, 0),
            text="Лейаут",
            text_size=14,
            scene=self,
            on_click=self._next_layout,
        )
        self.btn_align = s.Button(
            "",
            size=(140, btn_h),
            pos=(0, 0),
            text="Выравнивание",
            text_size=14,
            scene=self,
            on_click=self._next_align,
        )
        self.btn_width_minus = s.Button(
            "",
            size=(36, btn_h),
            pos=(0, 0),
            text="−",
            text_size=18,
            scene=self,
            on_click=self._shrink_width,
        )
        self.btn_width_plus = s.Button(
            "",
            size=(36, btn_h),
            pos=(0, 0),
            text="+",
            text_size=18,
            scene=self,
            on_click=self._grow_width,
        )
        self.btn_rotate = s.Button(
            "",
            size=(100, btn_h),
            pos=(0, 0),
            text="Вращать",
            text_size=14,
            scene=self,
            on_click=self._rotate_main,
        )
        self.btn_move = s.Button(
            "",
            size=(120, btn_h),
            pos=(0, 0),
            text="Переместить",
            text_size=14,
            scene=self,
            on_click=self._toggle_move,
        )
        self.btn_debug_borders = s.Button(
            "",
            size=(120, btn_h),
            pos=(0, 0),
            text="Границы лейаута",
            text_size=14,
            scene=self,
            on_click=self._toggle_layout_debug_borders,
        )
        btn_list = [
            self.btn_layout,
            self.btn_align,
            self.btn_width_minus,
            self.btn_width_plus,
            self.btn_rotate,
            self.btn_move,
            self.btn_debug_borders,
        ]
        self._buttons_layout = layout_flex_row(
            buttons_container,
            btn_list,
            gap=8,
            padding=0,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            wrap=False,
        )
        self._update_buttons_text()
        self._update_layout_debug_button()

        self.hint = s.TextSprite(
            "FLEX_ROW / FLEX_COLUMN / GRID / HORIZONTAL / VERTICAL / CIRCLE / LINE",
            12,
            (150, 150, 150),
            (cx, H - 18),
            anchor=s.Anchor.MID_BOTTOM,
            scene=self,
        )

        self._line_cont = cont_line
        self._line_path_sprite = line_path
        self._kids_line = kids_line

        self._all_layout_sprites = (
            [main_cont]
            + zone_containers
            + [line_path]
            + kids_fr
            + kids_fc
            + kids_gr
            + kids_h
            + kids_v
            + kids_c
            + kids_line
            + [
                self.title,
                self.btn_layout,
                self.btn_align,
                self.btn_width_minus,
                self.btn_width_plus,
                self.btn_rotate,
                self.btn_move,
                self.btn_debug_borders,
                self.hint,
                lbl_fr,
                lbl_fc,
                lbl_gr,
                lbl_h,
                lbl_v,
                lbl_c,
                lbl_ln,
            ]
        )

    def _refresh_line_zone(self):
        """Пересчитывает линию и детей LINE после сдвига/ресайза контейнера.

        Точки для layout_line — мировые (лейаут при use_local переведёт в локальные).
        Визуальная линия — дочерний спрайт с локальными точками, двигается с зоной.
        """
        r = self._line_cont.rect
        w, h = r.width, r.height
        points_world = [
            (r.left + 10, r.bottom - 12),
            (r.left + 45, r.centery - 5),
            (r.centerx, r.centery + 8),
            (r.right - 15, r.top + 12),
        ]
        points_local = [
            (10 - w / 2, h / 2 - 12),
            (45 - w / 2, -5),
            (0, 8),
            (w / 2 - 15, -h / 2 + 12),
        ]
        self._points_line_local = points_local
        self._line_path_sprite.set_polyline(
            points_local,
            color=(90, 90, 130),
            width=2,
            world_points=False,
        )
        layout_line(
            self._line_cont,
            self._kids_line,
            points=points_world,
            use_local=True,
        )

    def _update_buttons_text(self):
        d = self._main_directions[self._direction_index]
        a = self._align_options[self._align_index]
        self.btn_layout.text_sprite.text = f"Лейаут: {d.name}"
        self.btn_align.text_sprite.text = f"Выравнивание: {a.name}"

    def _next_layout(self):
        self._direction_index = (self._direction_index + 1) % len(self._main_directions)
        self.main_layout.direction = self._main_directions[self._direction_index]
        self.main_layout.apply()
        self._refresh_line_zone()
        self._update_buttons_text()

    def _next_align(self):
        self._align_index = (self._align_index + 1) % len(self._align_options)
        self.main_layout.align_main = self._align_options[self._align_index]
        self.main_layout.align_cross = LayoutAlignCross.CENTER
        self.main_layout.apply()
        self._refresh_line_zone()
        self._update_buttons_text()

    def _main_cont_pos(self):
        return self._alt_pos if self._moved else (PAD_SIDE, PAD_TOP)

    def _shrink_width(self):
        step = 60
        new_w = max(400, self._main_w - step)
        if new_w == self._main_w:
            return
        self._main_w = new_w
        self._main_cont.set_rect_shape(
            size=(self._main_w, self._main_h),
            color=MAIN_CONT_COLOR,
            width=MAIN_CONT_BORDER,
            border_radius=MAIN_CONT_RADIUS,
        )
        self._main_cont.set_position(self._main_cont_pos(), anchor=s.Anchor.TOP_LEFT)
        self.main_layout.apply()
        self._refresh_line_zone()

    def _grow_width(self):
        step = 60
        max_w = s.WH.x - 2 * PAD_SIDE
        new_w = min(max_w, self._main_w + step)
        if new_w == self._main_w:
            return
        self._main_w = new_w
        self._main_cont.set_rect_shape(
            size=(self._main_w, self._main_h),
            color=MAIN_CONT_COLOR,
            width=MAIN_CONT_BORDER,
            border_radius=MAIN_CONT_RADIUS,
        )
        self._main_cont.set_position(self._main_cont_pos(), anchor=s.Anchor.TOP_LEFT)
        self.main_layout.apply()
        self._refresh_line_zone()

    def _rotate_main(self):
        self._main_cont.angle = (self._main_cont.angle + 45) % 360

    def _toggle_move(self):
        self._moved = not self._moved
        if self._moved:
            self._main_cont.set_position(self._alt_pos, anchor=s.Anchor.TOP_LEFT)
        else:
            self._main_cont.set_position((PAD_SIDE, PAD_TOP), anchor=s.Anchor.TOP_LEFT)

    def _toggle_layout_debug_borders(self):
        """Вкл/выкл отладку границ у главного лейаута (Layout.debug_borders)."""
        self.main_layout.debug_borders = not self.main_layout.debug_borders
        self._update_layout_debug_button()

    def _update_layout_debug_button(self):
        self.btn_debug_borders.text_sprite.text = (
            "Границы: ВКЛ" if self.main_layout.debug_borders else "Границы: ВЫКЛ"
        )


def main():
    s.get_screen((900, 600), "Layout Demo")
    scene = LayoutDemoScene()
    s.set_scene(scene)
    while True:
        s.update(fill_color=(25, 25, 35))


if __name__ == "__main__":
    main()
