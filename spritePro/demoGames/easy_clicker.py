import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))
path = Path(__file__).parent

# =================================================================
import spritePro as s
import pygame


class Wallet:
    def __init__(self, value):
        self.value = value

    def add(self, amount):
        self.value += amount

    def spend(self, amount):
        if self.try_spent(amount):
            self.value -= amount
            return True

        return False

    def try_spent(self, amount):
        return self.value >= amount


class Btn_skin(s.Button):
    def init(self, id, on_buy):
        self.id = id
        self.price = price_skins[id]
        self.on_buy = on_buy
        self.on_click(self.buy)

    def update(self, screen: pygame.Surface = None):
        super().update()
        self.text_sprite.text = "use" if self.price == 0 else f"buy: {self.price}"

    def buy(self):
        print("Покупка")
        if money.spend(self.price):
            global score, skin_id

            self.price = 0
            self.on_buy(self._image_source)
            score = money.value
            skin_id = self.id
            price_skins[self.id] = 0
            s.PlayerPrefs._set_value("price_skins", price_skins)
            s.PlayerPrefs.set_int("score", score)
            s.PlayerPrefs.set_int("skin_id", skin_id)


def onclick():
    global score
    score += 1
    money.add(1)
    s.PlayerPrefs.set_int("score", score)
    emitter.set_position(s.WH_C)
    emitter.emit()


def use_skin(sprite):
    player.set_image(sprite)


def go_game():
    global game_state
    game_state = GAME


def go_shop():
    global game_state
    game_state = SHOP


skin_id = s.PlayerPrefs.get_int("skin_id", 0)
score = s.PlayerPrefs.get_int("score", 0)
money = Wallet(score)

SPACE = 50

GAME = 0
SHOP = 1

game_state = GAME

sprite_skins = [
    "spritePro\\demoGames\\Sprites\\c.png",
    "spritePro\\demoGames\\Sprites\\door.png",
    "spritePro\\demoGames\\Sprites\\platforma.png",
    "spritePro\\demoGames\\Sprites\\fog.png",
]
price_skins = s.PlayerPrefs._get_value("price_skins", [0, 50, 250, 300])
btn_skins = []


# Initialize the library
s.init()

# Create a window
s.get_screen((1280, 960), "My Game")

bg = s.Sprite("spritePro\\demoGames\\Sprites\\bg1.jpg", s.WH, s.WH_C)
# Create a basic sprite
emitter = s.ParticleEmitter(
    s.ParticleConfig(
        amount=100,
        size_range=(5, 15),
        speed_range=(800, 800),
        colors=[(255, 0, 0), (0, 0, 0), (255, 0, 255)],
        gravity=pygame.math.Vector2(0, 0),
    )
)
player = s.Button(sprite_skins[skin_id], (500, 500), s.WH_C, "", on_click=onclick)
text = s.TextSprite(f"{score}", 96, (255, 0, 0))
text.set_position((s.WH_C.x, SPACE), s.Anchor.MID_TOP)

btn_shop = s.Button("", text="Shop", text_size=56, on_click=go_shop)
btn_shop.set_position((SPACE, s.WH.y - SPACE), s.Anchor.BOTTOM_LEFT)

btn_back = s.Button("", text="Back", text_size=56, on_click=go_game)
btn_back.set_position((SPACE, s.WH.y - SPACE), s.Anchor.BOTTOM_LEFT)

x_start, y_start = 500, 300
size = 200, 200
grid_space = size[0] + SPACE * 2
for i, e in enumerate(sprite_skins):
    skin = Btn_skin(e, size, (200, 200), text_size=56, text_color=(255, 0, 255))
    skin.init(i, use_skin)
    skin.text_sprite.set_position((skin.rect.centerx, skin.rect.y), s.Anchor.MID_BOTTOM)
    x = i % 2
    y = i // 2
    skin.set_position((x_start + grid_space * x, y_start + grid_space * y))
    btn_skins.append(skin)

sprites_game = [player, btn_shop]
sprites_shop = [] + btn_skins


# Main game loop
while True:
    s.update()

    text.text = str(score)

    bg.set_color((255, 255, 255) if game_state == GAME else (100, 100, 100))
    btn_back.set_active(game_state != GAME)
    text.set_color(s.utils.ColorEffects.strobe(15, (255, 0, 0), (150, 0, 0)))

    for sprite in sprites_game:
        sprite.set_active(game_state == GAME)

    for sprite in sprites_shop:
        sprite.set_active(game_state == SHOP)

    if game_state == GAME:
        pass
    elif game_state == SHOP:
        pass
