"""Автолейаут для расстановки дочерних спрайтов.

Поддерживает направления: flex-ряд/колонка (с переносом), горизонталь/вертикаль,
сетка, размещение по окружности и вдоль ломаной линии. Класс Layout наследует Sprite:
при container=None лейаут сам является контейнером и его можно перемещать вместе
с детьми. Удобные функции layout_flex_row, layout_flex_column, layout_grid и т.д.
создают и применяют лейаут одной строкой.
"""

from __future__ import annotations

import math
from enum import Enum
from typing import List, Optional, Sequence, Tuple, Union

import pygame

from .constants import Anchor
from .sprite import Sprite

# Тип контейнера: Sprite с rect или (x, y, width, height)
ContainerInput = Union["pygame.sprite.Sprite", Tuple[float, float, float, float], None]

# Отладка границ лейаута (debug_borders=True)
_DEBUG_BORDER_COLOR = (80, 160, 220)
_DEBUG_ALPHA = 180


class LayoutDirection(str, Enum):
    """Тип лейаута: направление расстановки детей.

    Attributes:
        FLEX_ROW: Дети в ряд внутри ширины/высоты контейнера (flex по горизонтали).
        FLEX_COLUMN: Дети в колонку внутри контейнера (flex по вертикали).
        HORIZONTAL: Ряд слева направо.
        VERTICAL: Колонка сверху вниз.
        GRID: Сетка (rows x cols).
        CIRCLE: Элементы по окружности.
        LINE: Элементы вдоль ломаной (points).
    """

    FLEX_ROW = "flex_row"
    FLEX_COLUMN = "flex_column"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    GRID = "grid"
    CIRCLE = "circle"
    LINE = "line"


class LayoutAlignMain(str, Enum):
    """Выравнивание по основной оси.

    Attributes:
        START: В начало оси.
        CENTER: По центру.
        END: В конец оси.
        SPACE_BETWEEN: Равномерно между элементами (края без отступа).
        SPACE_AROUND: Равномерно с половинным отступом по краям.
        SPACE_EVENLY: Равномерно с одинаковым отступом везде.
    """

    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"
    SPACE_EVENLY = "space_evenly"


class LayoutAlignCross(str, Enum):
    """Выравнивание по поперечной оси.

    Attributes:
        START: К началу поперечной оси.
        CENTER: По центру.
        END: К концу.
    """

    START = "start"
    CENTER = "center"
    END = "end"


class GridFlow(str, Enum):
    """Порядок заполнения сетки.

    Attributes:
        ROW: Сначала по строке (слева направо, затем следующая строка).
        COLUMN: Сначала по столбцу (сверху вниз, затем следующий столбец).
    """

    ROW = "row"
    COLUMN = "column"


def _normalize_padding(
    padding: Union[int, float, Sequence[Union[int, float]]],
) -> Tuple[float, float, float, float]:
    """Приводит padding к (top, right, bottom, left).

    Args:
        padding: Одно число, (vertical, horizontal) или (top, right, bottom, left).

    Returns:
        Кортеж (top, right, bottom, left) в пикселях.
    """
    if isinstance(padding, (int, float)):
        p = float(padding)
        return (p, p, p, p)
    seq = tuple(padding)
    if len(seq) == 2:
        v, h = float(seq[0]), float(seq[1])
        return (v, h, v, h)
    if len(seq) >= 4:
        return (float(seq[0]), float(seq[1]), float(seq[2]), float(seq[3]))
    p = float(seq[0]) if seq else 0.0
    return (p, p, p, p)


def _normalize_gap(
    gap: Union[int, float, Tuple[float, float], Sequence[Union[int, float]]],
    gap_x: Optional[float],
    gap_y: Optional[float],
) -> Tuple[float, float]:
    """Приводит gap к (gap_x, gap_y).

    Args:
        gap: Одно число или (gap_x, gap_y).
        gap_x: Явный зазор по x (переопределяет компоненту из gap).
        gap_y: Явный зазор по y (переопределяет компоненту из gap).

    Returns:
        (gap_x, gap_y) в пикселях.
    """
    if isinstance(gap, (int, float)):
        g = float(gap)
        gx, gy = g, g
    elif isinstance(gap, (list, tuple)) and len(gap) >= 2:
        gx, gy = float(gap[0]), float(gap[1])
    else:
        gx, gy = 10.0, 10.0
    if gap_x is not None:
        gx = float(gap_x)
    if gap_y is not None:
        gy = float(gap_y)
    return (gx, gy)


