import spritePro as s

def on_click():
    text.set_text("Welcome! :)")
    button.kill()

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
)

button.rect.y+=200

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
