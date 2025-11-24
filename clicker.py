import spritePro as s
import pygame 

def on_click():
    global score
    score +=1
    text.set_text(f"score: {score}")
    text.set_active(True)
    emitter.emit(button.rect.center)


# Initialize the library
s.init()

# Create a window
s.get_screen((1280, 960), "My Game")

score = 0

bg = s.Sprite("", s.WH, s.WH_C)
bg.set_color((0,0,180))
bg.set_screen_space(True)
# text
text = s.TextSprite("", 74, (255, 255, 255), s.WH_C)
text.set_text(f"score: {score}")
text.rect.y = 50
text.set_active(False)
text.set_screen_space(True)
button = s.Button(
    "",
    (300, 300),
    s.WH_C,
    "Click Me",
    36,
    on_click=on_click,
)

emitter = s.ParticleEmitter(
    s.ParticleConfig(
        amount=100,
        size_range=(5, 15),
        speed_range=(50, 700),
        lifetime_range=(2000, 10000),
        colors=[(255, 200, 40), (255, 120, 200)],
        gravity=pygame.math.Vector2(0, 0),
    )
)

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
    s.process_camera_input()
    button.limit_movement(bg.rect)
    text.color = s.utils.ColorEffects.wave()
