"""Smoke-запуск скрипта без видимых окон (SDL dummy) с жёстким тайм-аутом.

Usage: python tools/smoke_timed.py <seconds> <path/to/script.py> [args...]
"""

import os
import sys
import threading
import time
import traceback

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

seconds = float(sys.argv[1])
path = sys.argv[2]
sys.argv = [path] + sys.argv[3:]


def _killer() -> None:
    time.sleep(seconds)
    print(f"SMOKE OK: {seconds}s without errors", flush=True)
    os._exit(0)


threading.Thread(target=_killer, daemon=True).start()

import runpy

try:
    runpy.run_path(path, run_name="__main__")
except SystemExit:
    pass
except Exception:
    traceback.print_exc()
    print("SMOKE FAIL", flush=True)
    os._exit(1)
