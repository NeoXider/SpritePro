import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

#================================ start ===========================

import pygame
import spritePro as s
from game_objects.ball import Ball
from game_objects.platform import Platform
from event_bus import ball_out_screen



class Game:
    def __init__(self):
        self.score_player_1 = 0
        self.score_player_2 = 0

        self.create_game_spretes()

        self.create_ui()

        ball_out_screen.connect(self.on_ball_out_screen)

    def create_game_spretes(self):
        self.bg = s.Sprite("", s.WH, s.WH_C)
        self.ball = Ball("", (70, 70), s.WH_C, 3, 1)
        self.ball.set_image(s.utils.round_corners(self.ball.image, 100))
        self.ball.random_push()

        self.platform_1 = Platform("", (30, 100) , (50, s.WH_C.y), 5, up = pygame.K_w, down = pygame.K_s)
        self.platform_1.color = (255, 150, 150)
        self.platform_1.set_image(s.utils.round_corners(self.platform_1.image, 50))
        
        self.platform_2 = Platform("", (30, 100) , (s.WH.x-50, s.WH_C.y), 5, up = pygame.K_UP, down = pygame.K_DOWN)
        self.platform_2.color = (150, 150, 255)
        self.platform_2.set_image(s.utils.round_corners(self.platform_2.image, 50))

    def create_ui(self):
        self.text_score_1 = s.TextSprite("0", 84, pos = (20,50))
        self.text_score_2 = s.TextSprite("0", 84, pos = (s.WH.x-20, 50))

    def update(self):
        self.bg.color = s.utils.ColorEffects.wave(0.5, ((100, 150, 100), (100, 100,100)))

        if self.ball.rect.colliderect(self.platform_1.rect) or self.ball.rect.colliderect(self.platform_2.rect):
            self.ball.velocity.x *= -1

    def on_ball_out_screen(self, sender, side):
        print("ball out screen", side)
        if not side:
            self.score_player_1 += 1
            self.text_score_1.text = str(self.score_player_1)
        else:
            self.score_player_2 += 1
            self.text_score_2.text = str(self.score_player_2)

        self.ball.random_push()