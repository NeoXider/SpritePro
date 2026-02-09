import random
from dataclasses import replace

import pygame

import spritePro as s
from config import WIN_SCORE
from objects import Paddle, Ball


class PingPongScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.score_left = 0
        self.score_right = 0
        self.game_over = False

        self.bg = s.Sprite("", s.WH, s.WH_C, scene=self)
        self.bg.set_color((20, 20, 30))

        self.center_line = s.Sprite("", (6, int(s.WH.y)), (s.WH_C.x, s.WH_C.y), scene=self)
        self.center_line.set_color((40, 40, 55))
        self.center_line.alpha = 140

        self.left_paddle = Paddle(
            (40, s.WH_C.y), (255, 150, 150), pygame.K_w, pygame.K_s, scene=self
        )
        self.right_paddle = Paddle(
            (s.WH.x - 40, s.WH_C.y),
            (150, 150, 255),
            pygame.K_UP,
            pygame.K_DOWN,
            scene=self,
        )

        self._setup_particles()

        self.ball = Ball((s.WH_C.x, s.WH_C.y), scene=self)
        self.ball.paddles = [self.left_paddle, self.right_paddle]
        self.ball.reset(serve_dir=random.choice([-1, 1]))
        self.ball.set_trail_config(self.trail_config)
        self.ball.stop_trail()

        self.score_left_text = s.TextSprite(
            "0",
            64,
            (200, 200, 200),
            (s.WH.x * 0.25, 40),
            anchor=s.Anchor.CENTER,
            sorting_order=1000,
            scene=self,
        )
        self.score_right_text = s.TextSprite(
            "0",
            64,
            (200, 200, 200),
            (s.WH.x * 0.75, 40),
            anchor=s.Anchor.CENTER,
            sorting_order=1000,
            scene=self,
        )
        self.score_left_text.set_screen_space(True)
        self.score_right_text.set_screen_space(True)

        self._setup_game_over_panel()

        self.tweens = s.TweenManager()

        # Логи сцены отключены для тихого переключения/перезапуска

    def _setup_particles(self):
        self.trail_config = s.ParticleConfig(
            amount=6,
            lifetime_range=(0.15, 0.3),
            speed_range=(20.0, 80.0),
            angle_range=(0.0, 360.0),
            fade_speed=320.0,
            gravity=s.Vector2(0, 0),
            colors=[(220, 220, 255), (180, 220, 255)],
            sorting_order=900,
        )
        self.hit_config = s.template_sparks()
        self.hit_config.amount = 20
        self.hit_config.sorting_order = 900
        self.goal_config = s.template_fire()
        self.goal_config.amount = 28
        self.goal_config.sorting_order = 900

    def _setup_game_over_panel(self):
        self.panel = s.Sprite("", (420, 220), (s.WH_C.x, s.WH_C.y), scene=self, sorting_order=2000)
        self.panel.set_color((30, 30, 40))
        self.panel.set_image(s.utils.round_corners(self.panel.image, 20))
        self.panel.set_screen_space(True)

        self.panel_title = s.TextSprite(
            "Player Wins",
            30,
            (240, 240, 240),
            (s.WH_C.x, s.WH_C.y - 50),
            anchor=s.Anchor.CENTER,
            sorting_order=2001,
            scene=self,
        )
        self.panel_title.set_screen_space(True)

        self.panel_hint = s.TextSprite(
            "First to 2 points",
            18,
            (160, 160, 180),
            (s.WH_C.x, s.WH_C.y - 10),
            anchor=s.Anchor.CENTER,
            sorting_order=2001,
            scene=self,
        )
        self.panel_hint.set_screen_space(True)

        self.restart_button = s.Button(
            "",
            (180, 46),
            (s.WH_C.x, s.WH_C.y + 60),
            "Restart",
            text_size=22,
            base_color=(240, 240, 240),
            hover_color=(255, 255, 255),
            press_color=(200, 200, 200),
            sorting_order=2002,
        )
        self.restart_button.set_screen_space(True)
        self.restart_button.on_click(self.restart_match)

        self._set_panel_visible(False, instant=True)

    def _set_panel_visible(self, visible: bool, instant: bool = False):
        if visible:
            self.panel.set_active(True)
            self.panel_title.set_active(True)
            self.panel_hint.set_active(True)
            self.restart_button.set_active(True)
            if instant:
                self._apply_panel_anim(1.0)
            else:
                self.tweens.add_tween(
                    "panel_in",
                    0.0,
                    1.0,
                    0.35,
                    easing=s.EasingType.EASE_OUT,
                    on_update=self._apply_panel_anim,
                )
        else:
            if instant:
                self._apply_panel_anim(0.0)
                self.panel.set_active(False)
                self.panel_title.set_active(False)
                self.panel_hint.set_active(False)
                self.restart_button.set_active(False)
            else:

                def on_complete():
                    self.panel.set_active(False)
                    self.panel_title.set_active(False)
                    self.panel_hint.set_active(False)
                    self.restart_button.set_active(False)

                self.tweens.add_tween(
                    "panel_out",
                    1.0,
                    0.0,
                    0.25,
                    easing=s.EasingType.EASE_IN,
                    on_update=self._apply_panel_anim,
                    on_complete=on_complete,
                )

    def _apply_panel_anim(self, value: float):
        scale = max(0.01, value)
        alpha = int(220 * value)
        text_alpha = int(255 * value)
        self.panel.scale = scale
        self.panel.alpha = alpha
        self.panel_title.alpha = text_alpha
        self.panel_hint.alpha = int(200 * value)
        self.restart_button.alpha = text_alpha

    def _emit_particles(self, config: s.ParticleConfig, position):
        emitter = s.ParticleEmitter(config)
        particles = emitter.emit(position)
        for particle in particles:
            particle.scene = self

    def update(self, dt):
        self.bg.color = s.utils.ColorEffects.wave(0.35, ((20, 20, 30), (25, 25, 45)))

        if self.game_over:
            return

        if self.ball.bounced:
            s.debug_log_info("Ball wall bounce")
            self._emit_particles(self.hit_config, self.ball.rect.center)

        if self._ball_hits_paddle():
            s.debug_log_info("Ball paddle bounce")
            self._emit_particles(self.hit_config, self.ball.rect.center)

        if self.ball.rect.right < 0:
            self._score_point(left=False)
        elif self.ball.rect.left > s.WH.x:
            self._score_point(left=True)

    def _ball_hits_paddle(self) -> bool:
        for paddle in self.ball.paddles:
            if self.ball.rect.colliderect(paddle.rect):
                return True
        return False

    def _score_point(self, left: bool):
        if left:
            self.score_left += 1
            self.score_left_text.text = str(self.score_left)
            s.debug_log_info(f"Point for Player 1 ({self.score_left}:{self.score_right})")
            self._play_score_feedback(self.score_left_text)
        else:
            self.score_right += 1
            self.score_right_text.text = str(self.score_right)
            s.debug_log_info(f"Point for Player 2 ({self.score_left}:{self.score_right})")
            self._play_score_feedback(self.score_right_text)

        if self.score_left >= WIN_SCORE or self.score_right >= WIN_SCORE:
            winner = "Player 1" if self.score_left > self.score_right else "Player 2"
            self._finish_match(winner)
            return

        serve_dir = 1 if left else -1
        self.ball.reset(serve_dir=serve_dir)

    def _play_score_feedback(self, label: s.TextSprite) -> None:
        score_config = replace(
            self.goal_config,
            angle_range=(70.0, 110.0),
            speed_range=(140.0, 260.0),
            gravity=s.Vector2(0, 120),
            screen_space=True,
        )
        self._emit_particles(score_config, label.rect.center)
        start_scale = 0.0
        end_scale = 1.0
        label.scale = start_scale
        self.tweens.add_tween(
            f"score_scale_{id(label)}",
            start_scale,
            end_scale,
            0.4,
            easing=s.EasingType.EASE_OUT,
            on_update=lambda value: setattr(label, "scale", value),
        )

    def _finish_match(self, winner: str):
        self.game_over = True
        self.ball.set_active(False)
        self.left_paddle.set_active(False)
        self.right_paddle.set_active(False)
        self.ball.stop_trail()
        self.panel_title.text = f"{winner} wins"
        self._set_panel_visible(True)
        s.debug_log_warning(f"Game over: {winner}")

    def restart_match(self):
        self.score_left = 0
        self.score_right = 0
        self.score_left_text.text = "0"
        self.score_right_text.text = "0"
        self.game_over = False
        self.ball.set_active(True)
        self.left_paddle.set_active(True)
        self.right_paddle.set_active(True)
        self.ball.reset(serve_dir=random.choice([-1, 1]))
        self.ball.start_trail()
        self._set_panel_visible(False)
        # no log on restart

    def on_enter(self, context):
        if not self.game_over:
            self.ball.start_trail()