class Layout(Sprite):
    """Лейаут для автоматической расстановки дочерних спрайтов (flex, сетка, круг, линия).

    Наследует Sprite: лейаут можно перемещать, дочерние элементы участвуют в иерархии
    parent/children. При container=None лейаут сам является контейнером (rect, size, pos);
    иначе контейнер задаётся снаружи (спрайт или (x, y, w, h)).
    """

    def __init__(
        self,
        container: ContainerInput,
        children: Optional[List[pygame.sprite.Sprite]] = None,
        direction: LayoutDirection = LayoutDirection.FLEX_ROW,
        gap: Union[int, float, Tuple[float, float], Sequence[Union[int, float]]] = 10,
        padding: Union[int, float, Sequence[Union[int, float]]] = 0,
        align_main: LayoutAlignMain = LayoutAlignMain.START,
        align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        gap_x: Optional[float] = None,
        gap_y: Optional[float] = None,
        flow: GridFlow = GridFlow.ROW,
        radius: Optional[float] = None,
        start_angle: float = 0,
        clockwise: bool = True,
        rotate_children: bool = True,
        offset_angle: float = 0,
        points: Optional[Sequence[Tuple[float, float]]] = None,
        use_local: bool = False,
        child_anchor: Optional[Anchor] = None,
        wrap: bool = True,
        size: Optional[Tuple[float, float]] = None,
        pos: Optional[Tuple[float, float]] = None,
        scene: Optional[object] = None,
        debug_borders: bool = False,
        auto_apply: bool = True,
    ):
        """Инициализирует лейаут.

        Args:
            container: Спрайт с rect, кортеж (x, y, width, height) или None. При None
                лейаут выступает контейнером — задайте size и pos.
            children: Список дочерних спрайтов для расстановки. Можно передать пустой
                и добавлять позже через add() / add_children().
            direction: Тип расстановки: FLEX_ROW, FLEX_COLUMN, HORIZONTAL, VERTICAL,
                GRID, CIRCLE, LINE.
            gap: Зазор между элементами. Число или (gap_x, gap_y). По умолчанию 10.
            padding: Внутренний отступ контейнера. Число или (top, right, bottom, left).
            align_main: Выравнивание по основной оси (START, CENTER, END, SPACE_*).
            align_cross: Выравнивание по поперечной оси (START, CENTER, END).
            rows: Количество строк для GRID. Опционально.
            cols: Количество столбцов для GRID. Опционально.
            gap_x: Зазор по X (переопределяет компоненту из gap).
            gap_y: Зазор по Y (переопределяет компоненту из gap).
            flow: Порядок заполнения сетки: ROW или COLUMN.
            radius: Радиус окружности для CIRCLE.
            start_angle: Начальный угол для CIRCLE, градусы.
            clockwise: Направление обхода по окружности (по часовой).
            rotate_children: Для CIRCLE — поворачивать ли детей по касательной.
            offset_angle: Смещение угла поворота детей для CIRCLE, градусы.
            points: Точки ломаной для LINE: [(x, y), ...].
            use_local: Если True и контейнер — Sprite, позиции задаются в локальных
                координатах контейнера (дети двигаются вместе с контейнером).
            child_anchor: Якорь при установке позиции ребёнка. None — использовать
                якорь самого спрайта.
            wrap: Для FLEX_ROW/FLEX_COLUMN — перенос на следующую строку/колонку
                при нехватке места. По умолчанию True.
            size: Размер лейаута при container=None. Иначе не используется.
            pos: Позиция лейаута при container=None. Иначе не используется.
            scene: Сцена при container=None. Иначе берётся из контейнера.
            debug_borders: Если True, отображаются границы контейнера лейаута (для отладки).
            auto_apply: Если True (по умолчанию), add/remove/set_size вызывают apply()
                автоматически. Если False — лейаут ручной: обновление только по refresh()/apply().
        """
        self._debug_borders = bool(debug_borders)
        self._auto_apply = bool(auto_apply)
        self._debug_overlay: Optional["Sprite"] = None
        if container is None:
            sz = size or (100, 100)
            p = pos or (0, 0)
            super().__init__("", sz, p, scene=scene)
            self.set_rect_shape(size=sz, color=(0, 0, 0), width=0)
            self.set_alpha(0)
            self._container = None
        else:
            super().__init__("", (1, 1), (0, 0), scene=getattr(container, "scene", scene))
            self.set_alpha(0)
            self._container = container
            self.active = False
        self.container = container
        self._children = list(children) if children else []
        for c in self._children:
            if self.container is None and hasattr(c, "set_parent"):
                c.set_parent(self, keep_world_position=False)
        self.direction = direction
        self.align_main = align_main
        self.align_cross = align_cross
        self.rows = rows
        self.cols = cols
        self.flow = flow
        self.radius = radius
        self.start_angle = start_angle
        self.clockwise = clockwise
        self.rotate_children = rotate_children
        self.offset_angle = offset_angle
        self.points = list(points) if points else []
        self.use_local = use_local
        self.child_anchor = child_anchor
        self.wrap = wrap
        self._padding = _normalize_padding(padding)
        gx, gy = _normalize_gap(gap, gap_x, gap_y)
        self._gap_x = gx
        self._gap_y = gy
        if self._auto_apply and self._children:
            self.apply()
        self._apply_debug_style()

    def _apply_debug_style(self) -> None:
        """Включает или выключает отображение границ контейнера (для отладки).

        Контейнер (сам лейаут при container=None) — слой -10. Обводка — отдельный
        overlay на слое 10000, чтобы была поверх содержимого.
        """
        if self._debug_borders:
            if self._debug_overlay is None:
                self._debug_overlay = Sprite(
                    "",
                    (1, 1),
                    (0, 0),
                    scene=self.scene,
                )
                self._debug_overlay.set_rect_shape(
                    size=(1, 1),
                    color=_DEBUG_BORDER_COLOR,
                    width=2,
                )
                self._debug_overlay.set_alpha(_DEBUG_ALPHA)
                self._debug_overlay.sorting_order = 10000
                if self.container is None:
                    self._debug_overlay.set_parent(self, keep_world_position=False)
                    if hasattr(self._debug_overlay, "local_position"):
                        self._debug_overlay.local_position = (0, 0)
                elif hasattr(self.container, "set_parent"):
                    self._debug_overlay.set_parent(self.container, keep_world_position=False)
                    if hasattr(self._debug_overlay, "local_position"):
                        self._debug_overlay.local_position = (0, 0)
            self._debug_overlay.active = True
            self._sync_debug_overlay()
            if self.container is None:
                self.set_alpha(0)
                self.set_rect_shape(size=tuple(self.rect.size), color=(0, 0, 0), width=0)
                self.sorting_order = -10
        else:
            if self._debug_overlay is not None:
                self._debug_overlay.active = False
            if self.container is None:
                self.set_alpha(0)
                self.set_rect_shape(size=tuple(self.rect.size), color=(0, 0, 0), width=0)
                self.sorting_order = None

    def _sync_debug_overlay(self) -> None:
        """Синхронизирует overlay с rect контейнера."""
        if self._debug_overlay is None:
            return
        r = self._get_container_rect()
        self._debug_overlay.set_rect_shape(
            size=(r.width, r.height),
            color=_DEBUG_BORDER_COLOR,
            width=2,
        )
        if self.container is None:
            return
        if hasattr(self.container, "rect"):
            self._debug_overlay._apply_parent_transform()
        else:
            self._debug_overlay.set_position((r.left, r.top), anchor=Anchor.TOP_LEFT)

    @property
    def debug_borders(self) -> bool:
        """Включено ли отображение границ контейнера (для отладки)."""
        return self._debug_borders

    @debug_borders.setter
    def debug_borders(self, value: bool) -> None:
        self._debug_borders = bool(value)
        self._apply_debug_style()

    def set_debug_borders(self, value: bool) -> "Layout":
        """Включает или выключает обводку контейнера (для отладки и видимости границ). Возвращает self."""
        self._debug_borders = bool(value)
        self._apply_debug_style()
        return self

    def _effective_container(
        self,
    ) -> Optional[Union[pygame.sprite.Sprite, Tuple[float, float, float, float]]]:
        """Возвращает объект, относительно которого считаются позиции детей.

        Returns:
            Сам лейаут при container=None, иначе переданный контейнер (спрайт или
            кортеж (x, y, w, h)).
        """
        return self if self.container is None else self.container

    def _get_container_rect(self) -> pygame.Rect:
        """Возвращает прямоугольник контейнера в мировых координатах.

        Returns:
            Копия rect контейнера (при container=None — self.rect).
        """
        if self.container is None:
            return self.rect.copy()
        if hasattr(self.container, "rect"):
            return self.container.rect.copy()
        x, y, w, h = self.container
        return pygame.Rect(int(x), int(y), int(w), int(h))

    def _inner_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Уменьшает прямоугольник на внутренние отступы (padding).

        Args:
            rect: Исходный прямоугольник контейнера.

        Returns:
            Новый rect с учётом padding (top, right, bottom, left).
        """
        top, right, bottom, left = self._padding
        return pygame.Rect(
            rect.left + left,
            rect.top + top,
            max(0, rect.width - left - right),
            max(0, rect.height - top - bottom),
        )

    def _set_child_position(
        self,
        child: pygame.sprite.Sprite,
        pos: Tuple[float, float],
        angle: Optional[float] = None,
    ) -> None:
        """Устанавливает мировую или локальную позицию ребёнка и при необходимости угол.

        Args:
            child: Спрайт-ребёнок.
            pos: Желаемая позиция (мировая или локальная при use_local).
            angle: Угол поворота в градусах; используется, например, в CIRCLE.
        """
        anchor = self.child_anchor
        if anchor is None and hasattr(child, "anchor"):
            anchor = getattr(child, "anchor", Anchor.CENTER)
        if anchor is None:
            anchor = Anchor.CENTER

        eff = self._effective_container()
        if self.use_local and eff is not None and hasattr(eff, "get_world_position"):
            center_world = eff.get_world_position()
            local_x = pos[0] - center_world.x
            local_y = pos[1] - center_world.y
            if hasattr(child, "set_parent"):
                child.set_parent(eff, keep_world_position=False)
            if hasattr(child, "local_position"):
                child.local_position = (local_x, local_y)
            else:
                if hasattr(child, "set_position"):
                    child.set_position((int(pos[0]), int(pos[1])), anchor=anchor)
        else:
            if hasattr(child, "set_position"):
                child.set_position((int(pos[0]), int(pos[1])), anchor=anchor)
        if angle is not None and hasattr(child, "angle"):
            child.angle = angle

    def _child_size(self, child: pygame.sprite.Sprite) -> Tuple[float, float]:
        """Возвращает размеры ребёнка для расчёта слотов.

        Args:
            child: Спрайт-ребёнок (должен иметь rect или size).

        Returns:
            Кортеж (width, height). При отсутствии rect/size — (50, 50).
        """
        if hasattr(child, "rect"):
            return (child.rect.width, child.rect.height)
        if hasattr(child, "size"):
            s = child.size
            return (s[0], s[1])
        return (50, 50)

    def set_size(self, size: Union[Tuple[float, float], Tuple[int, int], Sequence[float]]) -> "Layout":
        """Устанавливает ширину и высоту лейаута (пиксели). При container=None пересчитывает детей.

        Returns:
            Layout: self для цепочек вызовов.
        """
        super().set_size(size)
        if self.container is None:
            if self._debug_borders:
                self._apply_debug_style()
            else:
                self.set_rect_shape(size=tuple(self.rect.size), color=(0, 0, 0), width=0)
                self.set_alpha(0)
        if self._auto_apply:
            self.apply()
        return self

    def apply(self) -> "Layout":
        """Пересчитывает позиции всех дочерних спрайтов по текущему direction и применяет их.

        Returns:
            Layout: self для цепочек вызовов.
        """
        if self._debug_overlay is not None:
            self._sync_debug_overlay()
        if not self._children:
            return self
        rect = self._get_container_rect()
        inner = self._inner_rect(rect)
        cx = inner.centerx
        cy = inner.centery
        anchor = self.child_anchor if self.child_anchor is not None else Anchor.CENTER

        if self.direction in (LayoutDirection.FLEX_ROW, LayoutDirection.HORIZONTAL):
            self._apply_row(inner, cx, cy, is_flex=(self.direction == LayoutDirection.FLEX_ROW))
        elif self.direction in (LayoutDirection.FLEX_COLUMN, LayoutDirection.VERTICAL):
            self._apply_column(
                inner, cx, cy, is_flex=(self.direction == LayoutDirection.FLEX_COLUMN)
            )
        elif self.direction == LayoutDirection.GRID:
            self._apply_grid(inner)
        elif self.direction == LayoutDirection.CIRCLE:
            self._apply_circle(rect, inner, cx, cy)
        elif self.direction == LayoutDirection.LINE:
            self._apply_line()
        return self

    def _apply_row(
        self,
        inner: pygame.Rect,
        center_x: float,
        center_y: float,
        is_flex: bool,
    ) -> None:
        """Расставляет детей в один или несколько горизонтальных рядов.

        При is_flex и wrap=True переносит элементы на следующую строку при
        нехватке ширины inner.
        """
        children = self._children
        n = len(children)
        if n == 0:
            return
        gap_x = self._gap_x
        gap_y = self._gap_y
        widths = [self._child_size(c)[0] for c in children]
        heights = [self._child_size(c)[1] for c in children]

        if is_flex and self.wrap:
            rows: List[List[Tuple[int, float, float]]] = []
            row: List[Tuple[int, float, float]] = []
            row_width = 0.0
            for i, (w, h) in enumerate(zip(widths, heights)):
                if row and row_width + gap_x + w > inner.width:
                    rows.append(row)
                    row = []
                    row_width = 0.0
                row.append((i, w, h))
                row_width += w + (gap_x if row_width > 0 else 0)
            if row:
                rows.append(row)

            row_heights = [max(r[2] for r in row) for row in rows]
            total_h = sum(row_heights) + (len(rows) - 1) * gap_y if rows else 0
            if self.align_cross == LayoutAlignCross.START:
                start_y = inner.top
            elif self.align_cross == LayoutAlignCross.CENTER:
                start_y = inner.top + (inner.height - total_h) / 2
            else:
                start_y = inner.bottom - total_h

            y = start_y
            for row_idx, row in enumerate(rows):
                row_w = sum(r[1] for r in row) + (len(row) - 1) * gap_x
                row_h = row_heights[row_idx]
                if self.align_main == LayoutAlignMain.START:
                    x = inner.left
                elif self.align_main == LayoutAlignMain.CENTER:
                    x = inner.left + (inner.width - row_w) / 2
                elif self.align_main == LayoutAlignMain.END:
                    x = inner.right - row_w
                elif self.align_main == LayoutAlignMain.SPACE_BETWEEN and len(row) > 1:
                    x = inner.left
                    gap_x_row = (inner.width - sum(r[1] for r in row)) / (len(row) - 1)
                    for idx, w, h in row:
                        slot_cx = x + w / 2
                        slot_cy = y + row_h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        x += w + gap_x_row
                    y += row_h + gap_y
                    continue
                elif self.align_main == LayoutAlignMain.SPACE_AROUND and row:
                    gap_x_row = (inner.width - sum(r[1] for r in row)) / len(row)
                    x = inner.left + gap_x_row / 2
                    for idx, w, h in row:
                        slot_cx = x + w / 2
                        slot_cy = y + row_h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        x += w + gap_x_row
                    y += row_h + gap_y
                    continue
                elif self.align_main == LayoutAlignMain.SPACE_EVENLY and row:
                    gap_x_row = (inner.width - sum(r[1] for r in row)) / (len(row) + 1)
                    x = inner.left + gap_x_row
                    for idx, w, h in row:
                        slot_cx = x + w / 2
                        slot_cy = y + row_h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        x += w + gap_x_row
                    y += row_h + gap_y
                    continue
                else:
                    x = inner.left
                for idx, w, h in row:
                    slot_cx = x + w / 2
                    slot_cy = y + row_h / 2
                    self._set_child_position(children[idx], (slot_cx, slot_cy))
                    x += w + gap_x
                y += row_h + gap_y
            return

        total_w = sum(widths) + (n - 1) * gap_x
        if is_flex and total_w > inner.width:
            gap_x = 0
            total_w = inner.width

        if self.align_main == LayoutAlignMain.START:
            start_x = inner.left
        elif self.align_main == LayoutAlignMain.CENTER:
            start_x = inner.left + (inner.width - total_w) / 2
        elif self.align_main == LayoutAlignMain.END:
            start_x = inner.right - total_w
        elif self.align_main == LayoutAlignMain.SPACE_BETWEEN and n > 1:
            start_x = inner.left
            gap_x = (inner.width - sum(widths)) / (n - 1)
        elif self.align_main == LayoutAlignMain.SPACE_AROUND and n > 0:
            gap_x = (inner.width - sum(widths)) / n
            start_x = inner.left + gap_x / 2
        elif self.align_main == LayoutAlignMain.SPACE_EVENLY and n > 0:
            gap_x = (inner.width - sum(widths)) / (n + 1)
            start_x = inner.left + gap_x
        else:
            start_x = inner.left

        x = start_x
        for i, child in enumerate(children):
            w, h = self._child_size(child)
            slot_center_x = x + w / 2
            x += w + gap_x

            if self.align_cross == LayoutAlignCross.START:
                slot_center_y = inner.top + h / 2
            elif self.align_cross == LayoutAlignCross.CENTER:
                slot_center_y = inner.centery
            else:
                slot_center_y = inner.bottom - h / 2

            self._set_child_position(child, (slot_center_x, slot_center_y))

    def _apply_column(
        self,
        inner: pygame.Rect,
        center_x: float,
        center_y: float,
        is_flex: bool,
    ) -> None:
        """Расставляет детей в одну или несколько вертикальных колонок.

        При is_flex и wrap=True переносит элементы в следующую колонку при
        нехватке высоты inner.
        """
        children = self._children
        n = len(children)
        if n == 0:
            return
        gap_x = self._gap_x
        gap_y = self._gap_y
        widths = [self._child_size(c)[0] for c in children]
        heights = [self._child_size(c)[1] for c in children]

        if is_flex and self.wrap:
            columns: List[List[Tuple[int, float, float]]] = []
            col: List[Tuple[int, float, float]] = []
            col_height = 0.0
            for i, (w, h) in enumerate(zip(widths, heights)):
                if col and col_height + gap_y + h > inner.height:
                    columns.append(col)
                    col = []
                    col_height = 0.0
                col.append((i, w, h))
                col_height += h + (gap_y if col_height > 0 else 0)
            if col:
                columns.append(col)

            col_widths = [max(c[1] for c in col) for col in columns]
            total_w = sum(col_widths) + (len(columns) - 1) * gap_x if columns else 0
            if self.align_cross == LayoutAlignCross.START:
                start_x = inner.left
            elif self.align_cross == LayoutAlignCross.CENTER:
                start_x = inner.left + (inner.width - total_w) / 2
            else:
                start_x = inner.right - total_w

            x = start_x
            for col_idx, column in enumerate(columns):
                col_h = sum(c[2] for c in column) + (len(column) - 1) * gap_y
                col_w = col_widths[col_idx]
                if self.align_main == LayoutAlignMain.START:
                    y = inner.top
                elif self.align_main == LayoutAlignMain.CENTER:
                    y = inner.top + (inner.height - col_h) / 2
                elif self.align_main == LayoutAlignMain.END:
                    y = inner.bottom - col_h
                elif self.align_main == LayoutAlignMain.SPACE_BETWEEN and len(column) > 1:
                    y = inner.top
                    gap_y_col = (inner.height - sum(c[2] for c in column)) / (len(column) - 1)
                    for idx, w, h in column:
                        slot_cx = x + col_w / 2
                        slot_cy = y + h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        y += h + gap_y_col
                    x += col_w + gap_x
                    continue
                elif self.align_main == LayoutAlignMain.SPACE_AROUND and column:
                    gap_y_col = (inner.height - sum(c[2] for c in column)) / len(column)
                    y = inner.top + gap_y_col / 2
                    for idx, w, h in column:
                        slot_cx = x + col_w / 2
                        slot_cy = y + h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        y += h + gap_y_col
                    x += col_w + gap_x
                    continue
                elif self.align_main == LayoutAlignMain.SPACE_EVENLY and column:
                    gap_y_col = (inner.height - sum(c[2] for c in column)) / (len(column) + 1)
                    y = inner.top + gap_y_col
                    for idx, w, h in column:
                        slot_cx = x + col_w / 2
                        slot_cy = y + h / 2
                        self._set_child_position(children[idx], (slot_cx, slot_cy))
                        y += h + gap_y_col
                    x += col_w + gap_x
                    continue
                else:
                    y = inner.top
                for idx, w, h in column:
                    slot_cx = x + col_w / 2
                    slot_cy = y + h / 2
                    self._set_child_position(children[idx], (slot_cx, slot_cy))
                    y += h + gap_y
                x += col_w + gap_x
            return

        total_h = sum(heights) + (n - 1) * gap_y
        if is_flex and total_h > inner.height:
            gap_y = 0
            total_h = inner.height

        if self.align_main == LayoutAlignMain.START:
            start_y = inner.top
        elif self.align_main == LayoutAlignMain.CENTER:
            start_y = inner.top + (inner.height - total_h) / 2
        elif self.align_main == LayoutAlignMain.END:
            start_y = inner.bottom - total_h
        elif self.align_main == LayoutAlignMain.SPACE_BETWEEN and n > 1:
            start_y = inner.top
            gap_y = (inner.height - sum(heights)) / (n - 1)
        elif self.align_main == LayoutAlignMain.SPACE_AROUND and n > 0:
            gap_y = (inner.height - sum(heights)) / n
            start_y = inner.top + gap_y / 2
        elif self.align_main == LayoutAlignMain.SPACE_EVENLY and n > 0:
            gap_y = (inner.height - sum(heights)) / (n + 1)
            start_y = inner.top + gap_y
        else:
            start_y = inner.top

        y = start_y
        for i, child in enumerate(children):
            w, h = self._child_size(child)
            slot_center_y = y + h / 2
            y += h + gap_y

            if self.align_cross == LayoutAlignCross.START:
                slot_center_x = inner.left + w / 2
            elif self.align_cross == LayoutAlignCross.CENTER:
                slot_center_x = inner.centerx
            else:
                slot_center_x = inner.right - w / 2

            self._set_child_position(child, (slot_center_x, slot_center_y))

    def _apply_grid(self, inner: pygame.Rect) -> None:
        """Расставляет детей в сетку rows x cols с учётом flow и align_cross."""
        children = self._children
        n = len(children)
        if n == 0:
            return
        rows = self.rows
        cols = self.cols
        if rows is not None and cols is not None:
            pass
        elif cols is not None:
            rows = max(1, (n + cols - 1) // cols)
        elif rows is not None:
            cols = max(1, (n + rows - 1) // rows)
        else:
            cols = max(1, int(math.ceil(math.sqrt(n))))
            rows = max(1, (n + cols - 1) // cols)

        gx, gy = self._gap_x, self._gap_y
        cell_w = (inner.width - (cols - 1) * gx) / cols if cols else inner.width
        cell_h = (inner.height - (rows - 1) * gy) / rows if rows else inner.height
        if cell_w < 0:
            cell_w = 0
        if cell_h < 0:
            cell_h = 0

        for idx, child in enumerate(children):
            if self.flow == GridFlow.ROW:
                row = idx // cols
                col = idx % cols
            else:
                col = idx // rows
                row = idx % rows
            if row >= rows or col >= cols:
                continue
            w, h = self._child_size(child)
            slot_center_x = inner.left + col * (cell_w + gx) + cell_w / 2
            slot_center_y = inner.top + row * (cell_h + gy) + cell_h / 2

            if self.align_cross == LayoutAlignCross.START:
                slot_center_x = inner.left + col * (cell_w + gx) + w / 2
                slot_center_y = inner.top + row * (cell_h + gy) + h / 2
            elif self.align_cross == LayoutAlignCross.CENTER:
                pass
            else:
                slot_center_x = inner.left + (col + 1) * (cell_w + gx) - gx - w / 2
                slot_center_y = inner.top + (row + 1) * (cell_h + gy) - gy - h / 2

            self._set_child_position(child, (slot_center_x, slot_center_y))

    def _apply_circle(
        self,
        rect: pygame.Rect,
        inner: pygame.Rect,
        cx: float,
        cy: float,
    ) -> None:
        """Расставляет детей по окружности с центром (cx, cy) и заданным radius."""
        children = self._children
        n = len(children)
        if n == 0:
            return
        r = self.radius
        if r is None:
            r = min(inner.width, inner.height) / 2 - 10
        r = max(1, r)
        start = math.radians(self.start_angle)
        step_rad = (2 * math.pi / n) if n else 0
        if not self.clockwise:
            step_rad = -step_rad
        for i, child in enumerate(children):
            angle_rad = start + i * step_rad
            px = cx + r * math.cos(angle_rad)
            py = cy - r * math.sin(angle_rad)
            deg = math.degrees(angle_rad)
            if self.rotate_children:
                child_angle = deg + 90 + self.offset_angle
                self._set_child_position(child, (px, py), angle=child_angle)
            else:
                self._set_child_position(child, (px, py))

    def _apply_line(self) -> None:
        """Расставляет детей вдоль ломаной линии self.points (равномерно по длине)."""
        children = self._children
        pts = self.points
        if len(pts) < 2 or not children:
            return
        n = len(children)
        lengths = []
        total = 0.0
        for i in range(len(pts) - 1):
            ax, ay = pts[i][0], pts[i][1]
            bx, by = pts[i + 1][0], pts[i + 1][1]
            L = math.hypot(bx - ax, by - ay)
            lengths.append(L)
            total += L
        if total <= 0:
            total = 1.0
        positions = []
        if n == 0:
            return
        for k in range(n):
            t = (k + 1) / (n + 1)
            target_d = t * total
            d = 0.0
            for seg, L in enumerate(lengths):
                if d + L >= target_d:
                    local_t = (target_d - d) / L if L > 0 else 0
                    ax, ay = pts[seg][0], pts[seg][1]
                    bx, by = pts[seg + 1][0], pts[seg + 1][1]
                    px = ax + local_t * (bx - ax)
                    py = ay + local_t * (by - ay)
                    positions.append((px, py))
                    break
                d += L
            else:
                bx, by = pts[-1][0], pts[-1][1]
                positions.append((bx, by))
        for child, (px, py) in zip(children, positions):
            self._set_child_position(child, (px, py))

    def refresh(self) -> "Layout":
        """Пересчитывает позиции детей. Алиас для apply().

        Returns:
            Layout: self для цепочек вызовов.
        """
        self.apply()
        return self

    def add(self, child: pygame.sprite.Sprite) -> "Layout":
        """Добавляет одного ребёнка в конец списка и пересчитывает позиции.

        При container=None ребёнок привязывается к лейауту через set_parent(self).

        Args:
            child: Спрайт для добавления в лейаут.

        Returns:
            Layout: self для цепочек вызовов.
        """
        if child not in self._children:
            self._children.append(child)
            if self.container is None and hasattr(child, "set_parent"):
                child.set_parent(self, keep_world_position=False)
        if self._auto_apply:
            self.apply()
        return self

    def add_children(self, *children: pygame.sprite.Sprite) -> "Layout":
        """Добавляет нескольких детей в конец и пересчитывает позиции.

        Args:
            *children: Спрайты для добавления в лейаут.

        Returns:
            Layout: self для цепочек вызовов.
        """
        for c in children:
            if c not in self._children:
                self._children.append(c)
                if self.container is None and hasattr(c, "set_parent"):
                    c.set_parent(self, keep_world_position=False)
        if self._auto_apply:
            self.apply()
        return self

    def remove(self, child: pygame.sprite.Sprite) -> "Layout":
        """Удаляет одного ребёнка из лейаута и пересчитывает позиции остальных.

        При container=None у ребёнка вызывается set_parent(None).

        Args:
            child: Спрайт для удаления из лейаута.

        Returns:
            Layout: self для цепочек вызовов.
        """
        if child in self._children:
            self._children.remove(child)
            if self.container is None and hasattr(child, "set_parent"):
                child.set_parent(None, keep_world_position=True)
        if self._auto_apply:
            self.apply()
        return self

    def remove_children(self, *children: pygame.sprite.Sprite) -> "Layout":
        """Удаляет перечисленных детей из лейаута и пересчитывает позиции.

        При container=None у каждого удаляемого ребёнка вызывается set_parent(None).

        Args:
            *children: Спрайты для удаления из лейаута.

        Returns:
            Layout: self для цепочек вызовов.
        """
        for c in children:
            if c in self._children:
                self._children.remove(c)
                if self.container is None and hasattr(c, "set_parent"):
                    c.set_parent(None, keep_world_position=True)
        if self._auto_apply:
            self.apply()
        return self

    @property
    def auto_apply(self) -> bool:
        """Режим автообновления: True — add/remove/set_size вызывают apply(); False — только refresh()/apply()."""
        return self._auto_apply

    @auto_apply.setter
    def auto_apply(self, value: bool) -> None:
        self._auto_apply = bool(value)

    def set_auto_apply(self, value: bool) -> "Layout":
        """Включает или выключает автообновление при add/remove/set_size. Возвращает self."""
        self._auto_apply = bool(value)
        return self

    @property
    def arranged_children(self) -> List[pygame.sprite.Sprite]:
        """Список спрайтов, которые расставляет лейаут.

        При container=None совпадает с Sprite.children (иерархия родитель–дети).
        """
        return self._children


def layout_flex_row(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    gap: Union[int, float, Tuple[float, float]] = 10,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    align_main: LayoutAlignMain = LayoutAlignMain.START,
    align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    wrap: bool = True,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей в ряд (flex row) и возвращает настроенный Layout.

    При wrap=True элементы переносятся на следующую строку при нехватке ширины.
    При container=None можно задать size и pos (и scene) — размер и позиция контейнера.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h). Контейнер для расстановки.
        children: Список спрайтов для размещения в ряд.
        gap: Зазор между элементами. Число или (gap_x, gap_y). По умолчанию 10.
        padding: Отступ от границ контейнера. Число или (top, right, bottom, left).
        align_main: Выравнивание по основной оси (горизонталь).
        align_cross: Выравнивание по поперечной оси (вертикаль).
        use_local: True — позиции в локальных координатах контейнера.
        child_anchor: Якорь при установке позиции детей. None — якорь спрайта.
        wrap: Перенос на следующую строку при нехватке ширины. По умолчанию True.
        size: При container=None — (ширина, высота) контейнера в пикселях.
        pos: При container=None — (x, y) позиция центра контейнера.
        scene: При container=None — сцена для лейаута.
        auto_apply: True — сразу вызвать apply(); False — ручной режим, вызовите refresh() позже.

    Returns:
        Экземпляр Layout (с уже вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.FLEX_ROW,
        gap=gap,
        padding=padding,
        align_main=align_main,
        align_cross=align_cross,
        use_local=use_local,
        child_anchor=child_anchor,
        wrap=wrap,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_flex_column(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    gap: Union[int, float, Tuple[float, float]] = 10,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    align_main: LayoutAlignMain = LayoutAlignMain.START,
    align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    wrap: bool = True,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей в колонку (flex column) и возвращает Layout.

    При wrap=True элементы переносятся в следующую колонку при нехватке высоты.
    При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h).
        children: Список спрайтов для размещения в колонку.
        gap: Зазор между элементами. По умолчанию 10.
        padding: Отступ от границ контейнера.
        align_main: Выравнивание по основной оси (вертикаль).
        align_cross: Выравнивание по поперечной оси (горизонталь).
        use_local: True — локальные координаты контейнера.
        child_anchor: Якорь позиционирования детей.
        wrap: Перенос в следующую колонку при нехватке высоты. По умолчанию True.
        size: При container=None — (ширина, высота) контейнера в пикселях.
        pos: При container=None — (x, y) позиция центра контейнера.
        scene: При container=None — сцена для лейаута.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.FLEX_COLUMN,
        gap=gap,
        padding=padding,
        align_main=align_main,
        align_cross=align_cross,
        use_local=use_local,
        child_anchor=child_anchor,
        wrap=wrap,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_horizontal(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    gap: Union[int, float, Tuple[float, float]] = 10,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    align_main: LayoutAlignMain = LayoutAlignMain.START,
    align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей в один горизонтальный ряд без переноса (не flex).

    При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h).
        children: Список спрайтов.
        gap: Зазор между элементами. По умолчанию 10.
        padding: Отступ от границ контейнера.
        align_main: Выравнивание по основной оси.
        align_cross: Выравнивание по поперечной оси.
        use_local: True — локальные координаты контейнера.
        child_anchor: Якорь позиционирования детей.
        size: При container=None — (ширина, высота) контейнера.
        pos: При container=None — (x, y) позиция центра.
        scene: При container=None — сцена.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.HORIZONTAL,
        gap=gap,
        padding=padding,
        align_main=align_main,
        align_cross=align_cross,
        use_local=use_local,
        child_anchor=child_anchor,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_vertical(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    gap: Union[int, float, Tuple[float, float]] = 10,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    align_main: LayoutAlignMain = LayoutAlignMain.START,
    align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей в одну вертикальную колонку без переноса (не flex).

    При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h).
        children: Список спрайтов.
        gap: Зазор между элементами. По умолчанию 10.
        padding: Отступ от границ контейнера.
        align_main: Выравнивание по основной оси.
        align_cross: Выравнивание по поперечной оси.
        use_local: True — локальные координаты контейнера.
        child_anchor: Якорь позиционирования детей.
        size: При container=None — (ширина, высота) контейнера.
        pos: При container=None — (x, y) позиция центра.
        scene: При container=None — сцена.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.VERTICAL,
        gap=gap,
        padding=padding,
        align_main=align_main,
        align_cross=align_cross,
        use_local=use_local,
        child_anchor=child_anchor,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_grid(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    rows: Optional[int] = None,
    cols: Optional[int] = None,
    gap_x: float = 10,
    gap_y: float = 10,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    flow: GridFlow = GridFlow.ROW,
    align_main: LayoutAlignMain = LayoutAlignMain.START,
    align_cross: LayoutAlignCross = LayoutAlignCross.CENTER,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей в сетку rows x cols и возвращает Layout.

    Если заданы только rows или только cols, второе измерение вычисляется по количеству
    детей. При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h).
        children: Список спрайтов для размещения в сетку.
        rows: Количество строк. Опционально.
        cols: Количество столбцов. Опционально.
        gap_x: Зазор по горизонтали. По умолчанию 10.
        gap_y: Зазор по вертикали. По умолчанию 10.
        padding: Отступ от границ контейнера.
        flow: ROW — заполнение по строкам, COLUMN — по столбцам.
        align_main: Выравнивание по основной оси.
        align_cross: Выравнивание внутри ячейки.
        use_local: True — локальные координаты контейнера.
        child_anchor: Якорь позиционирования детей.
        size: При container=None — (ширина, высота) контейнера.
        pos: При container=None — (x, y) позиция центра.
        scene: При container=None — сцена.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.GRID,
        rows=rows,
        cols=cols,
        gap_x=gap_x,
        gap_y=gap_y,
        padding=padding,
        flow=flow,
        align_main=align_main,
        align_cross=align_cross,
        use_local=use_local,
        child_anchor=child_anchor,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_circle(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    radius: float = 100,
    start_angle: float = 0,
    clockwise: bool = True,
    rotate_children: bool = True,
    offset_angle: float = 0,
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей по окружности с центром в центре контейнера.

    При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h). Центр окружности — центр rect.
        children: Список спрайтов.
        radius: Радиус окружности в пикселях. По умолчанию 100.
        start_angle: Начальный угол в градусах (0 — справа).
        clockwise: True — по часовой стрелке.
        rotate_children: True — поворачивать детей по касательной к окружности.
        offset_angle: Смещение угла поворота детей в градусах.
        padding: Отступ от границ контейнера.
        use_local: True — локальные координаты контейнера.
        child_anchor: Якорь позиционирования детей.
        size: При container=None — (ширина, высота) контейнера.
        pos: При container=None — (x, y) позиция центра.
        scene: При container=None — сцена.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.CIRCLE,
        radius=radius,
        start_angle=start_angle,
        clockwise=clockwise,
        rotate_children=rotate_children,
        offset_angle=offset_angle,
        padding=padding,
        use_local=use_local,
        child_anchor=child_anchor,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout


def layout_line(
    container: ContainerInput,
    children: List[pygame.sprite.Sprite],
    points: Sequence[Tuple[float, float]],
    padding: Union[int, float, Sequence[Union[int, float]]] = 0,
    use_local: bool = False,
    child_anchor: Optional[Anchor] = None,
    size: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    pos: Optional[Union[Tuple[float, float], Tuple[int, int]]] = None,
    scene: Optional[object] = None,
    auto_apply: bool = True,
) -> Layout:
    """Расставляет детей вдоль ломаной линии (равномерно по длине).

    Точки задаются в мировых координатах; при use_local — относительно контейнера.
    При container=None можно задать size, pos и scene.

    Args:
        container: Спрайт с rect или кортеж (x, y, w, h). Нужен при use_local.
        children: Список спрайтов.
        points: Точки ломаной в порядке обхода: [(x, y), ...]. Минимум 2 точки.
        padding: Отступ от границ контейнера (при use_local).
        use_local: True — точки в локальных координатах контейнера.
        child_anchor: Якорь позиционирования детей.
        size: При container=None — (ширина, высота) контейнера.
        pos: При container=None — (x, y) позиция центра.
        scene: При container=None — сцена.
        auto_apply: True — сразу apply(); False — ручной режим.

    Returns:
        Экземпляр Layout (с вызванным apply() при auto_apply=True).
    """
    layout = Layout(
        container,
        children,
        direction=LayoutDirection.LINE,
        points=points,
        padding=padding,
        use_local=use_local,
        child_anchor=child_anchor,
        size=size,
        pos=pos,
        scene=scene,
        auto_apply=auto_apply,
    )
    if auto_apply:
        layout.apply()
    return layout
