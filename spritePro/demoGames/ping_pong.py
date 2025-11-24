import pygame
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

from spritePro import Sprite
from spritePro import Anchor
from spritePro.utils.surface import round_corners
import spritePro

path = Path(__file__).parent

SCREEN = spritePro.get_screen((960, 720))
WIDTH, HEIGHT = int(spritePro.WH.x), int(spritePro.WH.y)

SCORE_GAMEOVER = 3

# Состояния игры
STATE_MENU = 0
STATE_SHOP = 1
STATE_GAME = 2
STATE_WIN_LEFT = 3
STATE_WIN_RIGHT = 4

# Получаем глобальный AudioManager
audio = spritePro.audio_manager


class Ball(Sprite):
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
        ball.dir_x = 1 if right else -1
        if ball.x_bounch != ball.dir_x:
            ball.x_bounch = ball.dir_x
            bounce_sound.play()

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


def render_text():
    score_text_l.set_text(f"{leftScore}")

    score_text_r.set_text(f"{rightScore}")


def ball_bounch():
    if ball.rect.top <= 0:
        bounce_sound.play()
        ball.dir_y = 1

    if ball.rect.bottom >= HEIGHT:
        bounce_sound.play()
        ball.dir_y = -1

    if ball.rect.colliderect(player_right.rect):
        ball.baunch_x(right=False)

    if ball.rect.colliderect(player_left.rect):
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
    """Инициализирует музыку и звуки через AudioManager."""
    audio.set_sfx_volume(1.0)
    # Воспроизводим музыку сразу с нужной громкостью
    audio.play_music(str(path / "Audio" / "fon_musik.mp3"), volume=0.4)
    # Загружаем звук и сразу получаем объект Sound
    global bounce_sound
    bounce_sound = audio.load_sound("bounce", str(path / "Audio" / "baunch.mp3"))


