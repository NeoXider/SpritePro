import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

# ====================================================

import pygame
import spritePro as s
import json
import random


# TEST==============================================
class Question:
    def __init__(self, question, answers) -> None:
        self.question = question
        self.answers = answers
        self.correct_answer = answers[0]

    def get_shuffled_answers(self) -> list[str]:
        random_list = list(self.answers)
        random.shuffle(random_list)
        return random_list

    def check_answer(self, user_answer) -> bool:
        return user_answer == self.correct_answer


class Test:
    def __init__(self) -> None:
        self.questions = []
        self.current_question = 0
        self.score = 0

    def check_answer(self, user_answer) -> bool:
        return self.get_current_question().check_answer(user_answer)

    def get_current_question(self) -> Question:
        return self.questions[self.current_question]

    def answer(self, user_answer) -> bool:
        if self.check_answer(user_answer):
            self.score += 1
            self.current_question += 1
            return True
        self.current_question += 1
        return False

    def is_end(self) -> bool:
        return self.current_question >= len(self.questions)

    def save(self, file_name) -> None:
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(
                [q.__dict__ for q in self.questions], file, ensure_ascii=False, indent=4
            )

    def load(self, file_name) -> None:
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.questions = [Question(q["question"], q["answers"]) for q in data]
            random.shuffle(self.questions)
            self.current_question = 0
            self.score = 0


# VISUAL TEST==============================================


class Door(s.Sprite):
    def __init__(self, image, size, position, speed=3, text=""):
        super().__init__(image, size, position, speed)
        self.text = s.TextSprite(
            text, 48, (255, 255, 255), (self.rect.centerx, self.rect.top)
        )
        self.text.set_parent(self)

    def kill(self):
        self.text.kill()
        super().kill()


class Visual_test:
    def __init__(self, testirovanie: Test):
        self.text_question = s.TextSprite("вопрос", 64, (255, 255, 255), s.WH_C)
        self.text_question.rect.y = 50
        self.text_question.set_sorting_order(1001)
        self.text_score = s.TextSprite("вопрос", 64, (255, 255, 255), s.WH)
        self.text_score.rect.y -= 100
        self.text_score.rect.x = 250
        self.text_score.set_sorting_order(1001)

        self.testirovanie: Test = testirovanie
        self.doors: list[Door] = list()

    def start_game(self):
        self.testirovanie.load("test.json")
        self.question_game()

    def question_game(self):
        self.text_question.set_text(self.testirovanie.get_current_question().question)
        space = 450
        x = s.WH_C.x - space
        y = -100
        for i, e in enumerate(
            self.testirovanie.get_current_question().get_shuffled_answers()
        ):
            door = Door(
                "spritePro/demoGames/Sprites/door.png",
                (300, 300),
                (x + space * i, y),
                2,
                e,
            )
            self.doors.append(door)

    def update(self):
        self.text_question.set_color(
            s.utils.ColorEffects.pulse(5, (255, 255, 255), (255, 0, 0))
        )
        for i in self.doors:
            i.move_down()
        current = self.testirovanie.current_question
        self.text_score.text = f"{current + (0 if self.testirovanie.is_end() else 1)}/{len(self.testirovanie.questions)}"

    def kill_doors(self):
        for i in self.doors:
            i.kill()
        self.doors.clear()

    def answer(self, door: Door):
        result = self.testirovanie.answer(door.text.text)
        self.kill_doors()
        if not testirovanie.is_end():
            self.question_game()

        return result


# Game ===================================
s.init()
s.get_screen((1280, 960))
bg = s.Sprite("spritePro/demoGames/Sprites/fon.jpeg", s.WH, s.WH_C)
bg.set_color((255, 175, 175))

player = s.Sprite("spritePro/demoGames/Sprites/fog.png", (150, 150), (640, 870), 7)
player.set_position((s.WH_C.x, s.WH.y - 50), s.Anchor.MID_BOTTOM)

testirovanie = Test()
testirovanie.questions = [Question("вопрос", ["правильный ответ", "ответ", "ответ"])]
testirovanie.save("test.json")
visual_test = Visual_test(testirovanie)
visual_test.start_game()

emitter = s.ParticleEmitter(
    s.ParticleConfig(
        amount=20,
        lifetime_range=(1, 5),
        speed_range=(50.0, 150.0),
        fade_speed=300.0,
        gravity=pygame.Vector2(0, 0.0),
        image="spritePro/demoGames/Sprites/fog.png",
        image_scale_range=(0.1, 0.5),
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-180.0, 180.0),
        screen_space=False,
        angle_range=(0.0, 360.0),
        spawn_circle_radius=100,
    )
)

while True:
    s.update(fill_color=(0, 0, 0))
    player.handle_keyboard_input(
        up_key=None, down_key=None, left_key=pygame.K_a, right_key=pygame.K_d
    )
    visual_test.update()
    for door in visual_test.doors:
        if player.rect.colliderect(door.rect):
            if visual_test.answer(door):
                pass
            else:
                emitter.set_position(player.rect.center)
                emitter.emit()
