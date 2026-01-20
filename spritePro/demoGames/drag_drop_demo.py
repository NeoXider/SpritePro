import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class DragDropScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.title = s.TextSprite(
            "Drag & Drop Demo",
            30,
            (255, 255, 255),
            (400, 40),
            scene=self,
        )
        self.hint = s.TextSprite(
            "Drag box to slot | R: return | Q: toggle drag",
            20,
            (200, 200, 200),
            (400, 560),
            scene=self,
        )
        self.status = s.TextSprite(
            "Status: idle",
            20,
            (200, 220, 255),
            (400, 520),
            scene=self,
        )

        self.slot_left = s.Sprite("", (160, 160), (220, 300), scene=self)
        self.slot_left.set_color((50, 60, 90))
        self.slot_right = s.Sprite("", (160, 160), (580, 300), scene=self)
        self.slot_right.set_color((50, 60, 90))
        self.slot_left_label = s.TextSprite(
            "Slot A", 18, (180, 180, 200), (220, 300), scene=self
        )
        self.slot_right_label = s.TextSprite(
            "Slot B", 18, (180, 180, 200), (580, 300), scene=self
        )

        self.box = s.DraggableSprite(
            "",
            size=(90, 90),
            pos=(400, 150),
            scene=self,
            on_drag_start=self._on_drag_start,
            on_drag=self._on_drag,
            on_drag_end=self._on_drag_end,
        )
        self.box.set_color((255, 170, 100))

    def update(self, dt):
        if s.input.was_pressed(pygame.K_r):
            self.box.return_to_start()
            self.status.text = "Status: returned"
        if s.input.was_pressed(pygame.K_q):
            self.box.set_drag_enabled(not self.box.drag_enabled)
            state = "enabled" if self.box.drag_enabled else "disabled"
            self.status.text = f"Status: drag {state}"

    def _on_drag_start(self, sprite: s.DraggableSprite, world_pos, mouse_pos):
        sprite.set_color((255, 220, 120))
        self.status.text = "Status: dragging"

    def _on_drag(self, sprite: s.DraggableSprite, world_pos, mouse_pos):
        pass

    def _on_drag_end(self, sprite: s.DraggableSprite, world_pos, mouse_pos):
        target = self._get_drop_target(sprite)
        if target is not None:
            sprite.set_position(target.rect.center)
            sprite.set_color((120, 220, 160))
            self.status.text = "Status: dropped"
            return True
        sprite.set_color((255, 170, 100))
        self.status.text = "Status: rejected"
        return False

    def _get_drop_target(self, sprite: s.DraggableSprite):
        if sprite.rect.colliderect(self.slot_left.rect):
            return self.slot_left
        if sprite.rect.colliderect(self.slot_right.rect):
            return self.slot_right
        return None


def main():
    s.get_screen((800, 600), "Drag & Drop Demo")
    manager = s.get_context().scene_manager
    manager.add_scene("drag_demo", DragDropScene())
    s.scene.set_scene_by_name("drag_demo")

    while True:
        s.update(fill_color=(15, 15, 25))


if __name__ == "__main__":
    main()
