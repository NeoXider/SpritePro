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
    score += click
    money.add(click)
    s.PlayerPrefs.set_int("score", score)
    emitter.set_position(s.WH_C)
    emitter.emit()


def use_skin(sprite):
    player.set_image(sprite)
    player.set_image(s.utils.round_corners(player.image, 5000))



def go_game():
    global game_state
    game_state = GAME


def go_shop():
    global game_state
    game_state = SHOP


def go_upgrade():
    global game_state
    game_state = UPGRADE


skin_id = s.PlayerPrefs.get_int("skin_id", 0)
score = s.PlayerPrefs.get_int("score", 0)
money = Wallet(score)
click = 1

SPACE = 50

GAME = 0
SHOP = 1
UPGRADE = 2

game_state = GAME

sprite_skins = [
    "spritePro\\demoGames\\Sprites\\bg1.jpg",
    #"spritePro\\demoGames\\Sprites\\c.png",
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
bg.set_sorting_order(-1000)
# Create a basic sprite
emitter = s.ParticleEmitter(
    s.ParticleConfig(
        amount=100,
        image_scale_range=(0.5, 0.5),
        speed_range=(1200, 2000),
        colors=[(255, 0, 0), (0, 0, 0), (255, 0, 255)],
        gravity=pygame.math.Vector2(0, 0),
        fade_speed=500,
        angular_velocity_range=(-1000, 1000),
        spawn_circle_radius=100
    )
)

player = s.Button(sprite_skins[skin_id], (500, 500), s.WH_C, "", on_click=onclick)

text = s.TextSprite(f"{score}", 96, (255, 0, 0))
text.set_position((s.WH_C.x, SPACE), s.Anchor.MID_TOP)

btn_go_shop = s.Button("", text="Shop", text_size=56, on_click=go_shop)
btn_go_shop.set_position((SPACE, s.WH.y - SPACE), s.Anchor.BOTTOM_LEFT)
btn_go_shop.set_image(s.utils.round_corners(btn_go_shop.image, 50))

btn_go_back = s.Button("", text="Back", text_size=56, on_click=go_game)
btn_go_back.set_position((SPACE, s.WH.y - SPACE), s.Anchor.BOTTOM_LEFT)
btn_go_back.set_image(s.utils.round_corners(btn_go_back.image, 50))

btn_go_upgrade = s.Button("", text="Upgrade", text_size=56, on_click=go_upgrade)
btn_go_upgrade.set_position((s.WH_C.x, s.WH.y - SPACE), s.Anchor.MID_BOTTOM)
#btn_upgrade.set_position((s.WH.x - SPACE, 0 +SPACE), s.Anchor.TOP_RIGHT)
btn_go_upgrade.set_image(s.utils.round_corners(btn_go_upgrade.image, 50))

btn_upgrade = s.Button("", (550, 150), s.WH_C, text="buy: 20, upgrade 1 > 2", text_size=56, on_click=go_upgrade)
btn_upgrade.set_image(s.utils.round_corners(btn_upgrade.image, 50))

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

sprites_game = [player, btn_go_shop]
sprites_shop = [btn_go_upgrade] + btn_skins
sprites_upgrade = [btn_upgrade]


# Main game loop
while True:
    s.update()

    text.text = str(score)
    emitter.config.image = player.image
    emitter.config.amount = click

    btn_go_back.set_active(game_state != GAME)
    text.set_color(s.utils.ColorEffects.strobe(15, (255, 0, 0), (150, 0, 0),0.9))

    for sprite in sprites_game:
        sprite.set_active(game_state == GAME)

    for sprite in sprites_shop:
        sprite.set_active(game_state == SHOP)

    for spite in sprites_upgrade:
        spite.set_active(game_state == UPGRADE)

    if game_state == GAME:
        bg.set_color((100,100,100))
    elif game_state == SHOP:
        bg.set_color((255, 255, 255))
    elif game_state == UPGRADE:
        bg.set_color((100, 100, 255))
