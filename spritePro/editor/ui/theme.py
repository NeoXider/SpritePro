"""Тема редактора: цвета, размеры панелей и кнопок."""

# Размеры панелей (px)
UI_LEFT_WIDTH = 200
UI_RIGHT_WIDTH = 280
UI_TOP_HEIGHT = 40
UI_BOTTOM_HEIGHT = 30

# Иерархия
HIERARCHY_ITEM_HEIGHT = 22
HIERARCHY_HEADER_OFFSET = 35
HIERARCHY_LIST_PADDING = 8

# Тулбар
TOOLBAR_PADDING_LEFT = 10
TOOLBAR_PADDING_TOP = 5
TOOLBAR_PADDING_BOTTOM = 10
TOOLBAR_PADDING_RIGHT = 10
TOOLBAR_BUTTON_GAP = 10
TOOLBAR_RIGHT_BUTTON_HEIGHT = 24
TOOLBAR_RIGHT_BUTTON_GAP = 6
TOOLBAR_RIGHT_BUTTONS = [
    ("settings", "Settings", 72),
    ("grid", "Grid", 52),
    ("new", "New", 45),
    ("save", "Save", 45),
    ("load", "Load", 45),
    ("add", "Add", 45),
    ("rect", "Rect", 40),
    ("circle", "Circle", 45),
    ("ellipse", "Ellipse", 48),
]

# Статусбар
STATUSBAR_TOP_PADDING = 5
STATUSBAR_SLIDER_HEIGHT = 9
STATUSBAR_SLIDER_WIDTH = 140
STATUSBAR_SLIDER_GAP = 120
STATUSBAR_INPUT_WIDTH = 72
STATUSBAR_INPUT_GAP = 10
STATUSBAR_SNAP_WIDTH = 80
STATUSBAR_SNAP_HEIGHT = 18
STATUSBAR_LABELS_WIDTH = 85
STATUSBAR_LABELS_HEIGHT = 18

# Инспектор
INSPECTOR_ROW_HEIGHT = 20
INSPECTOR_INPUT_OFFSET_RIGHT = 112
INSPECTOR_TOGGLE_BTN_WIDTH = 50
INSPECTOR_TOGGLE_BTN_OFFSET = 60

# Редактор: зум и сетка
EDITOR_MIN_ZOOM = 0.01
EDITOR_MAX_ZOOM = 10.0
EDITOR_MIN_GRID_SIZE = 8
EDITOR_MAX_GRID_SIZE = 256

# Двойной клик (сек)
DOUBLE_CLICK_INTERVAL = 0.3

# Цвета
COLORS = {
    "background": (30, 30, 35),
    "grid": (50, 50, 55),
    "grid_major": (60, 60, 65),
    "selection": (0, 150, 255),
    "gizmo_move": (255, 100, 100),
    "gizmo_rotate": (100, 255, 100),
    "gizmo_scale": (100, 100, 255),
    "ui_bg": (40, 40, 45),
    "ui_border": (60, 60, 65),
    "ui_text": (200, 200, 200),
    "ui_accent": (0, 150, 255),
    "ui_hover": (50, 50, 55),
    "ui_selected_bg": (30, 30, 35),
    "ui_input_bg": (42, 42, 50),
    "ui_input_bg_hover": (48, 48, 56),
    "ui_input_bg_active": (62, 62, 70),
    "ui_input_border": (95, 95, 110),
    "ui_slider_track": (55, 55, 62),
    "ui_slider_thumb": (225, 225, 230),
    "ui_scrollbar_track": (50, 50, 55),
    "ui_scrollbar_thumb": (110, 110, 120),
    "camera_frame": (255, 210, 80),
    "camera_info_bg": (20, 20, 24),
    "camera_info_border": (80, 70, 30),
}

# Кнопки тулбара (специфичные цвета по ключу)
TOOLBAR_BUTTON_COLORS = {
    "add": {"normal": (40, 60, 40), "hover": (50, 100, 50)},
    "load": {"normal": (40, 40, 60), "hover": (50, 50, 80)},
    "grid": {"normal": (40, 40, 45), "hover": (50, 50, 55), "active": (0, 150, 255), "active_hover": (70, 170, 255)},
    "settings": {"normal": (48, 44, 66), "hover": (62, 58, 82)},
    "default": {"normal": (40, 40, 45), "hover": (50, 50, 55)},
}
