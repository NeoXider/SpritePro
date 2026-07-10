"""Регрессионные тесты ядра Sprite (аудит C2, C6, C8, C9, C14, C15)."""

import pygame
import pytest

import spritePro as s


def make_sprite(clean_game, pos=(100, 100), size=(20, 20)):
    return s.Sprite("", size=size, pos=pos)


class TestSubpixelVelocity:
    def test_slow_velocity_accumulates(self, clean_game):
        """Скорость < 1 px/кадр не должна теряться из-за int-усечения."""
        sprite = make_sprite(clean_game)
        sprite.velocity = pygame.math.Vector2(0.5, 0)
        start_x = sprite.rect.centerx
        for _ in range(4):
            sprite.update(screen=None)
        assert sprite.rect.centerx == start_x + 2

    def test_negative_slow_velocity(self, clean_game):
        sprite = make_sprite(clean_game)
        sprite.velocity = pygame.math.Vector2(-0.25, -0.25)
        start = sprite.rect.center
        for _ in range(8):
            sprite.update(screen=None)
        assert sprite.rect.center == (start[0] - 2, start[1] - 2)


class TestResetSprite:
    def test_reset_returns_to_start_after_velocity_move(self, clean_game):
        sprite = make_sprite(clean_game, pos=(50, 60))
        sprite.velocity = pygame.math.Vector2(5, 0)
        for _ in range(10):
            sprite.update(screen=None)
        assert sprite.rect.center != (50, 60)
        sprite.reset_sprite()
        assert sprite.rect.center == (50, 60)
        assert sprite.velocity.length() == 0

    def test_set_world_position_does_not_clobber_start_pos(self, clean_game):
        sprite = make_sprite(clean_game, pos=(50, 60))
        sprite.set_world_position((200, 200))
        assert sprite.start_pos == (50, 60)
        sprite.reset_sprite()
        assert sprite.rect.center == (50, 60)

    def test_set_position_updates_start_pos(self, clean_game):
        """set_position задокументирован как обновляющий стартовые координаты."""
        sprite = make_sprite(clean_game, pos=(50, 60))
        sprite.set_position((10, 20))
        assert sprite.start_pos == (10, 20)


class TestColorNone:
    def test_color_none_does_not_crash_update_image(self, clean_game):
        sprite = make_sprite(clean_game)
        sprite.color = None
        sprite._color_dirty = True
        sprite._update_image()  # не должно бросать TypeError


class TestKillStopsTweens:
    def test_kill_clears_active_tweens_and_unregisters(self, clean_game):
        sprite = make_sprite(clean_game)
        sprite.DoMove((300, 300), duration=10.0)
        assert len(sprite._active_tweens) == 1
        registered_before = len(clean_game.update_objects)
        sprite.kill()
        assert sprite._active_tweens == []
        assert len(clean_game.update_objects) < registered_before or registered_before == 0


class TestMove:
    def test_move_with_default_speed_moves_in_pixels(self, clean_game):
        sprite = make_sprite(clean_game, pos=(100, 100))
        assert sprite.speed == 0
        sprite.move(5, -3)
        assert sprite.rect.center == (105, 97)

    def test_move_respects_speed_when_set(self, clean_game):
        sprite = make_sprite(clean_game, pos=(100, 100))
        sprite.speed = 10
        sprite.move(1, 0)
        assert sprite.rect.center == (110, 100)


class TestUpdateObjectRegistry:
    def test_register_is_idempotent(self, clean_game):
        class Obj:
            def update(self):
                pass

        obj = Obj()
        for _ in range(5):
            clean_game.register_update_object(obj)
        assert sum(1 for e in clean_game.update_objects if getattr(e, "obj", e) is obj) == 1

    def test_unregister_removes_and_allows_reregister(self, clean_game):
        class Obj:
            def update(self):
                pass

        obj = Obj()
        clean_game.register_update_object(obj)
        clean_game.unregister_update_object(obj)
        assert all(getattr(e, "obj", e) is not obj for e in clean_game.update_objects)
        clean_game.register_update_object(obj)
        assert sum(1 for e in clean_game.update_objects if getattr(e, "obj", e) is obj) == 1

    def test_self_unregistering_object_does_not_skip_neighbors(self, clean_game):
        """Объект, снимающий себя в update(), не должен ломать итерацию."""
        calls = []

        class SelfRemoving:
            def __init__(self, name):
                self.name = name

            def update(self):
                calls.append(self.name)
                s.unregister_update_object(self)

        objs = [SelfRemoving(str(i)) for i in range(3)]
        for o in objs:
            clean_game.register_update_object(o)
        clean_game.update()
        assert calls == ["0", "1", "2"]
