import pygame
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

from spritePro.gameSprite import GameSprite
from spritePro.utils.surface import round_corners
import spritePro

path = Path(__file__).parent

pygame.init()
pygame.font.init()
pygame.mixer.init()

SCREEN = spritePro.get_screen((960, 720))
WIDTH, HEIGHT = spritePro.WH

SCORE_GAMEOVER = 3

# Состояния игры
STATE_MENU = 0
STATE_SHOP = 1
STATE_GAME = 2
STATE_WIN_LEFT = 3
STATE_WIN_RIGHT = 4
MUSIC_VOLUME = 0.4
SFX_VOLUME = 1


class Ball(GameSprite):
    add_speed_per_frame = 0.005
    max_speed = 5
    speed_rotate = 2
    x_bounch = 0
    dir_x = 1
    dir_y = 1

    def __init__(self, sprite, size, pos, speed):
        super().__init__(sprite, size, pos, speed)
        self.start_speed = speed

    def baunch_x(self, right: bool):
        global bounch_sound
        ball.dir_x = 1 if right else -1
        if ball.x_bounch != ball.dir_x:
            ball.x_bounch = ball.dir_x
            bounch_sound.play()

    def move(self, dx: float, dy: float):
        self.speed = min(self.speed + self.add_speed_per_frame, self.max_speed)
        self.rotate_by(self.speed_rotate * self.speed * self.dir_x * self.dir_y * -1)
        super().move(dx, dy)

    def reset(self):
        self.speed = self.start_speed
        self.rect.center = self.start_pos
        self.dir_x *= -1


def render_game():
    SCREEN.blit(BGS[STATE_GAME], (0, 0))
    player_left.update(SCREEN)
    player_right.update(SCREEN)
    ball.update(SCREEN)


def render_text():
    score_text_l.set_text(f"{leftScore}")
    score_text_l.rect.topleft = (10, 10)

    score_text_r.set_text(f"{rightScore}")
    score_text_r.rect.topright = (WIDTH - 10, 10)

    score_text_l.update(SCREEN)
    score_text_r.update(SCREEN)


def ball_bounch():
    if ball.rect.top <= 0:
        bounch_sound.play()
        ball.dir_y = 1

    if ball.rect.bottom >= HEIGHT:
        bounch_sound.play()
        ball.dir_y = -1

    if ball.collide_with(player_right):
        ball.baunch_x(right=False)

    if ball.collide_with(player_left):
        ball.baunch_x(right=True)


def player_input():
    player_left.handle_keyboard_input(
        up_key=pygame.K_w, down_key=pygame.K_s, left_key=None, right_key=None
    )
    player_right.handle_keyboard_input(
        up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=None, right_key=None
    )
    player_left.limit_movement(SCREEN.get_rect())
    player_right.limit_movement(SCREEN.get_rect())


def ball_fail():
    if ball.rect.right < 0:
        add_score(True)

    if ball.rect.x > WIDTH:
        add_score(False)


def add_score(right_player: bool):
    global rightScore, leftScore
    ball.reset()
    print("reset")

    if right_player:
        rightScore += 1
    else:
        leftScore += 1


def check_win():
    global current_state

    if rightScore >= SCORE_GAMEOVER:
        current_state = STATE_WIN_RIGHT
    elif leftScore >= SCORE_GAMEOVER:
        current_state = STATE_WIN_LEFT


