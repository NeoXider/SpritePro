"""Регрессионные тесты частиц и физики (аудит C1, C4, C5, C12, C16)."""

import pygame
import pytest

import spritePro as s
from spritePro.particles import Particle, ParticleEmitter, ParticleConfig
from spritePro.physics import PhysicsWorld, PhysicsBody, PhysicsConfig, BodyType


def _make_particle(velocity=(0.5, 0)):
    img = pygame.Surface((4, 4), pygame.SRCALPHA)
    return Particle(
        image=img,
        pos=(100, 100),
        velocity=pygame.math.Vector2(velocity),
        lifetime_ms=60_000,
        fade_speed=0.0,
        gravity=pygame.math.Vector2(0, 0),
        screen_space=True,
    )


class TestParticleSubpixel:
    def test_slow_particle_moves(self, clean_game, monkeypatch):
        monkeypatch.setattr(s, "dt", 1 / 60)
        p = _make_particle(velocity=(30, 0))  # 30 px/s = 0.5 px/кадр
        start_x = p.rect.centerx
        for _ in range(60):
            p.update(screen=None)
        moved = p.rect.centerx - start_x
        assert 25 <= moved <= 35, f"частица должна пройти ~30px за секунду, прошла {moved}"


class TestEmitterDestroy:
    def test_destroy_unregisters(self, clean_game):
        emitter = ParticleEmitter(auto_register=True)
        assert any(getattr(e, "obj", e) is emitter for e in clean_game.update_objects)
        emitter.destroy()
        assert all(getattr(e, "obj", e) is not emitter for e in clean_game.update_objects)

    def test_template_custom_attrs_copied(self, clean_game, monkeypatch):
        monkeypatch.setattr(s, "dt", 1 / 60)

        class MyParticle(Particle):
            pass

        template = _make_particle()
        template.__class__ = MyParticle
        template.my_custom_field = 42
        cfg = ParticleConfig(amount=1, particle_template=template)
        emitter = ParticleEmitter(config=cfg, auto_register=False)
        particles = emitter.emit(position=(0, 0))
        assert len(particles) == 1
        assert getattr(particles[0], "my_custom_field", None) == 42
        for p in particles:
            p.kill()
        template.kill()


class TestPhysicsEnabledToggle:
    def _world_with_sprite(self, clean_game):
        world = PhysicsWorld(gravity=900.0)
        sprite = s.Sprite("", size=(20, 20), pos=(100, 100))
        body = PhysicsBody(sprite, PhysicsConfig(body_type=BodyType.DYNAMIC))
        world.add(body)
        return world, sprite, body

    def test_disabled_body_leaves_space_and_freezes(self, clean_game):
        world, sprite, body = self._world_with_sprite(clean_game)
        sprite.active = False
        world.update(1 / 60)
        assert body.enabled is False
        assert body._body not in world._space.bodies

    def test_reenabled_body_returns_to_space(self, clean_game):
        world, sprite, body = self._world_with_sprite(clean_game)
        sprite.active = False
        world.update(1 / 60)
        sprite.active = True
        world.update(1 / 60)
        assert body.enabled is True
        assert body._body in world._space.bodies

    def test_scale_change_preserves_velocity(self, clean_game):
        world, sprite, body = self._world_with_sprite(clean_game)
        body.set_velocity(120.0, 0.0)
        world.update(1 / 60)
        sprite.scale = 1.5  # триггерит пересборку тела
        world.update(1 / 60)
        vx = body._body.velocity.x
        assert vx > 60.0, f"скорость должна сохраняться при пересборке, а не обнуляться (vx={vx})"
