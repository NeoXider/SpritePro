import pygame
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from spritePro.gameSprite import GameSprite

path = Path(__file__).parent

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
FONT_LABEL = pygame.font.Font(None, 72)
FPS = 60
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

SCORE_GAMEOVER = 3

STATE_GAME = 0
STATE_WIN_LEFT = 1
STATE_WIN_RIGHT = 2

current_state = STATE_GAME


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
        self.start_pos = self.position.copy()

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
        self.position = self.start_pos
        self.dir_x *= -1


def render_game():
    SCREEN.blit(bg, (0, 0))
    player_left.update(SCREEN)
    player_right.update(SCREEN)
    ball.update(SCREEN)


def render_text():
    score_text1 = FONT_LABEL.render(str(leftScore), 1, (255, 255, 255))
    SCREEN.blit(score_text1, (10, 10))

    score_text2 = FONT_LABEL.render(str(rightScore), 1, (255, 255, 255))
    SCREEN.blit(score_text2, (750, 10))


def ball_bounch():
    if ball.rect.bottom >= HEIGHT or ball.rect.top <= 0:
        bounch_sound.play()
        ball.dir_y *= -1

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
    if ball.position.x < 0:
        add_score(True)

    if ball.position.x > WIDTH:
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
    pygame.mixer.music.set_volume(0.4)


def create_text(FONT_LABEL: pygame.font.Font):
    global text_left_win, text_right_win
    text_right_win = FONT_LABEL.render("Победа правого", 1, (255, 255, 255))
    text_left_win = FONT_LABEL.render("Победа левого", 1, (255, 255, 255))


def win(text: pygame.Surface, player: GameSprite):
    SCREEN.blit(text, (320, 10))
    player.rotate_by(6)


pygame.display.set_caption("pin pong")
bg = pygame.transform.scale(
    pygame.image.load(path / "Sprites" / "bg.jpg"), (WIDTH, HEIGHT)
)

bounch_sound = pygame.mixer.Sound(path / "Audio" / "baunch.mp3")

create_music()
create_text(FONT_LABEL)

leftScore = 0
rightScore = 0

ball = Ball(path / "Sprites" / "ball.png", (50, 50), (400, 290), 2)

player_left = GameSprite(path / "Sprites" / "platforma.png", (120, 50), (50, 300), 6)
player_left.rotate_to(-90)

player_right = GameSprite(path / "Sprites" / "platforma.png", (120, 50), (750, 300), 6)
player_right.rotate_to(90)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    render_game()
    render_text()

    if current_state == STATE_GAME:
        player_input()
        ball.move(ball.dir_x, ball.dir_y)
        ball_bounch()
        ball_fail()
        check_win()

    elif current_state == STATE_WIN_LEFT:
        win(text_left_win, player_left)

    elif current_state == STATE_WIN_RIGHT:
        win(text_right_win, player_right)

    pygame.display.update()
    CLOCK.tick(FPS)
