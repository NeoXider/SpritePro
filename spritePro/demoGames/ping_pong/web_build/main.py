"""Async-вход для Pygbag (генерируется spritePro.web_build)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spritePro as s
import game_entry


async def main() -> None:
    game_entry.setup()
    while True:
        s.update(fill_color=(20, 20, 30))
        await asyncio.sleep(0)
        if s.quit_requested():
            break


if __name__ == "__main__":
    asyncio.run(main())