def win(player: Sprite):
    text = "Победа левого" if player == player_left else "Победа правого"
    text += " игрока!"
    textWin.set_text(text)
    textWin.set_position((WIDTH // 2, HEIGHT // 2), spritePro.Anchor.CENTER)

    player.rotate_by(-8)


def start_game():
    global current_state, leftScore, rightScore
    current_state = STATE_GAME
    leftScore = 0
    rightScore = 0
    # Сбрасываем камеру в начало координат
    spritePro.set_camera_position(0, 0)
    player_left.rect.center = player_left.start_pos
    player_right.rect.center = player_right.start_pos
    player_left.rotate_to(-90)
    player_right.rotate_to(90)
    ball.reset()
    bounce_sound.play()


def menu():
    global current_state
    current_state = STATE_MENU
    # Сбрасываем камеру в начало координат
    spritePro.set_camera_position(0, 0)
    bounce_sound.play()


def shop():
    global current_state
    current_state = STATE_SHOP
    # Сбрасываем камеру в начало координат
    spritePro.set_camera_position(0, 0)
    bounce_sound.play()


def logic_shop():
    SCREEN.blit(BGS[current_state], (0, 0))
    textShop.set_position((WIDTH // 2, 10), spritePro.Anchor.MID_TOP)
    bts[STATE_MENU].set_color(COLOR_EFX[STATE_MENU]())


def logic_menu():
    SCREEN.blit(BGS[current_state], (0, 0))
    bts[STATE_GAME].set_color(COLOR_EFX[STATE_GAME]())
    bts[STATE_SHOP].set_color(COLOR_EFX[STATE_SHOP]())


def logic_game():
    player_input()
    ball.move(ball.dir_x, ball.dir_y)
    ball_bounch()
    ball_fail()
    check_win()
    bts[STATE_MENU].set_color(COLOR_EFX[STATE_MENU]())


def music_toggle(is_on: bool) -> None:
    """Переключить музыку через AudioManager."""
    spritePro.audio_manager.set_music_enabled(is_on)
    bounce_sound.play()


def audio_toggle(is_on: bool) -> None:
    """Переключить звуковые эффекты через AudioManager."""
    spritePro.audio_manager.set_sfx_enabled(is_on)
    bounce_sound.play()


def update_sprite_visibility():
    """Управляет видимостью спрайтов в зависимости от состояния игры."""
    # Игровые спрайты (показываются в игре и при победе)
    is_game_or_win = current_state in (STATE_GAME, STATE_WIN_LEFT, STATE_WIN_RIGHT)
    player_left.active = is_game_or_win
    player_right.active = is_game_or_win
    ball.active = current_state == STATE_GAME  # Мяч только в игре
    score_text_l.active = current_state == STATE_GAME
    score_text_r.active = current_state == STATE_GAME

    # Кнопки меню
    bts[STATE_GAME].active = current_state == STATE_MENU
    bts[STATE_SHOP].active = current_state == STATE_MENU
    bts[STATE_MENU].active = current_state in (
        STATE_GAME,
        STATE_SHOP,
        STATE_WIN_LEFT,
        STATE_WIN_RIGHT,
    )

    # Переключатели (показываются только в меню)
    for toggle in TOGGLES.values():
        toggle.active = current_state == STATE_MENU

    # Текст магазина
    textShop.active = current_state == STATE_SHOP

    # Текст победы
    textWin.active = current_state in (STATE_WIN_LEFT, STATE_WIN_RIGHT)


pygame.display.set_caption("pin pong")

# Инициализируем музыку и звуки
bounce_sound = None  # Будет создан в create_music()
create_music()

leftScore = 0
rightScore = 0
current_state = STATE_MENU
size_text = 32
pading_x_player = 100


print(f"Создаем мяч с позицией: ({WIDTH // 2}, {HEIGHT // 2})")
ball = Ball(path / "Sprites" / "ball.png", (50, 50), (WIDTH // 2, HEIGHT // 2), 2)
ball.set_color((255, 255, 255))

print(f"Создаем левую платформу с позицией: ({pading_x_player}, {HEIGHT // 2})")
player_left = Sprite(
    path / "Sprites" / "platforma.png",
    (120, 50),
    (pading_x_player, HEIGHT // 2),
    6,
)

print(
    f"Создаем правую платформу с позицией: ({WIDTH - pading_x_player}, {HEIGHT // 2})"
)
player_right = Sprite(
    path / "Sprites" / "platforma.png",
    (120, 50),
    (WIDTH - pading_x_player, HEIGHT // 2),
    6,
)

textWin = spritePro.TextSprite("", 72, (255, 255, 100), (WIDTH // 2, HEIGHT // 2))
textShop = spritePro.TextSprite("Shop", 72, (255, 255, 100))
# Текст счета левого игрока (слева вверху)
score_text_l = spritePro.TextSprite(f"{leftScore}", 72, (255, 255, 255), (50, 50), anchor=spritePro.Anchor.TOP_LEFT)
# Текст счета правого игрока (справа вверху)
score_text_r = spritePro.TextSprite(f"{rightScore}", 72, (255, 255, 255), (WIDTH - 50, 50), anchor=spritePro.Anchor.TOP_RIGHT)

btn_size = 210, 50

btn_menu = spritePro.Button("", btn_size, (WIDTH // 2, HEIGHT - 20), "Menu", size_text)
btn_menu.on_click(menu)
btn_menu.set_alpha(150)
btn_menu.set_position((WIDTH // 2, HEIGHT - 20), spritePro.Anchor.MID_BOTTOM)

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

# Устанавливаем правильные якоря для кнопок
bts[STATE_SHOP].set_position((WIDTH // 2, HEIGHT // 2 + 100), spritePro.Anchor.CENTER)
bts[STATE_GAME].set_position((WIDTH // 2, HEIGHT // 2), spritePro.Anchor.CENTER)

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

# Устанавливаем правильные якоря для переключателей
TOGGLES["music"].set_position((150, 50), spritePro.Anchor.CENTER)
TOGGLES["audio"].set_position((150, 120), spritePro.Anchor.CENTER)

COLOR_EFX = {
    STATE_MENU: spritePro.utils.pulse,
    STATE_GAME: spritePro.utils.wave,
    STATE_SHOP: lambda: spritePro.utils.flicker(flicker_color=(50, 50, 255)),
}

fps_text = spritePro.readySprites.create_fps_counter((spritePro.WH_C[0], 15))

# Фиксируем камеру на (0, 0) для пинг-понга
spritePro.set_camera_position(0, 0)
print(f"Размер экрана: {WIDTH}x{HEIGHT}")
print(f"Центр экрана: {spritePro.WH_C}")
print(f"Позиция мяча: {ball.rect.center}")
print(f"Позиция левой платформы: {player_left.rect.center}")
print(f"Позиция правой платформы: {player_right.rect.center}")
print(f"Камера: {spritePro.get_camera_position()}")

# Устанавливаем начальную видимость спрайтов
update_sprite_visibility()

while True:
    fps_text.update()
    fps_text.update_fps()

    # Обновляем видимость спрайтов перед отрисовкой
    update_sprite_visibility()

    # Сначала рисуем фон
    render_game()
    render_text()

    # Затем обновляем и рисуем все спрайты (включая кнопки) поверх фона
    spritePro.update()

    for e in spritePro.events:
        pass

    if current_state == STATE_MENU:
        logic_menu()

    elif current_state == STATE_SHOP:
        logic_shop()

    elif current_state == STATE_GAME:
        logic_game()

    elif current_state == STATE_WIN_LEFT:
        win(player_left)

    elif current_state == STATE_WIN_RIGHT:
        win(player_right)