def create_music():
    pygame.mixer.music.load(path / "Audio" / "fon_musik.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)


def win(player: GameSprite):
    text = "Победа левого" if player == player_left else "Победа правого"
    text += " игрока!"
    textWin.set_text(text)
    textWin.rect.centerx, textWin.rect.y = (WIDTH // 2, HEIGHT // 2)
    textWin.update(SCREEN)

    player.rotate_by(-8)
    player.update(SCREEN)


def start_game():
    global current_state, leftScore, rightScore
    current_state = STATE_GAME
    leftScore = 0
    rightScore = 0
    player_left.rect.center = player_left.start_pos
    player_right.rect.center = player_right.start_pos
    player_left.rotate_to(-90)
    player_right.rotate_to(90)
    ball.reset()
    bounch_sound.play()


def menu():
    global current_state
    current_state = STATE_MENU
    bounch_sound.play()


def shop():
    global current_state
    current_state = STATE_SHOP
    bounch_sound.play()


def logic_shop():
    SCREEN.blit(BGS[current_state], (0, 0))
    textShop.rect.centerx, textShop.rect.y = (WIDTH // 2, 10)
    textShop.update(SCREEN)
    bts[STATE_MENU].set_color(COLOR_EFX[STATE_MENU]())
    bts[STATE_MENU].update(SCREEN)


def logic_menu():
    SCREEN.blit(BGS[current_state], (0, 0))
    bts[STATE_GAME].set_color(COLOR_EFX[STATE_GAME]())
    bts[STATE_GAME].update(SCREEN)

    bts[STATE_SHOP].set_color(COLOR_EFX[STATE_SHOP]())
    bts[STATE_SHOP].update(SCREEN)

    for toggle in TOGGLES.values():
        toggle.update(SCREEN)


def logic_game():
    player_input()
    ball.move(ball.dir_x, ball.dir_y)
    ball_bounch()
    ball_fail()
    check_win()
    bts[STATE_MENU].set_color(COLOR_EFX[STATE_MENU]())
    bts[STATE_MENU].update(SCREEN)


def music_toggle(is_on: bool) -> None:
    pygame.mixer.music.unpause() if is_on else pygame.mixer.music.pause()
    bounch_sound.play()


def audio_toggle(is_on: bool) -> None:
    for sound in efxs:
        sound.set_volume(SFX_VOLUME if is_on else 0)
    bounch_sound.play()


efxs = []

pygame.display.set_caption("pin pong")
bounch_sound = pygame.mixer.Sound(path / "Audio" / "baunch.mp3")
bounch_sound.set_volume(SFX_VOLUME)
efxs.append(bounch_sound)

create_music()

leftScore = 0
rightScore = 0
current_state = STATE_MENU
size_text = 32
pading_x_player = 50


ball = Ball(path / "Sprites" / "ball.png", (50, 50), spritePro.WH_C, 2)
ball.set_color((255, 255, 255))
player_left = GameSprite(
    path / "Sprites" / "platforma.png",
    (120, 50),
    (pading_x_player, spritePro.WH_C[1]),
    6,
)
player_right = GameSprite(
    path / "Sprites" / "platforma.png",
    (120, 50),
    (WIDTH - pading_x_player, spritePro.WH_C[1]),
    6,
)

textWin = spritePro.TextSprite("", 72, (255, 255, 100), spritePro.WH_C)
textShop = spritePro.TextSprite("Shop", 72, (255, 255, 100))
score_text_l = spritePro.TextSprite(f"{rightScore}", 72, (255, 255, 255))
score_text_r = spritePro.TextSprite(f"{rightScore}", 72, (255, 255, 255))

btn_size = 210, 50

btn_menu = spritePro.Button("", btn_size, (0, 0), "Menu", size_text)
btn_menu.on_click(menu)

btn_menu.set_alpha(150)
btn_menu.rect.centerx = WIDTH // 2
btn_menu.rect.bottom = HEIGHT - 20

bts = {
    STATE_MENU: btn_menu,
    STATE_SHOP: spritePro.Button(
        "", btn_size, (WIDTH // 2, HEIGHT // 2 + 100), "Shop", size_text, on_click=shop
    ),
    STATE_GAME: spritePro.Button(
        "",
        btn_size,
        (WIDTH // 2, HEIGHT // 2),
        "Start game",
        size_text,
        on_click=start_game,
    ),
}

# добавляем скругления
for bt in bts.values():
    bt.set_image(round_corners(bt.image, 50))

BGS = {
    STATE_MENU: pygame.transform.scale(
        pygame.image.load(path / "Sprites" / "bg.jpg"), (spritePro.WH)
    ),
    STATE_SHOP: pygame.transform.scale(
        pygame.image.load(path / "Sprites" / "bg.jpg"), (spritePro.WH)
    ),
    STATE_GAME: pygame.transform.scale(
        pygame.image.load(path / "Sprites" / "bg.jpg"), (spritePro.WH)
    ),
}


TOGGLES = {
    "music": spritePro.ToggleButton(
        "",
        size=(150, 40),
        pos=(150, 50),
        text_on="music: ON",
        text_off="music: OFF",
        on_toggle=music_toggle,
        color_off=(255, 100, 0),
    ),
    "audio": spritePro.ToggleButton(
        "",
        size=(150, 40),
        pos=(150, 120),
        text_on="audio: ON",
        text_off="audio: OFF",
        on_toggle=audio_toggle,
        color_off=(255, 100, 0),
    ),
}

COLOR_EFX = {
    STATE_MENU: spritePro.utils.pulse,
    STATE_GAME: spritePro.utils.wave,
    STATE_SHOP: lambda: spritePro.utils.flicker(flicker_color=(50, 50, 255)),
}

while True:
    spritePro.update()
    for e in spritePro.events:
        pass

    render_game()
    render_text()

    if current_state == STATE_MENU:
        logic_menu()

    elif current_state == STATE_SHOP:
        logic_shop()

    elif current_state == STATE_GAME:
        logic_game()

    elif current_state == STATE_WIN_LEFT:
        win(player_left)
        bts[STATE_MENU].update(SCREEN)

    elif current_state == STATE_WIN_RIGHT:
        win(player_right)
        bts[STATE_MENU].update(SCREEN)
