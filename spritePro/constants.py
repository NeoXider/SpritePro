"""Общие константы и перечисления для SpritePro."""

class Anchor:
    """Константы для якорей позиционирования спрайтов.
    
    Якорь определяет точку спрайта, которая используется для позиционирования.
    
    Attributes:
        CENTER (str): Центр спрайта.
        TOP_LEFT (str): Верхний левый угол.
        TOP_RIGHT (str): Верхний правый угол.
        BOTTOM_LEFT (str): Нижний левый угол.
        BOTTOM_RIGHT (str): Нижний правый угол.
        MID_TOP (str): Середина верхней стороны.
        MID_BOTTOM (str): Середина нижней стороны.
        MID_LEFT (str): Середина левой стороны.
        MID_RIGHT (str): Середина правой стороны.
        MAP (dict): Словарь для преобразования строковых значений в константы.
        ALL (tuple): Кортеж всех доступных якорей.
    """
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
    """Константы для направлений заполнения полос прогресса.
    
    Attributes:
        HORIZONTAL_LEFT_TO_RIGHT (str): Горизонтальное заполнение слева направо (по умолчанию).
        HORIZONTAL_RIGHT_TO_LEFT (str): Горизонтальное заполнение справа налево.
        VERTICAL_BOTTOM_TO_TOP (str): Вертикальное заполнение снизу вверх.
        VERTICAL_TOP_TO_BOTTOM (str): Вертикальное заполнение сверху вниз.
        LEFT_TO_RIGHT (str): Псевдоним для HORIZONTAL_LEFT_TO_RIGHT.
        RIGHT_TO_LEFT (str): Псевдоним для HORIZONTAL_RIGHT_TO_LEFT.
        BOTTOM_TO_TOP (str): Псевдоним для VERTICAL_BOTTOM_TO_TOP.
        TOP_TO_BOTTOM (str): Псевдоним для VERTICAL_TOP_TO_BOTTOM.
        MAP (dict): Словарь для преобразования строковых значений в константы.
        ALL (tuple): Кортеж всех доступных направлений.
    """
    
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