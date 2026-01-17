import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s


def main():
    s.get_screen((800, 600), "Resource Cache Demo")

    texture_path = "spritePro/demoGames/Sprites/ball.png"
    cached = s.load_texture(texture_path)
    if cached is None:
        sprite = s.Sprite("", (80, 80), (400, 300))
        sprite.set_color((255, 120, 120))
    else:
        sprite = s.Sprite(texture_path, (80, 80), (400, 300))

    s.load_sound("bounce", "spritePro/demoGames/Audio/baunch.mp3")

    while True:
        s.update(fill_color=(15, 15, 15))


if __name__ == "__main__":
    main()
