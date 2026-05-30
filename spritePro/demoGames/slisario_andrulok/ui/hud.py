import spritePro as s
from game.config import BOT_COUNT


class HUD:
    def __init__(self, scene: s.Scene):
        self.scene = scene
        self.score_label = s.TextSprite(
            "Score: 0",
            font_size=28,
            color=(200, 200, 200),
            pos=(20, 20),
            scene=scene,
        )
        self.score_label.set_position((20, 20), anchor="topleft")
        self.score_label.set_screen_space(True)
        self.score_label.set_sorting_order(100)

        self.length_label = s.TextSprite(
            "Length: 5",
            font_size=22,
            color=(160, 160, 160),
            pos=(20, 55),
            scene=scene,
        )
        self.length_label.set_position((20, 55), anchor="topleft")
        self.length_label.set_screen_space(True)
        self.length_label.set_sorting_order(100)

        self._lb_title = s.TextSprite(
            "Leaderboard",
            font_size=22, color=(200, 180, 100),
            pos=(20, 100), scene=scene,
        )
        self._lb_title.set_position((20, 100), anchor="topleft")
        self._lb_title.set_screen_space(True)
        self._lb_title.set_sorting_order(100)

        self._lb_entries: list[s.TextSprite] = []
        for _ in range(1 + BOT_COUNT):
            entry = s.TextSprite("", font_size=18, color=(180, 180, 180), pos=(20, 0), scene=scene)
            entry.set_position((20, 0), anchor="topleft")
            entry.set_screen_space(True)
            entry.set_sorting_order(100)
            self._lb_entries.append(entry)

    def update_leaderboard(self, snakes: list) -> None:
        sorted_snakes = sorted(snakes, key=lambda x: len(x[1].segments), reverse=True)
        y = 128
        for i, (name, snake) in enumerate(sorted_snakes):
            if i >= len(self._lb_entries):
                break
            entry = self._lb_entries[i]
            entry.set_text(f"{i+1}. {name} — {len(snake.segments)}")
            entry.set_position((20, y), anchor="topleft")
            entry.set_screen_space(True)
            if not entry.active:
                s.enable_sprite(entry)
            y += 24
        for i in range(len(sorted_snakes), len(self._lb_entries)):
            entry = self._lb_entries[i]
            if entry.active:
                s.disable_sprite(entry)

    def update_score(self, score: int) -> None:
        self.score_label.set_text(f"Score: {score}")

    def update_length(self, length: int) -> None:
        self.length_label.set_text(f"Length: {length}")

    def show_game_over(self, score: int) -> None:
        self.score_label.set_text(f"Game Over! Score: {score}")
        self.score_label.set_position((s.WH_C.x, s.WH_C.y - 20))
        self.score_label.set_sorting_order(100)

        self.length_label.set_screen_space(True)
        self.length_label.set_text("Press R to restart")
        self.length_label.set_position((s.WH_C.x, s.WH_C.y + 20))

    def clear(self) -> None:
        for spr in [self.score_label, self.length_label, self._lb_title] + self._lb_entries:
            if spr.active:
                s.disable_sprite(spr)
