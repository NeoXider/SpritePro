"""HUD: счёт, длина, пинг, таблица лидеров и экран смерти."""

import spritePro as s


class HUD:
    def __init__(self, scene: s.Scene, show_ping: bool = False):
        self.scene = scene

        self.score_label = self._make_label("Score: 0", 28, (200, 200, 200), (20, 20))
        self.length_label = self._make_label("Length: 3", 22, (160, 160, 160), (20, 55))
        self._lb_title = self._make_label("Leaderboard", 22, (200, 180, 100), (20, 100))

        self.ping_label = None
        self._last_ping_text = ""
        if show_ping:
            self.ping_label = s.TextSprite(
                "Ping: -", font_size=18, color=(140, 200, 140),
                pos=(s.WH.x - 20, 20), anchor="topright", scene=scene,
            )
            self.ping_label.set_screen_space(True)
            self.ping_label.set_sorting_order(100)

        self._lb_entries: list[s.TextSprite] = []
        self._lb_texts: list[str] = []

        self._go_title = s.TextSprite(
            "", font_size=42, color=(255, 120, 120),
            pos=(s.WH_C.x, s.WH_C.y - 30), scene=scene,
        )
        self._go_title.set_screen_space(True)
        self._go_title.set_sorting_order(110)
        self._go_hint = s.TextSprite(
            "Press R to restart", font_size=24, color=(220, 220, 220),
            pos=(s.WH_C.x, s.WH_C.y + 25), scene=scene,
        )
        self._go_hint.set_screen_space(True)
        self._go_hint.set_sorting_order(110)
        s.disable_sprite(self._go_title)
        s.disable_sprite(self._go_hint)

    def _make_label(self, text: str, size: int, color, pos) -> s.TextSprite:
        label = s.TextSprite(text, font_size=size, color=color, pos=pos, anchor="topleft", scene=self.scene)
        label.set_screen_space(True)
        label.set_sorting_order(100)
        return label

    def update_leaderboard(self, entries: list[tuple[str, int]]) -> None:
        ranked = sorted(entries, key=lambda e: e[1], reverse=True)
        while len(self._lb_entries) < len(ranked):
            entry = self._make_label("", 18, (180, 180, 180), (20, 128 + 24 * len(self._lb_entries)))
            self._lb_entries.append(entry)
            self._lb_texts.append("")

        for i, (name, length) in enumerate(ranked):
            text = f"{i + 1}. {name} — {length}"
            entry = self._lb_entries[i]
            # set_text перерисовывает шрифт — обновляем только при изменении.
            if self._lb_texts[i] != text:
                self._lb_texts[i] = text
                entry.set_text(text)
            if not entry.active:
                s.enable_sprite(entry)
        for i in range(len(ranked), len(self._lb_entries)):
            if self._lb_entries[i].active:
                s.disable_sprite(self._lb_entries[i])

    def update_score(self, score: int) -> None:
        self.score_label.set_text(f"Score: {score}")

    def update_length(self, length: int) -> None:
        self.length_label.set_text(f"Length: {length}")

    def update_ping(self, ping_ms: float) -> None:
        if self.ping_label is None:
            return
        text = f"Ping: {ping_ms:.0f} ms"
        if text != self._last_ping_text:
            self._last_ping_text = text
            self.ping_label.set_text(text)

    def show_game_over(self, score: int) -> None:
        self._go_title.set_text(f"Game Over! Score: {score}")
        s.enable_sprite(self._go_title)
        s.enable_sprite(self._go_hint)
