"""Общие утилиты путей для editor JSON/runtime."""

from __future__ import annotations

import os
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
    else:
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
