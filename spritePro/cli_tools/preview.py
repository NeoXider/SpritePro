from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path


SCREEN_PRESETS: dict[str, tuple[int, int]] = {
    "phone-portrait": (360, 640),
    "phone-tall": (412, 915),
    "phone-landscape": (640, 360),
    "tablet-landscape": (1280, 720),
    "tablet-portrait": (800, 1280),
}


def preview_target_from_path(target: Path) -> Path:
    resolved = target.resolve()
    if resolved.is_file() and resolved.suffix == ".py":
        return resolved
    if resolved.is_dir():
        main_file = resolved / "main.py"
        if main_file.is_file():
            return main_file
    raise FileNotFoundError(f"Не удалось найти main.py или указанный .py файл: {target}")


def parse_preview_size(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    normalized = value.lower().replace(" ", "")
    separator = "x" if "x" in normalized else ","
    if separator not in normalized:
        raise ValueError("Размер должен быть в формате WIDTHxHEIGHT, например 360x640")
    width_str, height_str = normalized.split(separator, 1)
    width = max(1, int(width_str))
    height = max(1, int(height_str))
    return width, height


def run_preview(
    target: Path,
    *,
    platform: str,
    preset: str | None,
    size: str | None,
    extra_args: list[str],
) -> int:
    main_file = preview_target_from_path(target)
    if preset and size:
        raise ValueError("Используйте либо --screen, либо --size, но не оба сразу")

    resolved_size = parse_preview_size(size)
    if preset:
        resolved_size = SCREEN_PRESETS[preset]
    if resolved_size is None:
        resolved_size = SCREEN_PRESETS["phone-portrait"]

    env = os.environ.copy()
    env["SPRITEPRO_WINDOW_SIZE"] = f"{resolved_size[0]}x{resolved_size[1]}"
    env["SPRITEPRO_PLATFORM"] = platform
    env["SPRITEPRO_TITLE_SUFFIX"] = f"[{platform} {resolved_size[0]}x{resolved_size[1]}]"

    logging.info("Preview target: %s", main_file)
    logging.info("Platform: %s", platform)
    logging.info("Window size: %sx%s", resolved_size[0], resolved_size[1])
    if extra_args:
        logging.info("Forward args: %s", " ".join(extra_args))

    completed = subprocess.run([sys.executable, str(main_file), *extra_args], env=env)
    return completed.returncode
