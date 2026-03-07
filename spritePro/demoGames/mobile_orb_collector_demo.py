"""Мобильное демо SpritePro: управление экранными кнопками и сбор орбов.

Запуск на desktop:
    python -m spritePro.demoGames.mobile_orb_collector_demo

Запуск через Kivy:
    python -m spritePro.demoGames.mobile_orb_collector_demo --kivy
"""

from __future__ import annotations

import random
import sys

import pygame

import spritePro as s


BACKGROUND_COLOR = (12, 18, 28)
WORLD_SIZE = (2200, 1400)
PLAYER_SIZE = (72, 72)
PLAYER_SPEED = 360.0
BOOST_SPEED = 560.0
ORB_COUNT = 18


class MobileOrbCollectorScene(s.Scene):
    def __init__(self) -> None:
        super().__init__()
        self.world_rect = pygame.Rect(0, 0, *WORLD_SIZE)
        self.rng = random.Random(42)
        self.score = 0
        self._orb_sprites: list[s.Sprite] = []
        self._build_world()
        self._build_ui()
        s.set_camera_follow(self.player, offset=(0,0))

    def _build_world(self) -> None:
        self.player = s.Sprite("", PLAYER_SIZE, (s.WH_C), scene=self)
        self.player.set_rect_shape(PLAYER_SIZE, (80, 220, 255), border_radius=24)
        
        for _ in range(ORB_COUNT):
            self._orb_sprites.append(self._spawn_orb())

        for _ in range(48):
            pos = (
                self.rng.randint(80, self.world_rect.width - 80),
                self.rng.randint(80, self.world_rect.height - 80),
            )
            size = self.rng.randint(20, 60)
            deco = s.Sprite("", (size, size), pos, scene=self, sorting_order=-50)
            deco.set_circle_shape(size // 2, (22, 36, 52))

    def _build_ui(self) -> None:
        self.score_label = s.TextSprite(
            "Score: 0",
            font_size=38,
            color=(255, 245, 170),
            pos=(24, 20),
            scene=self,
            sorting_order=2000,
        )
        self.score_label.set_screen_space(True)
        self.score_label.set_position((24, 20), s.Anchor.TOP_LEFT)

        self.tip_label = s.TextSprite(
            "Touch buttons or use WASD/Arrows",
            font_size=24,
            color=(185, 210, 240),
            pos=(24, 64),
            scene=self,
            sorting_order=2000,
        )
        self.tip_label.set_screen_space(True)
        self.tip_label.set_position((24, 64), s.Anchor.TOP_LEFT)

        self.left_button = self._create_button("LEFT", (110, s.WH.y - 110))
        self.right_button = self._create_button("RIGHT", (240, s.WH.y - 110))
        self.up_button = self._create_button("UP", (175, s.WH.y - 240))
        self.down_button = self._create_button("DOWN", (175, s.WH.y - 110))
        self.boost_button = self._create_button("BOOST", (s.WH.x - 130, s.WH.y - 130), size=(150, 150))
        self.boost_button.set_all_colors((255, 170, 80), (255, 120, 70), (255, 200, 110))

    def _create_button(
        self,
        text: str,
        pos: tuple[float, float],
        *,
        size: tuple[int, int] = (80, 80),
    ) -> s.Button:
        button = s.Button(
            "",
            size=size,
            pos=pos,
            text=text,
            text_size=18,
            scene=self,
            sorting_order=2000,
            base_color=(56, 78, 112),
            hover_color=(78, 108, 150),
            press_color=(104, 152, 214),
        )
        button.set_screen_space(True)
        button.set_position(pos, s.Anchor.CENTER)
        return button

    def _spawn_orb(self) -> s.Sprite:
        pos = (
            self.rng.randint(140, self.world_rect.width - 140),
            self.rng.randint(140, self.world_rect.height - 140),
        )
        orb = s.Sprite("", (42, 42), pos, scene=self)
        orb.set_circle_shape(21, (255, 196, 90))
        orb.sorting_order = 10
        return orb

    def _axis_from_buttons(self) -> pygame.Vector2:
        left = self._is_button_held(self.left_button) or s.input.is_pressed(pygame.K_a) or s.input.is_pressed(pygame.K_LEFT)
        right = self._is_button_held(self.right_button) or s.input.is_pressed(pygame.K_d) or s.input.is_pressed(pygame.K_RIGHT)
        up = self._is_button_held(self.up_button) or s.input.is_pressed(pygame.K_w) or s.input.is_pressed(pygame.K_UP)
        down = self._is_button_held(self.down_button) or s.input.is_pressed(pygame.K_s) or s.input.is_pressed(pygame.K_DOWN)
        return pygame.Vector2(int(right) - int(left), int(down) - int(up))

    def _is_button_held(self, button: s.Button) -> bool:
        return button.rect.collidepoint(s.input.mouse_pos) and s.input.is_mouse_pressed(1)

    def update(self, dt: float) -> None:
        direction = self._axis_from_buttons()
        speed = BOOST_SPEED if self._is_button_held(self.boost_button) or s.input.is_pressed(pygame.K_SPACE) else PLAYER_SPEED
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.player.rect.centerx += int(direction.x * speed * dt)
            self.player.rect.centery += int(direction.y * speed * dt)
            self.player.rect.clamp_ip(self.world_rect)

        collected: list[s.Sprite] = []
        for orb in self._orb_sprites:
            if self.player.rect.colliderect(orb.rect):
                collected.append(orb)

        for orb in collected:
            self._orb_sprites.remove(orb)
            orb.kill()
            self._orb_sprites.append(self._spawn_orb())
            self.score += 1
            self.score_label.text = f"Score: {self.score}"


def bootstrap_mobile_demo() -> None:
    s.set_scene(MobileOrbCollectorScene())


def run_demo(platform: str = "pygame") -> None:
    s.run(
        bootstrap_mobile_demo,
        size=(960, 640),
        title="SpritePro Mobile Demo",
        fps=60,
        fill_color=BACKGROUND_COLOR,
        platform=platform,
    )


if __name__ == "__main__":
    if "--kivy" in sys.argv:
        run_demo("kivy")
    else:
        run_demo("pygame")
