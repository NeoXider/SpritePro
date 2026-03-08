from __future__ import annotations

import argparse
import time

import pygame


def _print_color_format_probe() -> None:
    probe = pygame.Surface((2, 2), 0, 24)
    print("Color probe for raw pygame 24-bit surface bytes:")
    for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255), (10, 20, 30)):
        probe.fill(color)
        raw = list(memoryview(probe.get_buffer())[:3])
        rgb = list(pygame.image.tostring(probe, "RGB")[:3])
        print(f"  color={color} raw={raw} rgb={rgb}")
    print("Recommended Kivy colorfmt for raw 24-bit pygame buffer: bgr")


def _bench(label: str, iterations: int, func) -> None:
    started = time.perf_counter()
    for _ in range(iterations):
        func()
    elapsed_ms = (time.perf_counter() - started) * 1000.0 / max(1, iterations)
    print(f"{label}: {elapsed_ms:.3f} ms")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark heavy present-path operations used by SpritePro mobile/desktop runtime."
    )
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--output-width", type=int, default=1920)
    parser.add_argument("--output-height", type=int, default=864)
    parser.add_argument("--iterations", type=int, default=120)
    args = parser.parse_args()

    pygame.init()
    source = pygame.Surface((args.width, args.height), pygame.SRCALPHA, 32)
    source.fill((40, 80, 120, 255))
    output = pygame.Surface((args.output_width, args.output_height), 0, 24)
    scale_dest = pygame.Surface((args.output_width, args.output_height), pygame.SRCALPHA, 32)
    rgb_surface = pygame.Surface((args.output_width, args.output_height), 0, 24)
    rgb_surface.fill((30, 50, 70))
    surface_view = memoryview(rgb_surface.get_view("0"))
    src24 = pygame.Surface((args.width, args.height), 0, 24)
    src24.fill((40, 80, 120))
    dst24 = pygame.Surface((args.output_width, args.output_height), 0, 24)
    dst32 = pygame.Surface((args.output_width, args.output_height), pygame.SRCALPHA, 32)

    crop_y = int(round((args.output_height - args.height) / 2))

    print(
        f"Input: {args.width}x{args.height} | Output: {args.output_width}x{args.output_height} | "
        f"Iterations: {args.iterations}"
    )
    _print_color_format_probe()
    _bench(
        "pygame.image.tostring(rgb_surface, 'RGB')",
        args.iterations,
        lambda: pygame.image.tostring(rgb_surface, "RGB"),
    )
    _bench(
        "memoryview(surface.get_view('0')) reused",
        args.iterations,
        lambda: surface_view,
    )
    _bench(
        "pygame.transform.scale(new surface)",
        args.iterations,
        lambda: pygame.transform.scale(source, (args.output_width, args.output_height)),
    )
    _bench(
        "pygame.transform.scale(reused dest)",
        args.iterations,
        lambda: pygame.transform.scale(source, (args.output_width, args.output_height), scale_dest),
    )
    _bench(
        "cropped blit 32->24",
        args.iterations,
        lambda: output.blit(source, (0, crop_y)),
    )
    _bench(
        "cropped blit 32->32",
        args.iterations,
        lambda: dst32.blit(source, (0, crop_y)),
    )
    _bench(
        "cropped blit 24->24",
        args.iterations,
        lambda: dst24.blit(src24, (0, crop_y)),
    )


if __name__ == "__main__":
    main()
