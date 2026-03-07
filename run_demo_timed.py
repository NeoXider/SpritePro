"""Запуск демо на несколько секунд для проверки отсутствия ошибок при старте."""

import sys
import threading
import time


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_demo_timed.py <seconds> <demo_module_path>")
        sys.exit(2)
    seconds = float(sys.argv[1])
    path = sys.argv[2]
    err = []

    def run():
        try:
            import runpy

            runpy.run_path(path, run_name="__main__")
        except Exception as e:
            err.append(e)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(seconds)
    if err:
        raise err[0]
    print("OK: no errors in", seconds, "s")


if __name__ == "__main__":
    main()
