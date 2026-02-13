import spritePro as s


def on_click():
    global counter
    counter += 1
    textSprite.text = f"{counter}"
    particle.emit(button.position)
    textSprite.DoKill(True)
    textSprite.DoMoveBy((0, -10), 0.5).SetYoyo(True).SetLoops(2)


counter = 0

s.get_screen((800, 600), "Sprite Pro")

bg = s.Sprite("000000000247.jpg", s.WH, s.WH_C).set_color((100, 100, 100))
button = s.Button("000000000312.jpg", (300, 300), s.WH_C, "")
button.on_click(on_click)
textSprite = s.TextSprite("0", 64, pos=(400, 50))

particle = s.ParticleEmitter(s.ParticleConfig(sorting_order=10000, size_range=(20, 100)))


while True:
    s.update(fill_color=(0, 0, 100))
