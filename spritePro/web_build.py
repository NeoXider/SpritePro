"""
Сборка проекта SpritePro для запуска в браузере (Pygbag / WebAssembly).

Использование через CLI: python -m spritePro.cli --webgl <путь_к_проекту>
Либо из кода: spritePro.web_build.build_web(...), build_web_archive(...).

При установке через pip (pip install spritepro) PACKAGE_ROOT указывает на
site-packages/spritePro/, откуда копируется пакет в папку сборки.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Корень пакета: в репо — spritePro/, при pip install — site-packages/spritePro/
PACKAGE_ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG = {
    "size": (800, 600),
    "title": "SpritePro Game",
    "fill_color": (20, 20, 30),
    "scene_import": "from scene import MainScene",
    "scene_var": "MainScene",
    "py_files": ["scene.py", "config.py"],
    "extra_setup": "",
}

_CONFIG_SIZE_KEYS = ("WINDOW_SIZE", "SIZE", "SCREEN_SIZE", "GAME_SIZE")
_CONFIG_TITLE_KEYS = ("TITLE", "GAME_TITLE", "WINDOW_TITLE")
_CONFIG_FILL_COLOR_KEYS = ("FILL_COLOR", "BACKGROUND_COLOR", "BG_COLOR")


def _ignore_for_web(
    directory: Path,
    names: list,
    *,
    skip_dir_name: str | None = None,
    skip_dir_parent: Path | None = None,
) -> list:
    result = [
        n
        for n in names
        if n == "__pycache__"
        or n.endswith((".pyc", ".pyo", ".mp3", ".wav"))
        or n.startswith(".")
    ]
    if skip_dir_name and skip_dir_parent is not None and Path(directory).resolve() == skip_dir_parent.resolve():
        result.append(skip_dir_name)
    return result


def _infer_from_config_module(project_dir: Path, cfg: dict[str, Any], module_name: str = "config") -> None:
    """Подтягивает size, title, fill_color из модуля конфига игры, если они там заданы."""
    module_file = project_dir / f"{module_name}.py"
    if not module_file.is_file():
        return
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        if spec is None or spec.loader is None:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for key in _CONFIG_SIZE_KEYS:
            val = getattr(mod, key, None)
            if val is not None and isinstance(val, (tuple, list)) and len(val) >= 2:
                cfg["size"] = (int(val[0]), int(val[1]))
                break
        for key in _CONFIG_TITLE_KEYS:
            val = getattr(mod, key, None)
            if val is not None and isinstance(val, str):
                cfg["title"] = val
                break
        for key in _CONFIG_FILL_COLOR_KEYS:
            val = getattr(mod, key, None)
            if val is not None and isinstance(val, (tuple, list)) and len(val) >= 3:
                cfg["fill_color"] = (int(val[0]), int(val[1]), int(val[2]))
                break
    except Exception:
        pass


def load_config(project_dir: Path) -> dict[str, Any]:
    """Загружает конфиг из webgl.json; при отсутствии size/title/fill_color подтягивает из config.py игры."""
    cfg = DEFAULT_CONFIG.copy()
    data: dict[str, Any] = {}
    config_path = project_dir / "webgl.json"
    if config_path.is_file():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            if "size" in data:
                cfg["size"] = tuple(data["size"])
            if "title" in data:
                cfg["title"] = data["title"]
            if "fill_color" in data:
                cfg["fill_color"] = tuple(data["fill_color"])
            if "scene_import" in data:
                cfg["scene_import"] = data["scene_import"]
            if "scene_var" in data:
                cfg["scene_var"] = data["scene_var"]
            if "py_files" in data:
                cfg["py_files"] = list(data["py_files"])
            if "extra_setup" in data:
                cfg["extra_setup"] = data["extra_setup"]
        except (json.JSONDecodeError, OSError) as e:
            sys.stderr.write(f"Предупреждение: не удалось прочитать {config_path}: {e}\n")
    config_module = data.get("config_module", "config")
    _infer_from_config_module(project_dir, cfg, config_module)
    return cfg


def build_web(
    project_dir: Path,
    output_dir: Path | None = None,
    config: dict[str, Any] | None = None,
) -> Path:
    """
    Подготавливает папку для веб-сборки Pygbag.

    Копирует пакет spritePro и указанные файлы игры, создаёт main.py и game_entry.py.

    Args:
        project_dir: Папка проекта (содержит scene.py, config.py и опционально webgl.json).
        output_dir: Папка вывода. По умолчанию project_dir / "web_build".
        config: Конфиг сборки. Если None, загружается из project_dir / "webgl.json" или дефолт.

    Returns:
        Путь к папке сборки (output_dir).
    """
    if output_dir is None:
        output_dir = project_dir / "web_build"
    output_dir = output_dir.resolve()
    if config is None:
        config = load_config(project_dir)

    size = config["size"]
    title = config["title"]
    fill_color = config["fill_color"]
    scene_import = config["scene_import"]
    scene_var = config["scene_var"]
    py_files = config["py_files"]
    extra_setup = config.get("extra_setup", "")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Чтобы не копировать саму папку сборки, если она внутри пакета (например demoGames/ping_pong/web_build)
    skip_web_build = None
    try:
        if output_dir.resolve().relative_to(PACKAGE_ROOT):
            skip_web_build = output_dir.name
    except ValueError:
        pass

    def ignore(directory: Path, names: list) -> list:
        return _ignore_for_web(
            directory,
            names,
            skip_dir_name=skip_web_build,
            skip_dir_parent=output_dir.parent if skip_web_build else None,
        )

    # Копируем spritePro
    spritepro_dst = output_dir / "spritePro"
    if spritepro_dst.exists():
        shutil.rmtree(spritepro_dst)
    shutil.copytree(PACKAGE_ROOT, spritepro_dst, ignore=ignore)

    # Копируем файлы игры
    for fname in py_files:
        src = project_dir / fname
        if src.is_file():
            shutil.copy2(src, output_dir / fname)

    # game_entry.py
    extra_line = f"\n    {extra_setup}" if extra_setup else ""
    game_entry_py = f'''"""Точка входа для веб-сборки (генерируется spritePro.web_build)."""
import spritePro as s
{scene_import}


def setup() -> None:
    s.get_screen({size!r}, {title!r}){extra_line}
    s.set_scene({scene_var}())
'''
    (output_dir / "game_entry.py").write_text(game_entry_py, encoding="utf-8")

    # main.py
    r, g, b = fill_color
    main_py = f'''"""Async-вход для Pygbag (генерируется spritePro.web_build)."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import spritePro as s
