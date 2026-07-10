"""Регрессионные тесты твинов и анимации (аудит U7-U10, C8)."""

import time

import pygame
import pytest

import spritePro as s
from spritePro.components.tween import TweenManager, FrameTween
from spritePro.components.animation import Animation


class TestTweenManagerCleanup:
    def test_completed_tweens_removed(self, clean_game):
        mgr = TweenManager()
        mgr.add_tween("t", start_value=0.0, end_value=1.0, duration=0.01)
        deadline = time.monotonic() + 2.0
        while mgr.tweens and time.monotonic() < deadline:
            mgr.update()
            time.sleep(0.005)
        assert "t" not in mgr.tweens, "завершённый твин должен удаляться из менеджера"


class TestFrameTweenLoops:
    def test_set_loops_finite(self, clean_game):
        values = []
        tween = FrameTween(0, 10, 2, on_update=values.append, auto_register=False)
        tween.loop_count = 2
        tween.loop = True
        for _ in range(50):
            tween.update()
            if not tween.is_playing:
                break
        assert not tween.is_playing, "SetLoops(2) должен останавливаться после 2 циклов"


class TestAnimationLastFrame:
    def _make_frames(self, n=4):
        frames = []
        for i in range(n):
            surf = pygame.Surface((4, 4))
            surf.fill((i * 40, 0, 0))
            frames.append(surf)
        return frames

    def test_non_loop_ends_on_last_frame(self, clean_game):
        sprite = s.Sprite("", size=(4, 4), pos=(0, 0))
        frames = self._make_frames()
        anim = Animation(sprite, frames, frame_duration=0.001, loop=False, auto_register=False)
        anim.play()
        for _ in range(100):
            anim.update()
            if not anim.is_playing:
                break
            time.sleep(0.002)
        assert not anim.is_playing
        assert anim.current_frame == len(frames) - 1, (
            "незацикленная анимация должна завершаться последним кадром"
        )

    def test_kill_unregisters(self, clean_game):
        sprite = s.Sprite("", size=(4, 4), pos=(0, 0))
        anim = Animation(sprite, self._make_frames(), frame_duration=0.1, auto_register=True)
        assert any(getattr(e, "obj", e) is anim for e in clean_game.update_objects)
        anim.kill()
        assert all(getattr(e, "obj", e) is not anim for e in clean_game.update_objects)
