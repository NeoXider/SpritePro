"""Проверка физики: минимальная сцена + несколько кадров (без GUI-цикла демо)."""

import sys
import os

# Без окна — только инициализация и шаги физики
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import spritePro as s

    s.get_screen((800, 600), "Physics test")
    # Минимальная сцена как в physics_demo
    player = s.Sprite("", pos=(100, 200), size=(40, 40))
    player.set_circle_shape(radius=20, color=(100, 200, 255))
    player_body = s.add_physics(player, s.PhysicsConfig(mass=1.0, bounce=0.3, friction=0.95))
    floor = s.Sprite("", pos=(400, 570), size=(800, 40))
    floor.set_rect_shape(size=(800, 40), color=(80, 80, 80))
    s.add_static_physics(floor)
    s.physics.set_bounds(s.pygame.Rect(0, 0, 800, 600))
    # Несколько шагов
    ctx = s.get_context()
    for i in range(30):
        ctx.update(60, fill_color=(20, 20, 35), update_display=False)
    assert player_body._body is not None
    print("physics_demo (minimal): 30 frames OK")

    # Hoop: мяч + ограничение
    s.physics.set_gravity(400)
    ball = s.Sprite("", pos=(400, 200), size=(30, 30))
    ball.set_circle_shape(radius=15, color=(255, 100, 100))
    ball_body = s.add_physics(ball, s.PhysicsConfig(mass=0.5, bounce=0.8, friction=0.98))
    from spritePro.demoGames.hoop_bounce_demo import HoopConstraint

    constraint = HoopConstraint(ball_body, (400, 300), 220, 15, [(255, 100, 100), (100, 255, 150)])
    s.physics.add_constraint(constraint)
    for _ in range(20):
        ctx.update(60, fill_color=(15, 15, 25), update_display=False)
    print("hoop_bounce (minimal): 20 frames OK")

    print("All physics demos (minimal): OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
