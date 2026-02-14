import spritePro as s
import pygame

# --- Константы ---
GRAVITY = 0.5
JUMP_STRENGTH = -12
MOVE_SPEED = 7

# --- Инициализация SpritePro ---
s.init()
screen = s.get_screen((800, 600), "Платформер")
game = s.SpriteProGame.get()

# --- Классы ---
class Player(s.Sprite):
    def __init__(self, pos):
        # Создаем спрайт красного цвета
        super().__init__("Player", pos, (40, 60), color=(255, 80, 80))
        self.velocity_y = 0
        self.on_ground = False

    def update(self, platforms, *args, **kwargs):
        # Управление с клавиатуры
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += MOVE_SPEED

        # Гравитация
        self.velocity_y += GRAVITY
        # Простое ограничение максимальной скорости падения
        if self.velocity_y > 15:
            self.velocity_y = 15
            
        self.rect.y += self.velocity_y

        # Проверка столкновений с платформами
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Если игрок движется вниз и его низ пересекает верх платформы
                if self.velocity_y > 0 and self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                    break # Выходим, так как столкновение уже обработано

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH

# --- Создание объектов ---
# Игрок создается в центре экрана
player = Player(s.WH_C)

# Список платформ
platforms = [
    s.Sprite("Platform", (0, 580), (800, 20), color=(70, 200, 70)),
    s.Sprite("Platform", (200, 480), (150, 20), color=(70, 200, 70)),
    s.Sprite("Platform", (400, 380), (150, 20), color=(70, 200, 70)),
    s.Sprite("Platform", (100, 280), (100, 20), color=(70, 200, 70)),
    s.Sprite("Platform", (550, 200), (200, 20), color=(70, 200, 70)),
]


# --- Основной игровой цикл ---
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                player.jump()

    # Обновление состояния игры
    # Метод update игрока вызывается вручную, так как ему нужны платформы для проверки столкновений
    player.update(platforms)

    # s.update() очищает экран, обновляет все зарегистрированные объекты (кроме игрока) 
    # и отрисовывает все спрайты, включая игрока и платформы.
    s.update(fill_color=(135, 206, 255)) # Небесно-голубой фон

pygame.quit()