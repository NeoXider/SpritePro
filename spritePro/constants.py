"""Common constants and enums for SpritePro."""

class Anchor:
    CENTER = "center"
    TOP_LEFT = "topleft"
    TOP_RIGHT = "topright"
    BOTTOM_LEFT = "bottomleft"
    BOTTOM_RIGHT = "bottomright"
    MID_TOP = "midtop"
    MID_BOTTOM = "midbottom"
    MID_LEFT = "midleft"
    MID_RIGHT = "midright"

    MAP = {
        "center": CENTER,
        "topleft": TOP_LEFT,
        "topright": TOP_RIGHT,
        "bottomleft": BOTTOM_LEFT,
        "bottomright": BOTTOM_RIGHT,
        "midtop": MID_TOP,
        "midbottom": MID_BOTTOM,
        "midleft": MID_LEFT,
        "midright": MID_RIGHT,
    }

    ALL = tuple(MAP.keys())


class FillDirection:
    """Constants for bar fill directions."""
    
    # Горизонтальные направления
    HORIZONTAL_LEFT_TO_RIGHT = "horizontal_left_to_right"  # слева направо (default)
    HORIZONTAL_RIGHT_TO_LEFT = "horizontal_right_to_left"  # справа налево
    
    # Вертикальные направления
    VERTICAL_BOTTOM_TO_TOP = "vertical_bottom_to_top"  # снизу вверх
    VERTICAL_TOP_TO_BOTTOM = "vertical_top_to_bottom"  # сверху вниз
    
    MAP = {
        "horizontal_left_to_right": HORIZONTAL_LEFT_TO_RIGHT,
        "horizontal_right_to_left": HORIZONTAL_RIGHT_TO_LEFT,
        "vertical_bottom_to_top": VERTICAL_BOTTOM_TO_TOP,
        "vertical_top_to_bottom": VERTICAL_TOP_TO_BOTTOM,
    }
    
    ALL = tuple(MAP.keys())
    
    # Convenience aliases for easier usage
    LEFT_TO_RIGHT = HORIZONTAL_LEFT_TO_RIGHT
    RIGHT_TO_LEFT = HORIZONTAL_RIGHT_TO_LEFT
    BOTTOM_TO_TOP = VERTICAL_BOTTOM_TO_TOP
    TOP_TO_BOTTOM = VERTICAL_TOP_TO_BOTTOM