import spritePro as s

# Initialize the library
s.init()

# Create a window
s.get_screen((800, 600), "My Game")

prefs = s.PlayerPrefs()

# Create a basic sprite
player = s.Sprite(
    "",
    size=(100, 100),
    # load vector2 pos or default center position
    pos=prefs.get_vector2("player_pos", s.WH_C),
    speed=3,
)

last_pos = tuple(player.rect.center)

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
    player.handle_keyboard_input()
    player.update()
    player.handle_keyboard_input()

    # save if current_pos not last_pos
    current_pos = tuple(player.rect.center)
    if current_pos != last_pos:
        prefs.set_vector2("player_pos", current_pos)
        last_pos = current_pos
