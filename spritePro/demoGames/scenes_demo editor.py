"""
Сцены Demo → JSON редактора → правка в редакторе → загрузка в игре (round-trip).
"""
import sys
from pathlib import Path
import random

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402
from spritePro.editor.runtime import spawn_scene


def _enter_pressed() -> bool:
    return s.input.was_pressed(pygame.K_RETURN) or s.input.was_pressed(pygame.K_KP_ENTER)


def _is_current(scene: s.Scene) -> bool:
    return s.scene.current_scene is scene


class SceneA(s.Scene):
    def __init__(self):
        super().__init__()
        rt = spawn_scene(current_dir / "scene_a.json", scene=self, apply_camera=False)

        self.label = rt.exact("label").to_text_sprite(
            text="Scene A (Press Enter)", font_size=32, color=(255, 255, 255)
        )
        self.hint = rt.exact("hint").to_text_sprite(
            text="Enter: switch  |  Tab: overlay  |  Space: toggle  |  R: restart  |  Click: button",
            font_size=22,
            color=(200, 200, 200),
        )
        self.mover = rt.exact("mover").Sprite(speed=1)
        self.button = rt.exact("button").to_button(
            text="Click me",
            text_size=22,
            base_color=(210, 210, 210),
            hover_color=(235, 235, 235),
            press_color=(180, 180, 180),
            on_click=self._on_button_click,
        )
        self.toggle = rt.exact("toggle").to_toggle(
            text_on="Toggle: ON",
            text_off="Toggle: OFF",
            text_size=20,
            color_on=(80, 180, 120),
            color_off=(180, 80, 80),
            on_toggle=self._on_toggle,
        )
        self.timer_count = 0
        self.timer_label = rt.exact("timer_label").to_text_sprite(
            text="Timer: 0", font_size=20, color=(220, 220, 220)
        )
        self.timer_label.anchor = s.Anchor.TOP_LEFT
        self.tick_timer = s.Timer(
            1.0, callback=self._tick_timer, repeat=True, autostart=True, scene=self
        )
        self.toggle_obj = rt.exact("toggle_obj").Sprite()
        self.toggle_visible = True
        self.move_tween = None
        self.anim_sprite = rt.exact("anim_sprite").Sprite()
        self.anim = s.Animation(
            self.anim_sprite,
            frames=self._make_anim_frames(),
            frame_duration=0.12,
            loop=True,
            scene=self,
        )

    def on_enter(self, context):
        if self.move_tween is None:
            self._start_random_move()
        else:
            self.move_tween.resume()
        self.anim.play()

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
            scene=self,
        )

    def _tick_timer(self):
        self.timer_count += 1
        self.timer_label.set_text(f"Timer: {self.timer_count}")

    def _on_button_click(self):
        current = self.mover.color
        self.mover.set_color((255, 200, 120) if current != (255, 200, 120) else (120, 200, 255))

    def _on_toggle(self, is_on: bool):
        self.toggle_obj.set_active(is_on)

    def _make_anim_frames(self):
        frames = []
        size = 40
        for i in range(6):
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            color = (120 + i * 20, 180, 255 - i * 20)
            pygame.draw.circle(frame, color, (size // 2, size // 2), 8 + i * 4)
            frames.append(frame)
        return frames


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
            scene=self,
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
            if getattr(p, "scene", None) is self and getattr(p, "_scene_particle", False)
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
    s.enable_debug(True)

    s.scene.add_scene("scene_a", SceneA)
    s.scene.add_scene("scene_b", SceneB)
    s.scene.set_scene_by_name("scene_a")

    # Экспорт в JSON редактора: имена = атрибуты сцены (label, mover, button, ...), данные из спрайтов.
    from spritePro.editor.scene import Scene as EditorScene

    EditorScene.export_from_runtime(SceneA, str(current_dir / "scene_a.json"))

    while True:
        s.update(fill_color=(10, 10, 20))


if __name__ == "__main__":
    main()
