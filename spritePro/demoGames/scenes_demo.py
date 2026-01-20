import sys
from pathlib import Path
import random

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def _enter_pressed() -> bool:
    return s.input.was_pressed(pygame.K_RETURN) or s.input.was_pressed(
        pygame.K_KP_ENTER
    )


def _is_current(scene: s.Scene) -> bool:
    return s.scene.current_scene is scene


class SceneA(s.Scene):
    def __init__(self):
        super().__init__()
        self.label = s.TextSprite(
            "Scene A (Press Enter)",
            32,
            (255, 255, 255),
            (400, 300),
            scene=self,
        )
        self.hint = s.TextSprite(
            "Enter: switch  |  Tab: overlay  |  Space: toggle  |  R: restart  |  Mover: tween",
            22,
            (200, 200, 200),
            (400, 540),
            scene=self,
        )
        self.mover = s.Sprite("", (60, 60), (150, 300), speed=1, scene=self)
        self.mover.set_color((120, 200, 255))
        self.toggle_obj = s.Sprite("", (100, 40), (650, 120), scene=self)
        self.toggle_obj.set_color((255, 180, 90))
        self.toggle_visible = True
        self.move_tween = None

    def on_enter(self, context):
        if self.move_tween is None:
            self._start_random_move()
        else:
            self.move_tween.resume()

    def update(self, dt):
        if _enter_pressed():
            s.scene.set_scene_by_name("scene_b")
            return
        if s.input.was_pressed(pygame.K_TAB):
            if s.scene.is_scene_active("scene_b"):
                s.scene.deactivate_scene("scene_b")
            else:
                s.scene.activate_scene("scene_b")
        if s.input.was_pressed(pygame.K_SPACE):
            self.toggle_visible = not self.toggle_visible
            self.toggle_obj.set_active(self.toggle_visible)
        if s.input.was_pressed(pygame.K_r):
            s.scene.restart_current(s.get_context())

    def on_exit(self):
        if self.move_tween is not None:
            self.move_tween.pause()

    def _start_random_move(self):
        start = self.mover.rect.center
        target = (random.randint(60, 740), random.randint(100, 480))

        def apply_pos(value):
            self.mover.rect.center = (int(value.x), int(value.y))

        self.move_tween = s.Tween(
            start,
            target,
            1.0,
            easing=s.EasingType.EASE_OUT,
            on_update=apply_pos,
            on_complete=self._start_random_move,
            value_type="vector2",
        )


class SceneB(s.Scene):
    def __init__(self):
        super().__init__()
        self.order = 10
        self.label = s.TextSprite(
            "Scene B (Press Enter)",
            32,
            (255, 255, 0),
            (400, 300),
            scene=self,
        )
        self.info = s.TextSprite(
            "Random fireworks",
            24,
            (200, 220, 255),
            (400, 40),
            scene=self,
        )
        self.hint = s.TextSprite(
            "Enter: switch (current)  |  R: restart",
            22,
            (200, 200, 200),
            (400, 540),
            scene=self,
        )
        self.fire_timer = s.Timer(
            random.uniform(0.4, 1.2),
            callback=self._spawn_firework,
            repeat=False,
            autostart=False,
        )

    def on_enter(self, context):
        if self.fire_timer:
            self.fire_timer.start(random.uniform(0.4, 1.2))

    def update(self, dt):
        if _enter_pressed() and _is_current(self):
            s.scene.set_scene_by_name("scene_a")
            return
        if s.input.was_pressed(pygame.K_r):
            s.scene.restart_current(s.get_context())
        if self.fire_timer.done:
            self.fire_timer.start(random.uniform(0.4, 1.2))

    def on_exit(self):
        if self.fire_timer:
            self.fire_timer.stop()
        # Удаляем все частицы этой сцены (чтобы не "протекали" в другую)
        candidates = s.get_sprites_by_class(s.Sprite, active_only=False)
        to_kill = [
            p
            for p in candidates
            if getattr(p, "scene", None) is self
            and getattr(p, "_scene_particle", False)
        ]
        for particle in to_kill:
            particle.kill()

    def _spawn_firework(self):
        if not self.is_active:
            if self.fire_timer:
                self.fire_timer.stop()
            return
        pos = (random.randint(100, 700), random.randint(120, 520))
        emitter = s.ParticleEmitter(s.template_sparks())
        particles = emitter.emit(pos)
        for particle in particles:
            particle.scene = self
            particle._scene_particle = True


def main():
    s.get_screen((800, 600), "Scenes Demo")
    s.scene.add_scene("scene_a", SceneA)
    s.scene.add_scene("scene_b", SceneB)
    s.scene.set_scene_by_name("scene_a")

    while True:
        s.update(fill_color=(10, 10, 20))


if __name__ == "__main__":
    main()
