import spritePro as s
import pygame


def on_click():
    text.set_text("Welcome! :)")
    button.set_active(False)


# Initialize the library
s.init()

# Create a window
s.get_screen((800, 600), "My Game")
# text
text = s.TextSprite("Hello World", 74, (255, 50, 255), s.WH_C)
button = s.Button(
    "",
    (300, 100),
    s.WH_C,
    "Click Me",
    36,
    on_click=on_click,
).set_rect_shape(border_radius=10)
button.DoScale(1.5, 2).OnComplete(lambda: button.DoRotate(180, 1))

exit_button = s.Button(
    "", (300, 100), text="Exit", text_size=36, on_click=pygame.quit
).set_rect_shape(border_radius=10)

layout = (
    s.layout_flex_column(
        None, [text, button, exit_button], align_main=s.LayoutAlignMain.SPACE_EVENLY
    )
    .set_debug_borders(True)
    .set_position(s.WH_C)
    .set_size((400, 550))
)


button.rect.y += 200

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
