import pygame
import spritePro as s


class MainScene(s.Scene):
    def on_enter(self, context):
        self.player = s.Sprite("assets/player.png", (64, 64), (400, 300), speed=5)

    def update(self, dt):
        self.player.handle_keyboard_input()
        if s.input.was_pressed(pygame.K_SPACE):
            s.debug_log_info("Space pressed")


def main():
    s.get_screen((800, 600), "My SpritePro Game")
    s.enable_debug(True)
    s.debug_log_info("Game started")
    s.set_scene(MainScene())

    while True:
        s.update(fill_color=(20, 20, 30))

if __name__ == "__main__":
    main()