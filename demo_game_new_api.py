import pygame
import spritePro as s


class MainScene(s.Scene):
    def on_enter(self, context):
        self.player = s.Sprite("player.png", (64, 64), (400, 300), speed=5)

    def update(self, dt):
        self.player.handle_keyboard_input()

        if s.input.was_pressed(pygame.K_SPACE):
            self.player.set_scale(1.2)
        if s.input.was_released(pygame.K_SPACE):
            self.player.set_scale(1.0)


def on_quit(event):
    print("Quit")


def main():
    s.get_screen((800, 600), "SpritePro New API")
    s.events.on("quit", on_quit)
    s.set_scene(MainScene())

    while True:
        s.update(fill_color=(20, 20, 30))


if __name__ == "__main__":
    main()