import game_entry


async def main() -> None:
    game_entry.setup()
    while True:
        s.update(fill_color=({r}, {g}, {b}))
        await asyncio.sleep(0)
        if s.quit_requested():
            break


if __name__ == "__main__":
    asyncio.run(main())
'''
    (output_dir / "main.py").write_text(main_py, encoding="utf-8")

    return output_dir


def build_web_archive(
    project_dir: Path,
    output_dir: Path | None = None,
    config: dict[str, Any] | None = None,
    zip_path: Path | None = None,
) -> Path:
    """
    Подготавливает веб-сборку и создаёт ZIP-архив для публикации (Яндекс Игры, itch.io и др.).

    Вызывает build_web(), затем pygbag --build --archive. В архиве в корне лежит index.html
    и все файлы билда — формат подходит для загрузки на площадки HTML5-игр.

    Args:
        project_dir: Папка проекта с webgl.json и файлами игры.
        output_dir: Папка веб-сборки. По умолчанию project_dir / "web_build".
        config: Конфиг. Если None — из webgl.json или дефолт.
        zip_path: Куда сохранить ZIP. По умолчанию <output_dir>/build/web.zip (результат pygbag).

    Returns:
        Путь к созданному ZIP-файлу.

    Raises:
        FileNotFoundError: Если pygbag не установлен (pip install spritepro[web]).
        RuntimeError: Если pygbag завершился с ошибкой.
    """
    out = build_web(project_dir, output_dir=output_dir, config=config)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pygbag", "--build", "--archive", str(out)],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            "Для сборки архива нужен pygbag. Установите: pip install spritepro[web]"
        ) from e
    if proc.returncode != 0:
        raise RuntimeError(
            f"pygbag завершился с кодом {proc.returncode}. stderr: {proc.stderr or proc.stdout}"
        )
    if zip_path and zip_path.is_file():
        return zip_path
    build_dir = out / "build"
    if zip_path:
        archive_file = zip_path
    elif (build_dir / "web.zip").is_file():
        archive_file = build_dir / "web.zip"
    else:
        zips = list(build_dir.glob("*.zip"))
        if not zips:
            raise FileNotFoundError(
                f"Архив не найден в {build_dir}. Проверьте вывод pygbag."
            )
        archive_file = zips[0]
    return archive_file
