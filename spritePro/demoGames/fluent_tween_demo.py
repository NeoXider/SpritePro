"""Демо Fluent Tween API: DoMove, DoScale, SetEase, SetDelay, OnComplete, SetLoops, SetYoyo, Kill."""

import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class FluentTweenDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.box = s.Sprite("", (60, 60), (150, 300), scene=self)
        self.box.set_color((120, 200, 255))
        self.box_loop = s.Sprite("", (50, 50), (450, 200), scene=self)
        self.box_loop.set_color((255, 180, 100))
        self.box_kill = s.Sprite("", (50, 50), (700, 200), scene=self)
        self.box_kill.set_color((150, 255, 150))

        self.title = s.TextSprite(
            "Fluent Tween API (Do*)", 28, (255, 255, 255), (s.WH_C.x, 24), scene=self
        )
        hints = [
            "1: DoMove  |  2: DoMoveBy  |  3: DoScale  |  4: DoRotateBy(180)  |  5: DoColor  |  6: DoFadeOut/In",
            "7: DoMove(...).SetEase(Ease.OutCubic).SetDelay(0.3).OnComplete(callback)",
            "8: DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)  — бесконечный yoyo",
            "9: DoMove (loop reset)  |  0: DoMove (loop yoyo)",
            "K: Kill(complete=False)  |  L: Kill(complete=True)  — зелёный спрайт",
            "Z: reset",
        ]
        self.hint_sprites = [
            s.TextSprite(line, 14, (200, 200, 200), (s.WH_C.x, 480 + i * 20), scene=self)
            for i, line in enumerate(hints)
        ]
        self.base_pos = (150, 300)
        self.base_scale = 1.0
        self.base_angle = 0.0
        self.base_alpha = 255
        self.base_color = (120, 200, 255)
        self.base_pos_loop = (450, 200)
        self.base_pos_kill = (700, 200)
        self.active_loop_handle = None
        self.active_kill_handle = None

    def reset(self) -> None:
        if self.active_loop_handle:
            self.active_loop_handle.Kill(complete=False)
            self.active_loop_handle = None
        if self.active_kill_handle:
            self.active_kill_handle.Kill(complete=False)
            self.active_kill_handle = None
        self.box.set_position(self.base_pos).set_scale(self.base_scale).rotate_to(
            self.base_angle
        ).set_alpha(self.base_alpha).set_color(self.base_color)
        self.box_loop.set_position(self.base_pos_loop).set_scale(1.0).set_color(
            (255, 180, 100)
        ).set_alpha(255)
        self.box_kill.set_position(self.base_pos_kill).set_scale(1.0).set_color(
            (150, 255, 150)
        ).set_alpha(255)

    def update(self, dt: float) -> None:
        if s.input.was_pressed(pygame.K_1):
            self.box.DoMove((700, 300), 1.2)
        if s.input.was_pressed(pygame.K_2):
            self.box.DoMoveBy((80, -60), 0.8)
        if s.input.was_pressed(pygame.K_3):
            self.box.DoScale(1.6, 0.6)
        if s.input.was_pressed(pygame.K_4):
            self.box.DoRotateBy(180, 0.8)
        if s.input.was_pressed(pygame.K_5):
            self.box.DoColor((255, 120, 120), 0.7)
        if s.input.was_pressed(pygame.K_6):
            self.box.DoFadeOut(0.5).OnComplete(lambda: self.box.DoFadeIn(0.5))

        if s.input.was_pressed(pygame.K_7):
            self.box.DoMove((250, 400), 1.0).SetEase(s.Ease.OutCubic).SetDelay(0.3).OnComplete(
                lambda: None
            )

        if s.input.was_pressed(pygame.K_8):
            if self.active_loop_handle:
                self.active_loop_handle.Kill(complete=False)
            self.box_loop.set_position(self.base_pos_loop)
            self.box_loop.set_scale(1.0)
            self.active_loop_handle = self.box_loop.DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)

        if s.input.was_pressed(pygame.K_9):
            if self.active_loop_handle:
                self.active_loop_handle.Kill(complete=False)
            self.box_loop.set_position(self.base_pos_loop)
            self.box_loop.set_scale(1.0)
            self.active_loop_handle = self.box_loop.DoMove((450, 450), 1.2).SetLoops(-1)

        if s.input.was_pressed(pygame.K_0):
            if self.active_loop_handle:
                self.active_loop_handle.Kill(complete=False)
            self.box_loop.set_position(self.base_pos_loop)
            self.box_loop.set_scale(1.0)
            self.active_loop_handle = (
                self.box_loop.DoMove((450, 450), 1.2).SetLoops(-1).SetYoyo(True)
            )

        if s.input.was_pressed(pygame.K_k):
            if self.active_kill_handle:
                self.active_kill_handle.Kill(complete=False)
            self.active_kill_handle = self.box_kill.DoMove((700, 450), 1.5)
        if s.input.was_pressed(pygame.K_l):
            if self.active_kill_handle:
                self.active_kill_handle.Kill(complete=True)
                self.active_kill_handle = None

        if s.input.was_pressed(pygame.K_z):
            self.reset()


def main() -> None:
    s.run(
        scene=FluentTweenDemoScene,
        size=(900, 620),
        title="Fluent Tween API Demo",
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    main()
