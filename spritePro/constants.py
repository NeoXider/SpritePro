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
