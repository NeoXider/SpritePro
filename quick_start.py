import spritePro as s
import pygame

# Initialize the library
s.init()

# Create a window
s.get_screen((800, 600), "My Game")

# Create a basic sprite
player = s.Sprite(
    "",
    size=(100, 100),
    pos=s.WH_C,
    speed=3,
)

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
    player.handle_keyboard_input()
    player.update()
