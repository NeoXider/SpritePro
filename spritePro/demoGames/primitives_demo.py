import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def main():
    s.get_screen((900, 600), "Primitives Demo")

    title = s.TextSprite("Primitives Demo", 28, (255, 255, 255), (s.WH_C.x, 30))
    hints = s.TextSprite(
        "Rect, Circle, Ellipse, Polygon, Polyline",
        18,
        (200, 200, 200),
        (s.WH_C.x, 565),
    )

    rect = s.Sprite("", (120, 80), (140, 160))
    rect.set_rect_shape(color=(120, 200, 255), border_radius=12)

    circle = s.Sprite("", (80, 80), (320, 160))
    circle.set_circle_shape(radius=40, color=(255, 180, 100))

    ellipse = s.Sprite("", (140, 80), (520, 160))
    ellipse.set_ellipse_shape(size=(140, 80), color=(170, 255, 140))

    polygon = s.Sprite("", (1, 1), (220, 360))
    polygon_points = [(0, 0), (120, 20), (100, 100), (30, 120)]
    polygon.set_polygon_shape(polygon_points, color=(255, 140, 140))

    polyline = s.Sprite("", (1, 1), (520, 360))
    use_world_points = True
    if use_world_points:
        polyline_points = [
            (0, 0),
            (420, 340),
            (460, 370),
            (520, 330),
            (600, 380),
            (660, 350),
        ]
    else:
        polyline_points = [(0, 0), (40, 30), (80, -10), (140, 40), (180, 10)]
    polyline.set_polyline(
        polyline_points,
        color=(200, 200, 255),
        width=5,
        world_points=use_world_points,
    )

    _ = (title, hints, rect, circle, ellipse, polygon, polyline)

    while True:
        s.update(fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()
