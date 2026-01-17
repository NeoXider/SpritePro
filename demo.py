import spritePro as s
import pygame

# Initialize the library
s.init()

# Create a window
s.get_screen((800, 600), "My Game")

circle = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(
    circle,
    (130, 255, 70),
    (50, 50),
    radius=45,
)
had = s.Sprite(
    circle,
    size=(100, 100),
    pos=s.WH_C,
    speed=3,
)
had.set_scale(5)
had.rect.centery -= 50
had.update()

circle = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(circle, (255, 255, 255), (50, 50), radius=45)
eye = s.Sprite(
    circle,
    size=(70, 70),
    pos=(300, 150),
)
eye.set_parent(had)

circle = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(circle, (255, 255, 255), (50, 50), radius=45)
eye = s.Sprite(
    circle,
    size=(70, 70),
    pos=(500, 150),
)
eye.set_parent(had)

circle = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(circle, (255, 255, 255), (50, 50), radius=45, width=10)
smile = s.Sprite(
    circle,
    size=(100, 100),
    pos=s.WH_C,
)
smile.set_parent(had)

# tweenColor
tm_player = s.TweenManager()
tm_player.add_tween(
    name="color",
    start_value=0,
    end_value=255,
    duration=0.7,
    easing=s.EasingType.EASE_OUT,
    loop=True,
    yoyo=True,
    delay=0,
    on_update=lambda x, sprite=smile: sprite.set_color((100, int(x), 100)),
)

tm_player.add_tween(
    name="scale",
    start_value=1,
    end_value=2.5,
    duration=0.7,
    easing=s.EasingType.EASE_OUT,
    loop=True,
    yoyo=True,
    delay=0,
    on_update=lambda x, sprite=smile: sprite.set_scale(x),
)

# Main game loop
while True:
    s.update(fill_color=(0, 0, 100))
    tm_player.update()
    had.handle_keyboard_input()
