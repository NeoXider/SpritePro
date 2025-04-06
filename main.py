import pygame
import spritePro

pygame.init()

'''КОНСТАНТЫ'''
#размеры экрана
WIDTH, HEIGHT = 800, 600
FPS = 60

'''КЛАССЫ'''
class Cat():
    pass

'''ФУНКЦИИ'''
def clamp(value, min_value, max_value):
    """
    Ограничивает значение в заданном диапазоне [min_value, max_value].
    """
    return max(min_value, min(value, max_value))

def create_window(WIDTH, HEIGHT):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ping pong", "Sprite/ball.jpg")
    return screen

'''СЛУЖЕБНЫЕ ПЕРЕМЕННЫЕ'''
screen = create_window(WIDTH, HEIGHT)

'''ПОЛУЧАЕМ КАРТИНКИ'''
bg_image = pygame.transform.scale(pygame.image.load("Sprites/bg.jpg"), (WIDTH, HEIGHT))

clock = pygame.time.Clock()

player1 = spritePro.GameSprite("Sprites/platforma.png", (150, 50), (50, 250), 4)
player1.rotate_to(-90)

player2 = spritePro.GameSprite("Sprites/platforma.png", (150, 50), (750, 250), 4)
player2.rotate_to(90)

ball = spritePro.GameSprite("Sprites/ball.jpg", (50, 50), (400, 300), 3)

speed_x = 3
speed_y = 3

lose_frames = 0

pygame.font.init()
font_label = pygame.font.Font(None, 36)
text = font_label.render("lol", True, (255,255,255))

'''ИГРОВОЙ ЦИКЛ'''
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    screen.blit(bg_image, (0, 0))
    
    player1.handle_keyboard_input(up_key=pygame.K_w, down_key=pygame.K_s, left_key=None, right_key=None)
    if player1.rect.y > HEIGHT - player1.rect.height or player1.rect.y < 0:
        player1.stop()
        player1.rect.y = clamp(player1.rect.y, 0, HEIGHT - player1.rect.height)
    player1.update(screen)

    
    player2.handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=None, right_key=None)
    if player2.rect.y > HEIGHT - player2.rect.height or player2.rect.y < 0:
        player2.stop()
        player2.rect.y = clamp(player2.rect.y, 0, HEIGHT - player2.rect.height)
    
    player2.update(screen)

    ball.update(screen)
    ball.move(speed_x, speed_y)
    
    if ball.rect.bottom > HEIGHT or ball.rect.top < 0:
        speed_y *= -1
        
    if ball.collide_with(player1) or ball.collide_with(player2):
        speed_x *= -1
        
    if ball.rect.right > WIDTH:
        lose_frames = 30
        ball.position.x, ball.position.y = (400, 300)
        
    #отрисовка

    if lose_frames > 0:
        screen.blit(text, (350, 150))
        lose_frames -= 1

    
    pygame.display.update()
    clock.tick(FPS)        
    

