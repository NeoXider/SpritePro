from __future__ import annotations

import argparse
import time
from pathlib import Path

import pygame
import spritePro as s


def _bench(label: str, iterations: int, func) -> None:
    started = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed_ms = (time.perf_counter() - started) * 1000.0 / max(1, iterations)
    print(f"{label}: {elapsed_ms:.3f} ms")


def _clear_game(game) -> None:
    for sprite in list(game.all_sprites):
        sprite.kill()


def _spawn_sprites(asset_path: str, *, count: int, offscreen: bool) -> None:
    columns = max(1, int(count**0.5))
    for index in range(count):
        x = (index % columns) * 40
        y = (index // columns) * 40
        if offscreen:
            x += 5000
            y += 5000
        s.Sprite(asset_path, size=(32, 32), pos=(x, y), auto_register=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark SpritePro frame pipeline on desktop before APK checks."
    )
    parser.add_argument("--window-width", type=int, default=2400)
    parser.add_argument("--window-height", type=int, default=1080)
    parser.add_argument("--reference-width", type=int, default=1920)
    parser.add_argument("--reference-height", type=int, default=1080)
    parser.add_argument("--sprite-count", type=int, default=400)
    parser.add_argument("--iterations", type=int, default=30)
    args = parser.parse_args()

    pygame.init()
    screen = s.get_screen(
        (args.window_width, args.window_height),
        reference_size=(args.reference_width, args.reference_height),
    )
    ctx = s._context
    game = s.get_game()
    asset_path = str(
        Path(__file__).resolve().parent / "spritePro" / "demoGames" / "Sprites" / "hero.png"
    )

    print(
        f"Window: {args.window_width}x{args.window_height} | "
        f"Reference: {args.reference_width}x{args.reference_height} | "
        f"Viewport: {ctx._viewport_rect.size} | Sprites: {args.sprite_count}"
    )

    ctx._present_frame()
    _bench(
        "present scale only",
        args.iterations * 4,
        lambda: pygame.transform.scale(ctx.screen, ctx._viewport_rect.size, ctx._present_scale_surface),
    )
    _bench(
        "present scaled blit only",
        args.iterations * 4,
        lambda: ctx._output_surface.blit(ctx._present_scale_surface, ctx._viewport_rect.topleft),
    )
    _bench(
        "present whole frame blank",
        args.iterations * 4,
        lambda: ctx._present_frame(),
    )

    _clear_game(game)
    _spawn_sprites(asset_path, count=args.sprite_count, offscreen=False)
    game.camera.update(0, 0)
    game.camera_zoom = 1.0
    _bench(
        "sprite update zoom=1 onscreen",
        args.iterations,
        lambda: game.update(screen, dt=1 / 60, wh_c=ctx.WH_C),
    )
    _bench(
        "present after zoom=1 draw",
        args.iterations,
        lambda: ctx._present_frame(),
    )

    game.camera_zoom = 1.25
    _bench(
        "sprite update zoom=1.25 onscreen",
        args.iterations,
        lambda: game.update(screen, dt=1 / 60, wh_c=ctx.WH_C),
    )
    _bench(
        "present after zoom=1.25 draw",
        args.iterations,
        lambda: ctx._present_frame(),
    )

    _clear_game(game)
    _spawn_sprites(asset_path, count=args.sprite_count, offscreen=True)
    game.camera.update(0, 0)
    game.camera_zoom = 1.25
    _bench(
        "sprite update zoom=1.25 offscreen",
        args.iterations,
        lambda: game.update(screen, dt=1 / 60, wh_c=ctx.WH_C),
    )

    pygame.display.quit()


if __name__ == "__main__":
    main()
