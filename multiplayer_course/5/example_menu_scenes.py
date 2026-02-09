"""Пример 5: меню и сцены с готовностью.

Лобби (MenuScene) с кнопкой Ready и сетевой синхронизацией; при готовности обоих
хост шлёт start и все переходят в GameScene с движением игрока.
"""

import pygame
import spritePro as s


def _ctx() -> s.multiplayer.MultiplayerContext:
    return s.multiplayer.get_context()


class MenuScene(s.Scene):
    def on_enter(self, context):
        self.is_ready = False
        self.game_started = False
        self.ready_map = {"host": False, "client": False}

        s.TextSprite(
            "Menu", 34, (240, 240, 240), (20, 20), anchor=s.Anchor.TOP_LEFT, scene=self
        )
        self.status = s.TextSprite(
            "State: lobby",
            24,
            (220, 220, 220),
            (20, 70),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.ready_button = s.Button(
            "",
            size=(220, 60),
            pos=(400, 300),
            text="Ready: OFF",
            text_size=26,
            base_color=(230, 230, 230),
            on_click=self.toggle_ready,
            scene=self,
        )

    def toggle_ready(self):
        self.is_ready = not self.is_ready
        ctx = _ctx()
        player_key = "host" if ctx.is_host else "client"
        ctx.send("ready", {"id": player_key, "value": self.is_ready})
        self.ready_button.text_sprite.set_text(
            "Ready: ON" if self.is_ready else "Ready: OFF"
        )

    def update(self, dt):
        ctx = _ctx()
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            if event == "ready":
                player_id = data.get("id")
                if player_id in self.ready_map:
                    self.ready_map[player_id] = bool(data.get("value"))
            elif event == "start":
                self.game_started = True
                s.scene.set_scene_by_name("game")
                return

        # Хост: если оба готовы — отправляем start и переключаем сцену.
        if ctx.is_host and not self.game_started:
            if all(self.ready_map.values()):
                ctx.send("start", {})
                self.game_started = True
                s.scene.set_scene_by_name("game")
                return

        self.status.set_text(
            f"State: lobby | host={self.ready_map['host']} client={self.ready_map['client']}"
        )


class GameScene(s.Scene):
    def on_enter(self, context):
        s.TextSprite(
            "Game started",
            28,
            (240, 240, 240),
            (20, 20),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.player = s.Sprite("", (40, 40), (400, 300), speed=240, scene=self)
        ctx = _ctx()
        my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
        self.player.set_color(my_color)

    def update(self, dt):
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.player.get_world_position()
        pos.x += dx * 240.0 * dt
        pos.y += dy * 240.0 * dt
        self.player.set_position(pos)


def multiplayer_main(net: s.NetClient, role: str, color: str) -> None:
    s.multiplayer.init_context(net, role, color)
    s.get_screen((800, 600), "Lesson 5 - Menu + Scenes")
    s.scene.add_scene("menu", MenuScene)
    s.scene.add_scene("game", GameScene)
    s.scene.set_scene_by_name("menu")

    while True:
        s.update(fill_color=(16, 16, 22))


if __name__ == "__main__":
    # Запуск примера.
    s.networking.run()
