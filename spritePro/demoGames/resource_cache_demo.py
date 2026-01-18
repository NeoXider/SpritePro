import sys
from pathlib import Path
import time

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame  # noqa: E402
import spritePro as s  # noqa: E402
from spritePro.resources import resource_cache  # noqa: E402


TEXTURE_PATH = "spritePro/demoGames/Sprites/ball.png"
SOUND_PATH = "spritePro/demoGames/Audio/baunch.mp3"
ITERATIONS = 400


def _ms(seconds: float) -> float:
    return seconds * 1000.0


def _bench_texture_cache() -> tuple[float, float]:
    resource_cache.clear_textures()
    start = time.perf_counter()
    resource_cache.load_texture(TEXTURE_PATH)
    cold = _ms(time.perf_counter() - start)

    start = time.perf_counter()
    for _ in range(ITERATIONS):
        resource_cache.load_texture(TEXTURE_PATH)
    warm = _ms(time.perf_counter() - start)

    return cold, warm


def _bench_texture_no_cache() -> tuple[float, float]:
    start = time.perf_counter()
    surface = pygame.image.load(TEXTURE_PATH)
    try:
        surface = surface.convert_alpha()
    except pygame.error:
        surface = surface.convert()
    cold = _ms(time.perf_counter() - start)

    start = time.perf_counter()
    for _ in range(ITERATIONS):
        surface = pygame.image.load(TEXTURE_PATH)
        try:
            surface = surface.convert_alpha()
        except pygame.error:
            surface = surface.convert()
    warm = _ms(time.perf_counter() - start)

    return cold, warm


def _bench_sound_cache() -> tuple[float, float]:
    resource_cache.clear_sounds()
    start = time.perf_counter()
    resource_cache.load_sound(SOUND_PATH)
    cold = _ms(time.perf_counter() - start)

    start = time.perf_counter()
    for _ in range(ITERATIONS):
        resource_cache.load_sound(SOUND_PATH)
    warm = _ms(time.perf_counter() - start)

    return cold, warm


def _bench_sound_no_cache() -> tuple[float, float]:
    start = time.perf_counter()
    pygame.mixer.Sound(SOUND_PATH)
    cold = _ms(time.perf_counter() - start)

    start = time.perf_counter()
    for _ in range(ITERATIONS):
        pygame.mixer.Sound(SOUND_PATH)
    warm = _ms(time.perf_counter() - start)

    return cold, warm


def main():
    s.get_screen((800, 600), "Resource Cache Demo")

    _sprite = s.Sprite(TEXTURE_PATH, (120, 120), (400, 260))
    _title = s.TextSprite("Resource Cache Benchmark", 28, (240, 240, 240), (400, 40))
    _hint = s.TextSprite(
        "B: cache bench  |  N: no-cache bench  |  C: clear cache",
        20,
        (180, 180, 180),
        (400, 80),
    )
    texture_info = s.TextSprite("", 18, (200, 220, 255), (400, 500))
    sound_info = s.TextSprite("", 18, (200, 220, 255), (400, 535))

    def run_cached_benchmark() -> None:
        t_cold, t_warm = _bench_texture_cache()
        s_cold, s_warm = _bench_sound_cache()
        texture_info.set_text(
            f"[CACHE] Texture: cold {t_cold:.2f}ms | cached x{ITERATIONS} {t_warm:.2f}ms"
        )
        sound_info.set_text(
            f"[CACHE] Sound: cold {s_cold:.2f}ms | cached x{ITERATIONS} {s_warm:.2f}ms"
        )

    def run_no_cache_benchmark() -> None:
        t_cold, t_warm = _bench_texture_no_cache()
        s_cold, s_warm = _bench_sound_no_cache()
        texture_info.set_text(
            f"[NO CACHE] Texture: cold {t_cold:.2f}ms | reload x{ITERATIONS} {t_warm:.2f}ms"
        )
        sound_info.set_text(
            f"[NO CACHE] Sound: cold {s_cold:.2f}ms | reload x{ITERATIONS} {s_warm:.2f}ms"
        )

    run_cached_benchmark()

    while True:
        if s.input.was_pressed(pygame.K_b):
            run_cached_benchmark()
        if s.input.was_pressed(pygame.K_n):
            run_no_cache_benchmark()
        if s.input.was_pressed(pygame.K_c):
            resource_cache.clear_textures()
            resource_cache.clear_sounds()
            texture_info.set_text("Cache cleared. Press B to run benchmark.")
            sound_info.set_text("")
        s.update(fill_color=(15, 15, 15))


if __name__ == "__main__":
    main()
