import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
import pygame

path = Path(__file__).parent


def onclick(): 
    global score
    score +=1
    text.text = str(score)
    emitter.emit(s.WH_C)

score = 0
# Initialize the library
s.init()

# Create a window
s.get_screen((1280, 960), "My Game")

bg = s.Sprite("spritePro\\demoGames\\Sprites\\bg1.jpg", s.WH,s.WH_C)
# Create a basic sprite
emitter = s.ParticleEmitter(
    s.ParticleConfig(
        amount=100,
        size_range=(5, 15),
        speed_range=(800, 800),
        colors=[(255,0,0), (0,0,0), (255,0,255)],
        gravity=pygame.math.Vector2(0,0),
    )
)
player = s.Button(
    "spritePro\demoGames\Sprites\c.png",
    (500, 500),
    s.WH_C,'',on_click=onclick
)
text = s.TextSprite('0',96,(255,0,0))
text.set_position((s.WH_C.x,10),s.Anchor.MID_TOP)

# Main game loop
while True:
    s.update()