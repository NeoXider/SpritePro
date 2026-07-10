"""Запуск демо с реальным окном и скриншот через N секунд (для визуальной проверки)."""

import subprocess
import sys
import time
from pathlib import Path

from PIL import ImageGrab


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python visual_check.py <seconds> <demo_path> <out_png>")
        return 2
    seconds = float(sys.argv[1])
    demo = sys.argv[2]
    out_png = sys.argv[3]

    env = dict(**__import__("os").environ)
    env.pop("SDL_VIDEODRIVER", None)
    env["SDL_VIDEO_WINDOW_POS"] = "60,60"

    proc = subprocess.Popen(
        [sys.executable, demo],
        cwd=str(Path(demo).resolve().parents[2]),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    time.sleep(seconds)
    if proc.poll() is not None:
        err = proc.stderr.read().decode(errors="replace")[-800:]
        print(f"DIED rc={proc.returncode}\n{err}")
        return 1
    img = ImageGrab.grab()
    img.save(out_png)
    proc.kill()
    print("SHOT", out_png)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
