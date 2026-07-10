"""Общие утилиты путей для editor JSON/runtime."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


def _normalize_raw_path(raw_path: str | Path | None) -> str:
    if raw_path is None:
        return ""
    return str(raw_path).strip()


def _to_path(value: str | Path | None) -> Optional[Path]:
    raw = _normalize_raw_path(value)
    if not raw:
        return None
    return Path(raw).expanduser()


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for candidate in paths:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def _caller_dir_outside_package() -> Optional[Path]:
    """Папка первого файла в стеке вызовов вне пакета spritePro."""
    package_dir = str(Path(__file__).resolve().parents[1])
    frame = sys._getframe(1)
    while frame is not None:
        file = frame.f_globals.get("__file__")
        if file:
            resolved = str(Path(file).resolve())
            if not resolved.startswith(package_dir):
                return Path(resolved).parent
        frame = frame.f_back
    return None


def resolve_scene_path(raw_path: str | Path) -> Path:
    """Находит файл сцены по имени или относительному пути (как для спрайтов).

    Ищет по кандидатам: как есть, рядом со скриптом вызывающего, в его
    подпапках scenes/ и assets/, затем то же от cwd и от главного скрипта.
    Расширение .json можно не указывать.

    Raises:
        FileNotFoundError: С перечнем проверенных путей.
    """
    raw = _normalize_raw_path(raw_path)
    path = Path(raw).expanduser()
    names = [path]
    if path.suffix.lower() != ".json":
        names.append(path.with_name(path.name + ".json"))

    bases: list[Path] = []
    caller_dir = _caller_dir_outside_package()
    if caller_dir is not None:
        bases.append(caller_dir)
    bases.append(Path.cwd())
    main_script = sys.argv[0] if sys.argv and sys.argv[0] else ""
    if main_script:
        try:
            bases.append(Path(main_script).resolve().parent)
        except OSError:
            pass

    candidates: list[Path] = []
    for name in names:
        if name.is_absolute():
            candidates.append(name)
            continue
        for base in bases:
            candidates.append(base / name)
            candidates.append(base / "scenes" / name.name)
            candidates.append(base / "assets" / name.name)

    for candidate in _dedupe_paths(candidates):
        try:
            if candidate.is_file():
                return candidate.resolve()
        except OSError:
            continue
    tried = "\n  ".join(str(c) for c in _dedupe_paths(candidates))
    raise FileNotFoundError(f"Сцена '{raw}' не найдена. Проверены пути:\n  {tried}")


def resolve_sprite_path(
    raw_path: str | Path | None,
    *,
    scene_path: str | Path | None = None,
    project_root: str | Path | None = None,
    assets_folder: str | Path | None = None,
    cwd: str | Path | None = None,
) -> Optional[Path]:
    raw = _normalize_raw_path(raw_path)
    if not raw:
        return None

    cleaned = raw.replace("\\", "/")
    path = Path(cleaned)
    basename = Path(cleaned).name
    scene_file = _to_path(scene_path)
    project_dir = _to_path(project_root)
    assets_dir = _to_path(assets_folder)
    cwd_path = _to_path(cwd) or Path.cwd()

    candidates: list[Path] = []
    if path.is_absolute():
        candidates.append(path)
        # Абсолютный путь с другой машины: ищем файл по basename рядом
        # со сценой и в assets, иначе сцена непереносима между ПК
        rel_fallback = Path(basename) if basename else None
        if rel_fallback is not None:
            path = rel_fallback
    if not path.is_absolute():
        if scene_file is not None:
            scene_dir = scene_file.resolve().parent
            candidates.append(scene_dir / path)
            if basename:
                candidates.append(scene_dir / basename)
        if assets_dir is not None:
            candidates.append(assets_dir / path)
            if basename:
                candidates.append(assets_dir / basename)
            candidates.append(assets_dir / "images" / path)
            if basename:
                candidates.append(assets_dir / "images" / basename)
        if project_dir is not None:
            candidates.append(project_dir / path)
            if basename:
                candidates.append(project_dir / basename)
            candidates.append(project_dir / "assets" / path)
            if basename:
                candidates.append(project_dir / "assets" / basename)
            candidates.append(project_dir / "assets" / "images" / path)
            if basename:
                candidates.append(project_dir / "assets" / "images" / basename)
        candidates.append(cwd_path / path)
        if basename:
            candidates.append(cwd_path / basename)
        candidates.append(cwd_path / "assets" / path)
        if basename:
            candidates.append(cwd_path / "assets" / basename)
        candidates.append(cwd_path / "assets" / "images" / path)
        if basename:
            candidates.append(cwd_path / "assets" / "images" / basename)

    for candidate in _dedupe_paths(candidates):
        try:
            if candidate.exists():
                return candidate.resolve()
        except OSError:
            continue
    return None


def normalize_sprite_path(
    raw_path: str | Path | None,
    *,
    source_scene_path: str | Path | None = None,
    target_scene_path: str | Path | None = None,
    project_root: str | Path | None = None,
    assets_folder: str | Path | None = None,
    prefer_relative: bool = True,
) -> str:
    raw = _normalize_raw_path(raw_path)
    if not raw:
        return ""

    resolved = resolve_sprite_path(
        raw,
        scene_path=source_scene_path,
        project_root=project_root,
        assets_folder=assets_folder,
    )
    if resolved is None:
        return raw.replace("\\", "/")

    base_scene = _to_path(target_scene_path) or _to_path(source_scene_path)
    if prefer_relative and base_scene is not None:
        try:
            relative = os.path.relpath(str(resolved), start=str(base_scene.resolve().parent))
            return Path(relative).as_posix()
        except ValueError:
            pass

    return str(resolved).replace("\\", "/")
