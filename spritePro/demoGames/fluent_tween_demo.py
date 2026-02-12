"""Демо Fluent Tween API: DoMove, DoScale, SetEase, SetDelay, OnComplete, SetLoops, SetYoyo, Kill."""

import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def main() -> None:
    s.get_screen((900, 620), "Fluent Tween API Demo")

    box = s.Sprite("", (60, 60), (150, 300))
    box.set_color((120, 200, 255))

    box_loop = s.Sprite("", (50, 50), (450, 200))
    box_loop.set_color((255, 180, 100))

    box_kill = s.Sprite("", (50, 50), (700, 200))
    box_kill.set_color((150, 255, 150))

    title = s.TextSprite("Fluent Tween API (Do*)", 28, (255, 255, 255), (s.WH_C.x, 24))

    hints = [
        "1: DoMove  |  2: DoMoveBy  |  3: DoScale  |  4: DoRotateBy(180)  |  5: DoColor  |  6: DoFadeOut/In",
        "7: DoMove(...).SetEase(Ease.OutCubic).SetDelay(0.3).OnComplete(callback)",
        "8: DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)  — бесконечный yoyo",
        "9: DoMove (loop reset)  |  0: DoMove (loop yoyo)",
        "K: Kill(complete=False)  |  L: Kill(complete=True)  — зелёный спрайт",
        "Z: reset",
    ]
    hint_sprites = []
    for i, line in enumerate(hints):
        hint_sprites.append(s.TextSprite(line, 14, (200, 200, 200), (s.WH_C.x, 480 + i * 20)))

    _ = (title, box, box_loop, box_kill, *hint_sprites)

    base_pos = (150, 300)
    base_scale = 1.0
    base_angle = 0.0
    base_alpha = 255
    base_color = (120, 200, 255)
    base_pos_loop = (450, 200)
    base_pos_kill = (700, 200)

    active_loop_handle = None
    active_kill_handle = None

    def reset() -> None:
        nonlocal active_loop_handle, active_kill_handle
        if active_loop_handle:
            active_loop_handle.Kill(complete=False)
            active_loop_handle = None
        if active_kill_handle:
            active_kill_handle.Kill(complete=False)
            active_kill_handle = None
        box.set_position(base_pos).set_scale(base_scale).rotate_to(base_angle).set_alpha(base_alpha).set_color(base_color)
        box_loop.set_position(base_pos_loop).set_scale(1.0).set_color((255, 180, 100)).set_alpha(255)
        box_kill.set_position(base_pos_kill).set_scale(1.0).set_color((150, 255, 150)).set_alpha(255)

    while True:
        s.update(fill_color=(20, 20, 30))

        if s.input.was_pressed(pygame.K_1):
            box.DoMove((700, 300), 1.2)
        if s.input.was_pressed(pygame.K_2):
            box.DoMoveBy((80, -60), 0.8)
        if s.input.was_pressed(pygame.K_3):
            box.DoScale(1.6, 0.6)
        if s.input.was_pressed(pygame.K_4):
            box.DoRotateBy(180, 0.8)
        if s.input.was_pressed(pygame.K_5):
            box.DoColor((255, 120, 120), 0.7)
        if s.input.was_pressed(pygame.K_6):
            box.DoFadeOut(0.5).OnComplete(lambda: box.DoFadeIn(0.5))

        if s.input.was_pressed(pygame.K_7):
            box.DoMove((250, 400), 1.0).SetEase(s.Ease.OutCubic).SetDelay(0.3).OnComplete(
                lambda: None
            )

        if s.input.was_pressed(pygame.K_8):
            if active_loop_handle:
                active_loop_handle.Kill(complete=False)
            box_loop.set_position(base_pos_loop)
            box_loop.set_scale(1.0)
            active_loop_handle = box_loop.DoScale(1.5, 0.8).SetLoops(-1).SetYoyo(True)

        if s.input.was_pressed(pygame.K_9):
            if active_loop_handle:
                active_loop_handle.Kill(complete=False)
            box_loop.set_position(base_pos_loop)
            box_loop.set_scale(1.0)
            active_loop_handle = box_loop.DoMove((450, 450), 1.2).SetLoops(-1)

        if s.input.was_pressed(pygame.K_0):
            if active_loop_handle:
                active_loop_handle.Kill(complete=False)
            box_loop.set_position(base_pos_loop)
            box_loop.set_scale(1.0)
            active_loop_handle = box_loop.DoMove((450, 450), 1.2).SetLoops(-1).SetYoyo(True)

        if s.input.was_pressed(pygame.K_k):
            if active_kill_handle:
                active_kill_handle.Kill(complete=False)
            active_kill_handle = box_kill.DoMove((700, 450), 1.5)
        if s.input.was_pressed(pygame.K_l):
            if active_kill_handle:
                active_kill_handle.Kill(complete=True)
                active_kill_handle = None

        if s.input.was_pressed(pygame.K_z):
            reset()


if __name__ == "__main__":
    main()
